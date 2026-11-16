"""Jalankan model pada subset uji 500 dan simpan prediksi per foto.

Aturan sama dengan sheet Panduan dan batch_test_200.py: deteksi dihitung bila confidence >= --conf,
dan kelas prediksi sebuah foto adalah deteksi dengan confidence tertinggi.

Contoh:
  python ml/scripts/uji500/run_uji500.py --model ai-service/models/best.pt \
      --root D:/Project/DataSetZoo/uji500 --manifest ml/uji500/manifest_uji500.csv --out ml/uji500/prediksi_uji500.csv
"""
import argparse, csv, hashlib
from pathlib import Path
from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument('--model', required=True); ap.add_argument('--root', required=True)
ap.add_argument('--manifest', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--conf', type=float, default=0.5)
a = ap.parse_args()

model = YOLO(a.model)
rows = list(csv.DictReader(open(a.manifest, encoding='utf-8')))
with open(a.out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['no', 'file', 'kelas_prediksi', 'confidence', 'jumlah_deteksi', 'semua_deteksi'])
    for r in rows:
        p = Path(a.root) / r['folder'] / r['file']
        assert hashlib.md5(p.read_bytes()).hexdigest() == r['md5'], f'file berubah sejak dibekukan: {p}'
        res = model.predict(source=str(p), conf=a.conf, verbose=False)[0]
        dets = sorted(((float(b.conf[0]), res.names[int(b.cls[0])].lower()) for b in res.boxes), reverse=True)
        top = dets[0] if dets else (0.0, '')
        w.writerow([r['no'], r['file'], top[1], f'{top[0]:.4f}' if dets else '', len(dets),
                    '; '.join(f'{n} {c:.2f}' for c, n in dets)])
print('selesai:', len(rows), 'foto')
