# Laporan Milestone 1

### ZooLens: Aplikasi Deteksi Satwa Interaktif dan Edukasi Kebun Binatang Berbasis AI

**Kelompok 10**, Informatika, Universitas Kristen Petra  
Mata kuliah Manajemen Proyek TI · Dosen: Liliana, S.T., M.Eng., Ph.D.  
**Cakupan:** W1–W5 (28 Sep – 1 Nov 2026), dilaporkan sampai UTS 2 Nov 2026  
**Tim:** Ezra Desmond Sutanto (Ketua), Aldo Kurniawan Tanjung (Sekretaris), Joseph Natanael Phandean, Bryan Cristhoper Sugiono, Ivy Isabella Limanto, Felix Valerian Sutanto

---

## 1. Analisis Kebutuhan User

### 1.1 Konteks: Pengunjung Kebun Binatang Surabaya (KBS)
ZooLens dirancang berdasarkan kunjungan ke KBS. Pengguna utamanya adalah pengunjung umum, pelajar, dan keluarga. Mereka berjalan mengelilingi kebun binatang mengikuti jalur yang ada, berhenti di tiap area untuk melihat dan memotret satwa. Karena pengunjung terus bergerak mengikuti jalur, satwa yang terlewat sulit dilihat ulang, sehingga informasi satwa harus bisa didapat saat itu juga. Dari kondisi tersebut kelompok mengidentifikasi tiga masalah utama:
1. **Satwa tertutup atau terhalang (occlusion):** Satwa sering tersembunyi di balik pagar, tanaman, atau satwa lain, sehingga pengunjung tidak puas dan sulit memastikan satwa apa yang dilihat atau difoto.
2. **Papan informasi rusak:** Sebagian papan di KBS sudah agak rusak akibat hujan dan cuaca sehingga sulit dibaca; isinya juga statis dan mudah diabaikan.
3. **Sulit mengulang:** Karena terus berjalan, pengunjung tidak mudah kembali ke satwa yang terlewat atau terhalang untuk membaca informasinya.

*(Gambar 1: Alur kunjungan di KBS dan titik ZooLens membantu)*

### 1.2 User Story dan Alasan Fitur Menjawab Masalah

| ID | User Story | Masalah yang Diselesaikan | Mengapa Fitur Ini Menjawab Masalah (Problem Solving) |
|---|---|---|---|
| **US1** | Sebagai pengunjung, saya ingin memotret satwa lalu langsung tahu nama dan faktanya, agar tidak bergantung pada papan yang rusak. | Papan informasi rusak / lapuk | **Smart Animal Scanner & Factsheet:** Menampilkan nama umum, nama ilmiah, habitat, pola makan, dan status konservasi IUCN langsung di layar HP secara mandiri tanpa bergantung pada papan fisik. |
| **US2** | Sebagai pengunjung, saya ingin satwa yang sebagian tubuhnya tertutup tetap dikenali, agar kunjungan terasa memuaskan. | Satwa tertutup / terhalang (*occlusion & truncation*) | **Model YOLO11n Spesialis Oklusi:** Dilatih dan dievaluasi khusus pada citra satwa utuh, terhalang dahan/air, maupun terpotong frame dengan kotak deteksi dan skor confidence akurat. |
| **US3** | Sebagai pengunjung yang terus bergerak mengikuti jalur, saya ingin informasi muncul seketika dari satu jepretan foto, agar tidak perlu putar balik. | Pengunjung terus berjalan / sulit mengulang rute | **Web App Instan Tanpa Install:** Cukup buka browser dan ambil 1 foto, inferensi FastAPI merespons cepat dengan batas toleransi API 10 detik. |
| **US4** | Sebagai pelajar atau keluarga dengan anak, saya ingin tantangan mengoleksi satwa, agar aktivitas edukasi terasa seru dan interaktif. | Papan edukasi statis membosankan | **Zoo Digital Safari & Lencana:** Mengubah kunjungan pasif menjadi pencarian satwa interaktif dengan pembukaan lencana koleksi dan histori pemindaian. |

*Batasan:* Sistem tidak menjamin deteksi bila mayoritas tubuh satwa tertutup ekstrem (>80%); skenario ini diuji secara ilmiah pada tahap evaluasi W6–W7.

