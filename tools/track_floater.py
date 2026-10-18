"""Measure floater height (and lateral position) from a side-view video.

Setup: camera level with the floater, diffuse back-light behind the vessel, a printed scale
or the known floater diameter in the frame.  The floater appears as a dark disc.

  python track_floater.py video.mp4 --roi x0 y0 x1 y1 --ref-y <pixel row of shroud floor>
                         --mm-per-px <scale> [--out heights.csv]

Outputs per-frame centroid (mm below the shroud floor reference) and a summary:
mean height, RMS jitter, drift.  Requires opencv-python and numpy.
"""
import argparse, csv
import numpy as np
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--roi", nargs=4, type=int, required=True)
ap.add_argument("--ref-y", type=float, required=True, help="pixel row of the reference (shroud floor underside)")
ap.add_argument("--mm-per-px", type=float, required=True)
ap.add_argument("--thresh", type=int, default=0, help="0 = Otsu")
ap.add_argument("--out", default="heights.csv")
a = ap.parse_args()

cap = cv2.VideoCapture(a.video)
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
x0, y0, x1, y1 = a.roi
rows = []
i = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    g = cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    g = cv2.GaussianBlur(g, (5, 5), 0)
    if a.thresh:
        _, bw = cv2.threshold(g, a.thresh, 255, cv2.THRESH_BINARY_INV)
    else:
        _, bw = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(bw)
    if n > 1:
        k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        cx, cy = cent[k]
        d_px = 2*np.sqrt(stats[k, cv2.CC_STAT_AREA]/np.pi)
        rows.append((i/fps, (cx + x0), (cy + y0 - a.ref_y)*a.mm_per_px, d_px*a.mm_per_px))
    i += 1

with open(a.out, "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["t_s", "x_px", "depth_below_ref_mm", "apparent_diam_mm"])
    w.writerows(rows)
r = np.array(rows)
if len(r):
    z = r[:, 2]
    print(f"frames {len(r)}  mean depth {z.mean():.2f} mm  RMS jitter {z.std():.3f} mm  "
          f"drift {np.polyfit(r[:,0], z, 1)[0]*60:.3f} mm/min  apparent diameter {r[:,3].mean():.2f} mm")
