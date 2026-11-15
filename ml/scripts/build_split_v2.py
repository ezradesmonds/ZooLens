"""Bangun ZooLens_final_v2 = ZooLens_final (v1) + data tambahan kelas minoritas.

Aturan:
- Seluruh isi v1 disalin apa adanya. Split test TIDAK berubah, supaya hasil model lama
  dan baru bisa dibandingkan pada soal ujian yang sama.
- Data tambahan (label sudah memakai ID terpadu) hanya masuk train dan val.
- Gambar tambahan yang mirip satu sama lain (pHash) dijadikan satu kelompok dan selalu
  masuk split yang sama.
- Gambar tambahan yang mirip dengan gambar v1 mana pun dilewati (bukan data baru).

Contoh:
  python ml/scripts/build_split_v2.py --v1 D/ZooLens_final --out D/ZooLens_final_v2 \
      --add badak_oi=D/ZooLens/badak_openimages gajah_oi=D/ZooLens/gajah_openimages
"""
import argparse, collections, csv, hashlib, random, shutil
from pathlib import Path

import numpy as np
from PIL import Image

from audit_yolo import IMG_EXT, POPCOUNT, phash64

NAMES = ['elephant', 'giraffe', 'zebra', 'tiger', 'rhinoceros']

ap = argparse.ArgumentParser()
ap.add_argument('--v1', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--add', nargs='+', required=True, help='tag=folder (berisi images/ dan labels/)')
ap.add_argument('--val-ratio', type=float, default=0.1)
ap.add_argument('--threshold', type=int, default=5)
ap.add_argument('--seed', type=int, default=42)
ap.add_argument('--dry-run', action='store_true')
a = ap.parse_args()
v1, out = Path(a.v1), Path(a.out)


def ph(p):
    with Image.open(p) as im:
        return phash64(im)


def hamming(x, y):
    d = (x[:, None] ^ y[None, :]).view(np.uint8).reshape(len(x), len(y), 8)
    return POPCOUNT[d].sum(axis=2)


def classes_of(lbl):
    return collections.Counter(int(ln.split()[0]) for ln in lbl.read_text().splitlines() if ln.strip())


# ---------------------------------------------------------------- v1
rows = []  # (split, file, source, origin, Counter kelas, src_img, src_lbl)
for sp in ['train', 'val', 'test']:
    for img in sorted((v1 / 'images' / sp).iterdir()):
        if img.suffix.lower() not in IMG_EXT: continue
        lbl = v1 / 'labels' / sp / (img.stem + '.txt')
        rows.append((sp, img.name, img.name.split('__')[0], 'v1', classes_of(lbl), img, lbl))
h1 = np.array([ph(r[5]) for r in rows], dtype=np.uint64)
print(f'v1: {len(rows)} gambar')

# ---------------------------------------------------------------- data tambahan
rng = random.Random(a.seed)
skipped = collections.Counter()
for item in a.add:
    tag, _, folder = item.partition('=')
    src = Path(folder)
    imgs = [p for p in sorted((src / 'images').iterdir())
            if p.suffix.lower() in IMG_EXT and (src / 'labels' / (p.stem + '.txt')).exists()]
    hn = np.array([ph(p) for p in imgs], dtype=np.uint64)
    dup_v1 = (hamming(hn, h1) <= a.threshold).any(axis=1)
    skipped[f'{tag}: mirip gambar v1'] += int(dup_v1.sum())
    keep = [i for i in range(len(imgs)) if not dup_v1[i]]
    # kelompokkan gambar yang mirip satu sama lain (union-find)
    parent = {i: i for i in keep}
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    d = hamming(hn[keep], hn[keep])
    for x, y in np.argwhere(d <= a.threshold):
        if x < y: parent[find(keep[x])] = find(keep[y])
    groups = collections.defaultdict(list)
    for i in keep: groups[find(i)].append(i)
    order = sorted(groups); rng.shuffle(order)
    n_val_target, n_val = round(len(keep) * a.val_ratio), 0
    for g in order:
        sp = 'val' if n_val < n_val_target else 'train'
        if sp == 'val': n_val += len(groups[g])
        for i in groups[g]:
            p = imgs[i]; lbl = src / 'labels' / (p.stem + '.txt')
            name = f"{tag}__{p.stem.replace('openimages__', '')}{p.suffix.lower()}"
            rows.append((sp, name, tag, 'baru', classes_of(lbl), p, lbl))
    print(f'{tag}: {len(imgs)} gambar, dipakai {len(keep)} ({len(groups)} kelompok), val {n_val}')
if skipped: print('dilewati:', dict(skipped))

# ---------------------------------------------------------------- ringkasan
img_cnt, box_cnt = collections.Counter(), collections.Counter()
for sp, _, _, _, cls, _, _ in rows:
    for c, n in cls.items():
        img_cnt[(sp, c)] += 1; box_cnt[(sp, c)] += n
for title, cnt in [('Gambar (yang memuat kelas)', img_cnt), ('Box', box_cnt)]:
    print(f'\n{title} per split x kelas:')
    print(f"{'split':6}" + ''.join(f'{n:>12}' for n in NAMES))
    for sp in ['train', 'val', 'test']:
        print(f'{sp:6}' + ''.join(f'{cnt[(sp, c)]:>12}' for c in range(5)))
tot = collections.Counter(r[0] for r in rows)
print(f"\nTotal gambar: train {tot['train']}, val {tot['val']}, test {tot['test']}")
tr = [img_cnt[('train', c)] for c in range(5)]
print(f'Rasio train terbesar : terkecil = {max(tr) / min(tr):.2f} : 1')
if a.dry_run: raise SystemExit

# ---------------------------------------------------------------- tulis
for sp in ['train', 'val', 'test']:
    (out / 'images' / sp).mkdir(parents=True, exist_ok=True); (out / 'labels' / sp).mkdir(parents=True, exist_ok=True)
with open(out / 'split_manifest_v2.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['split', 'file', 'source', 'asal'] + NAMES)
    for sp, name, tag, origin, cls, img, lbl in rows:
        shutil.copy2(img, out / 'images' / sp / name)
        shutil.copy2(lbl, out / 'labels' / sp / (Path(name).stem + '.txt'))
        w.writerow([sp, name, tag, origin] + [cls.get(c, 0) for c in range(5)])
(out / 'data.yaml').write_text('path: .\ntrain: images/train\nval: images/val\ntest: images/test\n'
                               f'nc: 5\nnames: {NAMES}\n', encoding='utf-8')


def digest(folder):
    return {p.name: hashlib.md5(p.read_bytes()).hexdigest() for p in sorted(folder.iterdir())}


same = all(digest(v1 / k / 'test') == digest(out / k / 'test') for k in ('images', 'labels'))
print(f"\nTest v2 identik dengan v1: {'YA' if same else 'TIDAK'}")
