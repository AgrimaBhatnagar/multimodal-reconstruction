import numpy as np
from scipy.spatial import ConvexHull


def robust_plane_height(points, q=0.05, vertical_axis=2):
    values = points[:, vertical_axis]
    lo, hi = np.quantile(values, [q, 1 - q])
    return float((lo + hi) / 2)


def floor_ceiling(points, vertical_axis=2):
    """
    Estimate floor/ceiling extent along the selected vertical axis.

    Defaults to the original Z-axis behavior for backward compatibility.
    """
    values = np.asarray(points[:, vertical_axis], dtype=float)
    values = values[np.isfinite(values)]

    if len(values) < 20:
        raise ValueError("Insufficient finite vertical points")

    lo, hi = np.quantile(values, [0.08, 0.92])

    return (
        float(lo),
        float(hi),
        float(hi - lo),
    )


def xy_hull(points, horizontal_axes=(0, 1)):
    """
    Compute the convex hull on the selected horizontal plane.

    Defaults to XY to preserve the original public API.
    """
    xy = points[:, list(horizontal_axes)]

    if len(xy) < 3:
        return xy, 0.0, 0.0

    hull = ConvexHull(xy)
    poly = xy[hull.vertices]

    area = float(hull.volume)
    per = float(hull.area)

    return poly, area, per


def wall_segments(
    points,
    bins=180,
    horizontal_axes=(0, 1),
):
    """
    Extract dominant wall segments on the selected horizontal plane.

    Defaults to XY for backward compatibility.
    """
    xy = points[:, list(horizontal_axes)]

    if len(xy) < 10:
        return []

    c = xy.mean(0)
    centered = xy - c

    ang = np.arctan2(
        centered[:, 1],
        centered[:, 0],
    )

    hist, edges = np.histogram(
        ang,
        bins=bins,
    )

    idx = np.argsort(hist)[-8:]

    segs = []

    for i in idx:
        a0, a1 = edges[i], edges[i + 1]

        mask = (
            (ang >= a0)
            & (ang < a1)
        )

        p = xy[mask]

        if len(p) < 20:
            continue

        axis = p - p.mean(0)

        _, _, v = np.linalg.svd(
            axis,
            full_matrices=False,
        )

        d = v[0]

        t = axis @ d

        p0 = p.mean(0) + d * t.min()
        p1 = p.mean(0) + d * t.max()

        length = float(
            np.linalg.norm(p1 - p0)
        )

        if length > 0.3:
            segs.append(
                {
                    "start": p0.tolist(),
                    "end": p1.tolist(),
                    "length_m": length,
                }
            )

    segs.sort(
        key=lambda x: -x["length_m"]
    )

    return segs[:4]