### 1.3 Kebutuhan Fungsional dan Status
|---|---|---|---|
| **K1** | Mengenali satwa dari satu foto (kamera atau galeri) | Smart Animal Scanner | **Berjalan.** Kamera dan unggah galeri; validasi jpg/png/webp, maks. 2 MB. |
| **K2** | Melihat hasil deteksi yang jelas: kotak, nama, tingkat keyakinan | Model YOLO11n 5 kelas (*elephant, giraffe, zebra, tiger, rhinoceros*) + overlay bounding box | **Berjalan dengan API nyata sejak 26 Okt.** mAP50 0,940 (validasi). |
| **K3** | Mendapat informasi edukatif tentang satwa | Interactive Animal Factsheet: nama ilmiah, habitat, pola makan, status IUCN | **Tampil.** Isi masih data contoh; verifikasi IUCN Red List belum. |
| **K4** | Termotivasi mengoleksi satwa dan melihat riwayat | Zoo Digital Safari (lencana, progres) dan Riwayat Deteksi | **Tampilan jadi;** penyimpanan data nyata dikerjakan W6–W9. |
| **K5** | Tetap dikenali saat satwa tertutup atau terpotong | Evaluasi per kondisi visual (*full, occlusion, truncation*) | **Uji awal:** pilot 205 foto belum cukup sebagai evaluasi (tanpa foto tanpa satwa); uji ulang 500 foto (250 ada satwa, 250 tanpa satwa) direncanakan W6–W7. |
| **K6** | Nyaman di HP dan desktop, respons cepat | Antarmuka responsif; batas waktu API 10 detik | **UI responsif.** Uji perangkat dan user testing W9–W10. |

**Di luar lingkup:** deteksi video langsung, GPS/peta, audio, pembayaran, dan identifikasi individu, ras, umur, atau jenis kelamin satwa.  
**Risiko utama:** data satwa tertutup kurang, kelas tidak seimbang, dan integrasi model–web terlambat.

---

## 2. Roadmap Pengerjaan (W1–W12)

| W | Tanggal | Tahap | Langkah Pengerjaan | Status |
|---|---|---|---|---|
| **W1** | 28 Sep – 4 Okt | Perencanaan | Review proposal dan requirement, struktur tim, pembagian peran, format work log (M1) | Selesai |
| **W2** | 5 – 11 Okt | Audit dataset | Audit lima kelas, jumlah gambar, lisensi Open Images, bounding box, occlusion (M2) | Selesai |
| **W3** | 12 – 18 Okt | Kejar jadwal + web awal | Repo GitHub, FastAPI skeleton, kontrak JSON, tracker, rancangan database (ERD), mulai kurasi | Selesai |
| **W4** | 19 – 25 Okt | Dataset + baseline | Verifikasi duplikasi, split train/val/test, YOLO11n pretrained baseline, UI web awal, mock API (M3) | Selesai |
| **W5** | 26 Okt – 1 Nov | Fine-tuning + web | Training pertama dan fine-tuning, kamera/galeri, integrasi FastAPI nyata, uji awal (pilot) 205 foto | Selesai* |
| **W6** | 2 – 8 Nov | Kandidat model + web | Refine hyperparameter, latih ulang dengan optimizer eksplisit, uji ulang 500 foto (250 ada satwa + 250 tanpa satwa), overlay dan lencana (M4) | Berjalan |
| **W7** | 9 – 15 Nov | Evaluasi + FastAPI | Metrik per kelas dan kondisi visual, FP/FN, confusion matrix, waktu inference | Rencana |
| **W8** | 16 – 22 Nov | Model dan web selesai | Bandingkan baseline dan fine-tuned, pilih model final, fitur web MVP selesai (M5, M6) | Rencana |
| **W9** | 23 – 29 Nov | Integrasi + testing | Alur end-to-end: deteksi → factsheet → lencana; integration test dan defect log (M7) | Rencana |
| **W10** | 30 Nov – 6 Des | System dan user testing | Acceptance testing, user testing, perbaikan prioritas (M8) | Rencana |
| **W11** | 7 – 13 Des | Revisi + dokumentasi | Release candidate, dokumentasi teknis dan pengujian, dataset card, bahan presentasi | Rencana |
| **W12** | 14 – 20 Des | Penyerahan | Laporan akhir, demo, serah terima dataset, model, dan evaluasi (M9, M10) | Rencana |

