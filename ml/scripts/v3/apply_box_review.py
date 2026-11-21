"""Terapkan hasil halaman koreksi (koreksi_kotak.json) menjadi label YOLO.

- Foto OK: tulis <root>/labels/<nama>.txt (kelas cx cy w h).
- Foto Buang: pindahkan ke <root>/_dibuang/ dan catat di <root>/dibuang.csv.
- Foto yang belum dicek tidak disentuh dan dilaporkan.
- Laporan juga menghitung berapa foto yang kotak awalnya dipakai tanpa diubah.

Contoh:
  python ml/scripts/v3/apply_box_review.py --review koreksi_kotak.json --root D:/Project/DataSetZoo/ZooLens/badak_inaturalist
"""
import argparse, csv, json, os, shutil
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--review', required=True)
ap.add_argument('--root', required=True)
a = ap.parse_args()

root = Path(a.root); rev = json.load(open(a.review, encoding='utf-8'))
(root / 'labels').mkdir(exist_ok=True)
imgs = sorted(p.name for p in (root / 'images').glob('*.jpg'))
n = dict(ok=0, buang=0, belum=0, tanpa_ubah=0, kotak=0)
drop_log = root / 'dibuang.csv'; new_log = not drop_log.exists()
with open(drop_log, 'a', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    if new_log: w.writerow(['file', 'alasan'])
    for name in imgs:
        r = rev.get(name)
        if not r: n['belum'] += 1; continue
        if r['status'] == 'buang':
            (root / '_dibuang').mkdir(exist_ok=True)
            shutil.move(str(root / 'images' / name), str(root / '_dibuang' / name))
            lb = root / 'labels' / (name[:-4] + '.txt')
            if lb.exists(): lb.unlink()
            w.writerow([name, 'dibuang saat koreksi kotak']); n['buang'] += 1; continue
        lines = ['%d %.6f %.6f %.6f %.6f' % (int(b[0]), *[min(max(v, 0), 1) for v in b[1:5]]) for b in r['boxes']]
        (root / 'labels' / (name[:-4] + '.txt')).write_text('\n'.join(lines) + ('\n' if lines else ''))
        n['ok'] += 1; n['kotak'] += len(lines); n['tanpa_ubah'] += not r.get('edited')
print(n)
