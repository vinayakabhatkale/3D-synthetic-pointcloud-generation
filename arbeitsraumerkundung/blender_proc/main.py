import blenderproc as bproc
import argparse
import numpy as np
from scipy.spatial.transform import Rotation as R

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('camera', nargs='?', default="examples/resources/camera_positions", help="Path to the camera file")
    parser.add_argument('scene', nargs='?', default="examples/basics/semantic_segmentation/scene.blend", help="Path to the scene.obj file")
    parser.add_argument('output_dir', nargs='?', default="examples/basics/semantic_segmentation/output", help="Path to where the final files, will be saved")
    args = parser.parse_args()
    
    return args

def init_bproc(args):

    bproc.init()

    # load the objects into the scene
    objs = bproc.loader.load_blend(args.scene)

    # define a light and set its location and energy level
    light = bproc.types.Light()
    light.set_type("POINT")
    light.set_location([5, -5, 5])
    light.set_energy(1000)

    # define the camera intrinsics
    k_matrix = np.array([[322,0,178], \
                         [0,322,320], \
                         [0,0,1]])
    #bproc.camera.set_resolution(512, 512)
    bproc.camera.set_intrinsics_from_K_matrix(k_matrix, image_width=640,
            image_height=360)

    matrices = list()
    # read the camera positions file and convert into homogeneous camera-world transformation
    with open(args.camera, "r") as f:
        for line in f.readlines():
            line = [float(x) for x in line.split()]
            position, euler_rotation = line[:3], line[3:6]
            matrix_world = bproc.math.build_transformation_mat(position, euler_rotation)
            matrices.append(matrix_world)
            bproc.camera.add_camera_pose(matrix_world)

    # activate depth rendering
    bproc.renderer.enable_depth_output(activate_antialiasing=False)
#    bproc.renderer.enable_normals_output()
    return matrices

def render(with_seg: bool=True) -> dict:
    # render the whole pipeline
    data = bproc.renderer.render()

    if with_seg is True:
        # Render segmentation masks (per class and per instance)
        data.update(bproc.renderer.render_segmap(map_by=["class", "instance", "name"]))

    return data

def write_output(data):
    # write the data to a .hdf5 container
    bproc.writer.write_hdf5(args.output_dir, data)

def get_diff_mat(matrix_1, matrix_2):
    r1 = R.from_matrix(matrix_1[:3, :3])
    r2 = R.from_matrix(matrix_2[:3, :3])

    print(matrix_1)
    print()
    print(matrix_2)
    euler_rot1 = r1.as_euler('xyz')
    euler_rot2 = r2.as_euler('xyz')


    diff_rot = euler_rot1 - euler_rot2
    #rot_mat = R.from_euler('xyz', diff_rot).as_matrix()
    rot_mat = R.from_euler('z', [-25], degrees=True).as_matrix()

    diff_mat = np.identity(4, dtype=np.float64)
    diff_mat[:3, :3] = np.matmul(matrix_2[:3, :3], matrix_1[:3, :3].T)
    return diff_mat
    

def visualize_point_cloud(data, matrices):
    point_cloud = bproc.point_cloud.PointCloud()
    depth_data = data['depth']

    sem_data = data['class_segmaps']
    #normals = data['normals']
    intrinsics = bproc.camera.get_intrinsics_as_K_matrix()
    points, labels = point_cloud.point_cloud_from_depth_data(depth_data, intrinsics,
            sem_data)

    for idx, pcl in enumerate(points):
        if idx == 0:
            break
        # get rotation between point clouds
        diff_mat = get_diff_mat(matrices[idx-1], matrices[idx])
        new_point_cloud = list()
        printed = False
        count = 0
        for point in pcl:
            hom_point = np.array([0.,0.,0.,1.], dtype=np.float64)
            hom_point[:3] = point
            new_point = np.matmul(diff_mat, hom_point.T)
            new_point_cloud.append(new_point[:3])
        # replace old point cloud
        points[idx] = new_point_cloud

    point_colors = list()
    possible_colors = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 0],
            [0, 1, 1]
            ]

    #for i in range(sem_data[0].shape[0]):
    #    for j in range(sem_data[0].shape[1]):
    #        label = sem_data[0][i][j]
    #        point_colors.append(possible_colors[label])
    #point_colors.append(
    #        [[1,0,0] for _ in range(len(points[0]))]
    #        )
    #point_colors.append(
    #        [[0,1,0] for _ in range(len(points[1]))]
    #        )
    #point_colors.append(
    #        [[0,0,1] for _ in range(len(points[2]))]
    #        )   

    pcl = list()
    for cloud in points:
        pcl += cloud
    pcl = points[0] 
    colors_pcl = list()
    for color in point_colors:
       colors_pcl += color
    print(len(points[0]), len(point_colors))
    #pcls = point_cloud.merge_points_and_colors(points, point_colors, normals)
    #pcds = point_cloud.merge_point_clouds(pcls)
    point_cloud.visualize_point_cloud(pcl, labels[0])
     
    

if __name__ == "__main__":
    args = parse_args()
    matrices = init_bproc(args)
    data = render()
    visualize_point_cloud(data, matrices)
    #write_output(data)
