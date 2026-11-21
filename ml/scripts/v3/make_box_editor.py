"""Buat halaman koreksi kotak (HTML lokal) untuk foto yang sudah diberi kotak awal (pre-label).

Peninjau melihat satu foto per layar, membetulkan kotak, lalu menandai foto OK atau Buang.
Progres tersimpan di browser. Tombol "Simpan hasil" mengunduh koreksi_kotak_<name>.json, yang lalu
diubah menjadi label YOLO oleh apply_box_review.py.

Halaman ditulis di folder induk --images supaya gambar bisa dibuka lewat path relatif.
Buka lewat server lokal, mis.: python -m http.server 8765 --directory <folder induk>

Contoh:
  python ml/scripts/v3/make_box_editor.py --images D:/Project/DataSetZoo/ZooLens/badak_inaturalist/images \
      --pre D:/Project/DataSetZoo/ZooLens/badak_inaturalist/prelabel.json --name badak_inaturalist
"""
import argparse, json, os

NAMES = ['elephant', 'giraffe', 'zebra', 'tiger', 'rhinoceros', 'non_class']
ap = argparse.ArgumentParser()
ap.add_argument('--images', required=True)
ap.add_argument('--pre', required=True)
ap.add_argument('--name', required=True, help='kunci penyimpanan di browser, unik per folder')
ap.add_argument('--cls', type=int, default=4, help='kelas untuk kotak baru yang digambar manual')
a = ap.parse_args()

pre = json.load(open(a.pre))
sub = os.path.basename(os.path.normpath(a.images))
data = [{'f': f, 'p': sub + '/' + f, 'b': pre[f]} for f in sorted(pre)]
out = os.path.join(os.path.dirname(os.path.normpath(a.images)), 'koreksi.html')

