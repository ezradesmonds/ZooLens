# Perbaikan Data Kelas Minoritas (ZooLens_final_v2)

PIC: Joseph (Dataset & Evaluation). Tanggal: 15 November 2026.
Tugas tracker: W5 "Perbaiki data kelas minoritas bila perlu". Risiko terkait: R2 (distribusi kelas tidak seimbang).

## Ringkasan

| | v1 (ZooLens_final) | v2 (ZooLens_final_v2) |
|---|---|---|
| Gambar train / val / test | 2.076 / 261 / 259 | 2.932 / 356 / 259 |
| Train: gambar berisi gajah | 219 | 628 |
| Train: gambar berisi badak | 123 | 570 |
| Rasio kelas terbesar : terkecil (train) | 5,5 : 1 | 1,57 : 1 |
| Split test | 259 gambar | sama persis (cek MD5) |

Status: **data sudah diperbaiki, bukti hasil belum ada.** Perbaikan baru terbukti setelah model
dilatih ulang pada v2 dan metrik per kelas di split test dibandingkan dengan EXP-02.

## Mengapa perlu

- Audit: gambar berlabel per kelas tiger 849, giraffe 787, zebra 538, elephant 275, rhinoceros 154.
- Uji awal 205 foto: badak paling sering gagal (29 dari 40 berhasil, 72,5%).

## Yang dilakukan

1. **Badak.** 526 gambar berlabel diunduh dari Open Images V7. Seluruhnya dicek lewat lembar
   pratinjau; 29 dibuang (patung, awetan museum, sampul album, stiker, kuda nil, box meragukan). Dipakai 497.
2. **Gajah.** 500 gambar diunduh dari Open Images V7 (acak dari 1.329, seed 42). 46 dibuang
   (patung, awetan museum, ilustrasi, mainan, hanya belalai atau kaki). Dipakai 454.
3. **Cek kebocoran.** pHash semua gambar baru dibandingkan dengan train, val, test v1 dan 52 foto
   uji tim (badak dan zebra). Hasil: 0 gambar mirip. Satu pasang gambar badak baru kembar satu sama
   lain dan masuk split yang sama.
4. **Split.** v1 disalin utuh. Data baru hanya masuk train (856) dan val (95). Test tidak berubah.
5. **Validasi.** Tiap gambar punya label; semua label 5 kolom, kelas 0 sampai 4, koordinat 0 sampai 1.

Pemulihan 288 label gajah berdasarkan nama file diuji pada 1 November dan **ditolak**: sekitar
separuh box meleset karena salinan augmentasi Roboflow diputar dengan sudut berbeda
(bukti: `audit_out/elephant_recovery_check/`).

## Temuan tambahan: label dataset badak lama

Saat mengecek 154 gambar badak lama (Roboflow `badak-vkfo9`):

- Isinya memang badak. Asumsi "kelas lainnya = badak" di audit terkonfirmasi.
- **Label tidak lengkap.** Pada sekitar 20 foto yang berisi dua badak atau lebih, hanya satu yang
  diberi box. Badak tanpa box dianggap latar belakang saat training, sehingga bisa menurunkan
  recall badak. Bila foto seperti ini ada di split test, deteksi yang benar terhitung salah.
- Ada sekitar 10 gambar bukan foto: cetakan kuno yang sama berulang, kartun, patung pasir, render 3D.

Ini belum diperbaiki di v2 supaya perbandingan dengan v1 tetap bersih. Usulan: lengkapi box
(sekitar 20 gambar) dan buang gambar bukan foto dari train pada versi berikutnya.

## Cara membuktikan (EXP-03)

Notebook: `ml/notebooks/exp03_class_balance.ipynb` (Colab, GPU T4).

1. Evaluasi `best.pt` EXP-02 pada split test, catat precision, recall, mAP50 per kelas.
2. Latih EXP-03 pada v2 dengan konfigurasi yang sama seperti EXP-02 (jangan ganti optimizer di eksperimen ini).
3. Evaluasi EXP-03 pada split test yang sama, bandingkan per kelas.

Kriteria tuntas:

- recall dan mAP50 rhinoceros dan elephant naik dibanding EXP-02,
- mAP50 kelas lain tidak turun lebih dari 0,02,
- keberhasilan badak pada foto uji tim naik dari 72,5%.

Bila tidak tercapai: oversampling kelas minoritas saat training, atau lengkapi label badak lama.

## Batasan

- Cek visual memakai thumbnail; box yang sedikit meleset bisa lolos.
- Foto uji tim yang dicek kebocorannya baru 52 foto bagian Joseph. Folder uji lengkap perlu dicek ulang
  dengan `ml/scripts/leak_check.py`.
- Test badak hanya 15 gambar: satu gambar setara sekitar 0,07 recall.
- Lisensi dataset gajah Roboflow masih belum diketahui.

## Cara mengulang

```bash
python ml/scripts/fetch_openimages.py --cls rhinoceros --ann-dir oi --out ZooLens/badak_openimages
python ml/scripts/fetch_openimages.py --cls elephant --limit 500 --ann-dir oi --out ZooLens/gajah_openimages
python ml/scripts/preview_sheets.py --images ZooLens/gajah_openimages/images --labels ZooLens/gajah_openimages/labels --out audit_out/review_v2 --prefix gajah_oi
python ml/scripts/apply_review.py --index audit_out/review_v2/gajah_oi_index.csv --root ZooLens/gajah_openimages --drop "5:alasan"
python ml/scripts/leak_check.py --new ZooLens/badak_openimages/images ZooLens/gajah_openimages/images --ref test=ZooLens_final/images/test --out audit_out/leak_check_v2.csv
python ml/scripts/build_split_v2.py --v1 ZooLens_final --out ZooLens_final_v2 --add badak_oi=ZooLens/badak_openimages gajah_oi=ZooLens/gajah_openimages
```

Nomor pada lembar pratinjau saat cek 15 November tersimpan di `audit_out/review_v2/*_index.csv`,
dan daftar yang dibuang di `audit_out/review_v2/*_dibuang.csv`.

## Teks untuk Work Log

| Tanggal | PIC | Aktivitas dan hasil | Evidence |
|---|---|---|---|
| 15/11 | Joseph | Perbaikan data kelas minoritas: +497 gambar badak dan +454 gambar gajah dari Open Images V7 (CC BY), dicek visual (75 dibuang), cek kebocoran pHash 0 temuan. ZooLens_final_v2: train 2.932 / val 356 / test 259 (test tidak berubah). Rasio kelas train 5,5 : 1 menjadi 1,57 : 1. Menunggu training ulang (EXP-03) untuk bukti metrik per kelas. | `docs/CLASS_BALANCE_V2.md`, `audit_out/review_v2/`, `audit_out/leak_check_v2.csv` |
