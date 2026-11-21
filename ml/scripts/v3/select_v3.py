"""Pilih gambar tambahan untuk dataset v3 dan tulis manifest unduhan (belum mengunduh).

Kelas v3: 0 elephant, 1 giraffe, 2 zebra, 3 tiger, 4 rhinoceros, 5 non_class (hewan lain).
Background = foto tanpa hewan, label kosong.

Aturan label (Open Images):
- Kotak satwa target -> ID kelasnya. Kotak hewan spesifik lain -> 5 (non_class).
- Kotak umum (Animal, Mammal, Marine mammal, Reptile) dibuang bila menimpa kotak spesifik (IoU >= 0,5).
  Bila ada kotak umum yang tidak cocok dengan kotak spesifik mana pun, gambar dilewati (hewannya tidak jelas).
- Gambar dilewati bila ada kotak hewan IsDepiction=1 (patung, gambar) atau IsGroupOf=1 (satu kotak
  untuk sekelompok), atau ada Dinosaur/Teddy bear.
Aturan label (COCO 2017):
- elephant/giraffe/zebra -> 0/1/2; bird, cat, dog, horse, sheep, cow, bear -> 5.
- Gambar dengan anotasi hewan iscrowd=1 dilewati. Lisensi ND (no derivatives) dilewati.
Pengecualian: ID Open Images yang sudah dipakai di v2 dan di subset uji 500.

Contoh:
  python ml/scripts/v3/select_v3.py --oi-dir D:/Project/v3_work/oi --oi-valtest D:/Project/uji500_work/oi \
      --coco D:/Project/v3_work/coco/ann.zip --out D:/Project/v3_work/manifest --dry-run
"""
import argparse, collections, csv, glob, json, random, re, zipfile
from pathlib import Path

TARGET = {'/m/0bwd_0j': 0, '/m/03bk1': 1, '/m/0898b': 2, '/m/07dm6': 3, '/m/03d443': 4}
GENERIC = {'/m/0jbk', '/m/04rky', '/m/0gd2v', '/m/06bt6'}  # Animal, Mammal, Marine mammal, Reptile
SKIP = {'/m/029tx', '/m/0kmg4'}  # Dinosaur, Teddy bear
OI_URL = 'https://open-images-dataset.s3.amazonaws.com/{split}/{id}.jpg'
OI_LIC = 'Open Images V7; gambar CC BY 2.0, anotasi CC BY 4.0'
COCO_ANIMAL = {'elephant': 0, 'giraffe': 1, 'zebra': 2, 'bird': 5, 'cat': 5, 'dog': 5, 'horse': 5, 'sheep': 5, 'cow': 5, 'bear': 5}
COCO_ND = {3, 6}
# kuota non_class (gambar), hewan yang mirip satwa target diutamakan
NONCLASS_QUOTA = {'Deer': 260, 'Antelope': 200, 'Camel': 200, 'Lion': 200, 'Leopard': 180, 'Cheetah': 150, 'Jaguar (Animal)': 120,
                  'Lynx': 100, 'Hippopotamus': 160, 'Horse': 150, 'Cattle': 150, 'Bull': 60, 'Goat': 70, 'Sheep': 50,
                  'Brown bear': 60, 'Polar bear': 30, 'Bear': 30, 'Kangaroo': 60, 'Ostrich': 60, 'Monkey': 70, 'Dog': 40,
                  'Cat': 40, 'Pig': 30, 'Mule': 30, 'Alpaca': 30, 'Crocodile': 30, 'Bird': 30, 'Tortoise': 20, 'Fox': 20}

