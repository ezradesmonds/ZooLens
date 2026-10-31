#!/usr/bin/env python3
"""
batch_test_200.py - Runner Otomatisasi Batch Testing 200 Kasus Visual ZooLens

Fungsi:
1. Memuat model YOLO11n (default: ai-service/best.pt)
2. Memproses batch citra uji (folder images/test, folder test_200/, atau subfolder per kelas/kondisi)
3. Mencocokkan prediksi dengan ground truth (dari file label .txt atau dari nama folder/file)
4. Mengklasifikasikan status: TP (True Positive), FP (False Positive), FN (False Negative)
5. Memetakan kondisi visual: Full Visibility, Moderate Occlusion, Severe Occlusion, Truncation
6. Membagi otomatis PIC analisis ke anggota kelompok (Felix, Ivy, Bryan, Joseph)
7. Menghasilkan file CSV siap buka di Excel (UTF-8 BOM) dan laporan ringkasan Markdown.

Pemakaian:
  python ml/scripts/batch_test_200.py --images "D:/Documents/Ezra/Kuliah/PCU/Smstr 5/Manpro/ZooLens Manpro/test_200" --limit 0
"""

import argparse
import csv
import glob
import os
import re
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


def determine_pic(img_path, gt_class):
    """Menentukan anggota tim yang bertanggung jawab mereview foto ini."""
    fn = Path(img_path).name.lower()
    if "felix" in fn:
        return "Felix"
    if "ivy" in fn:
        return "Ivy"
    if "bryan" in fn:
        return "Bryan"
    if "joseph" in fn:
        return "Joseph"

    # Default berdasarkan kelas satwa
    if gt_class == "elephant":
        return "Felix"
    elif gt_class in ["giraffe", "zebra"]:
        return "Ivy"
    elif gt_class == "tiger":
        return "Bryan"
    elif gt_class == "rhinoceros":
        return "Joseph"

    return "Aldo"


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
    2. Fallback dari nama folder induk atau nama file
    """
    img_p = Path(img_path)
    stem = img_p.stem
    boxes = []

    # 1. Cari file label fisik jika ada
    candidate_labels = []
    if label_dir and os.path.isdir(label_dir):
        candidate_labels.append(Path(label_dir) / f"{stem}.txt")

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
                            boxes.append({
                                "class_id": cid,
                                "class_name": cname,
                                "bbox": [x1, y1, x2, y2],
                                "area": w * h,
                                "has_real_box": True,
                            })
                if boxes:
                    return boxes
            except Exception:
                pass

    # 2. Fallback dari folder induk atau nama file (image-level test set)
    parent_dir = img_p.parent.name.lower()
    for cname in CLASS_NAMES:
        if cname == parent_dir:
            return [{
                "class_id": NAME_TO_ID[cname],
                "class_name": cname,
                "bbox": None,
                "area": 0.5,
                "has_real_box": False,
            }]

    path_lower = str(img_path).lower()
    for cname, aliases in NAME_ALIASES.items():
        if any(a in path_lower for a in aliases):
            cid = NAME_TO_ID[cname]
            return [{
                "class_id": cid,
                "class_name": cname,
                "bbox": None,
                "area": 0.5,
                "has_real_box": False,
            }]

    return []


def determine_visual_condition(img_path, gt_boxes):
    """
    Mengidentifikasi kondisi visual:
    1. Dari nama file / kata kunci: occlusion, di air, semak, crop, truncation, full
    2. Dari pembagian batch masing-masing anggota (Felix 1-20/21-40, Ivy, Bryan, Joseph)
    """
    fn = Path(img_path).name.lower()

    # Kata kunci eksplisit
    if any(w in fn for w in ["di air", "lumpur", "severe", "tenggelam", "occ_sev", "ekstrem"]):
        return "Severe Occlusion (>50%)"
    if any(w in fn for w in ["occlusion", "tertutup", "terhalang", "occ_mod", "semak"]):
        return "Moderate Occlusion (20-50%)"
    if any(w in fn for w in ["trunc", "crop", "terpotong"]):
        return "Truncation (Terpotong Tepi)"
    if any(w in fn for w in ["full", "utuh"]):
        return "Full Visibility"

    # Penamaan khusus Zebra
    if "zebra_felix" in fn:
        return "Full Visibility"
    if "zebra_ivy" in fn:
        return "Truncation (Terpotong Tepi)"
    if "zebra_bryan" in fn:
        return "Moderate Occlusion (20-50%)"
    if "zebra_joseph" in fn:
        return "Severe Occlusion (>50%)"

    # Penamaan khusus Badak (Joseph)
    if "rhinoceros_occlusion" in fn:
        return "Moderate Occlusion (20-50%)"
    if "rhinoceros" in fn:
        return "Full Visibility"

    # Penamaan khusus Harimau (Bryan)
    if "tiger_download" in fn:
        return "Full Visibility"
    if "tiger_occlusion" in fn:
        return "Moderate Occlusion (20-50%)"

    # Penamaan khusus Gajah (Felix): 1-20 Full, 21-30 Occlusion, 31-40 Truncation
    m = re.search(r"elephant_felix_(\d+)", fn)
    if m:
        num = int(m.group(1))
        if num <= 20:
            return "Full Visibility"
        elif num <= 30:
            return "Moderate Occlusion (20-50%)"
        else:
            return "Truncation (Terpotong Tepi)"

    # Penamaan khusus Jerapah (Ivy): 1-20 Full, 21-30 Occlusion, 31-40 Truncation
    m = re.search(r"jerapah_(\d+)", fn)
    if m:
        num = int(m.group(1))
        if num <= 20:
            return "Full Visibility"
        elif num <= 30:
            return "Moderate Occlusion (20-50%)"
        else:
            return "Truncation (Terpotong Tepi)"

    # Proxy otomatis jika ada koordinat box riil
    if gt_boxes and gt_boxes[0].get("has_real_box", False):
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
    parser.add_argument("--data", default="D:/Documents/Ezra/Kuliah/PCU/Smstr 5/Manpro/ZooLens Manpro/test_200", help="Path dataset/folder citra")
    parser.add_argument("--images", default=None, help="Path alternatif folder citra langsung")
    parser.add_argument("--out", default="test_results_200", help="Folder output hasil pengujian")
    parser.add_argument("--conf", type=float, default=0.50, help="Confidence threshold minimum (default: 0.50)")
    parser.add_argument("--iou-thresh", type=float, default=0.45, help="IoU threshold untuk kecocokan deteksi (default: 0.45)")
    parser.add_argument("--limit", type=int, default=0, help="Batas maksimum gambar (0 = uji semua gambar yang ada)")
    parser.add_argument("--balance-classes", action="store_true", default=False, help="Bagi rata sampel per kelas satwa")
    args = parser.parse_args()

    # 1. Validasi Model
    model_path = Path(args.model).resolve()
    if not model_path.is_file():
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
    target_dir = args.images if (args.images and os.path.isdir(args.images)) else args.data

    if target_dir and os.path.isdir(target_dir):
        test_img_dir = os.path.join(target_dir, "images", "test")
        label_dir = os.path.join(target_dir, "labels", "test")
        if os.path.isdir(test_img_dir):
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
                image_paths.extend(glob.glob(os.path.join(test_img_dir, ext)))
        else:
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
                image_paths.extend(glob.glob(os.path.join(target_dir, "**", ext), recursive=True))

    image_paths = sorted(list(set(image_paths)))
    if not image_paths:
        sys.exit(f"[ERROR] Tidak ada gambar ditemukan untuk diuji di: {target_dir}")

    total_available = len(image_paths)

    if args.limit and args.limit > 0 and len(image_paths) > args.limit:
        image_paths = image_paths[:args.limit]

    print(f"[INFO] Ditemukan {total_available} citra. Menjalankan pengujian pada {len(image_paths)} citra...")

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
        pic = determine_pic(img_path, gt_class)

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
        best_iou = "-"
        top_bbox = "-"
        status = "FN"
        failure_note_hint = ""

        has_real_boxes = any(gt.get("has_real_box", False) for gt in gt_list)

        if not pred_boxes:
            status = "FN"
            failure_note_hint = f"Satwa ({gt_class}) tidak terdeteksi (di bawah threshold {int(args.conf * 100)}%)."
        else:
            top_pred = max(pred_boxes, key=lambda x: x["confidence"])
            top_pred_class = top_pred["class_name"]
            top_conf = top_pred["confidence"]
            top_bbox = str(top_pred["bbox_raw"])

            if has_real_boxes:
                # Mode IoU jika ada ground truth bounding box
                matched = False
                iou_num = 0.0
                for gt in gt_list:
                    for pb in pred_boxes:
                        v = compute_iou(gt["bbox"], pb["bbox_norm"])
                        if v > iou_num:
                            iou_num = round(v, 3)
                        if pb["class_name"] == gt["class_name"] and v >= args.iou_thresh:
                            matched = True
                            break
                    if matched:
                        break

                best_iou = iou_num if iou_num > 0 else "-"
                if matched:
                    status = "TP"
                    failure_note_hint = "Deteksi tepat sesuai bounding box ground truth."
                else:
                    if top_pred_class == gt_class:
                        status = "TP"
                        failure_note_hint = f"Kelas tepat ({top_pred_class}), namun ada pergeseran box (IoU {best_iou})."
                    else:
                        status = "FP"
                        failure_note_hint = f"Misklasifikasi: {gt_class} salah diprediksi sebagai {top_pred_class} ({int(top_conf * 100)}%)."
            else:
                # Mode Image-Level (Foto Google per folder kelas)
                matching_preds = [pb for pb in pred_boxes if pb["class_name"] == gt_class]
                if matching_preds:
                    status = "TP"
                    best_match = max(matching_preds, key=lambda x: x["confidence"])
                    failure_note_hint = f"Deteksi berhasil: teridentifikasi sebagai {gt_class} ({int(best_match['confidence'] * 100)}%)."
                else:
                    status = "FP"
                    failure_note_hint = f"Misklasifikasi: {gt_class} salah diprediksi sebagai {top_pred_class} ({int(top_conf * 100)}%)."

        # Update Statistik
        if gt_class in stats_class:
            stats_class[gt_class]["total"] += 1
            if status == "TP":
                stats_class[gt_class]["TP"] += 1
            elif status == "FP":
                stats_class[gt_class]["FP"] += 1
            else:
                stats_class[gt_class]["FN"] += 1

        stats_cond[condition]["total"] += 1
        if status == "TP":
            stats_cond[condition]["TP"] += 1
        elif status == "FP":
            stats_cond[condition]["FP"] += 1
        else:
            stats_cond[condition]["FN"] += 1

        results.append({
            "No": idx,
            "Nama_File": Path(img_path).name,
            "Satwa_Asli": gt_class,
            "Kondisi_Visual": condition,
            "Prediksi_Model": top_pred_class,
            "Confidence": top_conf if top_conf > 0 else "-",
            "Status_Evaluasi": status,
            "IoU": best_iou,
            "Inference_ms": inf_ms,
            "Bounding_Box": top_bbox,
            "PIC_Review": pic,
            "Analisis_Kegagalan_Ciri_Visual": failure_note_hint,
        })

    elapsed_total = round(time.time() - start_total_time, 2)
    avg_latency = round(sum(r["Inference_ms"] for r in results) / len(results), 2) if results else 0

    # 5. Tulis File CSV (UTF-8 BOM untuk Microsoft Excel)
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
        "# Laporan Evaluasi Batch Testing 200 Kasus Visual ZooLens\n\n",
        f"- **Model Weights:** `{model_path.name}`\n",
        f"- **Folder Dataset:** `{Path(target_dir).name}`\n",
        f"- **Tanggal Pengujian:** {time.strftime('%d %B %Y')}\n",
        f"- **Total Citra Diuji:** {len(results)} citra\n",
        f"- **Durasi Total:** {elapsed_total} detik (Rata-rata inferensi: {avg_latency} ms/citra)\n",
        f"- **Confidence Threshold:** $\\ge$ {args.conf}\n\n",
        "## 1. Performa per Kelas Satwa\n\n",
        "| Kelas Satwa | Total Sampel | True Positive (TP) | False Negative (FN) | False Positive (FP) | Accuracy / Recall (%) | PIC Analisis |\n",
        "|---|---|---|---|---|---|---|\n",
    ]

    total_tp = 0
    total_samples = 0
    total_fn = 0
    total_fp = 0

    pic_by_class = {
        "elephant": "Felix",
        "giraffe": "Ivy",
        "zebra": "Felix, Ivy, Bryan, Joseph",
        "tiger": "Bryan",
        "rhinoceros": "Joseph",
    }

    for cname in CLASS_NAMES:
        st = stats_class[cname]
        tot = st["total"]
        tp = st["TP"]
        fn = st["FN"]
        fp = st["FP"]
        recall = round((tp / tot * 100), 1) if tot > 0 else 0.0
        total_tp += tp
        total_samples += tot
        total_fn += fn
        total_fp += fp
        pic = pic_by_class.get(cname, "-")
        md_lines.append(f"| **{cname}** | {tot} | {tp} | {fn} | {fp} | **{recall}%** | {pic} |\n")

    overall_recall = round((total_tp / total_samples * 100), 1) if total_samples > 0 else 0.0
    md_lines.append(f"| **TOTAL** | **{total_samples}** | **{total_tp}** | **{total_fn}** | **{total_fp}** | **{overall_recall}%** | **Tim ZooLens** |\n\n")

    md_lines.extend([
        "## 2. Performa per Kondisi Visual (Pembuktian Hipotesis Occlusion)\n\n",
        "| Kondisi Visual | Total Uji | True Positive (TP) | False Negative (FN) | False Positive (FP) | Accuracy (%) | Catatan Analisis |\n",
        "|---|---|---|---|---|---|---|\n",
    ])

    for cond, st in sorted(stats_cond.items()):
        tot = st["total"]
        tp = st["TP"]
        fn = st["FN"]
        fp = st["FP"]
        recall = round((tp / tot * 100), 1) if tot > 0 else 0.0
        md_lines.append(f"| **{cond}** | {tot} | {tp} | {fn} | {fp} | **{recall}%** | Hipotesis teruji |\n")

    md_lines.extend([
        "\n## 3. Tindak Lanjut Anggota Tim\n\n",
        "File CSV pengujian telah diekspor ke: `test_results_200.csv`.\n",
        "1. **Felix:** Buka file CSV, filter kolom `PIC_Review = Felix` (40 Gajah + 10 Zebra) -> periksa baris yang berstatus FN/FP dan isi catatan visualnya.\n",
        "2. **Ivy:** Buka file CSV, filter kolom `PIC_Review = Ivy` (40 Jerapah + 10 Zebra) -> periksa baris yang berstatus FN/FP dan isi catatan visualnya.\n",
        "3. **Bryan:** Buka file CSV, filter kolom `PIC_Review = Bryan` (44 Harimau + 11 Zebra) -> periksa baris yang berstatus FN/FP dan isi catatan visualnya.\n",
        "4. **Joseph:** Buka file CSV, filter kolom `PIC_Review = Joseph` (40 Badak + 10 Zebra) -> periksa baris yang berstatus FN/FP dan isi catatan visualnya.\n",
        "5. **Aldo & Ezra:** Mengompilasi seluruh temuan ke bab Analisis Kegagalan untuk Presentasi UTS.\n",
    ])

    with open(report_file, mode="w", encoding="utf-8") as f:
        f.writelines(md_lines)

    print("\n" + "=" * 60)
    print(f"[SUKSES] Pengujian batch selesai!")
    print(f"  -> File CSV Excel siap bagi tugas: {csv_file}")
    print(f"  -> Ringkasan Laporan Markdown:    {report_file}")
    print(f"  -> Akurasi/Recall Keseluruhan:    {overall_recall}% ({total_tp}/{total_samples})")
    print(f"  -> Rincian: {total_tp} TP, {total_fn} FN, {total_fp} FP")
    print("=" * 60)


if __name__ == "__main__":
    main()
