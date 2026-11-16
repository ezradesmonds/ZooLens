# Hasil Uji Ulang 500 Foto

Model `W6_cand1_yolo11n_adamw_lr0005`, confidence >= 0,5. Foto dihitung: 491 (241 positif, 250 negatif).
Kondisi visual: hasil tinjauan (ml/uji500/kondisi_final.csv).

## Ringkasan

| Ukuran | Nilai |
|---|---|
| TP / FN / FP / TN | 158 / 83 / 66 / 184 |
| Precision, TP / (TP + FP) | 70.5% |
| Recall, TP / (TP + FN) | 65.6% |
| Accuracy | 69.7% |
| False positive rate, FP / (FP + TN) | 26.4% |

## Per kelas (foto positif)

| Kelas | Foto | TP | FN tidak terdeteksi | FN salah kelas | Recall |
|---|---|---|---|---|---|
| elephant | 49 | 22 | 22 | 5 | 44.9% |
| giraffe | 48 | 45 | 3 | 0 | 93.8% |
| zebra | 47 | 45 | 1 | 1 | 95.7% |
| tiger | 50 | 32 | 10 | 8 | 64.0% |
| rhinoceros | 47 | 14 | 26 | 7 | 29.8% |

## Per kondisi visual (foto positif)

| Kondisi | Foto | TP | FN | Recall | Rata-rata confidence TP |
|---|---|---|---|---|---|
| Full | 43 | 32 | 11 | 74.4% | 0.815 |
| Occlusion ringan | 56 | 45 | 11 | 80.4% | 0.816 |
| Occlusion sedang | 46 | 28 | 18 | 60.9% | 0.786 |
| Occlusion berat | 31 | 10 | 21 | 32.3% | 0.752 |
| Truncation | 65 | 43 | 22 | 66.2% | 0.796 |

## Recall per kelas x kondisi (TP/foto)

| Kelas | Full | Occlusion ringan | Occlusion sedang | Occlusion berat | Truncation |
|---|---|---|---|---|---|
| elephant | 10/14 | 3/10 | 4/10 | 0/5 | 5/10 |
| giraffe | 3/3 | 15/15 | 6/7 | 5/7 | 16/16 |
| zebra | 8/8 | 16/16 | 8/9 | 1/1 | 12/13 |
| tiger | 7/7 | 9/10 | 7/12 | 3/6 | 6/15 |
| rhinoceros | 4/11 | 2/5 | 3/8 | 1/12 | 4/11 |

## Foto negatif per jenis

| Jenis | Foto | FP | Tingkat FP | Kelas FP |
|---|---|---|---|---|
| vegetasi rimbun | 46 | 3 | 6.5% | zebra 1, elephant 1, giraffe 1 |
| vegetasi lain | 54 | 7 | 13.0% | giraffe 4, elephant 2, zebra 1 |
| hewan lain | 100 | 50 | 50.0% | giraffe 21, tiger 11, elephant 10, zebra 4, rhinoceros 4 |
| objek/bangunan/orang | 50 | 6 | 12.0% | tiger 3, elephant 1, giraffe 1, zebra 1 |

FP pada hewan lain (hewan sebenarnya -> prediksi): deer -> giraffe (3), camel -> giraffe (3), lynx -> tiger (3), mule -> elephant (2), lion -> giraffe (2), pig -> elephant (2), leopard -> giraffe (2), brown bear -> elephant (2), cheetah -> giraffe (2), monkey -> giraffe (2), kangaroo -> giraffe (2), leopard -> zebra (1), cattle -> elephant (1), antelope -> tiger (1), jaguar -> giraffe (1), horse -> elephant (1), goat -> tiger (1), mule -> rhinoceros (1), lynx -> giraffe (1), ostrich -> elephant (1), lion -> zebra (1), bull -> giraffe (1), sheep -> tiger (1), goat -> giraffe (1), horse -> rhinoceros (1), ostrich -> giraffe (1), kangaroo -> tiger (1), jaguar -> zebra (1), ostrich -> tiger (1), cattle -> tiger (1), monkey -> rhinoceros (1), sheep -> elephant (1), hippopotamus -> tiger (1), brown bear -> tiger (1), monkey -> zebra (1), pig -> rhinoceros (1).

Salah kelas pada foto positif (sebenarnya -> prediksi): tiger -> zebra (5), tiger -> giraffe (3), rhinoceros -> elephant (3), elephant -> giraffe (2), elephant -> tiger (2), rhinoceros -> giraffe (2), rhinoceros -> tiger (2), elephant -> zebra (1), zebra -> giraffe (1).

## Hipotesa

Kriteria: `docs/UJI_500_PROTOKOL.md` (ditetapkan sebelum model dijalankan). Uji Fisher satu sisi.

- **H1: Didukung.** Tingkat FN Occlusion berat 67.7% (21 dari 31) vs Full 25.6% (11 dari 43); p = 0.0003. Rata-rata confidence deteksi benar: berat 0.752, Full 0.815.
- **H2: Didukung.** Recall Truncation zebra 92.3% (12 dari 13) vs badak + gajah 42.9% (9 dari 21; badak 4/11, gajah 5/10); p = 0.0043.
- **H3: Tidak didukung.** FP vegetasi rimbun 6.5% (3 dari 46), berlabel tiger 0. Tingkat FP jenis lain: vegetasi lain 13.0%, hewan lain 50.0%, objek/bangunan/orang 12.0%. Dari seluruh 66 FP, 14 berlabel tiger.
- **H4: Didukung.** Recall Truncation 66.2% (43 dari 65) vs Occlusion sedang + berat 49.4% (38 dari 77); p = 0.0322.
