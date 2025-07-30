# src/docling_ocr/cli.py
import argparse
from pathlib import Path
from .core import convert, SUPPORTED_ENGINES

def main():
    p = argparse.ArgumentParser(prog="docling-ocr",
        description="Perform OCR on PDF/images using Docling backends.")
    p.add_argument("-e","--engine", choices=SUPPORTED_ENGINES,
                   default="rapidocr", help="OCR engine")
    p.add_argument("-i","--input", type=Path, required=True,
                   help="Input file (.pdf, image)")
    p.add_argument("-f","--format", choices=["md","json","html"],
                   default="md", help="Output format")
    p.add_argument("-o","--output", type=Path, required=True,
                   help="Output file path")
    args = p.parse_args()
    convert(args.input, args.engine, args.format, args.output)

if __name__ == "__main__":
    main()
