#!/usr/bin/env python3
"""
Standalone test script that extracts images from a PDF using the exact same
method as `extract_images_from_pdf_bytes` in `backend/app/services/document_utils.py`.

Usage:
    python extract_pdf_images_test.py path/to/input.pdf

This script will create an `images` folder next to this script and write
PNG files for page rasterizations and embedded images.

Behavior mirrors the repo implementation:
- Preferred method: PyMuPDF (fitz)
  - Rasterizes up to min(page_count, 10) pages at 1.5x scale and saves as PNG
  - For each page, also extracts up to 3 embedded images via xref
- Fallback: pdf2image (convert_from_bytes)
  - Converts up to 5 pages to PNG when PyMuPDF is unavailable

The file names follow these patterns:
- page_001_raster.png   (rasterized page)
- page_001_embedded_001.png  (embedded image extracted from page)

This helps debug discrepancies between expected and actual extracted image counts.
"""

from pathlib import Path
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def extract_images_from_pdf_bytes(file_bytes: bytes, out_dir: Path):
    """Extract images using the same approach as the repo's document_utils.

    Returns list of saved file paths.
    """
    import base64

    saved_files = []

    try:
        import fitz  # PyMuPDF

        doc = fitz.open("pdf", file_bytes)

        # Limit pages to the same cap used in the repo
        page_limit = min(doc.page_count, 10)

        for page_num in range(page_limit):
            page = doc[page_num]

            # SKIP: Full-page raster conversion (redundant with embedded images + text)
            # Rasterize page (matrix 1.5x)
            # try:
            #    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            #    img_data = pix.tobytes("png")
            #    raster_name = out_dir / f"page_{page_num+1:03d}_raster.png"
            #    with open(raster_name, "wb") as f:
            #        f.write(img_data)
            #    saved_files.append(raster_name)
            #    logger.info(f"Saved rasterized page image: {raster_name}")
            # except Exception as e:
            #    logger.warning(f"Failed to rasterize page {page_num+1}: {e}")

            # Extract embedded images from the page (limit embedded images per page)
            try:
                image_list = page.get_images()
                logger.info(
                    f"Found {len(image_list)} embedded images on page {page_num+1}"
                )
                # extract all embedded images (remove the repo's per-page cap)
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image.get("image")
                        if not image_bytes:
                            logger.warning(
                                f"No image bytes for xref {xref} on page {page_num+1}"
                            )
                            continue
                        embed_name = (
                            out_dir
                            / f"page_{page_num+1:03d}_embedded_{img_index+1:03d}.png"
                        )
                        with open(embed_name, "wb") as ef:
                            ef.write(image_bytes)
                        saved_files.append(embed_name)
                        logger.info(f"Saved embedded image: {embed_name}")
                    except Exception as ie:
                        logger.warning(
                            f"Failed to extract embedded image #{img_index+1} on page {page_num+1}: {ie}"
                        )
                        continue
            except Exception as e:
                logger.warning(f"Failed to get_images for page {page_num+1}: {e}")

        try:
            doc.close()
        except Exception:
            pass

        return saved_files

    except ImportError:
        logger.info(
            "Skipping PDF image extraction (PyMuPDF not available and fallback disabled)"
        )
        # logger.warning(
        #    "PyMuPDF (fitz) not available - falling back to pdf2image page conversion"
        # )
        # try:
        #    from pdf2image import convert_from_bytes
        #    import io
        #
        #    pages = convert_from_bytes(file_bytes, dpi=150, fmt="PNG")
        #    for i, page in enumerate(pages):  # repo fallback limits to 5 pages
        #        img_buffer = io.BytesIO()
        #        page.save(img_buffer, format="PNG")
        #        img_data = img_buffer.getvalue()
        #        raster_name = out_dir / f"page_{i+1:03d}_raster.png"
        #        with open(raster_name, "wb") as f:
        #            f.write(img_data)
        #        saved_files.append(raster_name)
        #        logger.info(f"Saved fallback rasterized page image: {raster_name}")
        #    return saved_files
        # except ImportError:
        #    logger.error("pdf2image not available - cannot extract images from PDF")
        #    return saved_files
        # except Exception as e:
        #    logger.error(f"pdf2image extraction failed: {e}")
        #    return saved_files


def main(argv):
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract images from a PDF using the project's method"
    )
    parser.add_argument("pdf", help="Path to the PDF file to extract images from")
    args = parser.parse_args(argv)

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        return 2

    script_dir = Path(__file__).resolve().parent
    out_dir = script_dir / "images"
    out_dir.mkdir(exist_ok=True)

    file_bytes = pdf_path.read_bytes()
    saved = extract_images_from_pdf_bytes(file_bytes, out_dir)

    logger.info(f"Extraction complete. Saved {len(saved)} images to: {out_dir}")
    for p in saved:
        logger.info(f" - {p}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
