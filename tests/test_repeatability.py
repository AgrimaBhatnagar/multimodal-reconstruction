from src.repeatability import repeatability_gate

def test_repeat():
    assert repeatability_gate([3.00,3.005],0.01)["status"]=="PASS"
    assert repeatability_gate([3.00,3.02],0.01)["status"]=="FAIL"
