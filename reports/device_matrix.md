# Device and Tier Matrix

| Input tier | Target hardware | Required input | Scale status | Local validation status |
|---|---|---|---|---|
| Photos | iPhone 15 or newer | 2-8 still images per room | Relative unless metric calibration is available | Pipeline structure implemented; physical iPhone capture not performed locally |
| Video | iPhone 15 or newer | Handheld walkthrough video | Calibration dependent | Pipeline structure implemented; physical iPhone capture not performed locally |
| LiDAR | Pro-class iPhone with LiDAR | Depth + confidence + poses + intrinsics | Metric when calibration is valid | Pipeline exercised with supplied depth/pose sample data; physical iPhone capture not performed locally |

## Photos

Required capture:

- 2-8 still images per room
- Overlapping views
- Walls and corners
- Floor/wall transitions
- Ceiling/wall transitions
- Doors and visible openings

The photo pipeline must widen uncertainty when metric calibration is unavailable.

## Video

Required capture:

- Handheld walkthrough
- Continuous motion
- Sufficient frame overlap
- Connector spaces between adjacent rooms

The video pipeline depends on available calibration, overlap and motion quality.

## LiDAR

Required capture:

- Depth
- Confidence
- Camera intrinsics
- Poses

The LiDAR pipeline supports metric reconstruction when the supplied calibration and pose information are valid.

## Local Validation Statement

No claim is made that the system was physically captured or tested on an iPhone 15+ locally.

The available development validation uses supplied sample sensor data and software test inputs.

Final device-level validation is expected during the assessment walk-in.

## Accuracy Policy

Device capability is not treated as proof of accuracy.

Physical accuracy claims require independent benchmark measurements, calibration evidence and the benchmark procedure specified by the assessment.