# Stock Capture Protocol — Route 2

## Tool

Use the stock iPhone Camera application for photos/video and a LiDAR-capable consumer scanning application for LiDAR/depth capture. Do not use developer-only sensors, markers, tripods, calibration boards, poses or body-mounted devices.

## Device matrix

| Tier | Minimum device | Capture | Required metadata | Intended output |
|---|---|---|---|---|
| Photos | iPhone 15+ | 2–8 stills per room | image dimensions + room id | room geometry + property stitch |
| Video | iPhone 15+ | handheld walkthrough | video timestamps | room geometry + property stitch |
| LiDAR | iPhone Pro with LiDAR | handheld scan | depth + poses + intrinsics | metric geometry + property stitch |

## Operator protocol

### Photos
1. Stand near room perimeter.
2. Capture 2–8 overlapping stills.
3. Include every wall and major opening.
4. Do not move furniture.
5. Avoid intentionally framing the room around the damage.
6. Repeat exactly for every room.
7. Place each room in its own folder.

### Video
1. Start at the doorway.
2. Walk slowly around the room perimeter.
3. Keep the camera approximately chest/eye height.
4. Maintain overlap between adjacent views.
5. Capture openings and ceiling.
6. Continue through the connector to the next room.
7. Do not stop recording between connected rooms.

### LiDAR
1. Start the scan outside the first room.
2. Walk the perimeter at a steady pace.
3. Include floor, walls, ceiling and openings.
4. Keep the device orientation stable.
5. Continue through the connector between rooms.
6. Save raw depth, poses, intrinsics and confidence.

## Benchmark conditions

The benchmark must contain:
- 3+ connected rooms plus connector.
- Furnished room with staged damage spanning two damage classes.
- Same rooms captured at all three tiers.
- One repeated capture at the same tier.
- Laser/tape measurements for openings, ceilings and walls.
- Raw sensor data and measurements.
- Mirror/glass/wet-look/low-light examples.

## Accuracy honesty

Do not change the benchmark after seeing results. Do not manually adjust outputs to pass a gate. A gate is passed only when the measured prediction is supported by recorded ground truth.
