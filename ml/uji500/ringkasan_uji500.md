# Hasil Uji Ulang 500 Foto

Model `W6_cand1_yolo11n_adamw_lr0005`, confidence >= 0,5. Foto dihitung: 500 (250 positif, 250 negatif).
Kondisi visual: penilaian awal dibantu AI, belum ditinjau anggota.

## Ringkasan

| Ukuran | Nilai |
|---|---|
| TP / FN / FP / TN | 161 / 89 / 66 / 184 |
| Precision, TP / (TP + FP) | 70.9% |
| Recall, TP / (TP + FN) | 64.4% |
| Accuracy | 69.0% |
| False positive rate, FP / (FP + TN) | 26.4% |

## Per kelas (foto positif)

| Kelas | Foto | TP | FN tidak terdeteksi | FN salah kelas | Recall |
|---|---|---|---|---|---|
| elephant | 50 | 22 | 22 | 6 | 44.0% |
| giraffe | 50 | 47 | 3 | 0 | 94.0% |
| zebra | 50 | 46 | 2 | 2 | 92.0% |
| tiger | 50 | 32 | 10 | 8 | 64.0% |
| rhinoceros | 50 | 14 | 29 | 7 | 28.0% |

## Per kondisi visual (foto positif)

| Kondisi | Foto | TP | FN | Recall | Rata-rata confidence TP |
|---|---|---|---|---|---|
| Full | 53 | 41 | 12 | 77.4% | 0.833 |
| Occlusion ringan | 59 | 47 | 12 | 79.7% | 0.808 |
| Occlusion sedang | 55 | 32 | 23 | 58.2% | 0.786 |
| Occlusion berat | 33 | 9 | 24 | 27.3% | 0.762 |
| Truncation | 50 | 32 | 18 | 64.0% | 0.778 |

## Recall per kelas x kondisi (TP/foto)

| Kelas | Full | Occlusion ringan | Occlusion sedang | Occlusion berat | Truncation |
|---|---|---|---|---|---|
| elephant | 5/10 | 8/13 | 4/12 | 0/5 | 5/10 |
| giraffe | 10/10 | 12/13 | 11/12 | 4/5 | 10/10 |
| zebra | 13/13 | 16/16 | 6/7 | 2/4 | 9/10 |
| tiger | 8/10 | 9/11 | 8/12 | 3/7 | 4/10 |
| rhinoceros | 5/10 | 2/6 | 3/12 | 0/12 | 4/10 |

## Foto negatif per jenis

| Jenis | Foto | FP | Tingkat FP | Kelas FP |
|---|---|---|---|---|
| vegetasi rimbun | 46 | 3 | 6.5% | zebra 1, elephant 1, giraffe 1 |
| vegetasi lain | 54 | 7 | 13.0% | giraffe 4, elephant 2, zebra 1 |
| hewan lain | 100 | 50 | 50.0% | giraffe 21, tiger 11, elephant 10, zebra 4, rhinoceros 4 |
| objek/bangunan/orang | 50 | 6 | 12.0% | tiger 3, elephant 1, giraffe 1, zebra 1 |

FP pada hewan lain (hewan sebenarnya -> prediksi): deer -> giraffe (3), camel -> giraffe (3), lynx -> tiger (3), mule -> elephant (2), lion -> giraffe (2), pig -> elephant (2), leopard -> giraffe (2), brown bear -> elephant (2), cheetah -> giraffe (2), monkey -> giraffe (2), kangaroo -> giraffe (2), leopard -> zebra (1), cattle -> elephant (1), antelope -> tiger (1), jaguar -> giraffe (1), horse -> elephant (1), goat -> tiger (1), mule -> rhinoceros (1), lynx -> giraffe (1), ostrich -> elephant (1), lion -> zebra (1), bull -> giraffe (1), sheep -> tiger (1), goat -> giraffe (1), horse -> rhinoceros (1), ostrich -> giraffe (1), kangaroo -> tiger (1), jaguar -> zebra (1), ostrich -> tiger (1), cattle -> tiger (1), monkey -> rhinoceros (1), sheep -> elephant (1), hippopotamus -> tiger (1), brown bear -> tiger (1), monkey -> zebra (1), pig -> rhinoceros (1).

Salah kelas pada foto positif (sebenarnya -> prediksi): tiger -> zebra (5), tiger -> giraffe (3), rhinoceros -> elephant (3), elephant -> giraffe (2), elephant -> tiger (2), elephant -> zebra (2), rhinoceros -> giraffe (2), rhinoceros -> tiger (2), zebra -> giraffe (1), zebra -> rhinoceros (1).

## Hipotesa

Kriteria: `docs/UJI_500_PROTOKOL.md` (ditetapkan sebelum model dijalankan). Uji Fisher satu sisi.

- **H1: Didukung.** Tingkat FN Occlusion berat 72.7% (24 dari 33) vs Full 22.6% (12 dari 53); p = 0.0000. Rata-rata confidence deteksi benar: berat 0.762, Full 0.833.
- **H2: Didukung.** Recall Truncation zebra 90.0% (9 dari 10) vs badak + gajah 45.0% (9 dari 20; badak 4/10, gajah 5/10); p = 0.0209.
- **H3: Tidak didukung.** FP vegetasi rimbun 6.5% (3 dari 46), berlabel tiger 0. Tingkat FP jenis lain: vegetasi lain 13.0%, hewan lain 50.0%, objek/bangunan/orang 12.0%. Dari seluruh 66 FP, 14 berlabel tiger.
- **H4: Didukung.** Recall Truncation 64.0% (32 dari 50) vs Occlusion sedang + berat 46.6% (41 dari 88); p = 0.0361.
