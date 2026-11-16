# Ringkasan Uji Ulang 500 Foto (untuk tim)

Joseph, 17 November 2026. Detail: `docs/UJI_500_HASIL.md`.

**Intinya:** pada foto baru di luar dataset, model aktif (`W6_cand1`) mengenali 66% foto satwa
dan salah mendeteksi satwa pada 26% foto tanpa satwa target. Pilot 205 foto dulu 89%.

## Angka

| | Hasil |
|---|---|
| Recall | 65,6% (158 dari 241 foto positif) |
| Precision | 70,5% |
| False positive rate | 26,4% (66 dari 250 foto negatif) |
| Per kelas | zebra 96%, jerapah 94%, harimau 64%, gajah 45%, badak 30% |
| Per kondisi | Full 74%, Occlusion ringan 80%, sedang 61%, berat 32%, Truncation 66% |

## Hipotesa

| | Status | Bukti singkat |
|---|---|---|
| H1 occlusion berat memicu gagal deteksi | Didukung | gagal 68% (21/31) vs Full 26% (11/43) |
| H2 zebra paling tahan saat terpotong | Didukung | zebra 12/13 vs badak + gajah 9/21 |
| H3 dedaunan rimbun dikira harimau | Tidak didukung | FP vegetasi rimbun hanya 3/46, tidak ada yang harimau |
| H4 terpotong lebih mudah daripada terhalang | Didukung | 66% (43/65) vs 49% (38/77) |

## Yang perlu ditindaklanjuti

- **Bryan:** latih ulang dengan `ZooLens_final_v2` (EXP-03). Cek juga dugaan penurunan badak:
  pada 42 foto badak pilot, `W6_cand1` mengenali 11, pilot dulu 29 dari 40.
- **Bryan, Ezra:** model belum pernah melihat contoh negatif. Hewan lain dikira satwa target pada
  50 dari 100 foto (rusa, unta, singa dikira jerapah). Perlu foto negatif di data training.
- **Aldo:** Excel Format Evaluasi terisi ada di `ml/uji500/ZooLens_Format_Evaluasi_Uji500_terisi.xlsx`.
  BUG-08, BUG-09, BUG-10 bisa diperbarui: 250 foto negatif sudah diuji, kondisi dinilai per foto,
  semua foto dicek duplikat terhadap data training (0 mirip).
- **Semua:** subset 500 foto dibekukan (`ml/uji500/manifest_uji500.csv`) dan tidak boleh masuk data training.

## Catatan cara uji

- 250 positif (50 per kelas) + 250 negatif; 9 foto positif dikeluarkan saat tinjauan, jadi 491 dihitung.
- Sumber: Open Images, iNaturalist, foto pilot bagian Joseph. Folder uji lengkap tim tidak dipakai.
- Kriteria H1 sampai H4 ditulis dan di-commit sebelum model dijalankan (`docs/UJI_500_PROTOKOL.md`).
- Kondisi visual: penilaian awal dibantu AI, lalu ditinjau Joseph per foto.
