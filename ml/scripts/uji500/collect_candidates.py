"""Kumpulkan kandidat foto uji 500 (positif dan negatif) beserta sumber dan lisensinya.

Sumber:
- Open Images V7 (anotasi CC BY 4.0, gambar CC BY 2.0): gajah, jerapah, zebra, harimau, dan semua foto negatif.
  Gambar yang sudah dipakai di data training v2 (badak_openimages, gajah_openimages) dikecualikan lewat ID.
- iNaturalist (lisensi CC per foto): badak, karena seluruh badak Open Images sudah dipakai untuk training v2.
- Foto pilot lokal (--pilot): disalin apa adanya.

Output: <out>/<kelompok>/<file>.jpg dan <out>/candidates.csv
"""
import argparse, collections, csv, glob, io, json, random, shutil, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image

T = {'/m/0bwd_0j': 'elephant', '/m/03bk1': 'giraffe', '/m/0898b': 'zebra', '/m/07dm6': 'tiger', '/m/03d443': 'rhinoceros'}
LOOKALIKE = {'/m/09f20': 'hippopotamus', '/m/096mb': 'lion', '/m/0c29q': 'leopard', '/m/0cd4d': 'cheetah',
             '/m/0449p': 'jaguar', '/m/03k3r': 'horse', '/m/01xq0k1': 'cattle', '/m/09kx5': 'deer',
             '/m/0czz2': 'antelope', '/m/01x_v': 'camel', '/m/01dxs': 'brown bear', '/m/0cnyhnx': 'bull',
             '/m/0dbzx': 'mule', '/m/07bgp': 'sheep', '/m/03fwl': 'goat', '/m/068zj': 'pig',
             '/m/04c0y': 'kangaroo', '/m/05n4y': 'ostrich', '/m/08pbxl': 'monkey', '/m/04g2r': 'lynx'}
VEG = {'/m/07j7r', '/m/05s2s', '/m/0c9ph5', '/m/0cdl1', '/m/03fp41'}
OBJ = {'/m/01g317', '/m/0cgh4', '/m/03jm5', '/m/0cvnqh', '/m/0k4j', '/m/0220r2', '/m/0d5gx', '/m/01fdzj'}
S3 = 'https://open-images-dataset.s3.amazonaws.com/{split}/{id}.jpg'
OI_LIC = 'Open Images V7; gambar CC BY 2.0, anotasi CC BY 4.0'
UA = {'User-Agent': 'ZooLens-student-project/1.0'}

