#!/usr/bin/env python3
"""
Layout duplicate detector for screenshot folders.

This script analyzes screenshots to determine which images share the same layout.
It normalizes images, optionally crops fixed top/bottom bars, optionally masks text
via OCR, computes multiple layout fingerprints (perceptual hashes, edge/block
signatures, and projection histograms), and clusters near-duplicates.

Outputs a CSV labeling each file with a cluster id, canonical representative,
and distance to canonical. Optionally generates contact sheets for each cluster.

Example:
    python dedupe_layouts.py \
      --input-dir folklife-screens-x \
      --output-csv layout_clusters.csv \
      --contact-sheets-dir layout_contact_sheets \
      --resize-width 1024 \
      --crop-top 0 --crop-bottom 0 \
      --mask-text
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# Third-party libraries. These are added to requirements.txt
from PIL import Image, ImageDraw
import imagehash
import cv2  # type: ignore
from sklearn.cluster import DBSCAN
from tqdm import tqdm


def try_import_pytesseract():
    try:
        import pytesseract  # type: ignore
        # Validate binary availability; if missing, accessing version may raise
        try:
            _ = pytesseract.get_tesseract_version()
        except Exception:
            # Binary not available; we will degrade gracefully
            pass
        return pytesseract
    except Exception:
        return None


@dataclass
class ImageFeatures:
    file_path: Path
    width: int
    height: int
    ahash_bits: np.ndarray
    phash_bits: np.ndarray
    dhash_bits: np.ndarray
    whash_bits: np.ndarray
    edge_signature: np.ndarray  # shape (edge_sig_size * edge_sig_size,)
    h_projection: np.ndarray    # shape (edge_sig_size,)
    v_projection: np.ndarray    # shape (edge_sig_size,)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cluster layout-duplicate screenshots")
    parser.add_argument("--input-dir", type=str, default="folklife-screens-x", help="Directory of screenshots")
    parser.add_argument("--glob", type=str, default="*.png", help="Glob to match files (e.g., '*.png')")
    parser.add_argument("--output-csv", type=str, default="layout_clusters.csv", help="Path to write results CSV")
    parser.add_argument("--clusters-dir", type=str, default="", help="Optional directory to copy/symlink clusters into")
    parser.add_argument("--contact-sheets-dir", type=str, default="", help="Optional directory to write contact sheets per cluster")
    parser.add_argument("--resize-width", type=int, default=1024, help="Normalize images to this width (keep aspect)")
    parser.add_argument("--crop-top", type=int, default=0, help="Crop this many pixels from the top after resizing")
    parser.add_argument("--crop-bottom", type=int, default=0, help="Crop this many pixels from the bottom after resizing")
    parser.add_argument("--mask-text", action="store_true", help="Use OCR to mask text so content doesn't affect layout")
    parser.add_argument("--ocr-lang", type=str, default="eng", help="Tesseract languages (comma-separated)")
    parser.add_argument("--edge-sig-size", type=int, default=64, help="Downsampled edge signature size (n -> n x n)")
    parser.add_argument("--eps", type=float, default=0.33, help="DBSCAN eps on combined distance [0..1]")
    parser.add_argument("--min-samples", type=int, default=1, help="DBSCAN min_samples (1 groups all closest)")
    parser.add_argument("--alpha", type=float, default=0.55, help="Weight for perceptual hash distance [0..1]")
    parser.add_argument("--beta", type=float, default=0.35, help="Weight for edge signature distance [0..1]")
    parser.add_argument("--gamma", type=float, default=0.10, help="Weight for projection histogram distance [0..1]")
    parser.add_argument("--max-images", type=int, default=0, help="Optional cap for number of images (0 = no cap)")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    return parser.parse_args()


def load_image(path: Path) -> Image.Image:
    image = Image.open(path)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    return image


def normalize_image(image: Image.Image, target_width: int, crop_top: int, crop_bottom: int) -> Image.Image:
    w, h = image.size
    if w != target_width:
        scale = target_width / float(w)
        new_h = max(1, int(round(h * scale)))
        image = image.resize((target_width, new_h), Image.LANCZOS)
    if crop_top > 0 or crop_bottom > 0:
        w, h = image.size
        top = min(max(0, crop_top), h)
        bottom = max(0, h - max(0, crop_bottom))
        if bottom <= top:
            top = 0
            bottom = h
        image = image.crop((0, top, w, bottom))
    return image


def mask_text_regions(image: Image.Image, ocr_langs: str, pytesseract_module) -> Image.Image:
    if pytesseract_module is None:
        return image
    try:
        # Use tesseract to get word boxes
        rgb = image if image.mode == "RGB" else image.convert("RGB")
        data = pytesseract_module.image_to_data(rgb, lang=ocr_langs, output_type=pytesseract_module.Output.DICT)
        draw = ImageDraw.Draw(rgb)
        n = len(data.get("text", []))
        for i in range(n):
            text = data["text"][i]
            if not text or text.strip() == "":
                continue
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            # Draw a filled rectangle to cover the text
            draw.rectangle([x, y, x + w, y + h], fill=(0, 0, 0))
        return rgb
    except Exception:
        # Degrade gracefully if OCR fails
        return image


def image_to_cv_gray(image: Image.Image) -> np.ndarray:
    if image.mode != "L":
        image = image.convert("L")
    arr = np.array(image, dtype=np.uint8)
    return arr


def compute_edge_signature(gray: np.ndarray, edge_sig_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Canny edges
    edges = cv2.Canny(gray, 100, 200)
    # Downsample to edge_sig_size x edge_sig_size using area interpolation
    small = cv2.resize(edges, (edge_sig_size, edge_sig_size), interpolation=cv2.INTER_AREA)
    small_f = (small.astype(np.float32) / 255.0).reshape(-1)
    # Projection histograms
    h_proj = small.astype(np.float32).mean(axis=1) / 255.0  # horizontal: rows
    v_proj = small.astype(np.float32).mean(axis=0) / 255.0  # vertical: cols
    return small_f, h_proj.astype(np.float32), v_proj.astype(np.float32)


def hash_to_bits(h: imagehash.ImageHash) -> np.ndarray:
    # imagehash.ImageHash.hash is a numpy bool array
    return h.hash.astype(np.uint8).reshape(-1)


def compute_hashes(image: Image.Image) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Use default hash sizes (8x8) which produce 64-bit signatures each
    ah = imagehash.average_hash(image)
    ph = imagehash.phash(image)
    dh = imagehash.dhash(image)
    wh = imagehash.whash(image)
    return hash_to_bits(ah), hash_to_bits(ph), hash_to_bits(dh), hash_to_bits(wh)


def compute_features(
    file_path: Path,
    resize_width: int,
    crop_top: int,
    crop_bottom: int,
    mask_text: bool,
    ocr_langs: str,
    edge_sig_size: int,
    pytesseract_module,
) -> ImageFeatures:
    image = load_image(file_path)
    image = normalize_image(image, resize_width, crop_top, crop_bottom)
    if mask_text:
        image = mask_text_regions(image, ocr_langs, pytesseract_module)
    gray = image_to_cv_gray(image)
    edge_sig, h_proj, v_proj = compute_edge_signature(gray, edge_sig_size)
    ah_bits, ph_bits, dh_bits, wh_bits = compute_hashes(image)
    h, w = gray.shape
    return ImageFeatures(
        file_path=file_path,
        width=w,
        height=h,
        ahash_bits=ah_bits,
        phash_bits=ph_bits,
        dhash_bits=dh_bits,
        whash_bits=wh_bits,
        edge_signature=edge_sig,
        h_projection=h_proj,
        v_projection=v_proj,
    )


def hamming_distance(a: np.ndarray, b: np.ndarray) -> int:
    return int(np.count_nonzero(a != b))


def normalized_hash_distance(a: ImageFeatures, b: ImageFeatures) -> float:
    # Sum hamming distances across four 64-bit hashes, normalize by total bits
    total_bits = a.ahash_bits.size + a.phash_bits.size + a.dhash_bits.size + a.whash_bits.size
    dist = (
        hamming_distance(a.ahash_bits, b.ahash_bits)
        + hamming_distance(a.phash_bits, b.phash_bits)
        + hamming_distance(a.dhash_bits, b.dhash_bits)
        + hamming_distance(a.whash_bits, b.whash_bits)
    )
    return dist / float(total_bits)


def cosine_distance(u: np.ndarray, v: np.ndarray) -> float:
    denom = (np.linalg.norm(u) * np.linalg.norm(v))
    if denom == 0:
        return 1.0
    return 1.0 - float(np.dot(u, v) / denom)


def l1_distance(u: np.ndarray, v: np.ndarray) -> float:
    return float(np.mean(np.abs(u - v)))


def combined_distance(a: ImageFeatures, b: ImageFeatures, alpha: float, beta: float, gamma: float) -> float:
    dh = normalized_hash_distance(a, b)
    de = cosine_distance(a.edge_signature, b.edge_signature)
    dp = 0.5 * (l1_distance(a.h_projection, b.h_projection) + l1_distance(a.v_projection, b.v_projection))
    # Weighted sum; ensure weights sum to 1
    weight_sum = alpha + beta + gamma
    alpha_n = alpha / weight_sum
    beta_n = beta / weight_sum
    gamma_n = gamma / weight_sum
    return alpha_n * dh + beta_n * de + gamma_n * dp


def build_distance_matrix(features: List[ImageFeatures], alpha: float, beta: float, gamma: float) -> np.ndarray:
    n = len(features)
    D = np.zeros((n, n), dtype=np.float32)
    for i in tqdm(range(n), desc="Distances", leave=False):
        D[i, i] = 0.0
        for j in range(i + 1, n):
            d = combined_distance(features[i], features[j], alpha, beta, gamma)
            D[i, j] = d
            D[j, i] = d
    return D


def choose_canonical(indices: Sequence[int], features: List[ImageFeatures]) -> int:
    # Prefer the image with the largest area; tie-break by shortest filename
    best = indices[0]
    best_area = features[best].width * features[best].height
    best_name = features[best].file_path.name
    for idx in indices[1:]:
        area = features[idx].width * features[idx].height
        name = features[idx].file_path.name
        if area > best_area or (area == best_area and name < best_name):
            best = idx
            best_area = area
            best_name = name
    return best


def write_csv(
    output_csv: Path,
    labels: np.ndarray,
    features: List[ImageFeatures],
    distance_matrix: Optional[np.ndarray],
) -> None:
    clusters: Dict[int, List[int]] = {}
    for i, label in enumerate(labels):
        clusters.setdefault(int(label), []).append(i)

    rows: List[Dict[str, str]] = []
    for label, idxs in clusters.items():
        canonical_idx = choose_canonical(idxs, features)
        canonical_path = features[canonical_idx].file_path
        for idx in idxs:
            f = features[idx]
            dist = 0.0
            if distance_matrix is not None:
                dist = float(distance_matrix[canonical_idx, idx])
            rows.append({
                "cluster_id": str(label),
                "canonical": canonical_path.name,
                "filename": f.file_path.name,
                "path": str(f.file_path),
                "distance_to_canonical": f"{dist:.6f}",
            })

    with output_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["cluster_id", "canonical", "filename", "path", "distance_to_canonical"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def make_contact_sheet(cluster_indices: Sequence[int], features: List[ImageFeatures], sheet_path: Path, thumb_width: int = 400, cols: int = 5) -> None:
    images: List[Image.Image] = []
    names: List[str] = []
    for idx in cluster_indices:
        try:
            im = Image.open(features[idx].file_path)
            w, h = im.size
            scale = thumb_width / float(w)
            im = im.resize((thumb_width, max(1, int(round(h * scale)))), Image.LANCZOS)
            images.append(im)
            names.append(features[idx].file_path.name)
        except Exception:
            continue
    if not images:
        return

    rows = math.ceil(len(images) / float(cols))
    col_widths = [max(im.width for im in images[i::cols]) for i in range(cols)]
    row_heights = [max(im.height for im in images[i * cols:(i + 1) * cols]) for i in range(rows)]
    sheet_w = int(sum(col_widths))
    sheet_h = int(sum(row_heights))
    sheet = Image.new("RGB", (sheet_w, sheet_h), color=(240, 240, 240))

    y = 0
    k = 0
    for r in range(rows):
        x = 0
        for c in range(cols):
            if k >= len(images):
                break
            im = images[k]
            sheet.paste(im, (x, y))
            x += col_widths[c]
            k += 1
        y += row_heights[r]

    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(sheet_path)


def generate_contact_sheets(labels: np.ndarray, features: List[ImageFeatures], out_dir: Path) -> None:
    clusters: Dict[int, List[int]] = {}
    for i, label in enumerate(labels):
        clusters.setdefault(int(label), []).append(i)
    for label, idxs in tqdm(clusters.items(), desc="Contact sheets", leave=False):
        sheet_path = out_dir / f"cluster_{label:04d}.jpg"
        make_contact_sheet(idxs, features, sheet_path)


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_csv = Path(args.output_csv)
    clusters_dir = Path(args.clusters_dir) if args.clusters_dir else None
    contact_sheets_dir = Path(args.contact_sheets_dir) if args.contact_sheets_dir else None

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory not found: {input_dir}")

    # Collect files
    files = sorted(input_dir.glob(args.glob))
    if args.max_images and args.max_images > 0:
        files = files[: args.max_images]
    if len(files) == 0:
        raise SystemExit("No images found.")

    pytesseract_module = try_import_pytesseract() if args.mask_text else None

    # Compute features
    features: List[ImageFeatures] = []
    for path in tqdm(files, desc="Features"):
        try:
            f = compute_features(
                file_path=path,
                resize_width=args.resize_width,
                crop_top=args.crop_top,
                crop_bottom=args.crop_bottom,
                mask_text=args.mask_text,
                ocr_langs=args.ocr_lang,
                edge_sig_size=args.edge_sig_size,
                pytesseract_module=pytesseract_module,
            )
            features.append(f)
        except Exception as e:
            if args.verbose:
                print(f"Failed to process {path}: {e}")

    if len(features) == 0:
        raise SystemExit("No features computed; aborting.")

    # Build distance matrix
    D = build_distance_matrix(features, alpha=args.alpha, beta=args.beta, gamma=args.gamma)

    # Cluster with DBSCAN on precomputed distances
    clustering = DBSCAN(eps=args.eps, min_samples=args.min_samples, metric="precomputed", n_jobs=-1)
    labels = clustering.fit_predict(D)

    # Normalize outliers (-1) into unique cluster ids after the max
    if np.any(labels == -1):
        max_label = labels[labels >= 0].max() if np.any(labels >= 0) else -1
        next_label = max_label + 1
        for i, lab in enumerate(labels):
            if lab == -1:
                labels[i] = next_label
                next_label += 1

    # Write CSV
    write_csv(output_csv, labels, features, D)

    # Optionally generate contact sheets
    if contact_sheets_dir is not None and str(contact_sheets_dir) != "":
        generate_contact_sheets(labels, features, contact_sheets_dir)

    # Optionally build clusters directory (symlinks)
    if clusters_dir is not None and str(clusters_dir) != "":
        clusters: Dict[int, List[int]] = {}
        for i, label in enumerate(labels):
            clusters.setdefault(int(label), []).append(i)
        for label, idxs in tqdm(clusters.items(), desc="Clusters", leave=False):
            cdir = clusters_dir / f"cluster_{label:04d}"
            cdir.mkdir(parents=True, exist_ok=True)
            canonical_idx = choose_canonical(idxs, features)
            # Write a text file with canonical name
            with (cdir / "canonical.txt").open("w") as fh:
                fh.write(features[canonical_idx].file_path.name + "\n")
            for idx in idxs:
                src = features[idx].file_path
                dst = cdir / src.name
                try:
                    if os.path.lexists(dst):
                        continue
                    os.symlink(src.resolve(), dst)
                except Exception:
                    # Fallback to copy if symlink not permitted
                    try:
                        from shutil import copy2
                        copy2(src, dst)
                    except Exception:
                        pass

    if args.verbose:
        n_clusters = len(set(int(l) for l in labels))
        print(f"Processed {len(features)} images -> {n_clusters} clusters")


if __name__ == "__main__":
    main()


