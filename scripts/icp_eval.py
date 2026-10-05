import argparse, numpy as np, cv2, open3d as o3d
from src.lidar import load_intrinsics, load_odometry, depth_to_points, pose_matrix
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("capture")
ap.add_argument("--frame-a",default="000800")
ap.add_argument("--frame-b",default="000820")
args=ap.parse_args()
d=Path(args.capture); K=load_intrinsics(d/"camera_matrix.csv"); odo=load_odometry(d/"odometry.csv")
def one(name):
    depth=cv2.imread(str(d/"depth"/f"{name}.png"),cv2.IMREAD_UNCHANGED)
    pts=depth_to_points(depth,K)
    row=odo.iloc[min(int(name),len(odo)-1)]
    T=pose_matrix(row); return (T[:3,:3]@pts.T).T+T[:3,3]
a=one(args.frame_a); b=one(args.frame_b)
pa=o3d.geometry.PointCloud(); pb=o3d.geometry.PointCloud()
pa.points=o3d.utility.Vector3dVector(a); pb.points=o3d.utility.Vector3dVector(b)
pa=pa.voxel_down_sample(0.03); pb=pb.voxel_down_sample(0.03)
reg=o3d.pipelines.registration.registration_icp(pa,pb,0.15,np.eye(4),
    o3d.pipelines.registration.TransformationEstimationPointToPoint())
print("fitness:",reg.fitness); print("rmse_m:",reg.inlier_rmse)
