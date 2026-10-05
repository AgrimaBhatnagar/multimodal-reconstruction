import cv2
from pathlib import Path

src = Path(r"..\spatial-reconstruction\benchmarks\extracted\single_room\c00a170fe1\rgb.mp4")
out = Path(r"benchmarks\test_capture\photos\room_01")
out.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(str(src))
targets = {100, 500, 900, 1300}
i = 0
saved = 0

while True:
    ok, frame = cap.read()
    if not ok:
        break

    if i in targets:
        path = out / f"room_01_{saved+1:02d}.jpg"
        cv2.imwrite(str(path), frame)
        saved += 1

    if saved == len(targets):
        break

    i += 1

cap.release()

print(f"Saved {saved} photos to {out}")
