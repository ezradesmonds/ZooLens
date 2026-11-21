"""Unduh gambar dari manifest select_v3.py dan tulis label YOLO.

Output: <out>/images/<file>, <out>/labels/<file>.txt (kosong untuk background), <out>/sources.csv.
Gambar diperkecil ke sisi terpanjang --max-side px; koordinat YOLO ternormalisasi jadi tetap benar.

Contoh:
  python ml/scripts/v3/fetch_manifest.py --manifest D:/Project/v3_work/manifest/zebra_coco.csv --out D:/Project/DataSetZoo/ZooLens/v3/zebra_coco
"""
import argparse, csv, io, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image

UA = {'User-Agent': 'ZooLens-student-project/1.0'}
ap = argparse.ArgumentParser()
ap.add_argument('--manifest', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--max-side', type=int, default=1024)
ap.add_argument('--workers', type=int, default=8)
a = ap.parse_args()

rows = list(csv.DictReader(open(a.manifest, encoding='utf-8')))
out = Path(a.out); (out / 'images').mkdir(parents=True, exist_ok=True); (out / 'labels').mkdir(exist_ok=True)


def fetch(r):
    dst = out / 'images' / r['file']; lb = out / 'labels' / (r['file'][:-4] + '.txt')
    if not dst.exists():
        err = None
        for i in range(3):
            try:
                data = urllib.request.urlopen(urllib.request.Request(r['url'], headers=UA), timeout=60).read()
                im = Image.open(io.BytesIO(data)).convert('RGB'); im.thumbnail((a.max_side, a.max_side))
                tmp = dst.with_suffix('.part'); im.save(tmp, 'JPEG', quality=92); tmp.replace(dst); err = None; break
            except Exception as e:
                err = e; time.sleep(2 * (i + 1))
        if err:
            print('GAGAL', r['file'], err); return False
    lines = [l for l in r['label'].split(';') if l]
    lb.write_text('\n'.join(lines) + ('\n' if lines else ''))
    return True


with ThreadPoolExecutor(a.workers) as ex:
    ok = list(ex.map(fetch, rows))
with open(out / 'sources.csv', 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['file', 'sumber_id', 'url', 'lisensi']); w.writeheader()
    for r, k in zip(rows, ok):
        if k: w.writerow({x: r[x] for x in w.fieldnames})
print(Path(a.manifest).stem, 'selesai:', sum(ok), 'dari', len(rows))
