#!/usr/bin/env python3
"""
PDF to Images Converter

Converts PDF pages to PNG images for visual analysis.
Requires: pdf2image (pip install pdf2image) and poppler-utils (brew install poppler)
"""

import sys
from pathlib import Path
from pdf2image import convert_from_path


def pdf_to_images(pdf_path: Path, output_dir: Path, dpi: int = 150):
    """
    Convert PDF pages to PNG images.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the images
        dpi: Resolution for the images (default: 150)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting {pdf_path} to images...")
    images = convert_from_path(pdf_path, dpi=dpi)
    
    for i, image in enumerate(images, start=1):
        output_path = output_dir / f"page_{i:03d}.png"
        image.save(output_path, 'PNG')
        print(f"  Saved page {i} to {output_path}")
    
    print(f"\nConverted {len(images)} pages to {output_dir}")
    return len(images)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_images.py <pdf_file> [output_dir] [dpi]")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else pdf_path.parent / f"{pdf_path.stem}_images"
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        sys.exit(1)
    
    pdf_to_images(pdf_path, output_dir, dpi)
