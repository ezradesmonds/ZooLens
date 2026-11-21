"""Buat kotak awal (pre-label) dengan YOLO-World untuk foto tanpa label. Hasilnya WAJIB dikoreksi manual.

YOLO-World mencari objek dari teks (mis. "rhinoceros"). Uji pada 150 foto badak Open Images berlabel
(212 objek): prompt "rhinoceros", conf 0,03 -> 87% badak ketemu dengan kotak tepat (IoU >= 0,5),
96% kotak benar. Jadi sebagian kecil kotak hilang atau salah dan harus dibetulkan di halaman koreksi.

Output JSON: {file: [[cls, cx, cy, w, h, conf], ...]} dengan koordinat ternormalisasi (format YOLO).

Contoh:
  python ml/scripts/v3/prelabel_yoloworld.py --images D:/Project/DataSetZoo/ZooLens/badak_inaturalist/images \
      --prompt rhinoceros --cls 4 --out D:/Project/DataSetZoo/ZooLens/badak_inaturalist/prelabel.json
"""
import argparse, glob, json, os
from ultralytics import YOLOWorld

ap = argparse.ArgumentParser()
ap.add_argument('--images', required=True)
ap.add_argument('--prompt', required=True)
ap.add_argument('--cls', type=int, required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--conf', type=float, default=0.03)
ap.add_argument('--weights', default='yolov8x-worldv2.pt')
a = ap.parse_args()

m = YOLOWorld(a.weights); m.set_classes([a.prompt])
res = json.load(open(a.out)) if os.path.exists(a.out) else {}
fs = sorted(glob.glob(os.path.join(a.images, '*.jpg')))
for i, f in enumerate(fs):
    name = os.path.basename(f)
    if name in res: continue
    r = m.predict(f, conf=a.conf, iou=0.5, verbose=False)[0]
    res[name] = [[a.cls] + [round(float(v), 5) for v in b] + [round(float(c), 3)] for b, c in zip(r.boxes.xywhn, r.boxes.conf)]
    if i % 100 == 0:
        print(i, '/', len(fs)); json.dump(res, open(a.out, 'w'))
json.dump(res, open(a.out, 'w'))
print('selesai', len(res), 'foto,', sum(len(v) for v in res.values()), 'kotak ->', a.out)
