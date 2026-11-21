# Dataset v3: Riset Jumlah Data dan Ketersediaan Sumber

PIC: Joseph (Dataset & Evaluation). Tanggal: 20 November 2026.
Latar: masukan Bu Liliana pada progress report. (1) Tambah kelas `non_class` untuk hal yang bukan
5 satwa target. (2) Perbanyak dataset, dengan acuan jumlah dari penelitian lain. (3) Pilih antara
latih ulang dengan data lebih banyak atau latih dengan data baru. (4) Data dicampur: satwa target,
hewan lain, dan foto tanpa hewan.

Dokumen ini berisi tahap 1 (riset) dan tahap 2 (hitung ketersediaan). Belum ada gambar yang diunduh.

## 1. Berapa banyak data yang dibutuhkan

### Panduan Ultralytics (pembuat YOLO)

Sumber: [Ultralytics, Tips for Best Training Results](https://docs.ultralytics.com/yolov5/tutorials/tips_for_best_training_results).
Halaman ini masuk bagian YOLOv5, tapi panduan datanya juga dirujuk untuk versi YOLO yang lebih baru.

| Hal | Rekomendasi |
|---|---|
| Gambar per kelas | minimal 1.500 |
| Objek berlabel per kelas | minimal 10.000 |
| Background image (tanpa objek, label kosong) | sekitar 0 sampai 10% dari total, untuk menekan deteksi palsu. COCO memakai sekitar 1% |
| Kelengkapan label | semua objek di semua gambar harus diberi kotak; label sebagian tidak akan berhasil |
| Bobot awal | dataset kecil sampai menengah: mulai dari bobot pretrained; dataset besar: boleh dari nol |
| Epoch | mulai dari 300, dengan early stopping (patience 50) |

### Penelitian lain dengan YOLO berukuran kecil

"YOLO11n light" yang dimaksud kemungkinan YOLO11n. Huruf n berarti nano, versi paling ringan
yang kita pakai.

| Penelitian / dataset | Data | Hasil |
|---|---|---|
| [African Wildlife Dataset (Ultralytics)](https://docs.ultralytics.com/datasets/detect/african-wildlife): kerbau, gajah, badak, zebra | 1.504 gambar, sekitar 376 per kelas | Dipakai sebagai pembanding di [Hjort-YOLO (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13713621): YOLO11n mAP50 gajah 0,885, badak 0,950, zebra 0,881 |
| [WildARe-YOLO (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S1574954124000839) | sekitar 1.200 sampai 1.400 gambar per kelas, termasuk jerapah, gajah, badak, zebra | model ringan berbasis YOLOv5 |
| [MMLA (Hugging Face)](https://huggingface.co/imageomics/mmla), foto drone | 7.658 gambar, 4.430 di antaranya zebra | YOLO11m |
| [YOLOv8 di learning factory (arXiv 2503.10356)](https://arxiv.org/pdf/2503.10356) | 1.600, 3.200, 4.800 gambar per kelas | YOLOv8n lebih stabil di gambar baru daripada model besar; selisih paling besar terjadi saat data paling sedikit |

### Kesimpulan untuk ZooLens

- **Target: 1.500 gambar per kelas** untuk data train, sesuai panduan Ultralytics. Penelitian satwa
  dengan sekitar 400 sampai 1.400 per kelas sudah mendapat mAP50 tinggi, tapi angka itu diukur pada
  split test dataset yang sama.
- Pengalaman kita sendiri: model mendapat 98% di split test dataset, tapi 66% pada 500 foto baru
  (`docs/UJI_500_HASIL.md`). Jadi **keragaman sumber foto** sama pentingnya dengan jumlah.
- **10.000 objek per kelas tidak realistis** untuk proyek ini (lihat tabel bagian 2). Target ini
  dicatat sebagai batasan.
- **Background sekitar 10%** dari total data train.

## 2. Ketersediaan data

### Data yang sudah ada (ZooLens_final_v2)

| Kelas | Train: gambar / objek | Val: objek | Test: objek |
|---|---|---|---|
| elephant | 628 / 1.217 | 135 | 42 |
| giraffe | 630 / 961 | 112 | 128 |
| zebra | 433 / 564 | 66 | 69 |
| tiger | 679 / 1.414 | 177 | 163 |
| rhinoceros | 570 / 753 | 85 | **16** |

Belum ada background image (0 file label kosong) dan belum ada kelas `non_class`. Split test hanya
punya 16 objek badak, terlalu sedikit untuk mengukur kelas ini.

### Satwa target: sumber tambahan

Angka Open Images sudah dikurangi gambar yang dipakai di v2 dan di uji 500. "Bersih" berarti
punya minimal satu kotak yang bukan patung atau gambar (IsDepiction = 0). Semua gambar tetap akan
dicek visual, biasanya 5 sampai 10% dibuang.

| Kelas | v2 train | Open Images belum dipakai: gambar / kotak | COCO train2017: semua lisensi / hanya CC BY, BY-SA, bebas | Total maksimal (lisensi bebas) | 1.500 tercapai? |
|---|---|---|---|---|---|
| elephant | 628 | 735 / 1.549 | 2.143 / 538 | sekitar 1.900 | Ya |
| giraffe | 630 | 771 / 1.220 | 2.546 / 567 | sekitar 1.970 | Ya |
| zebra | 433 | 485 / 940 | 1.916 / 458 | sekitar 1.380 | Hampir; bisa ditutup dengan COCO berlisensi NC |
| tiger | 679 | 848 / 1.032 | tidak ada kelas tiger | sekitar 1.530 | Pas-pasan |
| rhinoceros | 570 | **1 / 1** (sudah habis terpakai) | tidak ada kelas rhino | 571 | **Tidak** |

Badak hanya bisa ditambah dari foto tanpa kotak, misalnya [iNaturalist](https://www.inaturalist.org),
yang harus diberi kotak dulu. Jumlah observasi badak di iNaturalist:

| Lisensi foto | Liar | Di kebun binatang (captive) |
|---|---|---|
| CC BY, BY-SA, CC0 | 1.204 | 164 |
| ditambah CC BY-NC, BY-NC-SA | 9.316 | 2.250 |

Foto kebun binatang justru mirip kondisi pemakaian ZooLens.

### `non_class` (hewan lain): Open Images, gambar bersih

Diprioritaskan hewan yang di uji 500 sering dikira satwa target:

| Hewan | Gambar | Hewan | Gambar |
|---|---|---|---|
| Deer (rusa) | 1.743 | Cheetah | 531 |
| Camel (unta) | 612 | Jaguar | 453 |
| Lion (singa) | 781 | Lynx | 218 |
| Leopard (macan tutul) | 662 | Hippopotamus (kuda nil) | 352 |
| Antelope | 675 | Horse (kuda) | 5.364 |
| Cattle (sapi) | 2.392 | Bull, Goat, Bear, Kangaroo, Ostrich, dan lain-lain | ratusan sampai ribuan |

Cukup untuk 2.000 gambar `non_class`, dengan kuota per hewan supaya tidak didominasi kuda dan sapi.

### Background (tanpa hewan)

Ada sekitar 748.000 gambar Open Images train yang punya kotak pohon, tanaman, bunga, bangunan,
orang, atau mobil, tapi tidak punya kotak hewan. Kebutuhan kita hanya sekitar 1.000, jadi bisa
dipilih yang mirip lingkungan kebun binatang (pohon, semak, kandang, pengunjung). Tetap dicek visual,
karena hewan yang tidak dianotasi bisa saja ada di foto.

## 3. Usulan komposisi dataset v3

| Jenis | Train | Val | Test |
|---|---|---|---|
| 5 satwa target | 1.500 per kelas = 7.500 | sekitar 10% | sekitar 10%, minimal 100 per kelas |
| `non_class` | 2.000 | sekitar 10% | sekitar 10% |
| Background | sekitar 1.000 (10%) | sekitar 10% | sekitar 10% |
| **Total** | **sekitar 10.500** | **sekitar 1.300** | **sekitar 1.300** |

Perkiraan ukuran di disk: 3 sampai 4 GB (sisi terpanjang 1.024 px). Disk D masih kosong 120 GB.

Aturan yang tetap berlaku:
- Subset uji 500 tidak boleh masuk dataset v3. ID-nya dikecualikan dan dicek ulang dengan pHash.
- Semua gambar baru dicek kemiripan (pHash) terhadap v2 dan antar sumber. COCO dan Open Images
  sama-sama dari Flickr, jadi bisa ada foto yang sama.
- Foto yang berisi satwa target dan hewan lain: semua objek diberi kotak dengan kelasnya masing-masing.

## 4. Yang perlu diputuskan tim

1. **Kekurangan badak** (sekitar 930 gambar). Pilihan:
   - (a) Ambil foto iNaturalist, buat kotak awal otomatis dengan model open-vocabulary
     (misalnya YOLO-World dengan teks "rhinoceros"), lalu Joseph mengoreksi satu per satu.
   - (b) Terima badak sekitar 1.000 gambar dan catat sebagai batasan.
2. **Lisensi NC (non-komersial).** Boleh dipakai untuk tugas kuliah, tapi harus dicatat. Usulan:
   utamakan CC BY, BY-SA, CC0, dan pakai NC hanya untuk menutup kekurangan (zebra, badak).
3. **Nama kelas**: `non_class` sesuai permintaan dosen, sebagai kelas ke-6 (ID 5).
4. **Bobot awal training**: usulan dari `yolo11n.pt` (pretrained COCO), bukan dari `best.pt` lama.
   Keputusan akhir di Bryan.

## Bukti dan file

- Skrip hitung: `ml/scripts/v3/count_openimages.py`, daftar kelas hewan `ml/scripts/v3/animal_ids.csv`
- Hasil hitung Open Images: `ml/scripts/v3/openimages_train_counts.json`
- File kerja (tidak di-commit): `D:\Project\v3_work\oi\` (subset anotasi hewan, ID kandidat
  background), `D:\Project\v3_work\coco\ann.zip` (anotasi COCO 2017)

---

## 5. Keputusan tim (21 November 2026)

- Lisensi NC boleh dipakai (lisensi ND tetap tidak dipakai).
- Bobot awal training: `yolo11n.pt` (pretrained COCO).
- Kekurangan badak ditutup dengan iNaturalist + kotak awal YOLO-World + koreksi manual Joseph.

## 6. Tahap 3: pengumpulan dan pembersihan (21 November 2026)

### Badak (iNaturalist)

1.199 foto CC BY/BY-SA/CC0 diunduh; 7 kembar dibuang; 0 mirip dengan v2, uji 500, dan sumber badak lama.
Kotak awal YOLO-World (uji pada 150 foto berlabel: 87% badak ketemu, 96% kotak benar). Joseph sudah
mengoreksi 963 foto: 900 OK (1.263 kotak badak, 126 kotak non_class), 63 dibuang. 229 foto belum dicek.
Detail: `DataSetZoo/ZooLens/badak_inaturalist/README.md`.

### Satwa lain, non_class, background

Detail cara memilih dan membersihkan: `DataSetZoo/ZooLens/v3/README.md`. Ringkasnya, 8.391 gambar
diunduh, lalu dibuang 289: 68 kembar (termasuk 9 foto COCO yang identik dengan foto uji 500) dan 221
yang bukan foto satwa asli atau tidak jelas (patung, boneka, awetan, lukisan, foto berisi hewan di folder
background). Sisa 8.102 gambar.

### Jumlah gambar per kelas (semua split; satu gambar bisa berisi beberapa kelas)

| Kelas | v2 (train+val+test) | Tambahan v3 | Total | Target (~1.850) |
|---|---|---|---|---|
| elephant | 728 | 1.087 | 1.815 | tercapai |
| giraffe | 788 | 1.082 | 1.870 | tercapai |
| zebra | 540 | 1.343 | 1.883 | tercapai |
| tiger | 849 | 806 | 1.655 | kurang sekitar 200 |
| rhinoceros | 651 | 900 (+229 belum dicek) | 1.551 | kurang sekitar 300 |
| non_class | 0 | 2.778 + gambar badak | sekitar 2.800 | tercapai |
| background | 0 | 1.289 | 1.289 | tercapai (sekitar 10%) |

Target 1.850 = sekitar 1.500 train + 175 val + 175 test. Dengan split 80/10/10, badak dan harimau
mendapat sekitar 1.250 sampai 1.320 gambar train: di bawah 1.500, tapi jauh naik dari 570 dan 679 di v2.

### Langkah berikutnya

1. Bangun split v3 (train/val/test) dengan pengelompokan pHash, test v2 tetap di test, dan test v3
   memuat satwa target, non_class, dan background.
2. `data.yaml` dengan `nc: 6`, nama kelas ke-6 `non_class`.
3. Serahkan ke Bryan: training dari `yolo11n.pt`, evaluasi ulang di uji 500.

## 7. Split v3 (21 November 2026)

Sebelum split dibangun:

- Koreksi badak selesai: 1.120 foto dipakai, 72 dibuang, 1.814 kotak. Joseph juga memberi kotak untuk hewan
  lain di foto badak (zebra, non_class).
- Harimau ditambah 400 foto iNaturalist (takson 41967, sampel acak dari 6.133 observasi, lisensi termasuk NC),
  0 kembar. Setelah koreksi: 360 dipakai, 40 dibuang (jejak kaki, cakaran, bukan harimau).

`ml/scripts/build_split_v3.py` membangun `D:\Project\DataSetZoo\ZooLens_final_v3` (2,4 GB):

| Split | Gambar | elephant | giraffe | zebra | tiger | rhinoceros | non_class | tanpa hewan |
|---|---|---|---|---|---|---|---|---|
| train | 10.579 | 1.500 | 1.496 | 1.520 | 1.608 | 1.452 | 2.276 | 1.031 |
| val | 1.325 | 182 | 185 | 188 | 204 | 186 | 291 | 129 |
| test | 1.225 | 137 | 190 | 190 | 203 | 133 | 286 | 129 |

(angka kelas = jumlah gambar yang memuat kelas itu)

- Test v2 (259 gambar) ikut di test v3 tanpa perubahan (MD5 sama) dan bisa dievaluasi terpisah lewat
  `data_test_v2.yaml`, supaya model lama dan baru tetap dibandingkan pada soal yang sama.
- Data tambahan dibagi 80/10/10 per sumber. Gambar mirip (pHash <= 8) dan foto iNaturalist dari pengguna
  yang sama selalu satu split.
- Audit: 0 pasangan mirip lintas split, 0 gambar mirip foto uji 500, label kosong hanya pada 1.289 foto background.
- Rasio train satwa target terbesar : terkecil 1,11 : 1; background 9,7% dari train.

Yang perlu dilakukan anggota lain:

- Bryan: training dari `yolo11n.pt` dengan `data.yaml` (6 kelas), lalu evaluasi di test v3, `data_test_v2.yaml`,
  dan uji 500 foto (prediksi `non_class` dihitung "bukan satwa target").
- Felix: `ai-service` masih mengharapkan 5 kelas; perlu menerima model 6 kelas dan tidak menampilkan
  `non_class` sebagai satwa.
- Ivy: tampilan untuk hasil `non_class` (mis. "Satwa tidak dikenali").
