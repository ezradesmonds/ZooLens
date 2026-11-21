"""Bangun ZooLens_final_v3 = ZooLens_final_v2 + data tambahan v3 (6 kelas: + non_class, + foto tanpa hewan).

Aturan:
- Seluruh isi v2 disalin apa adanya ke split yang sama. Test v2 (259 gambar) tidak berubah, supaya model
  lama dan baru tetap bisa dibandingkan pada soal yang sama (subset "test_v2" di manifest).
- Data tambahan dibagi per sumber (tag) ke train/val/test dengan rasio --val-ratio / --test-ratio, sehingga
  test v3 juga berisi non_class dan foto tanpa hewan (background, label kosong).
- Gambar tambahan yang mirip satu sama lain (pHash, jarak <= --group-threshold) dijadikan satu kelompok dan
  selalu masuk split yang sama. Untuk sumber iNaturalist, foto dari pengguna yang sama juga satu kelompok
  (sering satwa yang sama di kandang yang sama).
- Gambar tambahan yang mirip gambar v2 mana pun (jarak <= --threshold) dilewati, dan gambar yang mirip
  foto uji 500 (--uji) membuat skrip berhenti: subset uji tidak boleh masuk dataset.

Contoh:
  python ml/scripts/build_split_v3.py --v2 D/ZooLens_final_v2 --out D/ZooLens_final_v3 --uji "D/uji500/*/*/*.jpg" \
      --add badak_inat=D/ZooLens/badak_inaturalist harimau_inat=D/ZooLens/harimau_inaturalist gajah_oi=D/ZooLens/v3/elephant_oi ...
"""
import argparse, collections, csv, glob, hashlib, random, shutil
from pathlib import Path

import numpy as np
from PIL import Image

from audit_yolo import IMG_EXT, POPCOUNT, phash64

NAMES = ['elephant', 'giraffe', 'zebra', 'tiger', 'rhinoceros', 'non_class']
NC = len(NAMES)
SPLITS = ['train', 'val', 'test']

