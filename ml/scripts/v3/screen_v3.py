"""Saring otomatis gambar sumber v3 dan tandai yang perlu dilihat manusia.

Mode:
- --mode foto : CLIP zero-shot; tandai bila peluang "bukan foto asli" (patung, mainan, lukisan, kartun,
                boneka, awetan) >= --th. Dipakai untuk folder satwa target dan non_class.
- --mode target : YOLO-World mencari satwa target yang tidak tertutup kotak berlabel (dipakai untuk non_class).
- --mode kosong : YOLO-World mencari hewan; tandai bila ada deteksi hewan >= --th. Dipakai untuk folder
                background, karena anotasi Open Images tidak selalu lengkap.

Output: <root>/saring.csv (file, skor, catatan, ditandai).

Contoh:
  python ml/scripts/v3/screen_v3.py --root D:/Project/DataSetZoo/ZooLens/v3/zebra_coco --mode foto
  python ml/scripts/v3/screen_v3.py --root D:/Project/DataSetZoo/ZooLens/v3/background_oi --mode kosong --th 0.15
"""
import argparse, csv
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--root', required=True)
ap.add_argument('--mode', choices=['foto', 'kosong', 'target'], required=True)
ap.add_argument('--th', type=float, default=0.5)
a = ap.parse_args()
root = Path(a.root); fs = sorted((root / 'images').glob('*.jpg'))
rows = []

if a.mode == 'foto':
    import clip, torch
    from PIL import Image
    model, prep = clip.load('ViT-B/32', device='cpu')
    texts = ['a photo of a real animal', 'a photo of animals in the wild', 'a photo of an animal in a zoo',
             'a statue or sculpture of an animal', 'a toy or plush animal', 'a drawing or painting of an animal',
             'a cartoon or illustration', 'a taxidermy animal in a museum', 'a photo of a screen or poster']
    BAD = 3
    with torch.no_grad():
        tf = model.encode_text(clip.tokenize(texts)); tf /= tf.norm(dim=-1, keepdim=True)
        for i in range(0, len(fs), 32):
            batch = fs[i:i + 32]
            x = torch.stack([prep(Image.open(f).convert('RGB')) for f in batch])
            imf = model.encode_image(x); imf /= imf.norm(dim=-1, keepdim=True)
            p = (100 * imf @ tf.T).softmax(-1)
            for f, pr in zip(batch, p):
                bad = float(pr[BAD:].sum()); top = texts[int(pr.argmax())]
                rows.append([f.name, round(bad, 3), top, int(bad >= a.th)])
elif a.mode == 'target':
    # cari satwa target yang TIDAK tertutup kotak berlabel mana pun (kemungkinan lupa diberi kotak)
    from ultralytics import YOLOWorld
    T = ['elephant', 'giraffe', 'zebra', 'tiger', 'rhinoceros']
    m = YOLOWorld('yolov8x-worldv2.pt'); m.set_classes(T)

    def iou(p, q):
        ix = max(0, min(p[2], q[2]) - max(p[0], q[0])); iy = max(0, min(p[3], q[3]) - max(p[1], q[1]))
        i = ix * iy; return i / ((p[2] - p[0]) * (p[3] - p[1]) + (q[2] - q[0]) * (q[3] - q[1]) - i + 1e-9)
    for f in fs:
        lb = root / 'labels' / (f.stem + '.txt')
        gt = []
        for ln in (lb.read_text().splitlines() if lb.exists() else []):
            c, x, y, w, h = map(float, ln.split()); gt.append([x - w / 2, y - h / 2, x + w / 2, y + h / 2])
        r = m.predict(str(f), conf=0.05, verbose=False)[0]
        best = (0.0, '')
        for b, c, k in zip(r.boxes.xyxyn.tolist(), r.boxes.conf.tolist(), r.boxes.cls.tolist()):
            if all(iou(b, g) < 0.3 for g in gt) and c > best[0]: best = (c, T[int(k)])
        rows.append([f.name, round(best[0], 3), best[1], int(best[0] >= a.th)])
else:
    from ultralytics import YOLOWorld
    animals = ['animal', 'bird', 'dog', 'cat', 'horse', 'cow', 'sheep', 'elephant', 'giraffe', 'zebra', 'tiger',
               'rhinoceros', 'deer', 'monkey', 'lion', 'bear']
    m = YOLOWorld('yolov8x-worldv2.pt'); m.set_classes(animals)
    for f in fs:
        r = m.predict(str(f), conf=0.05, verbose=False)[0]
        best = max(((float(c), animals[int(k)]) for c, k in zip(r.boxes.conf, r.boxes.cls)), default=(0.0, ''))
        rows.append([f.name, round(best[0], 3), best[1], int(best[0] >= a.th)])

with open(root / ('saring_target.csv' if a.mode == 'target' else 'saring.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['file', 'skor', 'catatan', 'ditandai']); w.writerows(rows)
print(root.name, len(rows), 'gambar,', sum(r[3] for r in rows), 'ditandai')
