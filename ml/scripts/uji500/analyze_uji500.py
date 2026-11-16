"""Hitung metrik uji 500 foto, uji hipotesa H1-H4, dan isi Excel Format Evaluasi.

Kondisi visual diambil dari manifest (penilaian awal). Bila --kondisi diberikan (CSV kolom
file,kondisi hasil tinjauan), nilai di file itu yang dipakai.

Output: <out>/hasil_uji500.csv, <out>/ringkasan_uji500.md, dan Excel terisi (bila --xlsx diberikan).
"""
import argparse, collections, csv
from pathlib import Path
from scipy.stats import fisher_exact

CONDS = ['Full', 'Occlusion ringan', 'Occlusion sedang', 'Occlusion berat', 'Truncation']
CLASSES = ['elephant', 'giraffe', 'zebra', 'tiger', 'rhinoceros']

ap = argparse.ArgumentParser()
ap.add_argument('--manifest', required=True); ap.add_argument('--pred', required=True)
ap.add_argument('--out', required=True); ap.add_argument('--kondisi')
ap.add_argument('--xlsx'); ap.add_argument('--xlsx-out'); ap.add_argument('--penilai', default='Joseph')
ap.add_argument('--catatan-kondisi', default='')
a = ap.parse_args()

pred = {r['file']: r for r in csv.DictReader(open(a.pred, encoding='utf-8'))}
final = {}
if a.kondisi:
    final = {r['file']: r['kondisi'] for r in csv.DictReader(open(a.kondisi, encoding='utf-8'))}
rows = []
for m in csv.DictReader(open(a.manifest, encoding='utf-8')):
    p = pred[m['file']]
    m['kondisi'] = final.get(m['file'], m['kondisi_awal'])
    m['kelas_prediksi'] = p['kelas_prediksi']; m['confidence'] = float(p['confidence']) if p['confidence'] else None
    m['semua_deteksi'] = p['semua_deteksi']
    det = bool(p['kelas_prediksi'])
    if m['kelompok'] == 'Positif':
        m['status'] = 'TP' if det and p['kelas_prediksi'] == m['kelas'] else 'FN'
        m['jenis_fn'] = '' if m['status'] == 'TP' else ('salah kelas' if det else 'tidak terdeteksi')
    else:
        m['status'] = 'FP' if det else 'TN'; m['jenis_fn'] = ''
    rows.append(m)
if final:
    rows = [r for r in rows if r['kondisi'] != 'Dikeluarkan']

out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
cols = ['no', 'file', 'kelompok', 'kelas', 'kondisi', 'jenis_negatif', 'hewan_lain', 'kelas_prediksi', 'confidence',
        'status', 'jenis_fn', 'semua_deteksi', 'sumber_lisensi', 'url']
