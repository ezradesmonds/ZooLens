# Rumusan Hipotesis Pengujian 200 Kasus Visual (Occlusion & Truncation)
**Proyek:** ZooLens – Aplikasi Deteksi Satwa Interaktif (Kelompok 10)  
**Penyusun:** Ezra Desmond Sutanto (Project Manager & Integration Lead)  
**Dokumentasi untuk:** Aldo Kurniawan Tanjung (Sekretaris / QA & Documentation)  
**Target Milestone:** Persiapan Laporan Lengkap UTS (Senin, 2 November 2026)  

---

## 1. Latar Belakang & Landasan Ilmiah
Sesuai arahan Dosen Client (Liliana, S.T., M.Eng., Ph.D.) pada review Week 5, tim ZooLens diminta melakukan pengujian empiris sebanyak $\approx$ 200 kasus visual guna menganalisis batas ketahanan (*boundary limits*) model YOLO11n pada kondisi satwa yang tampak sebagian (*partial visibility*). 

Sebelum pengujian 200 citra dieksekusi, tim merumuskan 4 (empat) hipotesis ilmiah sebagai tolok ukur evaluasi.

---

## 2. Daftar 4 Hipotesis Resmi Tim

### Hipotesis 1: Kegagalan Fitur Global akibat Severe Occlusion (>50%)
* **Pernyataan Hipotesis ($H_1$):**  
  > *"Tingkat keyakinan (confidence score) model akan turun drastis hingga di bawah batas threshold ($\le 0.50$) dan memicu False Negative (FN) pada citra satwa yang mengalami oklusi parah (>50% tubuh tertutup objek asing seperti air keruh, lumpur, atau semak tebal), karena model baseline YOLO11n sangat bergantung pada struktur siluet global (kombinasi kontur badan dan keempat tungkai)."*
* **Kriteria Pengujian di Excel:**  
  * Mengamati foto satwa (terutama Badak dan Gajah) yang sedang berendam air atau terhalang semak tebal.
  * **Terbukti Jika:** Persentase False Negative (FN) pada kategori *Severe Occlusion* signifikan lebih tinggi ($\ge 50\%$) dibanding kategori *Full Visibility*.

---

### Hipotesis 2: Ketahanan Tekstur Spasial Lokal (Zebra vs Badak & Gajah)
* **Pernyataan Hipotesis ($H_2$):**  
  > *"Zebra memiliki tingkat True Positive (TP) dan recall tertinggi pada kondisi terpotong (Truncation) dibanding Badak dan Gajah, karena corak belang (stripe pattern) merupakan fitur visual spasial lokal yang terdistribusi merata di seluruh permukaan tubuh, sedangkan Badak dan Gajah sangat bergantung pada organ kunci terpusat (kepala, cula, atau belalai)."*
* **Kriteria Pengujian di Excel:**  
  * Mengamati foto crop/close-up tubuh tanpa kepala (misal: hanya punggung atau badan samping).
  * **Terbukti Jika:** Foto potongan tubuh Zebra tetap berhasil terdeteksi sebagai Zebra (TP), sedangkan potongan tubuh Badak/Gajah tanpa kepala berstatus False Negative (FN).

---

### Hipotesis 3: False Positive Akibat Bias Latar Belakang Vegetasi Rimbun
* **Pernyataan Hipotesis ($H_3$):**  
  > *"Latar belakang dedaunan lebat dengan pola pencahayaan belang (dappled light / shadow) memiliki tingkat False Positive (FP) tertinggi yang keliru diprediksi sebagai Harimau (Tiger), akibat karakteristik dataset latih harimau yang didominasi oleh objek berskala kecil (<4% area citra) di dalam vegetasi hutan."*
* **Kriteria Pengujian di Excel:**  
  * Mengamati citra non-harimau (atau foto satwa lain di latar hutan/semak) yang memunculkan deteksi tak terduga.
  * **Terbukti Jika:** Terdapat bounding box harimau pada area dedaunan/ranting pohon (seperti pada temuan awal foto gajah di sungai).

---

### Hipotesis 4: Keunggulan Edge Truncation dibanding In-Frame Occlusion
* **Pernyataan Hipotesis ($H_4$):**  
  > *"Satwa yang mengalami pemotongan di tepi bingkai foto (Edge Truncation) memiliki peluang True Positive lebih tinggi dibanding satwa yang tertutup objek asing di tengah tubuh (In-Frame Occlusion) pada tingkat keterlihatan yang setara, selama organ pembeda utama (seperti kepala atau leher jerapah) tetap berada di dalam frame."*
* **Kriteria Pengujian di Excel:**  
  * Membandingkan satwa yang terpotong batas bingkai kamera vs satwa yang terhalang tiang/pohon tepat di tengah tubuhnya.
  * **Terbukti Jika:** Recall pada kategori *Truncation* lebih tinggi daripada kategori *Moderate/Severe Occlusion*.

---

## 3. Alur Verifikasi Pasca-Testing
1. **Eksekusi Otomatis:** Runner `batch_test_200.py` menguji 200 citra dan mengekspor metrik ke `test_results_200.csv`.
2. **Review Kualitatif:** Anggota tim (Felix, Ivy, Bryan, Joseph) memvalidasi baris kelas masing-masing dan mencatat penyebab visual kegagalan.
3. **Sintesis Laporan:** Aldo menyandingkan data empiris Excel dengan 4 hipotesis di atas pada bab *Analisis dan Pembuktian Hipotesis* dalam Laporan Resmi UTS.