ap = argparse.ArgumentParser()
ap.add_argument('--oi-dir', required=True)
ap.add_argument('--oi-valtest', required=True)
ap.add_argument('--coco', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--used-sources', default='D:/Project/DataSetZoo/ZooLens/*_openimages/sources.csv')
ap.add_argument('--uji500', default='ml/uji500/manifest_uji500.csv')
ap.add_argument('--need', default='elephant=1150,giraffe=1100,zebra=1350,tiger=1100')
ap.add_argument('--bg', type=int, default=1300)
ap.add_argument('--seed', type=int, default=42)
ap.add_argument('--dry-run', action='store_true')
a = ap.parse_args()
rng = random.Random(a.seed)
NAMES = {l.split(',')[0]: l.strip().split(',', 1)[1] for l in open(Path(__file__).with_name('animal_ids.csv'), encoding='utf-8')}
CLS = ['elephant', 'giraffe', 'zebra', 'tiger', 'rhinoceros']

used = set()
for f in glob.glob(a.used_sources):
    used |= {r['openimages_id'] for r in csv.DictReader(open(f, encoding='utf-8'))}
used |= set(re.findall(r'/([0-9a-f]{16})\.jpg', open(a.uji500, encoding='utf-8').read()))
print('ID Open Images dikecualikan:', len(used))


def iou(p, q):
    ix = max(0, min(p[1], q[1]) - max(p[0], q[0])); iy = max(0, min(p[3], q[3]) - max(p[2], q[2]))
    inter = ix * iy; u = (p[1] - p[0]) * (p[3] - p[2]) + (q[1] - q[0]) * (q[3] - q[2]) - inter
    return inter / u if u else 0


def oi_images(path, split):
    boxes = collections.defaultdict(list)
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if r['LabelName'] in NAMES or r['LabelName'] in SKIP:
            boxes[r['ImageID']].append(r)
    out = {}
    for img, bs in boxes.items():
        if img in used: continue
        if any(b['LabelName'] in SKIP or b['IsDepiction'] == '1' or b['IsGroupOf'] == '1' for b in bs): continue
        spec = [b for b in bs if b['LabelName'] not in GENERIC]
        gen = [b for b in bs if b['LabelName'] in GENERIC]
        xy = lambda b: [float(b['XMin']), float(b['XMax']), float(b['YMin']), float(b['YMax'])]
        if any(all(iou(xy(g), xy(s)) < 0.5 for s in spec) for g in gen): continue
        if not spec: continue
        cid = lambda b: TARGET.get(b['LabelName'], 5)
        # satu hewan diberi dua label berbeda (mis. Leopard + Cheetah): gabungkan bila sama-sama non_class,
        # lewati gambar bila salah satunya satwa target (labelnya meragukan)
        if any(cid(p) != cid(q) and iou(xy(p), xy(q)) >= 0.5 for i, p in enumerate(spec) for q in spec[i + 1:]): continue
        keep = []
        for b in spec:
            if not any(cid(k) == cid(b) == 5 and iou(xy(k), xy(b)) >= 0.7 for k in keep): keep.append(b)
        lines = []
        for b in keep:
            x0, x1, y0, y1 = xy(b)
            lines.append('%d %.6f %.6f %.6f %.6f' % (cid(b), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0))
        out[img] = dict(split=split, lines=lines, labels={NAMES[b['LabelName']] for b in spec},
                        targets={TARGET[b['LabelName']] for b in spec if b['LabelName'] in TARGET})
    return out


oi = oi_images(Path(a.oi_dir) / 'train-animals.sub.csv', 'train')
for sp, fn in [('validation', 'validation-bbox.csv'), ('test', 'test-bbox.csv')]:
    oi.update(oi_images(Path(a.oi_valtest) / fn, sp))
print('gambar Open Images lolos aturan:', len(oi))

# COCO
z = zipfile.ZipFile(a.coco); coco = {}
for split in ['train2017', 'val2017']:
    d = json.loads(z.read(f'annotations/instances_{split}.json'))
    cats = {c['id']: c['name'] for c in d['categories']}
    lic = {l['id']: l['name'] for l in d['licenses']}
    im = {i['id']: i for i in d['images']}
    anns = collections.defaultdict(list)
    for an in d['annotations']:
        if cats[an['category_id']] in COCO_ANIMAL: anns[an['image_id']].append(an)
    for iid, aa in anns.items():
        i = im[iid]
        if i['license'] in COCO_ND or any(an['iscrowd'] for an in aa): continue
        tg = {COCO_ANIMAL[cats[an['category_id']]] for an in aa} - {5}
        if not tg: continue
        W, H = i['width'], i['height']
        lines = ['%d %.6f %.6f %.6f %.6f' % (COCO_ANIMAL[cats[an['category_id']]], (an['bbox'][0] + an['bbox'][2] / 2) / W,
                                             (an['bbox'][1] + an['bbox'][3] / 2) / H, an['bbox'][2] / W, an['bbox'][3] / H) for an in aa]
        coco[f'{split}_{iid}'] = dict(url=i['coco_url'], lines=lines, targets=tg, license=lic[i['license']],
                                      flickr=i.get('flickr_url', ''))
print('gambar COCO lolos aturan:', len(coco))

need = {k: int(v) for k, v in (x.split('=') for x in a.need.split(','))}
groups = collections.defaultdict(list); taken = set()
for name, n in need.items():
    c = CLS.index(name)
    pool = sorted(i for i, r in oi.items() if c in r['targets'] and i not in taken); rng.shuffle(pool)
    pick = pool[:n]; taken |= set(pick)
    groups[f'{name}_oi'] = pick
    rest = n - len(pick)
    if rest > 0 and name in ('elephant', 'giraffe', 'zebra'):
        cp = sorted(k for k, r in coco.items() if c in r['targets'] and k not in taken)
        # lisensi tanpa NC diutamakan
        cp.sort(key=lambda k: ('NonCommercial' in coco[k]['license'], rng.random()))
        groups[f'{name}_coco'] = cp[:rest]; taken |= set(cp[:rest])

# non_class: gambar Open Images tanpa satwa target
for lab, q in NONCLASS_QUOTA.items():
    pool = sorted(i for i, r in oi.items() if not r['targets'] and lab in r['labels'] and i not in taken); rng.shuffle(pool)
    groups['nonclass_oi'] += pool[:q]; taken |= set(pool[:q])

# background
bgc = Path(a.oi_dir) / 'bg_categories.csv'
if bgc.exists():
    rows = [r for r in csv.DictReader(open(bgc)) if r['ada_depiction'] == '0' and r['ImageID'] not in used and r['ImageID'] not in taken]
    rng.shuffle(rows)
    plan = [('vegetasi', {'Tree', 'Plant', 'Flower', 'Palm tree'}, 0.45), ('bangunan', {'Building', 'House'}, 0.2),
            ('orang', {'Person'}, 0.25), ('kendaraan_lain', {'Car', 'Airplane', 'Food', 'lain'}, 0.1)]
    got = set()
    for nm, keys, frac in plan:
        sel = [r['ImageID'] for r in rows if r['ImageID'] not in got and keys & set(r['labels'].split('|'))][:int(a.bg * frac)]
        got |= set(sel); groups['background_oi'] += sel
else:
    print('bg_categories.csv belum ada, background dilewati')

total = 0
for g, ids in groups.items():
    print('%-16s %5d' % (g, len(ids))); total += len(ids)
print('total', total)
cnt = collections.Counter(l for i in groups['nonclass_oi'] for l in oi[i]['labels'])
print('non_class per hewan (label dalam gambar):', dict(cnt.most_common(15)))
if a.dry_run: raise SystemExit

out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
for g, ids in groups.items():
    with open(out / f'{g}.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f); w.writerow(['file', 'sumber_id', 'url', 'lisensi', 'label'])
        for i in ids:
            if g.endswith('_coco'):
                r = coco[i]; w.writerow([f'coco_{i}.jpg', i, r['url'], 'COCO 2017; anotasi CC BY 4.0; gambar ' + r['license'] + ' ' + r['flickr'], ';'.join(r['lines'])])
            elif g == 'background_oi':
                w.writerow([f'oi_{i}.jpg', i, OI_URL.format(split='train', id=i), OI_LIC, ''])
            else:
                r = oi[i]; w.writerow([f'oi_{i}.jpg', i, OI_URL.format(split=r['split'], id=i), OI_LIC, ';'.join(r['lines'])])
print('manifest ditulis ke', out)
