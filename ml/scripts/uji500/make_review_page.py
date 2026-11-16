"""Buat halaman tinjau kondisi visual (HTML lokal) untuk 250 foto positif.

Tiap foto tampil dengan pilihan kondisi yang sudah terisi penilaian awal. Peninjau membetulkan
yang salah lalu menekan "Simpan kondisi_final.csv". Hasil model sengaja tidak ditampilkan supaya
penilaian tidak terpengaruh. Pilihan tersimpan di browser, jadi bisa dilanjutkan nanti.

Contoh:
  python ml/scripts/uji500/make_review_page.py --manifest ml/uji500/manifest_uji500.csv --out D:/Project/DataSetZoo/uji500/tinjau.html
"""
import argparse, csv, html, json

OPTS = ['Full', 'Occlusion ringan', 'Occlusion sedang', 'Occlusion berat', 'Truncation', 'Dikeluarkan']
ap = argparse.ArgumentParser()
ap.add_argument('--manifest', required=True); ap.add_argument('--out', required=True)
a = ap.parse_args()
rows = [r for r in csv.DictReader(open(a.manifest, encoding='utf-8')) if r['kelompok'] == 'Positif']
data = [{'f': r['file'], 'p': r['folder'] + '/' + r['file'], 'k': r['kelas'], 'c': r['kondisi_awal']} for r in rows]

page = """<!doctype html><html lang="id"><head><meta charset="utf-8"><title>Tinjau kondisi visual</title>
<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f4f4f2;color:#222}
header{position:sticky;top:0;background:#fff;border-bottom:1px solid #ccc;padding:10px 16px;z-index:2}
header b{font-size:17px} .rub{font-size:13px;color:#444;margin-top:4px}
button{font-size:15px;padding:7px 14px;margin-left:12px;cursor:pointer}
#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px;padding:12px}
.card{background:#fff;border:2px solid #ddd;border-radius:6px;padding:8px}
.card.changed{border-color:#d98200}.card img{width:100%;height:240px;object-fit:contain;background:#eee}
.name{font-size:13px;color:#555;margin:4px 0}.opts label{display:inline-block;font-size:13px;margin:2px 8px 2px 0;cursor:pointer}
</style></head><body>
<header><b>Tinjau kondisi visual: 250 foto positif</b>
<span id="stat"></span><button onclick="save()">Simpan kondisi_final.csv</button>
<div class="rub">Full: seluruh tubuh terlihat. Occlusion ringan: tertutup benda kurang dari 25%. Sedang: 25 sampai 50%.
Berat: lebih dari 50%. Truncation: terpotong tepi foto. Dikeluarkan: bukan satwa target atau foto tidak layak.
Bingkai oranye = kamu mengubah penilaian awal.</div></header>
<div id="grid"></div>
<script>
const DATA = __DATA__, OPTS = __OPTS__, KEY = 'zoolens_uji500_kondisi';
let cur = JSON.parse(localStorage.getItem(KEY) || '{}');
const grid = document.getElementById('grid');
DATA.forEach((d, i) => {
  const c = document.createElement('div'); c.className = 'card'; c.id = 'c' + i;
  c.innerHTML = `<img loading="lazy" src="${d.p}"><div class="name">${i + 1}. ${d.f} (${d.k})</div><div class="opts">` +
    OPTS.map(o => `<label><input type="radio" name="r${i}" value="${o}" ${(cur[d.f] || d.c) === o ? 'checked' : ''}>${o}</label>`).join('') + '</div>';
  c.addEventListener('change', e => { cur[d.f] = e.target.value; localStorage.setItem(KEY, JSON.stringify(cur)); mark(i); stat(); });
  grid.appendChild(c); mark(i);
});
function mark(i) { const d = DATA[i]; document.getElementById('c' + i).classList.toggle('changed', (cur[d.f] || d.c) !== d.c); }
function stat() { const n = DATA.filter(d => (cur[d.f] || d.c) !== d.c).length; document.getElementById('stat').textContent = ` diubah: ${n} dari ${DATA.length}`; }
function save() {
  const lines = ['file,kondisi,kondisi_awal'].concat(DATA.map(d => `${d.f},${cur[d.f] || d.c},${d.c}`));
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([lines.join('\\n') + '\\n'], {type: 'text/csv'}));
  a.download = 'kondisi_final.csv'; a.click();
}
stat();
</script></body></html>"""
open(a.out, 'w', encoding='utf-8').write(page.replace('__DATA__', json.dumps(data)).replace('__OPTS__', json.dumps(OPTS)))
print('halaman tinjau:', a.out, len(data), 'foto')
