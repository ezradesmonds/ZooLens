"""Pilih dan bekukan subset uji 500 foto (250 positif + 250 negatif).

Input: kandidat (collect_candidates.py), indeks lembar pratinjau (preview_sheets.py), dan
file penilaian awal `<kelompok>.txt` berisi "nomor kode" per baris.
Kode positif: F Full, R Occlusion ringan, S Occlusion sedang, B Occlusion berat, T Truncation, X ditolak.
Kode negatif: H vegetasi rimbun, L bunga/lanskap, O objek/bangunan/orang, A hewan lain, X ditolak.

Kuota positif per kelas (50): Full 10, Truncation 10, Occlusion berat dan sedang masing-masing
sampai 12, sisanya Occlusion ringan (lalu Full bila masih kurang). Occlusion sengaja diperbanyak
karena hipotesa H1 dan H4 membandingkan kondisi itu.
Kuota negatif (250): 100 vegetasi (yang rimbun didahulukan), 100 hewan lain, 50 objek.

Output: <out>/positif/<kelas>/, <out>/negatif/<jenis>/, dan manifest CSV dengan MD5 tiap file.
Pemilihan acak memakai seed tetap, jadi hasilnya bisa diulang.
"""
import argparse, collections, csv, hashlib, random, shutil
from pathlib import Path

COND = {'F': 'Full', 'R': 'Occlusion ringan', 'S': 'Occlusion sedang', 'B': 'Occlusion berat', 'T': 'Truncation'}
NEG = {'H': 'vegetasi rimbun', 'L': 'vegetasi lain', 'O': 'objek/bangunan/orang', 'A': 'hewan lain'}
CLASSES = ['elephant', 'giraffe', 'zebra', 'tiger', 'rhinoceros']

ap = argparse.ArgumentParser()
ap.add_argument('--cand', required=True); ap.add_argument('--review', required=True)
ap.add_argument('--rating', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--manifest', required=True); ap.add_argument('--seed', type=int, default=500)
a = ap.parse_args()
cand, review, rating, out = Path(a.cand), Path(a.review), Path(a.rating), Path(a.out)
rng = random.Random(a.seed)
meta = {(r['kelompok'], r['file']): r for r in csv.DictReader(open(cand / 'candidates.csv', encoding='utf-8'))}


def rated(group):
    idx = {int(r['nomor']): r['file'] for r in csv.DictReader(open(review / f'{group}_index.csv', encoding='utf-8'))}
    by = collections.defaultdict(list)
    for ln in open(rating / f'{group}.txt'):
        n, code = ln.split(); by[code].append(idx[int(n)])
    return {k: sorted(v) for k, v in by.items()}


def take(pool, n):
    return rng.sample(pool, min(n, len(pool)))


picked = []  # (kelompok kandidat, file, Kelompok, kelas, kondisi awal, jenis negatif)
for cls in CLASSES:
    by = rated(f'pos_{cls}')
    sel = {'F': take(by.get('F', []), 10), 'T': take(by.get('T', []), 10),
           'B': take(by.get('B', []), 12), 'S': take(by.get('S', []), 12)}
    sel['R'] = take(by.get('R', []), 50 - sum(map(len, sel.values())))
    short = 50 - sum(map(len, sel.values()))
    if short > 0:
        sel['F'] += take([f for f in by.get('F', []) if f not in sel['F']], short)
    for code, files in sel.items():
        picked += [(f'pos_{cls}', f, 'Positif', cls, COND[code], '') for f in files]

by = rated('neg_vegetasi')
veg = [(f, 'H') for f in take(by['H'], 100)]
veg += [(f, 'L') for f in take(by['L'], 100 - len(veg))]
picked += [('neg_vegetasi', f, 'Negatif', '', 'Tidak berlaku', NEG[c]) for f, c in veg]
picked += [('neg_hewan_lain', f, 'Negatif', '', 'Tidak berlaku', NEG['A']) for f in take(rated('neg_hewan_lain')['A'], 100)]
picked += [('neg_objek', f, 'Negatif', '', 'Tidak berlaku', NEG['O']) for f in take(rated('neg_objek')['O'], 50)]

rows = []
count = collections.Counter()
for group, f, kel, cls, cond, neg in picked:
    m = meta[(group, f)]
    sub = Path('positif') / cls if kel == 'Positif' else Path('negatif') / group.replace('neg_', '')
    tag = cls if kel == 'Positif' else group.replace('neg_', '')
    count[tag] += 1
    name = f"{'P' if kel == 'Positif' else 'N'}_{tag}_{count[tag]:03d}.jpg"
    (out / sub).mkdir(parents=True, exist_ok=True)
    shutil.copy2(cand / group / f, out / sub / name)
    md5 = hashlib.md5((out / sub / name).read_bytes()).hexdigest()
    hint = m['petunjuk'] if kel == 'Negatif' and group == 'neg_hewan_lain' else ''
    rows.append([len(rows) + 1, name, str(sub).replace('\\', '/'), kel, cls, cond, neg, hint,
                 m['sumber_lisensi'], m['url'], f, md5])
with open(a.manifest, 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['no', 'file', 'folder', 'kelompok', 'kelas', 'kondisi_awal', 'jenis_negatif', 'hewan_lain',
                'sumber_lisensi', 'url', 'file_asal', 'md5'])
    w.writerows(rows)
print('total', len(rows), collections.Counter(r[3] for r in rows))
tab = collections.Counter((r[4], r[5]) for r in rows if r[3] == 'Positif')
print(f"{'kelas':11}" + ''.join(f'{c[:14]:>16}' for c in COND.values()))
for cls in CLASSES:
    print(f'{cls:11}' + ''.join(f'{tab[(cls, c)]:>16}' for c in COND.values()))
print(f"{'TOTAL':11}" + ''.join(f'{sum(tab[(k, c)] for k in CLASSES):>16}' for c in COND.values()))
print('negatif:', dict(collections.Counter(r[6] for r in rows if r[3] == 'Negatif')))
