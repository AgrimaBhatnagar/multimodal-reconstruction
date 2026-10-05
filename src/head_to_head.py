def shared_dimension_score(ours, consumer, tolerance):
    if not ours or not consumer:
        return {"status":"PENDING","reason":"Both systems' measurements are required"}
    n=min(len(ours),len(consumer))
    errors=[abs(ours[i]-consumer[i]) for i in range(n)]
    pass_rate=sum(e<=tolerance for e in errors)/n if n else 0
    return {"status":"PASS" if pass_rate>=0.70 else "FAIL",
            "shared_dimensions":n,"pass_rate":pass_rate,"tolerance_m":tolerance}
