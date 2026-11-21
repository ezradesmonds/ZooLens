"""Hitung ketersediaan data Open Images untuk dataset v3 (tanpa mengunduh gambar).

Membaca CSV bbox dari stdin, menghitung gambar per kelas, menyimpan baris kelas hewan, dan
mencari kandidat background (gambar berisi pohon/bangunan/orang tanpa kotak hewan).

Contoh:
  curl -s https://storage.googleapis.com/openimages/v6/oidv6-train-annotations-bbox.csv \
    | python ml/scripts/v3/count_openimages.py D:/Project/v3_work/oi ml/scripts/v3/animal_ids.csv
"""
import sys, csv, json
from collections import defaultdict

out_dir = sys.argv[1]
animal_ids = set(l.split(',')[0] for l in open(sys.argv[2], encoding='utf-8') if l.strip())
BG = {'/m/07j7r': 'Tree', '/m/05s2s': 'Plant', '/m/0c9ph5': 'Flower', '/m/0cdl1': 'Palm tree',
      '/m/0cgh4': 'Building', '/m/03jm5': 'House', '/m/01g317': 'Person', '/m/0k4j': 'Car'}

imgs = defaultdict(set); clean = defaultdict(set); boxes = defaultdict(int)
animal_imgs = set(); bg_imgs = defaultdict(set)
sub = open(out_dir + '/train-animals.sub.csv', 'w', encoding='utf-8', newline='')
r = csv.reader(sys.stdin)
header = next(r); sub.write(','.join(header) + '\n')
n = 0
for row in r:
    n += 1
    img, lab = row[0], row[2]
    gof, dep = row[10], row[11]
    boxes[lab] += 1; imgs[lab].add(img)
    if gof == '0' and dep == '0':
        clean[lab].add(img)
    if lab in animal_ids:
        animal_imgs.add(img); sub.write(','.join(row) + '\n')
    if lab in BG:
        bg_imgs[lab].add(img)
sub.close()
stats = {lab: {'boxes': boxes[lab], 'images': len(imgs[lab]), 'clean_images': len(clean[lab])} for lab in boxes}
bg = {}
allbg = set()
for lab, s in bg_imgs.items():
    s2 = s - animal_imgs; allbg |= s2
    bg[BG[lab]] = len(s2)
bg['union_tanpa_hewan'] = len(allbg)
json.dump({'rows': n, 'per_class': stats, 'background_candidates': bg}, open(out_dir + '/train_counts.json', 'w'), indent=1)
open(out_dir + '/train_bg_ids.txt', 'w').write('\n'.join(sorted(allbg)))
print('rows', n, 'animal images', len(animal_imgs), 'bg', bg)