ap = argparse.ArgumentParser()
ap.add_argument('--v2', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--add', nargs='+', required=True, help='tag=folder (berisi images/ dan labels/)')
ap.add_argument('--uji', required=True, help='glob foto uji 500 (pemeriksaan kebocoran terakhir)')
ap.add_argument('--val-ratio', type=float, default=0.1)
ap.add_argument('--test-ratio', type=float, default=0.1)
ap.add_argument('--threshold', type=int, default=5, help='jarak pHash untuk dianggap kembar dengan v2/uji')
ap.add_argument('--group-threshold', type=int, default=8, help='jarak pHash untuk mengelompokkan gambar tambahan')
ap.add_argument('--seed', type=int, default=42)
ap.add_argument('--dry-run', action='store_true')
a = ap.parse_args()
v2, out = Path(a.v2), Path(a.out)


def ph(p):
    with Image.open(p) as im:
        return phash64(im)


def hamming(x, y):
    d = (x[:, None] ^ y[None, :]).view(np.uint8).reshape(len(x), len(y), 8)
    return POPCOUNT[d].sum(axis=2)


def min_dist(x, y, chunk=500):
    return np.concatenate([hamming(x[i:i + chunk], y).min(axis=1) for i in range(0, len(x), chunk)]) if len(x) else np.array([])


def classes_of(lbl):
    cnt = collections.Counter()
    for ln in lbl.read_text().splitlines():
        if not ln.strip(): continue
        c = int(ln.split()[0])
        if not 0 <= c < NC: raise SystemExit(f'kelas {c} tidak sah di {lbl}')
        cnt[c] += 1
    return cnt


# ---------------------------------------------------------------- v2 (disalin apa adanya)
rows = []  # dict: split, file, source, asal, cls, img, lbl, test_v2
for sp in SPLITS:
    for img in sorted((v2 / 'images' / sp).iterdir()):
        if img.suffix.lower() not in IMG_EXT: continue
        lbl = v2 / 'labels' / sp / (img.stem + '.txt')
        rows.append(dict(split=sp, file=img.name, source=img.name.split('__')[0], asal='v2', cls=classes_of(lbl),
                         img=img, lbl=lbl, test_v2=int(sp == 'test')))
h2 = np.array([ph(r['img']) for r in rows], dtype=np.uint64)
uji = sorted(glob.glob(a.uji))
hu = np.array([ph(p) for p in uji], dtype=np.uint64)
print(f'v2: {len(rows)} gambar | foto uji: {len(uji)}')
if len(uji) < 500: raise SystemExit('foto uji kurang dari 500, cek --uji')
if (min_dist(h2, hu) <= a.threshold).any(): raise SystemExit('ada gambar v2 yang mirip foto uji 500')

# ---------------------------------------------------------------- kumpulkan data tambahan
add = []  # dict: tag, img, lbl, user
for item in a.add:
    tag, _, folder = item.partition('=')
    src = Path(folder)
    users = {}
    if (src / 'sources.csv').exists():
        for r in csv.DictReader(open(src / 'sources.csv', encoding='utf-8')):
            if r.get('user'): users[r['file']] = r['user']
    n0 = len(add)
    for p in sorted((src / 'images').iterdir()):
        if p.suffix.lower() not in IMG_EXT: continue
        lbl = src / 'labels' / (p.stem + '.txt')
        if not lbl.exists(): raise SystemExit(f'label tidak ada: {lbl}')
        add.append(dict(tag=tag, img=p, lbl=lbl, user=users.get(p.name)))
    print(f'{tag}: {len(add) - n0} gambar')
hn = np.array([ph(r['img']) for r in add], dtype=np.uint64)

bad_uji = min_dist(hn, hu) <= a.threshold
if bad_uji.any():
    raise SystemExit('BERHENTI: gambar tambahan mirip foto uji 500: ' + ', '.join(str(add[i]['img']) for i in np.where(bad_uji)[0]))
dup_v2 = min_dist(hn, h2) <= a.threshold
skipped = collections.Counter(add[i]['tag'] for i in np.where(dup_v2)[0])
keep = [i for i in range(len(add)) if not dup_v2[i]]

# kelompokkan (union-find): mirip secara visual, atau pengguna iNaturalist yang sama
parent = {i: i for i in keep}


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i


hk = hn[keep]
for s in range(0, len(keep), 500):
    d = hamming(hk[s:s + 500], hk)
    for x, y in np.argwhere(d <= a.group_threshold):
        if s + x < y: parent[find(keep[s + x])] = find(keep[y])
by_user = {}
for i in keep:
    u = add[i]['user']
    if u:
        key = (add[i]['tag'], u)
        if key in by_user: parent[find(i)] = find(by_user[key])
        else: by_user[key] = i
groups = collections.defaultdict(list)
for i in keep: groups[find(i)].append(i)
print(f'tambahan dipakai {len(keep)} gambar dalam {len(groups)} kelompok; dilewati (mirip v2): {dict(skipped)}')
cross = sum(1 for g in groups.values() if len({add[i]['tag'] for i in g}) > 1)
print(f'kelompok lintas sumber: {cross}')

# bagi per sumber: kelompok diurutkan acak, isi test lalu val sampai target, sisanya train
rng = random.Random(a.seed)
by_tag = collections.defaultdict(list)
for root, g in groups.items():
    by_tag[add[g[0]]['tag']].append(root)
for tag in sorted(by_tag):
    roots = sorted(by_tag[tag]); rng.shuffle(roots)
    total = sum(len(groups[r]) for r in roots)
    target = {'test': round(total * a.test_ratio), 'val': round(total * a.val_ratio)}
    got = collections.Counter()
    for r in roots:
        sp = 'test' if got['test'] < target['test'] else 'val' if got['val'] < target['val'] else 'train'
        got[sp] += len(groups[r])
        for i in groups[r]:
            x = add[i]
            rows.append(dict(split=sp, file=f"{x['tag']}__{x['img'].stem}{x['img'].suffix.lower()}", source=x['tag'],
                             asal='v3', cls=classes_of(x['lbl']), img=x['img'], lbl=x['lbl'], test_v2=0))
    print(f'  {tag:14} train {got["train"]:5}  val {got["val"]:4}  test {got["test"]:4}')

names = collections.Counter((r['split'], r['file']) for r in rows)
if max(names.values()) > 1: raise SystemExit('nama file bentrok')

# ---------------------------------------------------------------- ringkasan
img_cnt, box_cnt, bg = collections.Counter(), collections.Counter(), collections.Counter()
for r in rows:
    if not r['cls']: bg[r['split']] += 1
    for c, n in r['cls'].items():
        img_cnt[(r['split'], c)] += 1; box_cnt[(r['split'], c)] += n
summary = []
for title, cnt in [('Gambar yang memuat kelas', img_cnt), ('Jumlah kotak (objek)', box_cnt)]:
    summary.append(f'\n{title}:')
    summary.append(f"{'split':6}" + ''.join(f'{n:>11}' for n in NAMES) + (f"{'tanpa hewan':>13}" if 'Gambar' in title else ''))
    for sp in SPLITS:
        summary.append(f'{sp:6}' + ''.join(f'{cnt[(sp, c)]:>11}' for c in range(NC)) + (f'{bg[sp]:>13}' if 'Gambar' in title else ''))
tot = collections.Counter(r['split'] for r in rows)
summary.append(f"\nTotal gambar: train {tot['train']}, val {tot['val']}, test {tot['test']} (test_v2 {sum(r['test_v2'] for r in rows)})")
tr = [img_cnt[('train', c)] for c in range(5)]
summary.append(f'Rasio train 5 satwa target terbesar : terkecil = {max(tr) / min(tr):.2f} : 1')
summary.append(f"Background (tanpa hewan) di train: {bg['train'] / tot['train']:.1%}")
print('\n'.join(summary))
if a.dry_run: raise SystemExit

# ---------------------------------------------------------------- tulis
if out.exists() and any(out.iterdir()): raise SystemExit(f'{out} sudah berisi file; hapus dulu atau pilih folder lain')
for sp in SPLITS:
    (out / 'images' / sp).mkdir(parents=True, exist_ok=True); (out / 'labels' / sp).mkdir(parents=True, exist_ok=True)
with open(out / 'split_manifest_v3.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['split', 'file', 'source', 'asal', 'test_v2'] + NAMES)
    for r in rows:
        shutil.copy2(r['img'], out / 'images' / r['split'] / r['file'])
        shutil.copy2(r['lbl'], out / 'labels' / r['split'] / (Path(r['file']).stem + '.txt'))
        w.writerow([r['split'], r['file'], r['source'], r['asal'], r['test_v2']] + [r['cls'].get(c, 0) for c in range(NC)])
(out / 'data.yaml').write_text('path: .\ntrain: images/train\nval: images/val\ntest: images/test\n'
                               f'nc: {NC}\nnames: {NAMES}\n', encoding='utf-8')
(out / 'ringkasan_split_v3.txt').write_text('\n'.join(summary).strip() + '\n', encoding='utf-8')


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


same = all(md5(r['img']) == md5(out / 'images' / 'test' / r['file']) and
           md5(r['lbl']) == md5(out / 'labels' / 'test' / (Path(r['file']).stem + '.txt'))
           for r in rows if r['test_v2'])
print(f"\nTest v2 di dalam test v3 identik dengan aslinya: {'YA' if same else 'TIDAK'}")
