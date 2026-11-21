"""Catat kategori tiap kandidat background (foto tanpa kotak hewan) dari CSV bbox Open Images di stdin.

Contoh:
  curl -s <oidv6-train-annotations-bbox.csv> | python ml/scripts/v3/bg_categories.py train_bg_ids.txt bg_categories.csv
"""
import csv, sys
from collections import defaultdict

ids = set(open(sys.argv[1]).read().split())
NAMES = {'/m/07j7r': 'Tree', '/m/05s2s': 'Plant', '/m/0c9ph5': 'Flower', '/m/0cdl1': 'Palm tree', '/m/0cgh4': 'Building',
         '/m/03jm5': 'House', '/m/01g317': 'Person', '/m/0k4j': 'Car', '/m/02wbm': 'Food', '/m/0cmf2': 'Airplane'}
labs = defaultdict(set); depic = set()
r = csv.reader(sys.stdin); next(r)
for row in r:
    if row[0] in ids:
        labs[row[0]].add(NAMES.get(row[2], 'lain'))
        if row[11] == '1': depic.add(row[0])
with open(sys.argv[2], 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['ImageID', 'labels', 'ada_depiction'])
    for i in sorted(labs): w.writerow([i, '|'.join(sorted(labs[i])), int(i in depic)])
print(len(labs), 'kandidat')
