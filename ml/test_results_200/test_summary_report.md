# Laporan Evaluasi Batch Testing 200 Kasus Visual ZooLens

- **Model Weights:** `best.pt`
- **Folder Dataset:** `test_200`
- **Tanggal Pengujian:** 31 October 2026
- **Total Citra Diuji:** 205 citra
- **Durasi Total:** 47.76 detik (Rata-rata inferensi: 232.13 ms/citra)
- **Confidence Threshold:** $\ge$ 0.5

## 1. Performa per Kelas Satwa

| Kelas Satwa | Total Sampel | True Positive (TP) | False Negative (FN) | False Positive (FP) | Accuracy / Recall (%) | PIC Analisis |
|---|---|---|---|---|---|---|
| **elephant** | 40 | 40 | 0 | 0 | **100.0%** | Felix |
| **giraffe** | 40 | 37 | 3 | 0 | **92.5%** | Ivy |
| **zebra** | 41 | 35 | 3 | 3 | **85.4%** | Felix, Ivy, Bryan, Joseph |
| **tiger** | 44 | 44 | 0 | 0 | **100.0%** | Bryan |
| **rhinoceros** | 40 | 29 | 9 | 2 | **72.5%** | Joseph |
| **TOTAL** | **205** | **185** | **15** | **5** | **90.2%** | **Tim ZooLens** |

## 2. Performa per Kondisi Visual (Pembuktian Hipotesis Occlusion)

| Kondisi Visual | Total Uji | True Positive (TP) | False Negative (FN) | False Positive (FP) | Accuracy (%) | Catatan Analisis |
|---|---|---|---|---|---|---|
| **Full Visibility** | 94 | 93 | 1 | 0 | **98.9%** | Hipotesis teruji |
| **Moderate Occlusion (20-50%)** | 70 | 57 | 9 | 4 | **81.4%** | Hipotesis teruji |
| **Severe Occlusion (>50%)** | 11 | 9 | 1 | 1 | **81.8%** | Hipotesis teruji |
| **Truncation (Terpotong Tepi)** | 30 | 26 | 4 | 0 | **86.7%** | Hipotesis teruji |

## 3. Tindak Lanjut Anggota Tim

File CSV pengujian telah diekspor ke: `test_results_200.csv`.
1. **Felix:** Buka file CSV, filter kolom `PIC_Review = Felix` (40 Gajah + 10 Zebra) -> periksa baris yang berstatus FN/FP dan isi catatan visualnya.
2. **Ivy:** Buka file CSV, filter kolom `PIC_Review = Ivy` (40 Jerapah + 10 Zebra) -> periksa baris yang berstatus FN/FP dan isi catatan visualnya.
3. **Bryan:** Buka file CSV, filter kolom `PIC_Review = Bryan` (44 Harimau + 11 Zebra) -> periksa baris yang berstatus FN/FP dan isi catatan visualnya.
4. **Joseph:** Buka file CSV, filter kolom `PIC_Review = Joseph` (40 Badak + 10 Zebra) -> periksa baris yang berstatus FN/FP dan isi catatan visualnya.
5. **Aldo & Ezra:** Mengompilasi seluruh temuan ke bab Analisis Kegagalan untuk Presentasi UTS.
