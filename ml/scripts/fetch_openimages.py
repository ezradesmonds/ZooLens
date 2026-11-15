"""Unduh gambar satu kelas ZooLens dari Open Images V7 dan buat label YOLO dengan ID kelas terpadu.

Input: CSV anotasi bbox Open Images yang sudah disaring ke 5 kelas ZooLens
(train/validation/test-annotations-bbox.sub.csv), dibuat dengan:
  curl -sL <url bbox csv> | grep -F -f ids.txt > <split>-annotations-bbox.sub.csv
Output:
  <out>/images/*.jpg, <out>/labels/*.txt, <out>/sources.csv

Aturan:
- Ambil gambar yang punya minimal satu box kelas --cls.
- Lewati gambar yang punya box IsDepiction=1 (patung, gambar, mainan) atau
  IsGroupOf=1 (satu box untuk sekelompok hewan) agar label tetap bersih.
- Box kelas ZooLens lain di gambar yang sama ikut disimpan.
- --limit N mengambil N gambar secara acak (seed tetap) supaya bisa diulang.
- Gambar diperkecil ke sisi terpanjang --max-side px (koordinat YOLO tetap karena ternormalisasi).

Contoh:
  python ml/scripts/fetch_openimages.py --cls rhinoceros --ann-dir oi --out ZooLens/badak_openimages
  python ml/scripts/fetch_openimages.py --cls elephant --limit 500 --ann-dir oi --out ZooLens/gajah_openimages
"""
import argparse, collections, csv, io, random, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image

OI_ID = {'elephant': '/m/0bwd_0j', 'giraffe': '/m/03bk1', 'zebra': '/m/0898b', 'tiger': '/m/07dm6', 'rhinoceros': '/m/03d443'}
UNIFIED = {'/m/0bwd_0j': 0, '/m/03bk1': 1, '/m/0898b': 2, '/m/07dm6': 3, '/m/03d443': 4}
S3 = 'https://open-images-dataset.s3.amazonaws.com/{split}/{id}.jpg'

ap = argparse.ArgumentParser()
ap.add_argument('--cls', required=True, choices=sorted(OI_ID))
ap.add_argument('--ann-dir', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--limit', type=int, default=0)
ap.add_argument('--seed', type=int, default=42)
ap.add_argument('--max-side', type=int, default=1024)
ap.add_argument('--workers', type=int, default=8)
ap.add_argument('--dry-run', action='store_true')
a = ap.parse_args()
TARGET = OI_ID[a.cls]

boxes = collections.defaultdict(list)
for split, fn in [('train', 'train-annotations-bbox.sub.csv'),
                  ('validation', 'validation-annotations-bbox.sub.csv'),
                  ('test', 'test-annotations-bbox.sub.csv')]:
    for r in csv.reader(open(Path(a.ann_dir) / fn, encoding='utf-8')):
        img, _, lab, _, x0, x1, y0, y1, occ, trunc, grp, dep = r[:12]
        if lab in UNIFIED:
            boxes[(split, img)].append((lab, float(x0), float(x1), float(y0), float(y1), occ, trunc, grp, dep))

keep, skipped = [], collections.Counter()
for key, bs in boxes.items():
    if not any(b[0] == TARGET for b in bs): continue
    if any(b[8] == '1' for b in bs): skipped['depiction'] += 1; continue
    if any(b[7] == '1' for b in bs): skipped['group_of'] += 1; continue
    keep.append(key)
keep.sort()
total = len(keep)
if a.limit and a.limit < total:
    keep = sorted(random.Random(a.seed).sample(keep, a.limit))
print(f'gambar {a.cls} tersedia: {total} | dipakai: {len(keep)} | dilewati: {dict(skipped)}')
if a.dry_run: sys.exit()

out = Path(a.out); (out / 'images').mkdir(parents=True, exist_ok=True); (out / 'labels').mkdir(parents=True, exist_ok=True)


def fetch(key):
    split, img = key
    dst = out / 'images' / f'openimages__{img}.jpg'
    if dst.exists(): return True
    try:
        data = urllib.request.urlopen(S3.format(split=split, id=img), timeout=60).read()
        im = Image.open(io.BytesIO(data)).convert('RGB')
        im.thumbnail((a.max_side, a.max_side))
        tmp = dst.with_suffix('.part'); im.save(tmp, 'JPEG', quality=90); tmp.replace(dst)
        return True
    except Exception as e:
        print(f'GAGAL {img}: {e}'); return False


with ThreadPoolExecutor(a.workers) as ex:
    ok = dict(zip(keep, ex.map(fetch, keep)))
with open(out / 'sources.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['file', 'openimages_id', 'openimages_split', 'url', 'n_target', 'n_other', 'any_occluded', 'any_truncated'])
    for split, img in keep:
        if not ok[(split, img)]: continue
        name = f'openimages__{img}'
        dst = out / 'images' / f'{name}.jpg'
        url = S3.format(split=split, id=img)
        bs = boxes[(split, img)]
        lines = [f'{UNIFIED[b[0]]} {(b[1]+b[2])/2:.6f} {(b[3]+b[4])/2:.6f} {b[2]-b[1]:.6f} {b[4]-b[3]:.6f}' for b in bs]
        (out / 'labels' / f'{name}.txt').write_text('\n'.join(lines) + '\n')
        w.writerow([dst.name, img, split, url, sum(b[0] == TARGET for b in bs), sum(b[0] != TARGET for b in bs),
                    int(any(b[5] == '1' for b in bs)), int(any(b[6] == '1' for b in bs))])
print(f'selesai: {sum(ok.values())} berhasil, {len(keep) - sum(ok.values())} gagal')
