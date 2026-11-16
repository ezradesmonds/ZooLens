# Hasil Uji Ulang 500 Foto dan Kesimpulan H1 sampai H4

PIC: Joseph (Dataset & Evaluation). Tanggal: 17 November 2026.
Protokol dan kriteria (ditulis sebelum model dijalankan): `docs/UJI_500_PROTOKOL.md`.
Tabel lengkap: `ml/uji500/ringkasan_uji500.md`. Hasil per foto: `ml/uji500/hasil_uji500.csv`.
Excel Format Evaluasi terisi: `ml/uji500/ZooLens_Format_Evaluasi_Uji500_terisi.xlsx`.

Kondisi visual: penilaian awal dibantu AI, lalu ditinjau Joseph per foto (`ml/uji500/kondisi_final.csv`).
Dari 250 foto positif, 81 penilaian diubah dan 9 foto dikeluarkan karena tidak layak.
Foto yang dihitung: 491 (241 positif, 250 negatif).

## Hasil utama

| Ukuran | Uji 500 | Pilot 205 |
|---|---|---|
| Recall (foto positif) | 65,6% (158 dari 241) | 89,0% (162 dari 182) |
| Precision | 70,5% | tidak terukur |
| False positive rate (foto negatif) | 26,4% (66 dari 250) | tidak terukur |
| Accuracy | 69,7% | tidak terukur |

| Kelas | Recall | | Kondisi | Recall |
|---|---|---|---|---|
| zebra | 95,7% (45/47) | | Full | 74,4% (32/43) |
| giraffe | 93,8% (45/48) | | Occlusion ringan | 80,4% (45/56) |
| tiger | 64,0% (32/50) | | Occlusion sedang | 60,9% (28/46) |
| elephant | 44,9% (22/49) | | Occlusion berat | 32,3% (10/31) |
| rhinoceros | 29,8% (14/47) | | Truncation | 66,2% (43/65) |

Foto negatif: vegetasi rimbun 6,5% FP (3/46), vegetasi lain 13,0% (7/54), objek/bangunan/orang
12,0% (6/50), **hewan lain 50,0% (50/100)**.

## Kesimpulan hipotesa

| Hipotesa | Status | Bukti |
|---|---|---|
| H1 Occlusion berat memicu FN | **Didukung** | FN Occlusion berat 67,7% (21/31) vs Full 25,6% (11/43), p = 0,0003. Bagian confidence tidak terbukti kuat: rata-rata confidence deteksi benar 0,752 vs 0,815. |
| H2 Zebra paling tahan saat terpotong | **Didukung** | Recall Truncation zebra 92,3% (12/13) vs badak + gajah 42,9% (9/21), p = 0,004. |
| H3 Vegetasi rimbun memicu deteksi palsu harimau | **Tidak didukung** | FP vegetasi rimbun paling rendah (6,5%) dan tidak ada yang berlabel tiger. Dari 66 FP, 14 berlabel tiger; semuanya pada hewan lain dan objek. |
| H4 Terpotong lebih mudah dikenali daripada terhalang | **Didukung** | Recall Truncation 66,2% (43/65) vs Occlusion sedang + berat 49,4% (38/77), p = 0,032. |

Kesimpulan keempat hipotesa sama sebelum dan sesudah tinjauan kondisi visual.

## Temuan di luar hipotesa

1. **Model jauh lebih lemah pada foto di luar dataset.** Pada split test `ZooLens_final` recall
   tingkat foto 98% (254/258), pada foto baru 66%. Skrip yang sama dipakai untuk keduanya, jadi
   selisih ini bukan kesalahan pengukuran. Gajah dan badak paling terdampak; keduanya juga kelas
   dengan data training paling sedikit dan paling seragam.
2. **Foto Full pun sering gagal untuk badak (4/11) dan sebagian gajah (10/14).** Jadi occlusion bukan
   satu-satunya penyebab; data training kedua kelas kurang beragam.
3. **Model sering "melihat" satwa target pada hewan lain.** Rusa, unta, singa, macan tutul
   dikira jerapah; lynx dikira harimau. Data training tidak punya contoh negatif.
4. **Salah kelas antar satwa target:** tiger -> zebra (5), tiger -> giraffe (3), rhinoceros -> elephant (3).
5. **Dugaan penurunan pada badak dibanding model pilot.** Pada 42 foto badak pilot bagian Joseph,
   model aktif (`W6_cand1`) mengenali 11 foto (26%); pilot mencatat 29 dari 40 (72,5%) dengan
   model sebelumnya. Dari 20 foto yang namanya bisa dicocokkan, 10 TP di pilot menjadi 4.
   Perlu dicek Bryan: jalankan kedua bobot pada folder yang sama.

## Batasan

- Per kelas per kondisi sampelnya kecil (1 sampai 16 foto), jadi hanya gabungan lintas kelas yang disimpulkan.
- Occlusion berat 31 foto, 12 di antaranya badak; hasil H1 ikut dipengaruhi lemahnya kelas badak.
  Tanpa badak arahnya tetap sama: FN Occlusion berat 10/19 (53%) vs Full 4/32 (13%).
- Kondisi visual dinilai satu orang (Joseph) dengan penilaian awal dari AI; belum ada penilai kedua.
- Foto positif Open Images dipilih yang berisi satu satwa target; foto pilot zebra berisi kawanan.
- Evaluasi di tingkat foto (kelas dengan confidence tertinggi), tidak menilai ketepatan kotak.
- Sumber foto: Open Images, iNaturalist, dan foto pilot bagian Joseph. Folder uji lengkap tim (205 foto) tidak dipakai.

## Rekomendasi

1. Latih ulang dengan `ZooLens_final_v2` (EXP-03): menambah 497 badak dan 454 gajah dari sumber yang lebih beragam.
2. Tambahkan foto negatif (hewan lain, tanpa satwa) ke data training agar FP turun.
3. Uji ulang subset beku ini setelah latih ulang; subset tidak boleh dipakai untuk training.
4. Bryan membandingkan bobot pilot dan `W6_cand1` pada foto badak yang sama.
