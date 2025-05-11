import open3d as o3d

def main():
    pcl = o3d.io.read_point_cloud('./test.pcd')
    o3d.visualization.draw_geometries([pcl])

if __name__ == '__main__':
    main()