page = r"""<!doctype html><html lang="id"><head><meta charset="utf-8"><title>Koreksi kotak</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#1e1e1e;color:#eee}
header{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:8px 12px;background:#2b2b2b}
header b{font-size:16px}button{font-size:14px;padding:6px 12px;cursor:pointer}
#wrap{display:flex;gap:12px;padding:10px}#cv{background:#000;cursor:crosshair;max-width:100%;height:auto}
@media (max-width:900px){#wrap{flex-direction:column}#side{max-width:none}}
#side{min-width:260px;max-width:320px;font-size:13px;line-height:1.5}
.st{font-size:18px;font-weight:bold;margin:6px 0}.ok{color:#5c5}.buang{color:#f66}.belum{color:#fc3}
kbd{background:#444;border-radius:3px;padding:0 5px}
#bar{height:6px;background:#444}#bar div{height:6px;background:#5c5}
</style></head><body>
<header><b>Koreksi kotak: __NAME__</b><span id="prog"></span>
<button onclick="jumpTodo()">Lompat ke belum dicek</button>
<button onclick="save()">Simpan hasil (koreksi_kotak___NAME__.json)</button>
<label><button onclick="document.getElementById('imp').click()">Muat cadangan</button><input id="imp" type="file" accept=".json" style="display:none" onchange="load(this.files[0])"></label>
<label>Foto ke <input id="go" type="number" min="1" style="width:70px" onchange="show(this.value-1)"></label></header>
<div id="bar"><div></div></div>
<div id="wrap"><canvas id="cv"></canvas><div id="side">
<div id="fname"></div><div id="status" class="st"></div><div id="info"></div><hr>
<b>Cara pakai</b><br>
<kbd>Enter</kbd> kotak sudah benar, OK, lanjut<br>
<kbd>X</kbd> buang foto (bukan satwa asli, jejak kaki, cakaran, patung, awetan, gambar, terlalu kecil/buram), lanjut<br>
<kbd>&larr;</kbd> <kbd>&rarr;</kbd> pindah foto tanpa mengubah status<br>
Tarik di area kosong: buat kotak baru<br>
Klik kotak: pilih. <kbd>Delete</kbd> hapus kotak terpilih<br>
Tarik sudut kotak terpilih: ubah ukuran<br>
<kbd>0</kbd>-<kbd>5</kbd> ganti kelas kotak terpilih (0 gajah, 1 jerapah, 2 zebra, 3 harimau, 4 badak, 5 non_class)<br>
<kbd>R</kbd> kembalikan kotak awal<hr>
<b>Aturan kotak</b><br>
Setiap satwa target diberi satu kotak, termasuk yang sebagian tertutup atau terpotong.<br>
Kotak serapat mungkin ke tubuh yang terlihat.<br>
Satwa target lain (mis. zebra), walau buram: kotak dengan kelasnya (tekan 2 untuk zebra).<br>
Hewan lain di foto yang sama: beri kotak kelas 5 (non_class), satu kotak per individu.<br>
Terlalu kecil/buram sampai kamu ragu itu hewan apa: lewati. Kalau banyak yang meragukan, buang foto (X).<br>
Kotak putus-putus = kotak awal dari mesin; angka = keyakinan mesin.
</div></div>
<script>
const DATA = __DATA__, NAMES = __NAMES__, KEY = 'zoolens_koreksi___NAME__';
const COL = ['#4da3ff', '#ffb000', '#ffffff', '#ff6a00', '#00e676', '#e040fb'];
let st = {}; try { st = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
let idx = 0, img = new Image(), sel = -1, drag = null, scale = 1;
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
function cur() { const d = DATA[idx]; if (!st[d.f]) st[d.f] = {s: '', b: d.b.map(x => x.slice(0, 5)), pre: true}; return st[d.f]; }
function persist() { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} }
function show(i) {
  idx = Math.max(0, Math.min(DATA.length - 1, +i)); sel = -1;
  img = new Image(); img.onload = () => { fit(); draw(); }; img.src = DATA[idx].p; side();
}
function fit() {
  const maxW = window.innerWidth > 900 ? window.innerWidth - 360 : window.innerWidth - 24, maxH = window.innerHeight - 90;
  scale = Math.min(maxW / img.width, maxH / img.height, 2); cv.width = img.width * scale; cv.height = img.height * scale;
}
function px(b) { return [(b[1] - b[3] / 2) * cv.width, (b[2] - b[4] / 2) * cv.height, b[3] * cv.width, b[4] * cv.height]; }
function draw() {
  ctx.drawImage(img, 0, 0, cv.width, cv.height); const s = cur(), d = DATA[idx];
  s.b.forEach((b, i) => {
    const [x, y, w, h] = px(b); ctx.strokeStyle = COL[b[0]]; ctx.lineWidth = i === sel ? 4 : 2;
    ctx.setLineDash(s.pre ? [8, 5] : []); ctx.strokeRect(x, y, w, h); ctx.setLineDash([]);
    let t = NAMES[b[0]]; if (s.pre && d.b[i]) t += ' ' + d.b[i][5];
    ctx.font = '14px Segoe UI'; const tw = ctx.measureText(t).width;
    ctx.fillStyle = COL[b[0]]; ctx.fillRect(x, y - 18, tw + 8, 18); ctx.fillStyle = '#000'; ctx.fillText(t, x + 4, y - 4);
    if (i === sel) { ctx.fillStyle = '#fff'; [[x, y], [x + w, y], [x, y + h], [x + w, y + h]].forEach(([a, c]) => ctx.fillRect(a - 5, c - 5, 10, 10)); }
  });
  if (drag && drag.mode === 'new') { ctx.strokeStyle = '#00e676'; ctx.lineWidth = 2; ctx.strokeRect(drag.x0, drag.y0, drag.x1 - drag.x0, drag.y1 - drag.y0); }
}
function side() {
  const d = DATA[idx], s = st[d.f] || {s: ''};
  document.getElementById('fname').textContent = (idx + 1) + ' / ' + DATA.length + ': ' + d.f;
  const el = document.getElementById('status');
  el.className = 'st ' + (s.s || 'belum'); el.textContent = s.s === 'ok' ? 'OK' : s.s === 'buang' ? 'Dibuang' : 'Belum dicek';
  document.getElementById('info').textContent = 'Kotak: ' + (st[d.f] ? st[d.f].b.length : d.b.length) + ' (awal dari mesin: ' + d.b.length + ')';
  const done = DATA.filter(x => st[x.f] && st[x.f].s).length, ok = DATA.filter(x => st[x.f] && st[x.f].s === 'ok').length;
  document.getElementById('prog').textContent = ` dicek ${done} / ${DATA.length} (OK ${ok}, buang ${done - ok})`;
  document.querySelector('#bar div').style.width = (100 * done / DATA.length) + '%';
  document.getElementById('go').value = idx + 1;
}
function pos(e) { const r = cv.getBoundingClientRect(); return [(e.clientX - r.left) * cv.width / r.width, (e.clientY - r.top) * cv.height / r.height]; }
function edited() { const s = cur(); s.pre = false; }
cv.addEventListener('mousedown', e => {
  const [mx, my] = pos(e), s = cur();
  if (sel >= 0) {
    const [x, y, w, h] = px(s.b[sel]);
    const corners = [[x, y], [x + w, y], [x, y + h], [x + w, y + h]];
    const k = corners.findIndex(([a, c]) => Math.abs(a - mx) < 9 && Math.abs(c - my) < 9);
    if (k >= 0) { const opp = corners[3 - k]; drag = {mode: 'new', x0: opp[0], y0: opp[1], x1: mx, y1: my, replace: sel}; return; }
  }
  let best = -1, area = 1e18;
  s.b.forEach((b, i) => { const [x, y, w, h] = px(b); if (mx >= x && mx <= x + w && my >= y && my <= y + h && w * h < area) { best = i; area = w * h; } });
  if (best >= 0) { sel = best; draw(); return; }
  sel = -1; drag = {mode: 'new', x0: mx, y0: my, x1: mx, y1: my};
});
cv.addEventListener('mousemove', e => { if (!drag) return; [drag.x1, drag.y1] = pos(e); draw(); });
window.addEventListener('mouseup', () => {
  if (!drag) return; const s = cur();
  const x0 = Math.max(0, Math.min(drag.x0, drag.x1)), x1 = Math.min(cv.width, Math.max(drag.x0, drag.x1));
  const y0 = Math.max(0, Math.min(drag.y0, drag.y1)), y1 = Math.min(cv.height, Math.max(drag.y0, drag.y1));
  if (x1 - x0 > 6 && y1 - y0 > 6) {
    const cls = drag.replace !== undefined ? s.b[drag.replace][0] : __CLS__;
    const nb = [cls, (x0 + x1) / 2 / cv.width, (y0 + y1) / 2 / cv.height, (x1 - x0) / cv.width, (y1 - y0) / cv.height];
    edited();
    if (drag.replace !== undefined) { s.b[drag.replace] = nb; sel = drag.replace; } else { s.b.push(nb); sel = s.b.length - 1; }
    persist();
  }
  drag = null; draw(); side();
});
function mark(v) {
  const s = cur();
  if (v === 'ok' && !s.b.length && !confirm('Foto ini tidak punya kotak. Tetap tandai OK?')) return;
  s.s = v; persist(); show(idx + 1);
}
function jumpTodo() { const i = DATA.findIndex(d => !(st[d.f] && st[d.f].s)); if (i >= 0) show(i); else alert('Semua foto sudah dicek.'); }
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  const s = cur();
  if (e.key === 'Enter') mark('ok');
  else if (e.key === 'x' || e.key === 'X') mark('buang');
  else if (e.key === 'ArrowRight') show(idx + 1);
  else if (e.key === 'ArrowLeft') show(idx - 1);
  else if ((e.key === 'Delete' || e.key === 'Backspace') && sel >= 0) { s.b.splice(sel, 1); sel = -1; edited(); persist(); draw(); side(); }
  else if (/^[0-5]$/.test(e.key) && sel >= 0) { s.b[sel][0] = +e.key; edited(); persist(); draw(); }
  else if (e.key === 'r' || e.key === 'R') { delete st[DATA[idx].f]; persist(); sel = -1; draw(); side(); }
  else return;
  e.preventDefault();
});
window.addEventListener('resize', () => { fit(); draw(); });
function save() {
  const outp = {}; DATA.forEach(d => { const s = st[d.f]; if (s && s.s) outp[d.f] = {status: s.s, edited: !s.pre, boxes: s.b}; });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(outp)], {type: 'application/json'})); a.download = 'koreksi_kotak___NAME__.json'; a.click();
}
function load(file) {
  if (!file) return;
  file.text().then(t => {
    const j = JSON.parse(t); let n = 0;
    for (const [k, v] of Object.entries(j)) if (DATA.some(d => d.f === k)) { st[k] = {s: v.status, b: v.boxes, pre: !v.edited}; n++; }
    persist(); alert(n + ' foto dimuat dari cadangan.'); jumpTodo();
  }).catch(() => alert('File cadangan tidak bisa dibaca.'));
}
{ const i = DATA.findIndex(d => !(st[d.f] && st[d.f].s)); show(i >= 0 ? i : 0); }
</script></body></html>"""
page = page.replace('__DATA__', json.dumps(data)).replace('__NAMES__', json.dumps(NAMES)).replace('__NAME__', a.name).replace('__CLS__', str(a.cls))
open(out, 'w', encoding='utf-8').write(page)
print('halaman koreksi:', out, len(data), 'foto')
