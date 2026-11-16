# Hasil Uji Ulang 500 Foto dan Kesimpulan H1 sampai H4

PIC: Joseph (Dataset & Evaluation). Tanggal: 17 November 2026.
Protokol dan kriteria (ditulis sebelum model dijalankan): `docs/UJI_500_PROTOKOL.md`.
Tabel lengkap: `ml/uji500/ringkasan_uji500.md`. Hasil per foto: `ml/uji500/hasil_uji500.csv`.
Excel Format Evaluasi terisi: `ml/uji500/ZooLens_Format_Evaluasi_Uji500_terisi.xlsx`.

**Status kondisi visual: penilaian awal dibantu AI, belum ditinjau anggota.** Angka per kondisi dan
kesimpulan H1, H2, H4 bisa bergeser setelah tinjauan. Angka keseluruhan, per kelas, dan H3 tidak
bergantung pada kondisi visual.

## Hasil utama

| Ukuran | Uji 500 | Pilot 205 |
|---|---|---|
| Recall (foto positif) | 64,4% (161 dari 250) | 89,0% (162 dari 182) |
| Precision | 70,9% | tidak terukur |
| False positive rate (foto negatif) | 26,4% (66 dari 250) | tidak terukur |
| Accuracy | 69,0% | tidak terukur |

| Kelas | Recall | | Kondisi | Recall |
|---|---|---|---|---|
| giraffe | 94,0% (47/50) | | Full | 77,4% (41/53) |
| zebra | 92,0% (46/50) | | Occlusion ringan | 79,7% (47/59) |
| tiger | 64,0% (32/50) | | Occlusion sedang | 58,2% (32/55) |
| elephant | 44,0% (22/50) | | Occlusion berat | 27,3% (9/33) |
| rhinoceros | 28,0% (14/50) | | Truncation | 64,0% (32/50) |

Foto negatif: vegetasi rimbun 6,5% FP (3/46), vegetasi lain 13,0% (7/54), objek/bangunan/orang
12,0% (6/50), **hewan lain 50,0% (50/100)**.

## Kesimpulan hipotesa

| Hipotesa | Status | Bukti |
|---|---|---|
| H1 Occlusion berat memicu FN | **Didukung** | FN Occlusion berat 72,7% (24/33) vs Full 22,6% (12/53), p < 0,001. Bagian confidence tidak terbukti kuat: rata-rata confidence deteksi benar 0,762 vs 0,833. |
| H2 Zebra paling tahan saat terpotong | **Didukung** | Recall Truncation zebra 90% (9/10) vs badak + gajah 45% (9/20), p = 0,021. Sampel zebra hanya 10 foto. |
| H3 Vegetasi rimbun memicu deteksi palsu harimau | **Tidak didukung** | FP vegetasi rimbun paling rendah (6,5%) dan tidak ada yang berlabel tiger. Dari 66 FP, 14 berlabel tiger; semuanya pada hewan lain dan objek. |
| H4 Terpotong lebih mudah dikenali daripada terhalang | **Didukung** | Recall Truncation 64,0% (32/50) vs Occlusion sedang + berat 46,6% (41/88), p = 0,036. |

## Temuan di luar hipotesa

1. **Model jauh lebih lemah pada foto di luar dataset.** Pada split test `ZooLens_final` recall
   tingkat foto 98% (254/258), pada foto baru 64%. Skrip yang sama dipakai untuk keduanya, jadi
   selisih ini bukan kesalahan pengukuran. Gajah dan badak paling terdampak; keduanya juga kelas
   dengan data training paling sedikit dan paling seragam.
2. **Foto Full pun sering gagal untuk gajah (5/10) dan badak (5/10).** Jadi occlusion bukan
   satu-satunya penyebab; data training kedua kelas kurang beragam.
3. **Model hampir selalu "melihat" satwa target pada hewan lain.** Rusa, unta, singa, macan tutul
   sering dikira jerapah; lynx dikira harimau. Data training tidak punya contoh negatif.
4. **Salah kelas antar satwa target:** tiger -> zebra (5), tiger -> giraffe (3), rhinoceros -> elephant (3).
5. **Dugaan penurunan pada badak dibanding model pilot.** Pada 42 foto badak pilot bagian Joseph,
   model aktif (`W6_cand1`) mengenali 11 foto (26%); pilot mencatat 29 dari 40 (72,5%) dengan
   model sebelumnya. Dari 20 foto yang namanya bisa dicocokkan, 10 TP di pilot menjadi 4.
   Perlu dicek Bryan: jalankan kedua bobot pada folder yang sama.

## Batasan

- Kondisi visual belum ditinjau anggota (lihat status di atas). Halaman tinjau: `uji500/tinjau.html`.
- Per kelas per kondisi sampelnya kecil (4 sampai 16 foto), jadi hanya gabungan lintas kelas yang disimpulkan.
- Occlusion berat 33 foto, 12 di antaranya badak; hasil H1 ikut dipengaruhi lemahnya kelas badak.
  Tanpa badak: FN Occlusion berat 12/21 (57%) vs Full 7/43 (16%).
- Foto positif Open Images dipilih yang berisi satu satwa target; foto pilot zebra berisi kawanan.
- Evaluasi di tingkat foto (kelas dengan confidence tertinggi), tidak menilai ketepatan kotak.

## Rekomendasi

1. Latih ulang dengan `ZooLens_final_v2` (EXP-03): menambah 497 badak dan 454 gajah dari sumber yang lebih beragam.
2. Tambahkan foto negatif (hewan lain, tanpa satwa) ke data training agar FP turun.
3. Uji ulang subset beku ini setelah latih ulang; subset tidak boleh dipakai untuk training.

## Teks untuk tracker

Weekly Target (kolom Joseph):

| Minggu | Tugas | Status |
|---|---|---|
| W5 | Perbaiki data kelas minoritas bila perlu | Done (ZooLens_final_v2, 15/11) |
| W6 | Subset uji kondisi visual | Done (subset 500 foto dibekukan, 17/11) |
| W7 | Metrik per kelas dan kondisi visual | Done setelah tinjauan kondisi visual selesai; sebelum itu In Progress |

Work Log:

| Tanggal | PIC | Aktivitas dan hasil | Evidence |
|---|---|---|---|
| 01/11 | Joseph | Uji pemulihan 288 label gajah berdasarkan nama: ditolak, sekitar separuh box meleset akibat augmentasi rotasi. Unduh 526 gambar badak berlabel dari Open Images V7. | `audit_out/elephant_recovery_check/`, `audit_out/rhino_openimages_check/` |
| 15/11 | Joseph | ZooLens_final_v2: +497 badak dan +454 gajah (Open Images, CC BY), cek visual 75 dibuang, cek kebocoran pHash 0 temuan, test tidak berubah. Rasio kelas train 5,5 : 1 menjadi 1,57 : 1. | `docs/CLASS_BALANCE_V2.md`, commit e2b4ba7 |
| 17/11 | Joseph | Uji ulang 500 foto (250 positif, 250 negatif): subset dibekukan, cek duplikat pHash 0 temuan (1 foto pilot badak identik dengan data val dibuang), kondisi visual dinilai per foto, kriteria H1 sampai H4 ditetapkan sebelum model dijalankan. Hasil: recall 64,4%, precision 70,9%, FPR 26,4%. H1, H2, H4 didukung; H3 tidak didukung. | `docs/UJI_500_PROTOKOL.md`, `docs/UJI_500_HASIL.md`, `ml/uji500/` |
