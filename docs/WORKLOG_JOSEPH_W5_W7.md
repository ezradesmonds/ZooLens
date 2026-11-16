# Work Log Joseph, W5 sampai W7

Baris siap tempel ke tab "2. Work Log" dan status untuk tab "1. Weekly Target".

## Weekly Target (kolom Joseph)

| Minggu | Tugas | Status | Catatan |
|---|---|---|---|
| W5 | Perbaiki data kelas minoritas bila perlu | Done | ZooLens_final_v2 selesai 15/11; bukti metrik menunggu EXP-03 |
| W6 | Subset uji kondisi visual | Done | Subset 500 foto dibekukan 17/11 |
| W7 | Metrik per kelas dan kondisi visual | Done | Dihitung pada subset 500, kondisi sudah ditinjau |

## Work Log

| Tanggal | Minggu | PIC | Aktivitas | Hasil | Evidence |
|---|---|---|---|---|---|
| 01/11 | W5 | Joseph | Uji pemulihan 288 label gajah berdasarkan nama file | Ditolak: sekitar separuh box meleset karena salinan augmentasi Roboflow diputar berbeda | `audit_out/elephant_recovery_check/` |
| 01/11 | W5 | Joseph | Unduh gambar badak berlabel dari Open Images V7 | 526 gambar, 743 box, lisensi CC BY | `audit_out/rhino_openimages_check/` |
| 15/11 | W5 | Joseph | Cek visual data tambahan badak dan gajah | 1.026 gambar diperiksa, 75 dibuang (patung, awetan, ilustrasi) | `audit_out/review_v2/` |
| 15/11 | W5 | Joseph | Cek kebocoran dan bangun ZooLens_final_v2 | +497 badak, +454 gajah; pHash 0 temuan; test tidak berubah; rasio kelas train 5,5 : 1 menjadi 1,57 : 1 | `docs/CLASS_BALANCE_V2.md`, commit e2b4ba7 |
| 15/11 | W5 | Joseph | Temuan label dataset badak lama | Sekitar 20 foto multi-badak hanya diberi satu box; sekitar 10 gambar bukan foto | `docs/CLASS_BALANCE_V2.md` |
| 17/11 | W6 | Joseph | Kumpulkan dan bekukan subset uji 500 foto | 250 positif + 250 negatif dengan sumber, lisensi, MD5; pHash 0 mirip; 1 foto pilot badak identik dengan data val dibuang | `ml/uji500/manifest_uji500.csv`, commit 9bcbefb |
| 17/11 | W6 | Joseph | Tetapkan rubrik kondisi visual dan kriteria H1 sampai H4 sebelum model dijalankan | Protokol tertulis | `docs/UJI_500_PROTOKOL.md` |
| 17/11 | W6 | Joseph | Nilai kondisi visual per foto | 250 foto ditinjau; 81 penilaian awal diubah, 9 foto dikeluarkan | `ml/uji500/kondisi_final.csv` |
| 17/11 | W7 | Joseph | Jalankan model dan hitung metrik per kelas dan per kondisi | Recall 65,6%, precision 70,5%, FPR 26,4%; badak 30%, gajah 45% | `ml/uji500/ringkasan_uji500.md`, Excel Format Evaluasi terisi |
| 17/11 | W7 | Joseph | Simpulkan H1 sampai H4 | H1, H2, H4 didukung; H3 tidak didukung | `docs/UJI_500_HASIL.md` |
