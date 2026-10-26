#!/usr/bin/env python3
"""
audit_yolo.py - Audit dataset YOLO untuk ZooLens (W2-W3, Joseph).

Menangani folder yang berisi BEBERAPA dataset terpisah (mis. gajah/,
jerapah/, zebra/, harimau/, dataset_badak/) yang masing-masing punya data.yaml
dan nomor kelas sendiri. Nomor kelas tiap sumber dibaca dari data.yaml terdekat,
lalu dipetakan ke lima kelas ZooLens berdasarkan NAMA kelasnya.

Yang diperiksa:
  - sumber dataset: data.yaml, lisensi dan URL dari README, jumlah gambar/box
  - gambar dan box per split x kelas, keseimbangan kelas
  - pasangan gambar-label (hilang, yatim, dan nama beda hash Roboflow '.rf.')
  - validitas label, box kecil/besar/menempel tepi (proxy truncation)
  - gambar korup, resolusi rendah
  - duplikat persis, near-duplicate (pHash), nama dasar sama lintas split
  - sampel gambar bergambar box untuk pemeriksaan visual

Tidak bisa diperiksa dari format YOLO: occlusion, group-of, depiction.

Pemakaian:
  pip install pillow numpy pandas pyyaml
  python audit_yolo.py --root "C:/Users/EUNIKE/DataSetZoo/ZooLens" --out audit_out
"""
import argparse
import hashlib
import random
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
DEFAULT_CLASSES = ["elephant", "giraffe", "zebra", "tiger", "rhinoceros"]
ALIASES = {"elephant": ["gajah"], "giraffe": ["jerapah"], "zebra": [],
           "tiger": ["harimau"], "rhinoceros": ["rhino", "badak"]}
OTHER = "lainnya"
SPLIT_ALIASES = {"train": "train", "training": "train", "val": "val",
                 "valid": "val", "validation": "val", "test": "test",
                 "testing": "test"}
SPLIT_ORDER = ["train", "val", "test", "unsplit"]
POPCOUNT = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
COLORS = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#008080"]


# ----------------------------------------------------------------- helpers
def split_of(path, root):
    for part in path.relative_to(root).parts[:-1]:
        if part.lower() in SPLIT_ALIASES:
            return SPLIT_ALIASES[part.lower()]
    return "unsplit"


def label_path_for(img_path):
    parts = list(img_path.parts)
    for i in range(len(parts) - 2, -1, -1):
        if parts[i].lower() == "images":
            parts[i] = "labels"
            return Path(*parts).with_suffix(".txt")
    return img_path.with_suffix(".txt")


def base_name(stem):
    """Nama dasar tanpa hash Roboflow: 'abc_jpg.rf.123' -> 'abc_jpg'."""
    return stem.split(".rf.")[0]


def make_dct(n=32):
    k = np.arange(n)[:, None]
    i = np.arange(n)[None, :]
    c = np.sqrt(2.0 / n) * np.cos(np.pi * (2 * i + 1) * k / (2 * n))
    c[0, :] /= np.sqrt(2)
    return c


DCT = make_dct()


def phash64(im):
    g = np.asarray(im.convert("L").resize((32, 32), Image.LANCZOS), dtype=np.float64)
    low = (DCT @ g @ DCT.T)[:8, :8].flatten()
    bits = low > np.median(low[1:])
    return int("".join("1" if b else "0" for b in bits), 2)


def iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def md_table(df, index=True):
    if df.empty:
        return "_(kosong)_\n"
    d = df.reset_index() if index else df
    cols = [str(c) for c in d.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, row in d.iterrows():
        cells = []
        for v in row:
            if isinstance(v, float):
                cells.append(f"{v:.2f}".rstrip("0").rstrip("."))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------- sumber dataset
def read_yaml_names(yp):
    try:
        import yaml
        data = yaml.safe_load(yp.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None
    names = data.get("names") if isinstance(data, dict) else None
    if isinstance(names, dict):
        try:
            return [str(names[k]) for k in sorted(names, key=int)]
        except Exception:
            return None
    if isinstance(names, list):
        return [str(n) for n in names]
    return None


class Sources:
    def __init__(self, root, classes):
        self.root, self.classes = root, classes
        self.cache = {}

    def find(self, d):
        """Cari folder sumber (yang punya yaml berisi 'names') dari direktori d ke atas."""
        chain = []
        while True:
            if d in self.cache:
                res = self.cache[d]
                break
            found = None
            for yp in sorted(d.glob("*.y*ml")):
                names = read_yaml_names(yp)
                if names:
                    found = (d, names, yp.name)
                    break
            if found:
                res = found
                break
            chain.append(d)
            if d == self.root or d.parent == d:
                res = (None, None, None)
                break
            d = d.parent
        for c in chain:
            self.cache[c] = res
        self.cache[d] = res
        return res

    def key(self, d, rel_fallback):
        sd, _, _ = self.find(d)
        if sd is None:
            return f"(tanpa yaml) {rel_fallback}"
        rel = sd.relative_to(self.root).as_posix()
        return rel if rel != "." else "(root)"

    def unify(self, src_name):
        s = src_name.lower().strip()
        for u in self.classes:
            if s == u.lower():
                return u
        for u in self.classes:
            for a in [u.lower()] + ALIASES.get(u.lower(), []):
                if a in s:
                    return u
        return None


def readme_info(src_dir, root):
    lic, url = "-", "-"
    dirs = [src_dir]
    if src_dir != root and src_dir.parent != src_dir:
        dirs.append(src_dir.parent)
    for d in dirs:
        for rp in sorted(list(d.glob("README*.txt")) + list(d.glob("README*.md"))):
            try:
                t = rp.read_text(encoding="utf-8", errors="replace")[:30000]
            except Exception:
                continue
            if lic == "-":
                m = re.search(r"(?im)^.*licen[sc]e.*$", t)
                if m:
                    lic = m.group(0).strip()[:90]
            if url == "-":
                us = re.findall(r"https?://[^\s)>\]]+", t)
                rf = [u for u in us if "roboflow" in u]
                if rf or us:
                    url = (rf or us)[0]
    return lic, url


# ----------------------------------------------------------------- parsing
def parse_label(path, src_names, src_map, classes, issues, img_key):
    boxes = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for ln, line in enumerate(text.splitlines(), 1):
        tok = line.split()
        if not tok:
            continue
        if len(tok) > 5 and (len(tok) - 1) % 2 == 0:
            issues.append(("polygon_label", img_key, f"baris {ln}: format polygon, bukan bbox"))
            continue
        if len(tok) != 5:
            issues.append(("bad_line", img_key, f"baris {ln}: {len(tok)} kolom (harus 5)"))
            continue
        try:
            cls_f = float(tok[0])
            xc, yc, w, h = (float(t) for t in tok[1:])
        except ValueError:
            issues.append(("bad_line", img_key, f"baris {ln}: nilai bukan angka"))
            continue
        if cls_f != int(cls_f) or int(cls_f) < 0 or int(cls_f) >= len(src_names):
            issues.append(("class_out_of_range", img_key, f"baris {ln}: kelas {tok[0]}"))
            continue
        if w <= 0 or h <= 0:
            issues.append(("nonpositive_size", img_key, f"baris {ln}: w={w} h={h}"))
            continue
        x1, y1, x2, y2 = xc - w / 2, yc - h / 2, xc + w / 2, yc + h / 2
        if min(x1, y1) < -1e-4 or max(x2, y2) > 1 + 1e-4:
            issues.append(("coord_out_of_range", img_key, f"baris {ln}: box keluar gambar"))
        x1, y1, x2, y2 = (min(max(v, 0.0), 1.0) for v in (x1, y1, x2, y2))
        uni = src_map.get(int(cls_f))
        boxes.append({"cls": classes.index(uni) if uni else len(classes),
                      "class_name": uni or OTHER, "src_class": src_names[int(cls_f)],
                      "x1": x1, "y1": y1, "x2": x2, "y2": y2})
    return boxes


def process_image(p):
    rec = {"ok": True, "error": "", "width": 0, "height": 0, "md5": "", "phash": 0}
    try:
        rec["md5"] = hashlib.md5(p.read_bytes()).hexdigest()
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            im.load()
            rec["width"], rec["height"] = im.size
            rec["phash"] = phash64(im)
    except Exception as e:  # noqa: BLE001
        rec["ok"] = False
        rec["error"] = f"{type(e).__name__}: {e}"
    return rec


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Audit dataset YOLO ZooLens v2")
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="audit_out")
    ap.add_argument("--classes", help="nama kelas terpadu, pisahkan koma "
                                      "(default: elephant,giraffe,zebra,tiger,rhinoceros)")
    ap.add_argument("--near-threshold", type=int, default=5)
    ap.add_argument("--small-box", type=float, default=0.005)
    ap.add_argument("--edge-margin", type=float, default=0.005)
    ap.add_argument("--low-res", type=int, default=320)
    ap.add_argument("--sample", type=int, default=30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--skip-neardup", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    if not root.is_dir():
        sys.exit(f"Folder tidak ditemukan: {root}")
    out.mkdir(parents=True, exist_ok=True)
    classes = [c.strip() for c in args.classes.split(",")] if args.classes else DEFAULT_CLASSES
    S = Sources(root, classes)

    images = sorted(p for p in root.rglob("*")
                    if p.suffix.lower() in IMG_EXT and out not in p.parents
                    and not any(x.startswith(".") for x in p.relative_to(root).parts))
    if not images:
        sys.exit("Tidak ada gambar ditemukan. Cek --root.")
    print(f"{len(images)} gambar ditemukan di {root}")

    issues, img_rows, box_rows = [], [], []
    expected_labels = set()
    src_info = {}   # key -> dict(names, map, yaml, dir)

    def source_of(d, rel):
        key = S.key(d, rel)
        if key not in src_info:
            sd, names, yml = S.find(d)
            if sd is None:
                names_, smap = list(classes), {i: c for i, c in enumerate(classes)}
                issues.append(("source_without_yaml", key,
                               "tidak ada data.yaml, nomor kelas dianggap sama dengan urutan kelas ZooLens"))
            else:
                names_ = names
                smap = {i: S.unify(n) for i, n in enumerate(names)}
                for i, n in enumerate(names):
                    if smap[i] is None:
                        issues.append(("unmapped_class_name", key,
                                       f"kelas '{n}' (ID {i}) tidak cocok dengan lima kelas ZooLens"))
            src_info[key] = {"names": names_, "map": smap, "yaml": yml or "-",
                             "dir": sd or d}
        return key

    for i, p in enumerate(images, 1):
        if i % 500 == 0:
            print(f"  diproses {i}/{len(images)}")
        rel = str(p.relative_to(root)).replace("\\", "/")
        skey = source_of(p.parent, rel.split("/")[0])
        si = src_info[skey]
        rec = process_image(p)
        rec.update({"image": rel, "split": split_of(p, root), "source": skey})
        lp = label_path_for(p)
        expected_labels.add(lp.resolve())
        boxes = []
        if not lp.exists():
            rec["label_status"] = "missing"
            issues.append(("missing_label", rel, "file label tidak ada"))
        else:
            boxes = parse_label(lp, si["names"], si["map"], classes, issues, rel)
            rec["label_status"] = "ok" if boxes else "empty"
            if not boxes and lp.stat().st_size == 0:
                issues.append(("empty_label", rel, "label kosong (background?)"))
        if not rec["ok"]:
            issues.append(("corrupt_image", rel, rec["error"]))
        elif min(rec["width"], rec["height"]) < args.low_res:
            issues.append(("low_resolution", rel, f'{rec["width"]}x{rec["height"]}'))
        for b in boxes:
            area = (b["x2"] - b["x1"]) * (b["y2"] - b["y1"])
            m = args.edge_margin
            b.update({"image": rel, "split": rec["split"], "source": skey, "area": area,
                      "tiny": area < args.small_box, "huge": area >= 0.9,
                      "touches_edge": b["x1"] <= m or b["y1"] <= m
                                      or b["x2"] >= 1 - m or b["y2"] >= 1 - m})
            if b["tiny"]:
                issues.append(("tiny_box", rel, f'{b["class_name"]} luas {area:.4f}'))
            box_rows.append(b)
        for a in range(len(boxes)):
            for c in range(a + 1, len(boxes)):
                A = (boxes[a]["x1"], boxes[a]["y1"], boxes[a]["x2"], boxes[a]["y2"])
                B = (boxes[c]["x1"], boxes[c]["y1"], boxes[c]["x2"], boxes[c]["y2"])
                v = iou(A, B)
                if boxes[a]["cls"] == boxes[c]["cls"] and v >= 0.9:
                    issues.append(("duplicate_box", rel, f'{boxes[a]["class_name"]} IoU {v:.2f}'))
                elif boxes[a]["cls"] != boxes[c]["cls"] and v >= 0.8:
                    issues.append(("overlap_diff_class", rel,
                                   f'{boxes[a]["class_name"]} vs {boxes[c]["class_name"]} IoU {v:.2f}'))
        rec["n_boxes"] = len(boxes)
        rec["classes"] = ",".join(sorted({b["class_name"] for b in boxes}))
        rec["base"] = base_name(p.stem)
        rec["has_rf"] = ".rf." in p.stem
        img_rows.append(rec)

    # label yatim
    orphans = []
    for lp in root.rglob("*.txt"):
        if out in lp.parents or lp.name.lower() in {"classes.txt", "readme.txt"} \
                or lp.name.upper().startswith("README"):
            continue
        parts = [x.lower() for x in lp.relative_to(root).parts]
        if "labels" in parts and lp.resolve() not in expected_labels:
            rel = str(lp.relative_to(root)).replace("\\", "/")
            skey = source_of(lp.parent, rel.split("/")[0])
            orphans.append({"source": skey, "label": rel, "base": base_name(lp.stem),
                            "split": split_of(lp, root)})
            issues.append(("orphan_label", rel, "label tanpa gambar"))

    idf, bdf, odf = pd.DataFrame(img_rows), pd.DataFrame(box_rows), pd.DataFrame(orphans)

    # pasangan yang hanya beda hash Roboflow
    idf["rf_mismatch"] = False
    if not odf.empty:
        ob = set(zip(odf.source, odf.split, odf.base))
        miss = idf.label_status == "missing"
        idf.loc[miss, "rf_mismatch"] = [(s, sp, b) in ob for s, sp, b in
                                        zip(idf[miss].source, idf[miss].split, idf[miss].base)]

    # nama dasar yang sama di lebih dari satu split (indikasi kebocoran)
    grp = idf.groupby(["source", "base"]).split.nunique()
    leak_keys = set(grp[grp > 1].index)
    for (s, b) in sorted(leak_keys):
        sub = idf[(idf.source == s) & (idf.base == b)]
        issues.append(("cross_split_same_base", f"{s}/{b}",
                       "split: " + ",".join(sorted(set(sub.split)))))

    # ------------------------------------------------ duplikat
    dup_rows = []
    ok = idf[idf.ok].reset_index(drop=True)
    if not args.skip_neardup and len(ok) > 1:
        if len(ok) > 30000:
            print("! >30000 gambar, near-duplicate bisa lama (--skip-neardup).")
        print("Mencari duplikat / near-duplicate ...")
        hashes = np.array([int(h) for h in ok.phash], dtype=np.uint64)
        for i in range(len(ok) - 1):
            x = hashes[i + 1:] ^ hashes[i]
            d = POPCOUNT[x.view(np.uint8).reshape(-1, 8)].sum(axis=1)
            for j in np.nonzero(d <= args.near_threshold)[0]:
                r1, r2 = ok.iloc[i], ok.iloc[i + 1 + j]
                dup_rows.append({
                    "image_a": r1.image, "split_a": r1.split,
                    "image_b": r2.image, "split_b": r2.split,
                    "hamming": int(d[j]), "exact_md5": r1.md5 == r2.md5,
                    "cross_split": r1.split != r2.split,
                    "same_base": (r1.source == r2.source and r1.base == r2.base)})
    ddf = pd.DataFrame(dup_rows)
    if not ddf.empty:
        for _, r in ddf[ddf.cross_split].iterrows():
            issues.append(("cross_split_duplicate", r.image_a,
                           f"{r.split_a} <-> {r.split_b}: {r.image_b} (d={r.hamming})"))

    # ------------------------------------------------ tabel sumber
    srows = []
    for key, si in src_info.items():
        sub = idf[idf.source == key]
        sb = bdf[bdf.source == key] if not bdf.empty else bdf
        lic, url = readme_info(si["dir"], root) if si["dir"] else ("-", "-")
        mapping = "; ".join(f"{i}:{n}->{si['map'].get(i) or OTHER}"
                            for i, n in enumerate(si["names"]))
        srows.append({
            "sumber": key, "yaml": si["yaml"], "kelas (ID:nama->terpadu)": mapping,
            "gambar": len(sub), "label_ok": int((sub.label_status == "ok").sum()),
            "label_hilang": int((sub.label_status == "missing").sum()),
            "label_kosong": int((sub.label_status == "empty").sum()),
            "label_yatim": int((odf.source == key).sum()) if not odf.empty else 0,
            "beda_hash_rf": int(sub.rf_mismatch.sum()),
            "box": len(sb), "lisensi (README)": lic, "url (README)": url})
    sdf = pd.DataFrame(srows).sort_values("sumber")

    # ------------------------------------------------ simpan CSV
    idf.drop(columns=["phash"]).to_csv(out / "images.csv", index=False)
    if not bdf.empty:
        bdf.drop(columns=["cls"]).to_csv(out / "boxes.csv", index=False)
    pd.DataFrame(issues, columns=["type", "file", "detail"]).to_csv(out / "issues.csv", index=False)
    ddf.to_csv(out / "duplicates.csv", index=False)
    sdf.to_csv(out / "sources.csv", index=False)
    if not odf.empty:
        odf.to_csv(out / "orphan_labels.csv", index=False)

    # ------------------------------------------------ ringkasan
    cols = classes + [OTHER]
    L = ["# Ringkasan Audit Dataset YOLO ZooLens (v2)\n",
         f"- Folder: `{root}`\n- Kelas terpadu: {', '.join(f'{i}={n}' for i, n in enumerate(classes))}\n"
         f"- Total gambar: {len(idf)} (korup: {int((~idf.ok).sum())})\n- Total box: {len(bdf)}\n"
         f"- Jumlah sumber dataset: {len(sdf)}\n"]
    L.append("\n## Sumber dataset\n")
    L.append("Nomor kelas dibaca dari data.yaml tiap sumber lalu dipetakan lewat NAMA kelas.\n\n")
    L.append(md_table(sdf.drop(columns=["lisensi (README)", "url (README)"]), index=False))
    L.append("\n### Lisensi dan URL (diambil otomatis dari README, verifikasi manual)\n")
    L.append(md_table(sdf[["sumber", "lisensi (README)", "url (README)"]], index=False))

    L.append("\n## Gambar per split\n")
    sp = idf.groupby("split").agg(gambar=("image", "size"), nama_dasar_unik=("base", "nunique"),
                                  bernama_rf=("has_rf", "sum"))
    sp = sp.reindex([s for s in SPLIT_ORDER if s in sp.index])
    sp["persen"] = (sp.gambar / sp.gambar.sum() * 100).round(1)
    L.append(md_table(sp))
    L.append("\n_Gambar jauh lebih banyak dari nama dasar unik = ada salinan augmentasi "
             "Roboflow (hash `.rf.` berbeda) dari gambar sumber yang sama._\n")
    L.append("\n## Status label per split\n")
    L.append(md_table(idf.groupby(["split", "label_status"]).size().unstack(fill_value=0)))
    n_rf = int(idf.rf_mismatch.sum())
    L.append(f"\nGambar tanpa label yang punya label yatim dengan nama dasar sama "
             f"(hanya beda hash `.rf.`): **{n_rf}**\n")

    if not bdf.empty:
        order = [s for s in SPLIT_ORDER if s in set(bdf.split)]
        cc = [c for c in cols if c in set(bdf.class_name)] or classes
        cc = [c for c in classes] + ([OTHER] if OTHER in set(bdf.class_name) else [])
        L.append("\n## Box per split x kelas\n")
        t = bdf.groupby(["split", "class_name"]).size().unstack(fill_value=0)
        t = t.reindex(order).reindex(columns=cc, fill_value=0)
        t.loc["TOTAL"] = t.sum()
        L.append(md_table(t))
        L.append("\n## Gambar unik per split x kelas\n")
        t2 = bdf.groupby(["split", "class_name"]).image.nunique().unstack(fill_value=0)
        t2 = t2.reindex(order).reindex(columns=cc, fill_value=0)
        t2.loc["TOTAL"] = t2.sum()
        L.append(md_table(t2))
        tot = t2.loc["TOTAL"][classes]
        if tot.min() > 0:
            L.append(f"\nRasio kelas terbanyak : tersedikit (gambar unik) = "
                     f"{tot.max() / tot.min():.2f} ({tot.idxmax()} vs {tot.idxmin()})\n")
        else:
            L.append(f"\n! Kelas tanpa box berlabel: {', '.join(tot[tot == 0].index)}\n")
        L.append("\n## Box per sumber x kelas terpadu\n")
        t3 = bdf.groupby(["source", "class_name"]).size().unstack(fill_value=0).reindex(columns=cc, fill_value=0)
        L.append(md_table(t3))
        L.append("\n## Ukuran box per kelas\n")
        g = bdf.groupby("class_name")
        sz = pd.DataFrame({"box": g.size(), "median_luas": g.area.median(),
                           "pct_tiny": g.tiny.mean() * 100,
                           "pct_menempel_tepi": g.touches_edge.mean() * 100,
                           "pct_huge": g.huge.mean() * 100}).reindex(cc).fillna(0).round(2)
        L.append(md_table(sz))
        L.append("\n_'Menempel tepi' hanyalah proxy truncation. Occlusion tidak bisa diukur "
                 "dari format YOLO._\n")
        per_img = idf[idf.n_boxes > 0].n_boxes
        L.append(f"\nBox per gambar: median {per_img.median():.0f}, maks {per_img.max()}, "
                 f"gambar dengan >=10 box: {(per_img >= 10).sum()}\n")

    L.append("\n## Resolusi gambar\n")
    okd = idf[idf.ok]
    if len(okd):
        short = okd[["width", "height"]].min(axis=1)
        L.append(f"- Sisi terpendek: min {short.min()}, median {short.median():.0f}\n"
                 f"- Di bawah {args.low_res}px: {(short < args.low_res).sum()} gambar\n")

    L.append("\n## Kebocoran dan duplikat\n")
    L.append(f"- Nama dasar sama muncul di lebih dari satu split (per sumber): **{len(leak_keys)}**\n")
    if args.skip_neardup:
        L.append("- Near-duplicate dilewati (--skip-neardup).\n")
    else:
        n_exact = int(ddf.exact_md5.sum()) if not ddf.empty else 0
        n_cross = int(ddf.cross_split.sum()) if not ddf.empty else 0
        n_cross_nb = int((ddf.cross_split & ~ddf.same_base).sum()) if not ddf.empty else 0
        L.append(f"- Pasangan mirip (Hamming <= {args.near_threshold}): {len(ddf)}\n"
                 f"- Duplikat persis (MD5): {n_exact}\n"
                 f"- Pasangan mirip lintas split: {n_cross} (di antaranya nama dasar berbeda: {n_cross_nb})\n"
                 f"- Detail di `duplicates.csv`. Near-duplicate perlu dicek manual "
                 f"(frame video berurutan juga bisa terdeteksi mirip).\n")

    L.append("\n## Rekap masalah (detail di issues.csv)\n")
    if issues:
        it = pd.Series([t for t, _, _ in issues]).value_counts().rename_axis("jenis").to_frame("jumlah")
        L.append(md_table(it))
    else:
        L.append("Tidak ada masalah terdeteksi.\n")
    L.append("\n## Tidak dapat diperiksa dari format YOLO\n"
             "- Occlusion, group-of, depiction (butuh pemeriksaan manual)\n"
             "- Lisensi gambar per foto (hanya lisensi tingkat dataset dari README)\n")
    summary = "\n".join(L)
    (out / "audit_summary.md").write_text(summary, encoding="utf-8")
    print("\n" + summary)

    # ------------------------------------------------ sampel visual
    if args.sample > 0 and not bdf.empty:
        rnd = random.Random(args.seed)
        for cname in classes:
            cand = sorted(bdf[bdf.class_name == cname].image.unique())
            pick = rnd.sample(cand, min(args.sample, len(cand)))
            d = out / "samples" / cname
            d.mkdir(parents=True, exist_ok=True)
            for key in pick:
                try:
                    with Image.open(root / key) as im:
                        im = im.convert("RGB")
                        W, H = im.size
                        dr = ImageDraw.Draw(im)
                        for _, b in bdf[bdf.image == key].iterrows():
                            col = COLORS[int(b.cls) % len(COLORS)]
                            dr.rectangle([b.x1 * W, b.y1 * H, b.x2 * W, b.y2 * H],
                                         outline=col, width=max(2, W // 200))
                            dr.text((b.x1 * W + 3, b.y1 * H + 3), b.class_name, fill=col)
                        im.thumbnail((1024, 1024))
                        im.save(d / (Path(key).stem[:80] + ".jpg"), quality=85)
                except Exception:  # noqa: BLE001
                    continue
        print(f"Sampel visual disimpan di {out / 'samples'}")
    print(f"\nSelesai. Output di: {out}")


if __name__ == "__main__":
    main()