ap = argparse.ArgumentParser()
ap.add_argument('--ann', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--exclude', nargs='*', default=[], help='sources.csv data training (kolom openimages_id)')
ap.add_argument('--pilot', nargs='*', default=[], help='kelas=pola_glob foto pilot lokal')
ap.add_argument('--seed', type=int, default=500)
a = ap.parse_args()
rng = random.Random(a.seed); ann = Path(a.ann); out = Path(a.out)
used = set()
for f in a.exclude:
    used |= {r['openimages_id'] for r in csv.DictReader(open(f, encoding='utf-8'))}
jobs = []  # (kelompok, nama, url unduh, meta)

# ------------------------------------------------ positif Open Images (satu satwa target per foto)
per = collections.defaultdict(list)
for split in ['train', 'validation', 'test']:
    for r in csv.reader(open(ann / f'{split}-annotations-bbox.sub.csv', encoding='utf-8')):
        if r[2] in T: per[(split, r[0])].append(r)
bucket = collections.defaultdict(list)
for (split, img), rs in per.items():
    if img in used or len(rs) != 1: continue
    r = rs[0]; cls = T[r[2]]
    if cls == 'rhinoceros' or r[10] == '1' or r[11] == '1': continue
    area = (float(r[5]) - float(r[4])) * (float(r[7]) - float(r[6]))
    if area < 0.03: continue
    occ, trunc = r[8] == '1', r[9] == '1'
    kind = 'occ' if occ and not trunc else 'trunc' if trunc and not occ else 'none' if not occ and not trunc else None
    if kind: bucket[(cls, kind)].append((split, img))
for (cls, kind), items in sorted(bucket.items()):
    n = {'occ': 60, 'trunc': 25, 'none': 20}[kind]
    for split, img in rng.sample(sorted(items), min(n, len(items))):
        url = S3.format(split=split, id=img)
        jobs.append((f'pos_{cls}', f'oi_{img}.jpg', url, dict(kelas=cls, sumber=OI_LIC, url=url, petunjuk=kind)))

# ------------------------------------------------ negatif Open Images (validation + test, anotasi lengkap)
labs = collections.defaultdict(set); dep = set()
for split in ['validation', 'test']:
    for r in csv.reader(open(ann / f'{split}-bbox.csv', encoding='utf-8')):
        if r[0] == 'ImageID': continue
        labs[(split, r[0])].add(r[2])
        if r[11] == '1': dep.add((split, r[0]))
veg = [k for k, s in labs.items() if s <= VEG]
obj = [k for k, s in labs.items() if s <= OBJ and k not in dep]
look = collections.defaultdict(list)
for k, s in labs.items():
    if s & set(T) or k in dep: continue
    hit = s & set(LOOKALIKE)
    if len(hit) == 1: look[LOOKALIKE[next(iter(hit))]].append(k)


def add_neg(group, items, n, hint):
    for split, img in rng.sample(sorted(items), min(n, len(items))):
        url = S3.format(split=split, id=img)
        jobs.append((group, f'oi_{img}.jpg', url, dict(kelas='', sumber=OI_LIC, url=url, petunjuk=hint)))


add_neg('neg_vegetasi', veg, 140, 'vegetasi')
add_neg('neg_objek', obj, 75, 'objek/orang')
for name, items in sorted(look.items()): add_neg('neg_hewan_lain', items, 8, name)


# ------------------------------------------------ badak iNaturalist
def api(path, **q):
    req = urllib.request.Request('https://api.inaturalist.org/v1/' + path + '?' + urllib.parse.urlencode(q), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=60))


tid = api('taxa', q='Rhinocerotidae', rank='family')['results'][0]['id']
seen = collections.Counter(); rh = []
for hint, extra in [('liar', dict(quality_grade='research')), ('captive', dict(captive='true'))]:
    for page in (1, 2):
        res = api('observations', taxon_id=tid, photo_license='cc-by,cc0,cc-by-sa,cc-by-nc', per_page=200, page=page,
                  order_by='id', order='desc', **extra)['results']
        for o in res:
            if not o.get('photos') or seen[o['user']['login']] >= 2: continue
            p = o['photos'][0]
            if not p.get('license_code'): continue
            seen[o['user']['login']] += 1
            rh.append(('pos_rhinoceros', f"inat_{p['id']}.jpg", p['url'].replace('square', 'large'),
                       dict(kelas='rhinoceros', sumber=f"iNaturalist; {p['license_code'].upper()}; {p['attribution']}",
                            url=f"https://www.inaturalist.org/observations/{o['id']}", petunjuk=hint)))
jobs += rng.sample(rh, min(110, len(rh)))


# ------------------------------------------------ unduh
def fetch(j):
    group, name, url, meta = j
    dst = out / group / name; dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists(): return True
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        im = Image.open(io.BytesIO(data)).convert('RGB')
        im.thumbnail((1280, 1280)); tmp = dst.with_suffix('.part'); im.save(tmp, 'JPEG', quality=90); tmp.replace(dst)
        return True
    except Exception as e:
        print('GAGAL', name, e); return False


with ThreadPoolExecutor(8) as ex: ok = list(ex.map(fetch, jobs))
rows = [(g, n, m['kelas'], m['sumber'], m['url'], m['petunjuk']) for (g, n, u, m), k in zip(jobs, ok) if k]
for item in a.pilot:
    cls, _, pat = item.partition('=')
    for f in sorted(glob.glob(pat)):
        dst = out / f'pos_{cls}' / ('pilot_' + Path(f).name); dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
        rows.append((f'pos_{cls}', dst.name, cls, 'Foto pilot tim (sumber bebas; lihat catatan pengumpul)', '', 'pilot'))
with open(out / 'candidates.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['kelompok', 'file', 'kelas', 'sumber_lisensi', 'url', 'petunjuk']); w.writerows(rows)
print(sorted(collections.Counter(r[0] for r in rows).items()))