*\* Satu butir W5 (perbaikan data kelas minoritas, Joseph) masih berjalan. M = milestone pada Project Management Plan.*

---

## 3. Pembagian Tugas, Kendala, Solusi, dan Hasil (W1–W5)

| Tahap Roadmap | PIC | Kendala | Solusi | Hasil | Lampiran |
|---|---|---|---|---|---|
| **Perencanaan (W1–W3)** | Ezra, Aldo | Proyek terlambat; teguran dosen 13 Okt | Tracker 7 tab, jobdesc, target mingguan; W1–W3 dikejar paralel | W1–W4 selesai 100%; GitHub, kontrak API, notulen, dan work log berjalan | Lampiran F |
| **Audit dan kurasi dataset (W2–W4)** | Joseph, Bryan | Hanya 55% gambar berlabel; kelas timpang 5,5 : 1; kebocoran antar split (218 nama dasar) | Audit otomatis, pemulihan label, split dibuat ulang | Audit 4.703 gambar; ZooLens_final: 2.076 / 261 / 259 tanpa berkas identik lintas split | Lampiran D |
| **Baseline dan fine-tuning (W4–W5)** | Bryan | Training awal memakai dataset yang salah; lr0 diabaikan karena optimizer=auto (AdamW) | Training ulang di ZooLens_final; masalah lr0 dicatat, latih ulang diusulkan W6 | EXP-02 mAP50 0,932; fine-tuning mAP50 0,940 (+0,8 poin), precision 92,4% | Lampiran D |
| **Pengembangan web (W3–W5)** | Ivy, Felix | Hasil AI belum tersedia: respons masih mock dan gambar belum tersimpan | Mock API dengan kontrak JSON; backend dan UI dikerjakan di branch terpisah lalu digabung | Scanner kamera/galeri, overlay, factsheet, Safari, Riwayat; 4 tabel database, seeder, validasi upload | Lampiran A, B, C |
| **Integrasi FastAPI (W5)** | Ezra, Felix, Aldo | Error 503 karena bobot model belum terpasang; respons mock | Pasang bobot, atur MODEL_PATH, tulis API Contract, uji endpoint | /predict aktif; scanner memakai API nyata sejak 26 Okt; pytest lulus | Lampiran A |
| **Evaluasi dan QA (W5)** | Ezra, Joseph, Aldo, anggota | Occlusion gagal pada beberapa foto (masukan dosen 27 Okt); prosedur uji awal keliru: 205 foto semuanya berisi satwa, tanpa foto tanpa satwa; 23 foto identik dengan data training | Uji batch 205 foto dijadikan pilot; prosedur dikoreksi (500 foto: 250 ada satwa + 250 tanpa satwa), uji ulang W6–W7; 23 foto identik dikeluarkan | Pilot: 89,0% (162 dari 182) hanya gambaran awal mengenali satwa, bukan evaluasi model; kegagalan terbanyak badak di rumput tinggi; hipotesa dirumuskan ulang | Lampiran E |
| **Dokumentasi (W1–W5)** | Aldo | Versi dataset dan data tersebar di beberapa sumber | Dokumentasi konfigurasi eksperimen; acuan tunggal ZooLens_final | Laporan progres 27 Okt, dokumentasi eksperimen, tindak lanjut, kerangka analisis awal | Lampiran F |

---

## Tautan Bukti

- **Work Log dan Tracker:** `https://docs.google.com/spreadsheets/d/1ZZ2fI-xgkqlMaMXok7dOx1i3z-SW8-XtafZKULGOBfg`
- **Kode (Laravel, FastAPI):** `https://github.com/ezradesmonds/ZooLens`
- **Drive Milestone 1 (dataset, notebook, hasil uji, dokumen, screenshot):** `https://drive.google.com/drive/folders/1to97S6C5I_RDt_AVhHivXK3JSBf1gOvy`
