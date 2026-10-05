def absolute_spread(values):
    values=list(values)
    return max(values)-min(values) if values else None

def repeatability_gate(values,tolerance=0.01):
    s=absolute_spread(values)
    return {"status":"PASS" if s is not None and s<=tolerance else "FAIL" if s is not None else "PENDING",
            "spread_m":s,"tolerance_m":tolerance}
