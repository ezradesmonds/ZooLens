# Ringkasan Audit Dataset YOLO ZooLens (v2)

- Folder: `C:\Users\EUNIKE\DataSetZoo\ZooLens`
- Kelas terpadu: 0=elephant, 1=giraffe, 2=zebra, 3=tiger, 4=rhinoceros
- Total gambar: 4703 (korup: 0)
- Total box: 4204
- Jumlah sumber dataset: 5


## Sumber dataset

Nomor kelas dibaca dari data.yaml tiap sumber lalu dipetakan lewat NAMA kelas.


| sumber | yaml | kelas (ID:nama->terpadu) | gambar | label_ok | label_hilang | label_kosong | label_yatim | beda_hash_rf | box |
|---|---|---|---|---|---|---|---|---|---|
| dataset_badak/badak | data.yaml | 0:Project - v1 2024-10-28 8-29am->lainnya | 269 | 154 | 115 | 0 | 125 | 0 | 157 |
| gajah/elephant-dataset-yolov | dataset.yaml | 0:elephant->elephant | 2092 | 275 | 1807 | 10 | 1699 | 288 | 399 |
| harimau | data.yaml | 0:harimau->tiger | 849 | 849 | 0 | 0 | 0 | 0 | 1754 |
| jerapah | data.yaml | 0:jerapah->giraffe; 1:zebra->zebra | 787 | 787 | 0 | 0 | 0 | 0 | 1208 |
| zebra | data.yaml | 0:zebra->zebra | 706 | 532 | 0 | 174 | 0 | 0 | 686 |


### Lisensi dan URL (diambil otomatis dari README, verifikasi manual)

| sumber | lisensi (README) | url (README) |
|---|---|---|
| dataset_badak/badak | License: CC BY 4.0 | https://universe.roboflow.com/bagas13x/badak-vkfo9 |
| gajah/elephant-dataset-yolov | - | - |
| harimau | License: CC BY 4.0 | https://universe.roboflow.com/hewan1-yosi/harimau |
| jerapah | License: CC BY 4.0 | https://universe.roboflow.com/hewan1-yosi/jerapah |
| zebra | License: CC BY 4.0 | https://universe.roboflow.com/zebra-na7su/zebra-vrl1e |


## Gambar per split

| split | gambar | nama_dasar_unik | bernama_rf | persen |
|---|---|---|---|---|
| train | 3139 | 2955 | 3139 | 66.7 |
| val | 1060 | 1031 | 1060 | 22.5 |
| test | 504 | 486 | 504 | 10.7 |


_Gambar jauh lebih banyak dari nama dasar unik = ada salinan augmentasi Roboflow (hash `.rf.` berbeda) dari gambar sumber yang sama._


## Status label per split

| split | empty | missing | ok |
|---|---|---|---|
| test | 21 | 344 | 139 |
| train | 126 | 1191 | 1822 |
| val | 37 | 387 | 636 |


Gambar tanpa label yang punya label yatim dengan nama dasar sama (hanya beda hash `.rf.`): **288**


## Box per split x kelas

| split | elephant | giraffe | zebra | tiger | rhinoceros | lainnya |
|---|---|---|---|---|---|---|
| train | 147 | 871 | 491 | 1363 | 0 | 92 |
| val | 168 | 309 | 131 | 365 | 0 | 65 |
| test | 84 | 19 | 73 | 26 | 0 | 0 |
| TOTAL | 399 | 1199 | 695 | 1754 | 0 | 157 |


## Gambar unik per split x kelas

| split | elephant | giraffe | zebra | tiger | rhinoceros | lainnya |
|---|---|---|---|---|---|---|
| train | 108 | 590 | 378 | 659 | 0 | 90 |
| val | 107 | 186 | 106 | 175 | 0 | 64 |
| test | 60 | 11 | 54 | 15 | 0 | 0 |
| TOTAL | 275 | 787 | 538 | 849 | 0 | 154 |


! Kelas tanpa box berlabel: rhinoceros


## Box per sumber x kelas terpadu

| source | elephant | giraffe | zebra | tiger | rhinoceros | lainnya |
|---|---|---|---|---|---|---|
| dataset_badak/badak | 0 | 0 | 0 | 0 | 0 | 157 |
| gajah/elephant-dataset-yolov | 399 | 0 | 0 | 0 | 0 | 0 |
| harimau | 0 | 0 | 0 | 1754 | 0 | 0 |
| jerapah | 0 | 1199 | 9 | 0 | 0 | 0 |
| zebra | 0 | 0 | 686 | 0 | 0 | 0 |


## Ukuran box per kelas

| class_name | box | median_luas | pct_tiny | pct_menempel_tepi | pct_huge |
|---|---|---|---|---|---|
| elephant | 399 | 0.21 | 0.75 | 30.33 | 1.25 |
| giraffe | 1199 | 0.22 | 0.75 | 19.1 | 0.25 |
| zebra | 695 | 0.81 | 1.44 | 53.38 | 36.4 |
| tiger | 1754 | 0.04 | 8.21 | 8.15 | 0 |
| rhinoceros | 0 | 0 | 0 | 0 | 0 |
| lainnya | 157 | 0.58 | 0 | 40.13 | 7.64 |


_'Menempel tepi' hanyalah proxy truncation. Occlusion tidak bisa diukur dari format YOLO._


Box per gambar: median 1, maks 14, gambar dengan >=10 box: 6


## Resolusi gambar

- Sisi terpendek: min 416, median 640
- Di bawah 320px: 0 gambar


## Kebocoran dan duplikat

- Nama dasar sama muncul di lebih dari satu split (per sumber): **218**

- Pasangan mirip (Hamming <= 5): 502
- Duplikat persis (MD5): 0
- Pasangan mirip lintas split: 290 (di antaranya nama dasar berbeda: 284)
- Detail di `duplicates.csv`. Near-duplicate perlu dicek manual (frame video berurutan juga bisa terdeteksi mirip).


## Rekap masalah (detail di issues.csv)

| jenis | jumlah |
|---|---|
| missing_label | 1922 |
| orphan_label | 1824 |
| cross_split_duplicate | 290 |
| cross_split_same_base | 218 |
| empty_label | 174 |
| tiny_box | 166 |
| class_out_of_range | 16 |
| unmapped_class_name | 1 |


## Tidak dapat diperiksa dari format YOLO
- Occlusion, group-of, depiction (butuh pemeriksaan manual)
- Lisensi gambar per foto (hanya lisensi tingkat dataset dari README)
