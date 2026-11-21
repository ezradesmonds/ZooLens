"""Buang gambar baru yang kembar menurut hasil leak_check.py.

- Kembar dengan acuan (train/val/test v2, uji 500, dll.): gambar baru dibuang.
- Kembar antar gambar baru: satu dibuang; bila salah satunya dari COCO, yang COCO yang dibuang
  (label Open Images dipertahankan supaya konsisten).
Gambar dipindah ke <folder>/_dibuang/images (label ikut ke _dibuang/labels) dan dicatat di <folder>/dibuang.csv.

Contoh:
  python ml/scripts/v3/drop_duplicates.py --leak D:/Project/DataSetZoo/ZooLens/v3/leak_check_v3.csv
"""
import argparse, csv, shutil
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--leak', required=True)
ap.add_argument('--dry-run', action='store_true')
a = ap.parse_args()

drop = {}
for r in csv.reader(open(a.leak, encoding='utf-8')):
    if r[0] == 'acuan': continue
    ref, new, other, dist = r[0], Path(r[1]), Path(r[2]), r[3]
    if ref != 'antar_baru':
        drop.setdefault(new, f'kembar dengan {ref} ({other.name}, jarak {dist})')
    else:
        if new in drop or other in drop: continue
        victim, keep = (new, other) if 'coco' in new.name and 'coco' not in other.name else (other, new)
        drop[victim] = f'kembar dengan {keep.parent.parent.name}/{keep.name} (jarak {dist})'

per_folder = {}
for img, why in drop.items():
    root = img.parent.parent; per_folder[root.name] = per_folder.get(root.name, 0) + 1
    if a.dry_run or not img.exists(): continue
    for sub, name in (('images', img.name), ('labels', img.stem + '.txt')):
        src = root / sub / name
        if src.exists():
            (root / '_dibuang' / sub).mkdir(parents=True, exist_ok=True); shutil.move(str(src), str(root / '_dibuang' / sub / name))
    log = root / 'dibuang.csv'; new_log = not log.exists()
    with open(log, 'a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        if new_log: w.writerow(['file', 'alasan'])
        w.writerow([img.name, why])
print('dibuang:', len(drop), per_folder)
