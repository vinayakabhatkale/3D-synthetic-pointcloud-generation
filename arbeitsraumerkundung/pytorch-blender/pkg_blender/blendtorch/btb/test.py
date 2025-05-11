import open3d as o3d
import numpy as np

def main():
    origin = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=(0,0,0))
    cam = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=(0,0,0))

    # transformation matrix
    T = np.eye(4)

    x,y,z = (1.2890441417694092, -0.1610880047082901, 1.955739974975586)

    # translation
    T[0,3] = x
    T[1,3] = y
    T[2,3] = z

    rx, ry, rz = (-2.507345024585724, -0.0859069973230362, -1.9421099424362183)

    rot_mat = o3d.geometry.TriangleMesh.get_rotation_matrix_from_xyz((rx, ry, rz))
    T[:3,:3] = rot_mat

    # wrong transformation
    cam.transform(T)

    # visualize
    o3d.visualization.draw_geometries([origin, cam])

    rot_mat = o3d.geometry.TriangleMesh.get_rotation_matrix_from_xyz((rx, ry,0))
    z_rot_mat = o3d.geometry.TriangleMesh.get_rotation_matrix_from_xyz((0, 0, rz))
    T[:3,:3] = rot_mat

    # correct transformation
    cam = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=(0,0,0))

    # transformation like seen in blender
    cam.transform(T)
    cam.rotate(z_rot_mat)

    o3d.visualization.draw_geometries([origin, cam])


if __name__ == "__main__":
    main()

