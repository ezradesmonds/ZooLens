"""Unduh foto satu takson dari iNaturalist (tanpa kotak) untuk diberi kotak lalu dikoreksi manual.

Aturan:
- Hanya foto berlisensi --licenses (default CC BY, CC BY-SA, CC0). Lisensi dicatat per foto.
- Observasi liar: research grade. Observasi kebun binatang (captive=true): semua grade, tetap dicek manual.
- Hanya foto pertama tiap observasi (foto lain biasanya hampir sama).
- Maksimal --per-user observasi per pengguna supaya sumber beragam.
- Observasi yang ada di --exclude (mis. manifest uji 500) dilewati.
- Gambar diperkecil ke sisi terpanjang --max-side px.
- --max N: ambil sampel acak N observasi (seed 0) bila kandidat lebih banyak.

Output: <out>/images/inat_<photo_id>.jpg dan <out>/sources.csv

Contoh:
  python ml/scripts/v3/fetch_inaturalist.py --taxon 43341 --out D:/Project/DataSetZoo/ZooLens/badak_inaturalist \
      --exclude ml/uji500/manifest_uji500.csv
"""
import argparse, collections, csv, io, json, random, re, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image

UA = {'User-Agent': 'ZooLens-student-project/1.0'}
ap = argparse.ArgumentParser()
ap.add_argument('--taxon', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--licenses', default='cc-by,cc-by-sa,cc0')
ap.add_argument('--per-user', type=int, default=15)
ap.add_argument('--exclude', nargs='*', default=[])
ap.add_argument('--max-side', type=int, default=1024)
ap.add_argument('--workers', type=int, default=4)
ap.add_argument('--max', type=int, default=0, help='ambil sampel acak (seed 0) sebanyak ini; 0 = semua')
ap.add_argument('--dry-run', action='store_true')
a = ap.parse_args()


def api(path, **q):
    url = 'https://api.inaturalist.org/v1/' + path + '?' + urllib.parse.urlencode(q)
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception as e:
            print('ulang', e); time.sleep(5 * (i + 1))
    raise SystemExit('API gagal: ' + url)


excl = set()
for f in a.exclude:
    excl |= set(re.findall(r'inaturalist\.org/observations/(\d+)', open(f, encoding='utf-8').read()))
# --taxon boleh angka (ID takson, paling aman) atau nama; pencarian nama bisa salah sasaran
# (mis. 'Panthera tigris' mengembalikan genus Panthera), jadi namanya dicek harus sama persis.
if a.taxon.isdigit():
    tax = api('taxa/' + a.taxon)['results'][0]
else:
    tax = api('taxa', q=a.taxon, per_page=1)['results'][0]
    if tax['name'].lower() != a.taxon.lower(): raise SystemExit(f"takson '{a.taxon}' tidak cocok persis ({tax['name']}); pakai ID takson")
print('takson:', tax['id'], tax['name'], '| observasi dikecualikan:', len(excl))

obs = {}
for kind, extra in [('liar', dict(quality_grade='research', captive='false')), ('captive', dict(captive='true'))]:
    id_below = None
    while True:
        q = dict(taxon_id=tax['id'], photos='true', photo_license=a.licenses, per_page=200, order_by='id', order='desc', **extra)
        if id_below: q['id_below'] = id_below
        res = api('observations', **q)['results']
        if not res: break
        for o in res:
            o['_kind'] = kind; obs.setdefault(o['id'], o)
        id_below = res[-1]['id']; time.sleep(1)
print('observasi ditemukan:', len(obs))

per_user = collections.Counter(); jobs = []
for oid, o in sorted(obs.items()):
    if str(oid) in excl: continue
    lic_ok = [p for p in o.get('photos', []) if (p.get('license_code') or '') in a.licenses.split(',')]
    if not lic_ok: continue
    user = o['user']['login']
    if per_user[user] >= a.per_user: continue
    per_user[user] += 1
    p = lic_ok[0]
    jobs.append(dict(file=f"inat_{p['id']}.jpg", url=p['url'].replace('square', 'large'), observation_url=f'https://www.inaturalist.org/observations/{oid}',
                     photo_id=p['id'], license=p['license_code'], attribution=p['attribution'], jenis=o['_kind'],
                     taxon=(o.get('taxon') or {}).get('name', ''), user=user, observed_on=o.get('observed_on') or '',
                     place=(o.get('place_guess') or '').replace('\n', ' ')))
if a.max and len(jobs) > a.max: jobs = sorted(random.Random(0).sample(jobs, a.max), key=lambda j: j['file'])
print('akan diunduh:', len(jobs), collections.Counter(j['jenis'] for j in jobs), collections.Counter(j['license'] for j in jobs))
if a.dry_run: raise SystemExit

out = Path(a.out); (out / 'images').mkdir(parents=True, exist_ok=True)


def fetch(j):
    dst = out / 'images' / j['file']
    if dst.exists(): return True
    for i in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(j['url'], headers=UA), timeout=60).read()
            im = Image.open(io.BytesIO(data)).convert('RGB'); im.thumbnail((a.max_side, a.max_side))
            tmp = dst.with_suffix('.part'); im.save(tmp, 'JPEG', quality=92); tmp.replace(dst)
            return True
        except Exception as e:
            err = e; time.sleep(2)
    print('GAGAL', j['file'], err); return False


with ThreadPoolExecutor(a.workers) as ex:
    ok = list(ex.map(fetch, jobs))
rows = [j for j, k in zip(jobs, ok) if k]
with open(out / 'sources.csv', 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(jobs[0])); w.writeheader(); w.writerows(rows)
print('selesai:', len(rows), 'foto ->', out)
