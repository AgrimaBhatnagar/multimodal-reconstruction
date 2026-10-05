from pathlib import Path
import pandas as pd, numpy as np, sys
p=Path(sys.argv[1])
odo=pd.read_csv(p/"odometry.csv",skipinitialspace=True)
odo.columns=[str(c).strip() for c in odo.columns]
d=np.sqrt(np.diff(odo.x)**2+np.diff(odo.y)**2+np.diff(odo.z)**2)
print("frames:",len(odo))
print("translation median:",float(np.median(d)))
print("translation p95:",float(np.percentile(d,95)))
print("translation max:",float(np.max(d)))
print("quaternion norm min/max:",
      float(np.min(np.sqrt(odo.qx**2+odo.qy**2+odo.qz**2+odo.qw**2))),
      float(np.max(np.sqrt(odo.qx**2+odo.qy**2+odo.qz**2+odo.qw**2))))
