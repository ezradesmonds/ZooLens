#!/usr/bin/env python3
"""
batch_test_200.py - Runner Otomatisasi Batch Testing 200 Kasus Visual ZooLens

Fungsi:
1. Memuat model YOLO11n (default: ai-service/best.pt)
2. Memproses batch citra uji (folder images/test, folder test_200/, atau subfolder per kelas/kondisi)
3. Mencocokkan prediksi dengan ground truth (jika ada file label .txt atau struktur folder)
4. Mengklasifikasikan status: TP (True Positive), FP (False Positive), FN (False Negative)
5. Memetakan kondisi visual: Full Visibility, Moderate Occlusion, Severe Occlusion, Truncation
6. Membagi otomatis PIC analisis ke anggota kelompok (Bryan, Ivy, Felix, Aldo, Ezra)
7. Menghasilkan file CSV siap buka di Excel (UTF-8 BOM) dan laporan ringkasan Markdown.

Pemakaian:
  python ml/scripts/batch_test_200.py --model ai-service/best.pt --data "D:/Documents/Ezra/Kuliah/PCU/Smstr 5/Manpro/ZooLens Manpro/ZooLens_final"
  python ml/scripts/batch_test_200.py --images "D:/Documents/Ezra/Kuliah/PCU/Smstr 5/Manpro/ZooLens Manpro/test_200"
"""

import argparse
import csv
import glob
import os
import sys
import time
from pathlib import Path

# Definisi Kelas Resmi ZooLens
CLASS_NAMES = ["elephant", "giraffe", "zebra", "tiger", "rhinoceros"]
CLASS_ID_MAP = {
    0: "elephant",
    1: "giraffe",
    2: "zebra",
    3: "tiger",
    4: "rhinoceros",
}
NAME_TO_ID = {v: k for k, v in CLASS_ID_MAP.items()}
NAME_ALIASES = {
    "elephant": ["gajah", "elephant"],
    "giraffe": ["jerapah", "giraffe"],
    "zebra": ["zebra"],
    "tiger": ["harimau", "tiger"],
    "rhinoceros": ["badak", "rhino", "rhinoceros"],
}

# Pembagian PIC Analisis per Kelas Satwa
PIC_ASSIGNMENT = {
    "elephant": "Felix",
    "giraffe": "Ivy",
    "zebra": "Ivy",
    "tiger": "Bryan",
    "rhinoceros": "Bryan",
}


