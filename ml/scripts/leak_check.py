"""Cek kebocoran: bandingkan gambar baru dengan kumpulan acuan memakai pHash (sidik jari visual).

Dua gambar dianggap mirip bila jarak Hamming pHash <= --threshold (sama dengan audit_yolo.py).
Dipakai sebelum menambah data training, agar tidak ada gambar baru yang kembar dengan
gambar test atau foto uji tim.

Contoh:
  python ml/scripts/leak_check.py --new D/badak_openimages/images D/gajah_openimages/images \
      --ref test=D2/images/test train=D2/images/train uji="Downloads/*rhino*" --out audit_out/leak_check_v2.csv
"""
import argparse, csv, glob
from pathlib import Path

import numpy as np
from PIL import Image

from audit_yolo import IMG_EXT, POPCOUNT, phash64


def collect(spec):
    p = Path(spec)
    files = sorted(p.iterdir()) if p.is_dir() else [Path(f) for f in sorted(glob.glob(spec))]
    return [f for f in files if f.suffix.lower() in IMG_EXT]


def hashes(files):
    out = []
    for f in files:
        with Image.open(f) as im:
            out.append(phash64(im))
    return np.array(out, dtype=np.uint64)


def hamming(a, b):
    x = (a[:, None] ^ b[None, :]).view(np.uint8).reshape(len(a), len(b), 8)
    return POPCOUNT[x].sum(axis=2)


ap = argparse.ArgumentParser()
ap.add_argument('--new', nargs='+', required=True)
ap.add_argument('--ref', nargs='+', required=True, help='nama=folder_atau_pola')
ap.add_argument('--threshold', type=int, default=5)
ap.add_argument('--out', required=True)
a = ap.parse_args()

new = [f for s in a.new for f in collect(s)]
hn = hashes(new)
rows = []
for item in a.ref:
    name, _, spec = item.partition('=')
    ref = collect(spec)
    if not ref: print(f'{name}: 0 gambar acuan (cek path)'); continue
    d = hamming(hn, hashes(ref))
    hit = np.argwhere(d <= a.threshold)
    for i, j in hit:
        rows.append([name, str(new[i]), str(ref[j]), int(d[i, j])])
    print(f'{name}: {len(ref)} acuan, {len(hit)} pasangan mirip, {len(set(i for i, _ in hit))} gambar baru terlibat')
# antar gambar baru (untuk pengelompokan saat split)
d = hamming(hn, hn)
pair = [(i, j) for i, j in np.argwhere(d <= a.threshold) if i < j]
for i, j in pair:
    rows.append(['antar_baru', str(new[i]), str(new[j]), int(d[i, j])])
print(f'antar_baru: {len(new)} gambar, {len(pair)} pasangan mirip')
with open(a.out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['acuan', 'gambar_baru', 'gambar_acuan', 'jarak']); w.writerows(rows)
