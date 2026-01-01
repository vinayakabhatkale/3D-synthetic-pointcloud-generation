import open3d as o3d

def main():
    origin = o3d.geometry.TriangleMesh.create_coordinate_frame(size=2, origin=(3,3,3))

    test = o3d.geometry.TriangleMesh.create_coordinate_frame(size=2, origin=(3,3,3))
    r_matrix = test.get_rotation_matrix_from_xyz((0,0,3.1415/2.))
    test.rotate(r_matrix, center=(3,3,3))
    o3d.visualization.draw_geometries([origin, test])

if __name__ == '__main__':
    main()