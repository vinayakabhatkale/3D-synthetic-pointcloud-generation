import open3d as o3d

def main():
    pcd = o3d.io.read_point_cloud('./test.pcd')
    mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5)
    o3d.visualization.draw_geometries([pcd, mesh_frame])

if __name__=='__main__':
    main()
