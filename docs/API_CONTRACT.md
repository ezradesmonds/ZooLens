# ZooLens API Contract

Dokumen kontrak resmi antarmuka data (API Contract) antara **Laravel Backend** dan **FastAPI AI Service (YOLO11n Inference)** pada proyek ZooLens (Kelompok 10).

---

## 1. Arsitektur Komunikasi

```
[ Frontend (Blade + JS) ]
           │
           │ (1) POST /scan (multipart image, maks 2 MB)
           ▼
[ Laravel Backend ] ──(2) POST /predict (multipart file)──► [ FastAPI Service ]
                    ◄──(3) JSON detections (class_id, bbox)─┤ (YOLO11n Model)
           │
           ├─ (4) Lookup tabel 'animals' via FactsheetService
           ├─ (5) Cek badge & update riwayat (user_animals, detections)
           │
           ▼ (6) Return JSON hasil deteksi + factsheet + progress koleksi
[ Frontend (Blade UI / Scanner Overlay) ]
```

* **Service AI Endpoint:** Ditentukan lewat environment variable `AI_SERVICE_URL` di `backend/.env` (default: `http://127.0.0.1:8001`).
* **Format Koordinat Bounding Box:** `[x1, y1, x2, y2]` piksel absolut terhadap dimensi asli gambar (`image_width`, `image_height`).

---

## 2. Kelas Satwa Terpadu (Unified Class Mapping)

Model inferensi dan database backend menyepakati pemetaan `class_id` numerik (0–4) sebagai berikut:

| Class ID | Nama Label (English) | Nama Satwa (Indonesia) | Status di Baseline COCO |
| :---: | :--- | :--- | :--- |
| `0` | `elephant` | Gajah | Pretrained (COCO ID: 20) |
| `1` | `giraffe` | Jerapah | Pretrained (COCO ID: 23) |
| `2` | `zebra` | Zebra | Pretrained (COCO ID: 22) |
| `3` | `tiger` | Harimau | Custom Fine-tune |
| `4` | `rhinoceros` | Badak | Custom Fine-tune |

---

## 3. Spesifikasi Endpoint FastAPI (`ai-service`)

### 3.1. Health Check
* **Method:** `GET`
* **Path:** `/health`
* **Deskripsi:** Memeriksa kesiapan layanan AI dan ketersediaan bobot model YOLO.

**Response (HTTP 200 OK):**
```json
{
  "status": "ok",
  "service": "zoolens-ai",
  "model_configured": true,
  "model_path": "yolo11n.pt"
}
```

---

### 3.2. Inference Predict
* **Method:** `POST`
* **Path:** `/predict`
* **Content-Type:** `multipart/form-data`

**Request Body:**
* `file`: Binary file gambar (MIME: `image/jpeg`, `image/png`, `image/webp`). Maksimal 10 MB.

**Response Sukses (HTTP 200 OK):**
```json
{
  "image_width": 1280,
  "image_height": 960,
  "detections": [
    {
      "class_id": 0,
      "class_name": "elephant",
      "confidence": 0.9245,
      "bbox": [120.5, 80.0, 640.2, 720.8]
    }
  ]
}
```

*Catatan: Jika tidak ada satwa yang terdeteksi, `detections` mengembalikan array kosong `[]`.*

**Error Responses:**
* `400 Bad Request`: File gambar korup atau tidak dapat dibaca (`{"detail": "Invalid image"}`).
* `413 Payload Too Large`: Ukuran file melebihi batas 10 MB (`{"detail": "Image exceeds 10 MB"}`).
* `415 Unsupported Media Type`: Format bukan JPEG, PNG, atau WEBP (`{"detail": "JPEG, PNG, or WEBP required"}`).
* `503 Service Unavailable`: File weights model belum dipasang (`{"detail": "Model not installed. Set MODEL_PATH to YOLO weights."}`).

---

## 4. Spesifikasi Endpoint Laravel (`backend`)

### 4.1. Scan & Factsheet Resolution
* **Method:** `POST`
* **Path:** `/scan`
* **Headers:** `X-CSRF-TOKEN` (wajib untuk form web), `Accept: application/json`
* **Content-Type:** `multipart/form-data`

**Request Body:**
* `image`: File gambar kamera/galeri (jpg, jpeg, png, webp). Maksimal 2048 KB (2 MB).

**Response Sukses (HTTP 200 OK):**
```json
{
  "status": "success",
  "image": {
    "width": 1280,
    "height": 960
  },
  "detections": [
    {
      "class_id": 0,
      "confidence": 0.9245,
      "bbox": [120.5, 80.0, 640.2, 720.8],
      "animal": {
        "id": 1,
        "common_name": "Elephant",
        "scientific_name": "Elephas maximus",
        "habitat": "Hutan tropis dan sabana",
        "diet": "Herbivora",
        "iucn_status": "Endangered"
      },
      "is_new_discovery": true,
      "badge": {
        "name": "Lencana Gajah",
        "description": "Berhasil menemukan Gajah.",
        "icon": "badges/elephant.svg"
      }
    }
  ],
  "progress": {
    "collected": 1,
    "total": 5,
    "percentage": 20.0
  }
}
```

**Response Tidak Ada Satwa / Unknown (HTTP 200 OK):**
```json
{
  "status": "error",
  "code": "unknown_class",
  "message": "Satwa tidak dikenali."
}
```

**Response Validasi Gagal (HTTP 422 Unprocessable Entity):**
```json
{
  "message": "Gambar tidak valid atau ukuran melebihi 2 MB.",
  "errors": {
    "image": [
      "File harus berupa gambar (jpeg, png, webp).",
      "Ukuran gambar maksimal 2048 KB."
    ]
  }
}
```
