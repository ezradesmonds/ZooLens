# Protokol Uji Ulang 500 Foto

PIC: Joseph (Dataset & Evaluation). Ditulis 17 November 2026, **sebelum model dijalankan pada subset ini**.
Tujuan: menguji ulang hipotesa H1 sampai H4 (`docs/HIPOTESIS_PENGUJIAN_200.md`) yang tidak bisa
disimpulkan dari pilot 205 foto (BUG-08, BUG-09, BUG-10 di Bug Log).

## Yang diperbaiki dari pilot

| Masalah pilot | Perbaikan |
|---|---|
| Tidak ada foto tanpa satwa, FP dan TN tidak terukur | 250 foto negatif |
| Kondisi visual diturunkan dari nama file | Kondisi dinilai per foto dari gambarnya |
| 23 foto harimau identik dengan data training | Semua foto dicek pHash terhadap data training; yang mirip dibuang |

## Subset (dibekukan)

Daftar file dan MD5: `ml/uji500/manifest_uji500.csv`. Foto: folder `uji500/` di Drive tim.

- 250 positif, 50 per kelas. Kondisi (penilaian awal): Full 53, Occlusion ringan 59,
  Occlusion sedang 55, Occlusion berat 33, Truncation 50.
- 250 negatif: 100 vegetasi (46 rimbun: dedaunan, rumput tinggi, hutan; 54 bunga dan lanskap),
  100 hewan lain (kuda nil, singa, macan tutul, kuda, sapi, rusa, unta, beruang, dan lain-lain), 50 objek, bangunan, orang.
- Sumber: Open Images V7 (gajah, jerapah, zebra, harimau, semua negatif), iNaturalist (badak),
  dan foto pilot bagian Joseph (badak, zebra). Lisensi per foto ada di manifest.
- Gambar Open Images yang dipakai di data training v2 dikecualikan lewat ID.
- Cek duplikat pHash (jarak Hamming <= 5) terhadap train, val, test `ZooLens_final_v2`:
  0 foto mirip pada subset akhir (`ml/uji500/cek_duplikat_uji500.csv`). Saat seleksi, 1 foto pilot
  badak ditemukan identik dengan gambar val dan dibuang.

## Rubrik kondisi visual

| Kondisi | Definisi |
|---|---|
| Full | Seluruh tubuh satwa terlihat, tidak tertutup benda dan tidak terpotong tepi foto |
| Occlusion ringan | Kurang dari 25% tubuh tertutup benda (rumput, pagar, orang, air) |
| Occlusion sedang | 25% sampai 50% tubuh tertutup |
| Occlusion berat | Lebih dari 50% tubuh tertutup |
| Truncation | Tubuh terpotong tepi foto (termasuk foto jarak dekat), bukan tertutup benda |

Bila foto tertutup sekaligus terpotong, dipilih penyebab yang paling dominan. Foto dengan beberapa
satwa dinilai dari satwa yang paling jelas.

Penilaian awal dibuat dengan bantuan AI dari gambar tiap foto, lalu ditinjau Joseph. Analisis
akhir memakai kondisi setelah tinjauan.

## Aturan penilaian (sama dengan sheet Panduan Aldo)

- Model: `best.pt` aktif di README (`W6_cand1_yolo11n_adamw_lr0005`), `imgsz` bawaan, confidence >= 0,5.
- Kelas prediksi = deteksi dengan confidence tertinggi pada foto itu (sama dengan `batch_test_200.py`).
- TP: foto positif, kelas prediksi benar. FN: foto positif, tidak ada deteksi atau kelas salah.
- FP: foto negatif dengan deteksi. TN: foto negatif tanpa deteksi.

## Kriteria keputusan hipotesa (ditetapkan sebelum melihat hasil)

Uji statistik: uji Fisher satu sisi sesuai arah dugaan, batas p < 0,05. Jumlah sampel selalu disebut.

| Hipotesa | Yang dibandingkan | Didukung bila | Tidak didukung bila | Belum pasti bila |
|---|---|---|---|---|
| H1 | Tingkat FN: Occlusion berat vs Full | FN berat >= 50% dan p < 0,05 | FN berat tidak lebih tinggi dari Full | arah sesuai tetapi salah satu syarat tidak terpenuhi |
| H2 | Recall pada Truncation: zebra vs badak + gajah | recall zebra lebih tinggi dan p < 0,05 | recall zebra tidak lebih tinggi | arah sesuai tetapi p >= 0,05 |
| H3 | Tingkat FP: vegetasi rimbun vs jenis negatif lain, dan kelas FP-nya | FP vegetasi rimbun tertinggi di antara jenis negatif dan mayoritas FP-nya berlabel tiger | FP vegetasi rimbun bukan yang tertinggi, atau FP-nya bukan mayoritas tiger | arah sesuai tetapi jumlah FP kurang dari 5 |
| H4 | Recall: Truncation vs Occlusion sedang + berat | recall Truncation lebih tinggi dan p < 0,05 | recall Truncation tidak lebih tinggi | arah sesuai tetapi p >= 0,05 |

Bagian H1 tentang confidence ("turun sampai di bawah 0,50") dilaporkan terpisah: rata-rata confidence
deteksi benar pada Occlusion berat dibanding Full.
