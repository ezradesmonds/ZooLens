"""Pindahkan gambar yang ditolak saat cek visual ke subfolder _dibuang (bisa dikembalikan).

Nomor mengacu ke <prefix>_index.csv buatan preview_sheets.py. Gambar dan labelnya dipindah
ke <root>/_dibuang/images dan <root>/_dibuang/labels, dan alasannya dicatat di <root>/dibuang.csv.

Contoh:
  python ml/scripts/apply_review.py --index audit_out/review_v2/badak_oi_index.csv \
      --root D/badak_openimages --drop "1:awetan museum" "24:patung"
"""
import argparse, csv, shutil
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--index', required=True); ap.add_argument('--root', required=True)
ap.add_argument('--drop', nargs='+', required=True, help='"nomor:alasan"')
a = ap.parse_args()

idx = {int(r['nomor']): r['file'] for r in csv.DictReader(open(a.index, encoding='utf-8'))}
root = Path(a.root); bin_ = root / '_dibuang'
(bin_ / 'images').mkdir(parents=True, exist_ok=True); (bin_ / 'labels').mkdir(parents=True, exist_ok=True)
log = root / 'dibuang.csv'; new = not log.exists()
moved = 0
with open(log, 'a', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    if new: w.writerow(['file', 'alasan'])
    for item in a.drop:
        n, _, why = item.partition(':'); name = idx[int(n)]
        img = root / 'images' / name; lbl = root / 'labels' / (Path(name).stem + '.txt')
        if not img.exists(): print(f'lewati {n}: {name} sudah tidak ada'); continue
        shutil.move(str(img), bin_ / 'images' / name)
        if lbl.exists(): shutil.move(str(lbl), bin_ / 'labels' / lbl.name)
        w.writerow([name, why]); moved += 1
print(f'dipindah: {moved} | tersisa: {len(list((root / "images").iterdir()))}')
