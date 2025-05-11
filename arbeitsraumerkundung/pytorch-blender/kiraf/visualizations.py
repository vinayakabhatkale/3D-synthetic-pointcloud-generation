import open3d as o3d
import h5py
import numpy as np
import sys
import glob
import os


class Visualizations:
    def __init__(self):
        # TODO not that hardcoded colors
        self.possible_colors = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 0],
            [0, 1, 1]
            ]

    def visualize_point_cloud(self, filename: str, from_hdf: bool=True, show_labels: bool=False) -> None:
        if from_hdf is True:
            x,y,z,r,g,b,label = self._import_from_hdf(filename)
        
        for idx in range(x.shape[0]):
            labels = label[idx].astype(int)
            points = np.stack((x[idx], y[idx], z[idx]), axis=1)

            if show_labels is True:
                point_colors = list()
                label_list = labels.tolist()
                map_label_to_color = lambda i: self.possible_colors[i]
                point_colors = list(map(map_label_to_color, label_list))
            else:
                point_colors = np.stack((r[idx], g[idx], b[idx]), axis=1)

            print(f'Point cloud contains {len(point_colors)} points')
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points)
            pcd.colors = o3d.utility.Vector3dVector(point_colors)

            #indices = [i for i, x in enumerate(point_colors) if x == [0,0,1]]
            #shadow_board_pcl = pcd.select_by_index(indices)

            pcd.estimate_normals()
            #self._vis_point_cloud(pcd)
            radii = [0.005, 0.01, 0.02, 0.04]
            rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
                pcd, o3d.utility.DoubleVector(radii))
            
            #for extension in ['.ply', '.obj', '.glb']:
            #    o3d.io.write_triangle_mesh(f'/home/andi/reconstructed{extension}', rec_mesh)
            o3d.visualization.draw_geometries([pcd, rec_mesh])

    def visualize_point_cloud2(self, points: np.ndarray= None, point_labels: np.ndarray=None, filename: str=None, from_hdf: bool=True) -> None:
        if from_hdf is True:
            x,y,z,label = self._import_from_hdf(filename)
        elif points is not None:
            x = points[:, 0]
            y = points[:, 1]
            z = points[:, 2]
            label = point_labels

        point_colors = list()
        label_list = label.tolist()
        map_label_to_color = lambda i: self.possible_colors[i]
        point_colors = list(map(map_label_to_color, label_list))

        print(f'Point cloud contains {len(point_colors)} points')
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points[:, :3])
        pcd.colors = o3d.utility.Vector3dVector(point_colors)
        self._vis_point_cloud(pcd)

    def _vis_point_cloud(self, pcd: o3d.geometry.PointCloud) -> None:
        """
            visualize point cloud with open3d standard visualizer
        """
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        vis.add_geometry(pcd)
        view_ctl = vis.get_view_control()
        view_ctl.set_front((1, 1, 0))
        view_ctl.set_up((0, -1, -1))
        view_ctl.set_lookat(pcd.get_center())
        vis.run()
        vis.destroy_window()



    def _import_from_hdf(self, filename):
        """
        import point cloud from hdf file format
        :return x,y,z, label
        """ 
        f = h5py.File(filename)
        x = f['location_x']
        y = f['location_y']
        z = f['location_z']
        r = f['color_r']
        g = f['color_g']
        b = f['color_b']
        label = f['categoryID']

        return np.array(x), np.array(y), np.array(z), np.array(r), np.array(g), np.array(b), np.array(label)



if __name__ == '__main__':
    viz = Visualizations()
    #data = np.load(sys.argv[1])
    #labels = data[:,0]
    #points = data[:,1:]
    #print(labels.shape)
    #print(points.shape)
    # hdf
    #viz.visualize_point_cloud(filename=sys.argv[1])

    # numpy

    #if os.path.isdir(sys.argv[1]):
    #    file_list = glob.glob(sys.argv[1] + '*.hdf5')
    #    for f in file_list:
    #        print(f)
    #        viz.visualize_point_cloud(filename=f)
    #elif os.path.isfile(sys.argv[1]):
    #    viz.visualize_point_cloud(filename=sys.argv[1])
    viz.visualize_point_cloud(filename='/home/andi/surface_reconstruction_frames_1_to_1_merged.hdf5')