with open(out / 'hasil_uji500.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)

pos = [r for r in rows if r['kelompok'] == 'Positif']; neg = [r for r in rows if r['kelompok'] == 'Negatif']
n = collections.Counter(r['status'] for r in rows)
TP, FN, FP, TN = n['TP'], n['FN'], n['FP'], n['TN']


def pct(x, y): return f'{100 * x / y:.1f}%' if y else '-'
def rec(rs): return sum(r['status'] == 'TP' for r in rs), len(rs)
def fisher(a1, n1, a2, n2, alt):
    """p uji Fisher untuk proporsi a1/n1 dibanding a2/n2."""
    return fisher_exact([[a1, n1 - a1], [a2, n2 - a2]], alternative=alt)[1]
def mean(v): return sum(v) / len(v) if v else float('nan')


L = ['# Hasil Uji Ulang 500 Foto', '',
     f'Model `W6_cand1_yolo11n_adamw_lr0005`, confidence >= 0,5. Foto dihitung: {len(rows)} ({len(pos)} positif, {len(neg)} negatif).',
     f'Kondisi visual: {"hasil tinjauan (" + a.kondisi + ")" if a.kondisi else "penilaian awal dibantu AI, belum ditinjau anggota"}.', '',
     '## Ringkasan', '', '| Ukuran | Nilai |', '|---|---|',
     f'| TP / FN / FP / TN | {TP} / {FN} / {FP} / {TN} |',
     f'| Precision, TP / (TP + FP) | {pct(TP, TP + FP)} |', f'| Recall, TP / (TP + FN) | {pct(TP, TP + FN)} |',
     f'| Accuracy | {pct(TP + TN, len(rows))} |', f'| False positive rate, FP / (FP + TN) | {pct(FP, FP + TN)} |', '',
     '## Per kelas (foto positif)', '', '| Kelas | Foto | TP | FN tidak terdeteksi | FN salah kelas | Recall |', '|---|---|---|---|---|---|']
for c in CLASSES:
    rs = [r for r in pos if r['kelas'] == c]; t, k = rec(rs)
    L.append(f"| {c} | {k} | {t} | {sum(r['jenis_fn'] == 'tidak terdeteksi' for r in rs)} | {sum(r['jenis_fn'] == 'salah kelas' for r in rs)} | {pct(t, k)} |")
L += ['', '## Per kondisi visual (foto positif)', '', '| Kondisi | Foto | TP | FN | Recall | Rata-rata confidence TP |', '|---|---|---|---|---|---|']
for c in CONDS:
    rs = [r for r in pos if r['kondisi'] == c]; t, k = rec(rs)
    L.append(f"| {c} | {k} | {t} | {k - t} | {pct(t, k)} | {mean([r['confidence'] for r in rs if r['status'] == 'TP']):.3f} |")
L += ['', '## Recall per kelas x kondisi (TP/foto)', '', '| Kelas | ' + ' | '.join(CONDS) + ' |', '|---|' + '---|' * len(CONDS)]
for c in CLASSES:
    cells = []
    for k in CONDS:
        t, m_ = rec([r for r in pos if r['kelas'] == c and r['kondisi'] == k]); cells.append(f'{t}/{m_}')
    L.append(f'| {c} | ' + ' | '.join(cells) + ' |')
L += ['', '## Foto negatif per jenis', '', '| Jenis | Foto | FP | Tingkat FP | Kelas FP |', '|---|---|---|---|---|']
types = ['vegetasi rimbun', 'vegetasi lain', 'hewan lain', 'objek/bangunan/orang']
fpr = {}
for t in types:
    rs = [r for r in neg if r['jenis_negatif'] == t]; fps = [r for r in rs if r['status'] == 'FP']
    fpr[t] = (len(fps), len(rs))
    kinds = ', '.join(f'{k} {v}' for k, v in collections.Counter(r['kelas_prediksi'] for r in fps).most_common()) or '-'
    L.append(f'| {t} | {len(rs)} | {len(fps)} | {pct(len(fps), len(rs))} | {kinds} |')
fp_animal = collections.Counter((r['hewan_lain'], r['kelas_prediksi']) for r in neg if r['status'] == 'FP' and r['hewan_lain'])
if fp_animal:
    L += ['', 'FP pada hewan lain (hewan sebenarnya -> prediksi): ' + ', '.join(f'{h} -> {k} ({v})' for (h, k), v in fp_animal.most_common()) + '.']
wrong = collections.Counter((r['kelas'], r['kelas_prediksi']) for r in pos if r['jenis_fn'] == 'salah kelas')
L += ['', 'Salah kelas pada foto positif (sebenarnya -> prediksi): ' + (', '.join(f'{x} -> {y} ({v})' for (x, y), v in wrong.most_common()) or 'tidak ada') + '.']

# ------------------------------------------------ hipotesa
def grp(cond=None, cls=None):
    return [r for r in pos if (cond is None or r['kondisi'] in cond) and (cls is None or r['kelas'] in cls)]
L += ['', '## Hipotesa', '', 'Kriteria: `docs/UJI_500_PROTOKOL.md` (ditetapkan sebelum model dijalankan). Uji Fisher satu sisi.', '']
# H1
tb, nb = rec(grp(['Occlusion berat'])); tf, nf = rec(grp(['Full']))
p1 = fisher(nb - tb, nb, nf - tf, nf, 'greater')
fnb = (nb - tb) / nb if nb else 0
s1 = 'Didukung' if fnb >= 0.5 and p1 < 0.05 else 'Tidak didukung' if (nb - tb) / max(nb, 1) <= (nf - tf) / max(nf, 1) else 'Belum pasti'
cb = mean([r['confidence'] for r in grp(['Occlusion berat']) if r['status'] == 'TP']); cf = mean([r['confidence'] for r in grp(['Full']) if r['status'] == 'TP'])
L.append(f'- **H1: {s1}.** Tingkat FN Occlusion berat {pct(nb - tb, nb)} ({nb - tb} dari {nb}) vs Full {pct(nf - tf, nf)} ({nf - tf} dari {nf}); p = {p1:.4f}. '
         f'Rata-rata confidence deteksi benar: berat {cb:.3f}, Full {cf:.3f}.')
# H2
tz, nz = rec(grp(['Truncation'], ['zebra'])); to, no = rec(grp(['Truncation'], ['rhinoceros', 'elephant']))
p2 = fisher(tz, nz, to, no, 'greater')
s2 = 'Didukung' if tz / max(nz, 1) > to / max(no, 1) and p2 < 0.05 else 'Tidak didukung' if tz / max(nz, 1) <= to / max(no, 1) else 'Belum pasti'
tr_, nr_ = rec(grp(['Truncation'], ['rhinoceros'])); te_, ne_ = rec(grp(['Truncation'], ['elephant']))
L.append(f'- **H2: {s2}.** Recall Truncation zebra {pct(tz, nz)} ({tz} dari {nz}) vs badak + gajah {pct(to, no)} ({to} dari {no}; badak {tr_}/{nr_}, gajah {te_}/{ne_}); p = {p2:.4f}.')
# H3
fv, nv = fpr['vegetasi rimbun']
rates = {t: (x / y if y else 0) for t, (x, y) in fpr.items()}
vt = sum(r['kelas_prediksi'] == 'tiger' for r in neg if r['jenis_negatif'] == 'vegetasi rimbun' and r['status'] == 'FP')
highest = all(rates['vegetasi rimbun'] > rates[t] for t in types if t != 'vegetasi rimbun')
if highest and fv and vt > fv / 2: s3 = 'Didukung' if fv >= 5 else 'Belum pasti'
else: s3 = 'Tidak didukung'
tig = sum(r['kelas_prediksi'] == 'tiger' for r in neg if r['status'] == 'FP')
L.append(f'- **H3: {s3}.** FP vegetasi rimbun {pct(fv, nv)} ({fv} dari {nv}), berlabel tiger {vt}. Tingkat FP jenis lain: '
         + ', '.join(f'{t} {pct(*fpr[t])}' for t in types if t != 'vegetasi rimbun')
         + f'. Dari seluruh {FP} FP, {tig} berlabel tiger.')
# H4
tt, nt = rec(grp(['Truncation'])); tm, nm = rec(grp(['Occlusion sedang', 'Occlusion berat']))
p4 = fisher(tt, nt, tm, nm, 'greater')
s4 = 'Didukung' if tt / max(nt, 1) > tm / max(nm, 1) and p4 < 0.05 else 'Tidak didukung' if tt / max(nt, 1) <= tm / max(nm, 1) else 'Belum pasti'
L.append(f'- **H4: {s4}.** Recall Truncation {pct(tt, nt)} ({tt} dari {nt}) vs Occlusion sedang + berat {pct(tm, nm)} ({tm} dari {nm}); p = {p4:.4f}.')
(out / 'ringkasan_uji500.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print('\n'.join(L))

# ------------------------------------------------ Excel Format Evaluasi
if a.xlsx:
    import openpyxl
    wb = openpyxl.load_workbook(a.xlsx); ws = wb['Format Evaluasi']
    assert len(rows) <= 500
    for i, r in enumerate(rows):
        x = 5 + i
        note = []
        if r['kelompok'] == 'Negatif': note.append('Negatif: ' + r['jenis_negatif'] + (f" ({r['hewan_lain']})" if r['hewan_lain'] else ''))
        if r['jenis_fn'] == 'salah kelas': note.append('Salah kelas: diprediksi ' + r['kelas_prediksi'])
        if r['status'] == 'FP': note.append('Deteksi: ' + r['semua_deteksi'])
        if r['kelompok'] == 'Positif' and a.catatan_kondisi: note.append(a.catatan_kondisi)
        ws.cell(x, 2, r['file']); ws.cell(x, 3, r['kelompok'])
        ws.cell(x, 4, r['kelas'] or 'Tidak ada'); ws.cell(x, 5, r['kondisi']); ws.cell(x, 6, a.penilai)
        ws.cell(x, 7, r['kelas_prediksi'] or None); ws.cell(x, 8, r['confidence'])
        ws.cell(x, 11, 'Tidak'); ws.cell(x, 12, r['sumber_lisensi'] + (' | ' + r['url'] if r['url'] else ''))
        ws.cell(x, 13, '; '.join(note) or None)
    wb.save(a.xlsx_out); print('Excel tersimpan:', a.xlsx_out)