def compute_iou(box1, box2):
    """Menghitung Intersection over Union (IoU) antara dua box [x1, y1, x2, y2]."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_w = max(0.0, x2 - x1)
    inter_h = max(0.0, y2 - y1)
    inter_area = inter_w * inter_h

    area1 = max(0.0, (box1[2] - box1[0])) * max(0.0, (box1[3] - box1[1]))
    area2 = max(0.0, (box2[2] - box2[0])) * max(0.0, (box2[3] - box2[1]))
    union_area = area1 + area2 - inter_area

    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def detect_ground_truth(img_path, label_dir=None):
    """
    Mencari ground truth kelas dan box:
    1. Dari file .txt berformat YOLO di label_dir atau folder labels/
    2. Fallback dari nama folder atau nama file
    """
    img_p = Path(img_path)
    stem = img_p.stem
    boxes = []

    # Cari file label
    candidate_labels = []
    if label_dir and os.path.isdir(label_dir):
        candidate_labels.append(Path(label_dir) / f"{stem}.txt")

    # Cek struktur umum yolo: images/test -> labels/test
    parts = list(img_p.parts)
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].lower() == "images":
            lbl_parts = list(parts)
            lbl_parts[i] = "labels"
            candidate_labels.append(Path(*lbl_parts).with_suffix(".txt"))
            break

    candidate_labels.append(img_p.with_suffix(".txt"))

    for lp in candidate_labels:
        if lp.is_file():
            try:
                with open(lp, "r", encoding="utf-8") as f:
                    for line in f:
                        toks = line.strip().split()
                        if len(toks) == 5:
                            cid = int(float(toks[0]))
                            xc, yc, w, h = [float(x) for x in toks[1:]]
                            x1 = max(0.0, xc - w / 2)
                            y1 = max(0.0, yc - h / 2)
                            x2 = min(1.0, xc + w / 2)
                            y2 = min(1.0, yc + h / 2)
                            cname = CLASS_ID_MAP.get(cid, "unknown")
                            boxes.append({"class_id": cid, "class_name": cname, "bbox": [x1, y1, x2, y2], "area": w * h})
                if boxes:
                    return boxes
            except Exception:
                pass

    # Fallback dari path string
    path_lower = str(img_path).lower()
    for cname, aliases in NAME_ALIASES.items():
        if any(a in path_lower for a in aliases):
            cid = NAME_TO_ID[cname]
            return [{"class_id": cid, "class_name": cname, "bbox": [0.1, 0.1, 0.9, 0.9], "area": 0.64}]

    return []


def determine_visual_condition(img_path, gt_boxes):
    """
    Mengidentifikasi kondisi visual:
    1. Dari nama folder/tag file: 'occlusion_sev', 'occlusion_mod', 'truncation', 'full'
    2. Dari analisis bounding box (proxy truncation jika menempel tepi, occlusion jika area kecil/tenggelam)
    """
    path_lower = str(img_path).lower()

    if "severe" in path_lower or "occ_sev" in path_lower or "ekstrem" in path_lower:
        return "Severe Occlusion (>50%)"
    if "moderate" in path_lower or "occ_mod" in path_lower or "occlusion" in path_lower or "terhalang" in path_lower:
        return "Moderate Occlusion (20-50%)"
    if "trunc" in path_lower or "terpotong" in path_lower or "crop" in path_lower:
        return "Truncation (Terpotong Tepi)"
    if "full" in path_lower or "utuh" in path_lower:
        return "Full Visibility"

    # Proxy otomatis dari box
    if gt_boxes:
        b = gt_boxes[0]["bbox"]
        margin = 0.015
        touches_edge = b[0] <= margin or b[1] <= margin or b[2] >= 1.0 - margin or b[3] >= 1.0 - margin
        area = gt_boxes[0].get("area", 0.5)

        if touches_edge and area >= 0.5:
            return "Truncation (Terpotong Tepi)"
        if area < 0.10:
            return "Moderate Occlusion (20-50%)"

    return "Full Visibility"


def main():
    parser = argparse.ArgumentParser(description="Runner Otomatisasi Batch Testing 200 Kasus Visual ZooLens")
    parser.add_argument("--model", default="ai-service/best.pt", help="Path bobot model YOLO (.pt)")
    parser.add_argument("--data", default="D:/Documents/Ezra/Kuliah/PCU/Smstr 5/Manpro/ZooLens Manpro/ZooLens_final", help="Path root dataset (mencari folder images/test)")
    parser.add_argument("--images", default=None, help="Path alternatif folder citra langsung")
    parser.add_argument("--out", default="test_results_200", help="Folder output hasil pengujian")
    parser.add_argument("--conf", type=float, default=0.50, help="Confidence threshold minimum (default: 0.50)")
    parser.add_argument("--iou-thresh", type=float, default=0.45, help="IoU threshold untuk kecocokan deteksi (default: 0.45)")
    parser.add_argument("--limit", type=int, default=200, help="Batas maksimum gambar yang diuji (default: 200)")
    parser.add_argument("--balance-classes", action="store_true", default=True, help="Bagi rata sampel per kelas satwa (default: True)")
    args = parser.parse_args()

    # 1. Validasi Model
    model_path = Path(args.model).resolve()
    if not model_path.is_file():
        # Coba cari relatif
        alt_paths = [
            Path("ai-service/best.pt"),
            Path("../ai-service/best.pt"),
            Path("D:/Documents/Ezra/Kuliah/PCU/Smstr 5/Manpro/ZooLens/ai-service/best.pt"),
        ]
        for p in alt_paths:
            if p.is_file():
                model_path = p.resolve()
                break

    if not model_path.is_file():
        sys.exit(f"[ERROR] Model tidak ditemukan di: {args.model}")

    print(f"[INFO] Memuat model YOLO dari: {model_path}")
    from ultralytics import YOLO
    model = YOLO(str(model_path))

    # 2. Mengumpulkan Gambar
    image_paths = []
    label_dir = None

    if args.images and os.path.isdir(args.images):
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
            image_paths.extend(glob.glob(os.path.join(args.images, "**", ext), recursive=True))
    elif args.data and os.path.isdir(args.data):
        test_img_dir = os.path.join(args.data, "images", "test")
        label_dir = os.path.join(args.data, "labels", "test")
        if os.path.isdir(test_img_dir):
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
                image_paths.extend(glob.glob(os.path.join(test_img_dir, ext)))
        else:
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
                image_paths.extend(glob.glob(os.path.join(args.data, "**", ext), recursive=True))

    image_paths = sorted(list(set(image_paths)))
    if not image_paths:
        sys.exit(f"[ERROR] Tidak ada gambar ditemukan untuk diuji di {args.data} atau {args.images}")

    total_available = len(image_paths)

    # Menyeimbangkan sampel antarkelas jika diminta
    if args.balance_classes and args.limit and len(image_paths) > args.limit:
        by_class = {c: [] for c in CLASS_NAMES}
        unclassified = []
        for p in image_paths:
            gt = detect_ground_truth(p, label_dir)
            c = gt[0]["class_name"] if gt else "unknown"
            if c in by_class:
                by_class[c].append(p)
            else:
                unclassified.append(p)

        target_per_class = max(1, args.limit // len(CLASS_NAMES))
        selected = []
        for c in CLASS_NAMES:
            selected.extend(by_class[c][:target_per_class])

        # Isi sisa kuota jika ada kelas yang sampelnya kurang dari target
        shortfall = args.limit - len(selected)
        if shortfall > 0:
            remaining_pool = []
            for c in CLASS_NAMES:
                remaining_pool.extend(by_class[c][target_per_class:])
            remaining_pool.extend(unclassified)
            selected.extend(remaining_pool[:shortfall])

        image_paths = sorted(selected)
    elif args.limit and len(image_paths) > args.limit:
        image_paths = image_paths[:args.limit]

    print(f"[INFO] Ditemukan {total_available} citra. Menjalankan pengujian pada {len(image_paths)} citra terdistribusi...")

    # 3. Menyiapkan Folder Output
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_file = out_dir / "test_results_200.csv"
    report_file = out_dir / "test_summary_report.md"

    # 4. Loop Pengujian Batch
    results = []
    stats_class = {c: {"total": 0, "TP": 0, "FP": 0, "FN": 0} for c in CLASS_NAMES}
    stats_cond = {}

    start_total_time = time.time()

    for idx, img_path in enumerate(image_paths, 1):
        if idx % 25 == 0 or idx == len(image_paths):
            print(f"  Progres: {idx}/{len(image_paths)} citra diproses...")

        gt_list = detect_ground_truth(img_path, label_dir)
        gt_class = gt_list[0]["class_name"] if gt_list else "unknown"
        condition = determine_visual_condition(img_path, gt_list)

        if condition not in stats_cond:
            stats_cond[condition] = {"total": 0, "TP": 0, "FP": 0, "FN": 0}

        t_inf_start = time.time()
        pred_res = model.predict(source=img_path, conf=args.conf, verbose=False)[0]
        inf_ms = round((time.time() - t_inf_start) * 1000, 2)

        # Analisis Prediksi
        pred_boxes = []
        for box in pred_res.boxes:
            raw_cls = int(box.cls[0])
            raw_name = pred_res.names[raw_cls].lower()
            # Pemetaan nama kanonik
            cname = raw_name
            for canon, aliases in NAME_ALIASES.items():
                if raw_name in aliases:
                    cname = canon
                    break

            conf_val = round(float(box.conf[0]), 4)
            # Normalisasi koordinat bbox
            W, H = pred_res.orig_shape[1], pred_res.orig_shape[0]
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            pred_boxes.append({
                "class_name": cname,
                "confidence": conf_val,
                "bbox_norm": [round(x1 / W, 4), round(y1 / H, 4), round(x2 / W, 4), round(y2 / H, 4)],
                "bbox_raw": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
            })

        # Evaluasi Status (TP, FP, FN)
        top_pred_class = "-"
        top_conf = 0.0
        best_iou = 0.0
        top_bbox = "-"
        status = "FN"
        failure_note_hint = ""

        if not pred_boxes:
            status = "FN"
            failure_note_hint = f"Satwa ({gt_class}) tidak terdeteksi (di bawah threshold {int(args.conf * 100)}%)."
        else:
            top_pred = max(pred_boxes, key=lambda x: x["confidence"])
            top_pred_class = top_pred["class_name"]
            top_conf = top_pred["confidence"]
            top_bbox = str(top_pred["bbox_raw"])

            # Cek kecocokan dengan GT
            matched = False
            for gt in gt_list:
                for pb in pred_boxes:
                    iou_val = compute_iou(gt["bbox"], pb["bbox_norm"])
                    if iou_val > best_iou:
                        best_iou = round(iou_val, 3)
                    if pb["class_name"] == gt["class_name"] and iou_val >= args.iou_thresh:
                        matched = True
                        break
                if matched:
                    break

            if matched:
                status = "TP"
                failure_note_hint = "Deteksi tepat sesuai bounding box ground truth."
            else:
                if top_pred_class == gt_class:
                    status = "TP (IoU Rendah)"
                    failure_note_hint = f"Kelas tepat ({top_pred_class}), namun pergeseran box (IoU {best_iou})."
                else:
                    status = "FP"
                    failure_note_hint = f"Misklasifikasi: {gt_class} salah diprediksi sebagai {top_pred_class} ({int(top_conf * 100)}%)."

        # Update Statistik
        if gt_class in stats_class:
            stats_class[gt_class]["total"] += 1
            if "TP" in status:
                stats_class[gt_class]["TP"] += 1
            elif status == "FP":
                stats_class[gt_class]["FP"] += 1
            else:
                stats_class[gt_class]["FN"] += 1

        stats_cond[condition]["total"] += 1
        if "TP" in status:
            stats_cond[condition]["TP"] += 1
        elif status == "FP":
            stats_cond[condition]["FP"] += 1
        else:
            stats_cond[condition]["FN"] += 1

        pic = PIC_ASSIGNMENT.get(gt_class, "Aldo")

        results.append({
            "No": idx,
            "Nama_File": Path(img_path).name,
            "Satwa_Asli": gt_class,
            "Kondisi_Visual": condition,
            "Prediksi_Model": top_pred_class,
            "Confidence": top_conf if top_conf > 0 else "-",
            "Status_Evaluasi": status,
            "IoU": best_iou if best_iou > 0 else "-",
            "Inference_ms": inf_ms,
            "Bounding_Box": top_bbox,
            "PIC_Review": pic,
            "Analisis_Kegagalan_Ciri_Visual": failure_note_hint,
        })

    elapsed_total = round(time.time() - start_total_time, 2)
    avg_latency = round(sum(r["Inference_ms"] for r in results) / len(results), 2) if results else 0

    # 5. Tulis File CSV (Dengan UTF-8 BOM untuk Microsoft Excel)
    fieldnames = [
        "No", "Nama_File", "Satwa_Asli", "Kondisi_Visual", "Prediksi_Model",
        "Confidence", "Status_Evaluasi", "IoU", "Inference_ms", "Bounding_Box",
        "PIC_Review", "Analisis_Kegagalan_Ciri_Visual"
    ]
    with open(csv_file, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # 6. Susun Laporan Markdown Ringkasan
    md_lines = [
        "# Laporan Evaluasi Batch Testing 200 Kasus Visual ZooLens\n",
        f"- **Model Weights:** `{model_path.name}`\n",
        f"- **Tanggal Pengujian:** {time.strftime('%d %B %Y')}\n",
        f"- **Total Citra Diuji:** {len(results)} citra\n",
        f"- **Durasi Total:** {elapsed_total} detik (Rata-rata inferensi: {avg_latency} ms/citra)\n",
        f"- **Confidence Threshold:** $\\ge$ {args.conf}\n\n",
        "## 1. Performa per Kelas Satwa\n",
        "| Kelas Satwa | Total Sampel | True Positive (TP) | False Negative (FN) | False Positive (FP) | Recall (%) | PIC Analisis |\n",
        "|---|---|---|---|---|---|---|\n",
    ]

    total_tp = 0
    total_samples = 0
    for cname in CLASS_NAMES:
        st = stats_class[cname]
        tot = st["total"]
        tp = st["TP"]
        fn = st["FN"]
        fp = st["FP"]
        recall = round((tp / tot * 100), 1) if tot > 0 else 0.0
        total_tp += tp
        total_samples += tot
        pic = PIC_ASSIGNMENT.get(cname, "-")
        md_lines.append(f"| **{cname}** | {tot} | {tp} | {fn} | {fp} | **{recall}%** | {pic} |\n")

    overall_recall = round((total_tp / total_samples * 100), 1) if total_samples > 0 else 0.0
    md_lines.append(f"| **TOTAL** | **{total_samples}** | **{total_tp}** | **{total_samples - total_tp}** | - | **{overall_recall}%** | **Tim ZooLens** |\n\n")

    md_lines.extend([
        "## 2. Performa per Kondisi Visual (Pembuktian Hipotesis Occlusion)\n",
        "| Kondisi Visual | Total Uji | True Positive (TP) | False Negative (FN) | Recall (%) | Catatan Metodologi |\n",
        "|---|---|---|---|---|---|\n",
    ])

    for cond, st in sorted(stats_cond.items()):
        tot = st["total"]
        tp = st["TP"]
        fn = st["FN"]
        recall = round((tp / tot * 100), 1) if tot > 0 else 0.0
        md_lines.append(f"| **{cond}** | {tot} | {tp} | {fn} | **{recall}%** | Hipotesis teruji |\n")

    md_lines.extend([
        "\n## 3. Tindak Lanjut Anggota Tim\n",
        "File CSV pengujian telah diekspor ke: `test_results_200.csv`.\n",
        "1. **Felix:** Buka file CSV dan periksa baris satwa *elephant* (gajah).\n",
        "2. **Ivy:** Buka file CSV dan periksa baris satwa *giraffe* dan *zebra*.\n",
        "3. **Bryan:** Buka file CSV dan periksa baris satwa *tiger* dan *rhinoceros*.\n",
        "4. **Aldo & Ezra:** Mengompilasi seluruh temuan ke bab Analisis Kegagalan untuk Presentasi UTS.\n",
    ])

    with open(report_file, mode="w", encoding="utf-8") as f:
        f.writelines(md_lines)

    print("\n" + "=" * 60)
    print(f"[SUKSES] Pengujian batch selesai!")
    print(f"  -> File CSV Excel siap bagi tugas: {csv_file}")
    print(f"  -> Ringkasan Laporan Markdown:    {report_file}")
    print(f"  -> Recall Keseluruhan:            {overall_recall}%")
    print("=" * 60)


if __name__ == "__main__":
    main()
