#!/usr/bin/env python3
"""
Diagnostic script to investigate why the repo extraction finds fewer embedded images
than you expect.

This script:
- Uses PyMuPDF (`fitz`) when available.
- For each page, prints `page.get_images(full=True)` count and the image tuples (xref and metadata).
- Attempts to `doc.extract_image(xref)` for every xref found and logs ext/width/height.
- Saves ALL extracted images (no per-page limit) into an `images_diagnostic` folder.
- Optionally rasterizes pages (use `--rasterize`) and saves raster images for every page.

Run:
    python extract_pdf_images_diagnostic.py path/to/file.pdf

Or, in an IDE/Spyder you can import and call `run_diagnostic(path, out_dir, rasterize=True)` directly.

This will show whether images are present as embedded XObjects (extractable) or only visible
when the page is rendered (in which case a rasterization will capture them).
"""

from pathlib import Path
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def run_diagnostic(pdf_path: Path, out_dir: Path = None, rasterize: bool = False):
    pdf_path = Path(pdf_path)
    if out_dir is None:
        out_dir = Path(__file__).resolve().parent / "images_diagnostic"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        logger.error(f"PDF not found: {pdf_path}")
        return 2

    file_bytes = pdf_path.read_bytes()

    try:
        import fitz
    except Exception as e:
        logger.error(
            "PyMuPDF (fitz) is required for this diagnostic script. Please `pip install pymupdf`."
        )
        raise

    doc = fitz.open("pdf", file_bytes)
    logger.info(f"Opened PDF: {pdf_path} -- pages={doc.page_count}")

    total_saved = []

    for page_num in range(doc.page_count):
        page = doc[page_num]
        imgs = page.get_images(full=True)
        logger.info(
            f"Page {page_num+1}/{doc.page_count}: get_images(full=True) returned {len(imgs)} entries"
        )

        if imgs:
            for i, img in enumerate(imgs):
                # PyMuPDF page.get_images(full=True) tuples typically are:
                # (xref, smask, width, height, bpc, colorspace, alt, name)
                try:
                    xref = img[0]
                    logger.info(f"  Entry {i+1}: xref={xref} tuple={img}")
                    try:
                        info = doc.extract_image(xref)
                        if not info or "image" not in info:
                            logger.warning(
                                f"    extract_image returned no image bytes for xref {xref}"
                            )
                            continue
                        ext = info.get("ext", "png")
                        width = info.get("width")
                        height = info.get("height")
                        logger.info(
                            f"    extract_image: ext={ext} size={width}x{height} (bytes={len(info.get('image',b''))})"
                        )

                        out_name = out_dir / f"page_{page_num+1:03d}_xref_{xref}.{ext}"
                        with open(out_name, "wb") as of:
                            of.write(info.get("image"))
                        total_saved.append(out_name)
                        logger.info(f"    Saved -> {out_name}")
                    except Exception as ex:
                        logger.warning(f"    Failed to extract/save xref {xref}: {ex}")
                except Exception as ex:
                    logger.warning(
                        f"  Failed reading image tuple #{i+1} on page {page_num+1}: {ex}"
                    )
        else:
            logger.info(f"  No embedded XObject images on page {page_num+1}")

        # Optionally rasterize each page to capture render-time visuals
        if rasterize:
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                raster_name = out_dir / f"page_{page_num+1:03d}_raster_full.png"
                pix.save(str(raster_name))
                total_saved.append(raster_name)
                logger.info(f"  Rasterized page saved -> {raster_name}")
            except Exception as e:
                logger.warning(f"  Failed to rasterize page {page_num+1}: {e}")

    doc.close()

    logger.info(
        f"Diagnostic complete. Total saved files: {len(total_saved)} in {out_dir}"
    )
    for p in total_saved:
        logger.info(f" - {p}")
    return total_saved


def main(argv):
    import argparse

    parser = argparse.ArgumentParser(
        description="Diagnostic: extract all images and show metadata"
    )
    parser.add_argument("pdf", help="path to PDF file")
    parser.add_argument("--out", help="output dir", default=None)
    parser.add_argument("--rasterize", help="rasterize every page", action="store_true")
    args = parser.parse_args(argv)

    out_dir = Path(args.out) if args.out else None
    rasterize = bool(args.rasterize)

    result = run_diagnostic(Path(args.pdf), out_dir=out_dir, rasterize=rasterize)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
