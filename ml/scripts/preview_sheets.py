"""Buat lembar pratinjau bernomor (gambar + box) untuk cek label secara visual.

Tiap petak diberi nomor urut. Petak berbingkai kuning = ada box yang hampir seluruhnya
berada di dalam box lain dari kelas yang sama (kemungkinan box ganda), perlu dilihat.
Output: <out>/<prefix>_NN.jpg dan <out>/<prefix>_index.csv (nomor -> nama file, tanda).

Contoh:
  python ml/scripts/preview_sheets.py --images D/images --labels D/labels --out audit_out/review_v2 --prefix badak_oi
"""
import argparse, csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

COLORS = ['orange', 'cyan', 'magenta', 'lime', 'red', 'white']  # ID terpadu 0..4, 5 = non_class

ap = argparse.ArgumentParser()
ap.add_argument('--images', required=True); ap.add_argument('--labels', required=True)
ap.add_argument('--out', required=True); ap.add_argument('--prefix', required=True)
ap.add_argument('--only-labeled', action='store_true', help='lewati gambar tanpa file label')
ap.add_argument('--cols', type=int, default=6); ap.add_argument('--rows', type=int, default=4)
ap.add_argument('--tile', type=int, default=230)
ap.add_argument('--files', help='CSV berkolom file + ditandai; hanya gambar dengan ditandai=1 yang ditampilkan')
a = ap.parse_args()


def read_boxes(p):
    out = []
    if p.exists():
        for ln in p.read_text().splitlines():
            t = ln.split()
            if len(t) == 5:
                c, x, y, w, h = int(float(t[0])), *map(float, t[1:])
                out.append((c, x - w / 2, y - h / 2, x + w / 2, y + h / 2))
    return out


def nested(bs):
    """True bila ada box yang >=90% luasnya di dalam box lain sekelas dan luasnya < setengahnya."""
    for i, b in enumerate(bs):
        ab = (b[3] - b[1]) * (b[4] - b[2])
        for j, o in enumerate(bs):
            if i == j or b[0] != o[0] or ab <= 0: continue
            ao = (o[3] - o[1]) * (o[4] - o[2])
            ix = max(0, min(b[3], o[3]) - max(b[1], o[1])); iy = max(0, min(b[4], o[4]) - max(b[2], o[2]))
            if ix * iy >= 0.9 * ab and ab < 0.5 * ao: return True
    return False


imgs = sorted(p for p in Path(a.images).iterdir() if p.suffix.lower() in ('.jpg', '.jpeg', '.png'))
if a.only_labeled:
    imgs = [p for p in imgs if (Path(a.labels) / (p.stem + '.txt')).exists()]
if a.files:
    keep = {r['file'] for r in csv.DictReader(open(a.files, encoding='utf-8')) if r.get('ditandai', '1') == '1'}
    imgs = [p for p in imgs if p.name in keep]
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
font = ImageFont.load_default(size=20)
per, T = a.cols * a.rows, a.tile
rows = []
for s in range(0, len(imgs), per):
    sheet = Image.new('RGB', (a.cols * T, a.rows * T), 'white')
    for k, p in enumerate(imgs[s:s + per]):
        n = s + k + 1
        bs = read_boxes(Path(a.labels) / (p.stem + '.txt'))
        flag = 'box_bertumpuk' if nested(bs) else ''
        im = Image.open(p).convert('RGB'); im.thumbnail((T - 6, T - 6)); W, H = im.size
        d = ImageDraw.Draw(im)
        for c, x0, y0, x1, y1 in bs:
            d.rectangle([x0 * W, y0 * H, x1 * W, y1 * H], outline=COLORS[c % 6], width=3)
        tile = Image.new('RGB', (T, T), 'gold' if flag else 'white'); tile.paste(im, (3, 3))
        d = ImageDraw.Draw(tile)
        d.rectangle([3, 3, 3 + 11 * len(str(n)) + 8, 27], fill='black'); d.text((7, 4), str(n), fill='white', font=font)
        sheet.paste(tile, ((k % a.cols) * T, (k // a.cols) * T))
        rows.append([n, p.name, len(bs), flag])
    sheet.save(out / f'{a.prefix}_{s // per + 1:02d}.jpg', quality=85)
with open(out / f'{a.prefix}_index.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['nomor', 'file', 'jumlah_box', 'tanda']); w.writerows(rows)
print(f'{len(imgs)} gambar, {(len(imgs) + per - 1) // per} lembar, bertanda: {sum(1 for r in rows if r[3])}')
