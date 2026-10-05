import numpy as np
from src.geometry import xy_hull, floor_ceiling

def test_hull():
    p=np.array([[0,0,0],[4,0,0],[4,3,0],[0,3,0],[1,1,2]])
    h,a,per=xy_hull(p)
    assert abs(a-12)<1e-6
    assert per>0

def test_ceiling():
    z=np.r_[np.zeros(100),np.ones(100)*2.5]
    p=np.c_[np.random.randn(200),np.random.randn(200),z]
    _,_,h=floor_ceiling(p)
    assert 2.0<h<3.0
