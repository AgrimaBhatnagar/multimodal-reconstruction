from pathlib import Path
from src.capture import validate_capture

def test_lidar_validation(tmp_path):
    for x in ["depth","confidence"]:
        (tmp_path/x).mkdir()
    (tmp_path/"odometry.csv").write_text("frame,x,y,z,qx,qy,qz,qw\n0,0,0,0,0,0,0,1\n")
    (tmp_path/"camera_matrix.csv").write_text("1,0,0\n0,1,0\n0,0,1\n")
    r=validate_capture(tmp_path,"lidar")
    assert r["valid"]
