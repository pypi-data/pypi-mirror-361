<!--
  ____   ____ ____  _      _     
 / __ \ / __ \___ \| |    | |    
| |  | | |  | |__) | |    | |    
| |  | | |  | |__ <| |    | |    
| |__| | |__| |__) | |____| |____
 \____/ \____/____/|______|______|

 A simple, extensible CLI wrapper around Docling OCR
-->

[![PyPI version](https://badge.fury.io/py/ocrguru.svg)](https://badge.fury.io/py/ocrguru)
[![CI Status](https://github.com/yourusername/ocrguru/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/ocrguru/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# ocrguru

**ocrguru** is a lightweight, extensible CLI tool that wraps the powerful [Docling OCR](https://docling-project.github.io/) pipeline.  
Process scanned PDFs or images in one command, choose your OCR engine, and export clean text in Markdown, JSON, or hOCR—all without the usual setup fuss.

---

## 📖 Table of Contents

1. [✨ Features](#-features)  
2. [🚀 Installation](#-installation)  
3. [⚡ Quick Start](#-quick-start)  
4. [🛠️ CLI Reference](#-cli-reference)  
5. [🎯 Examples](#-examples)  
6. [📂 Project Structure](#-project-structure)  
7. [🤝 Contributing](#-contributing)  
8. [✅ Testing](#-testing)  
9. [📜 License](#-license)  

---

## ✨ Features

- **Multiple Engines**  
  - **RapidOCR** (default ONNX-based)  
  - **EasyOCR** (PyTorch-powered)  
  - **Tesseract** (Python wrapper or CLI)  

- **Input Formats**  
  - `.pdf`, `.png`, `.jpg`/`.jpeg`, `.tiff`, `.bmp`  

- **Output Formats**  
  - **Markdown** (`.md`) – human-friendly  
  - **JSON** (`.json`) – full coordinates & metadata  
  - **hOCR** (`.html`) – preserve layout & styling  

- **Zero-Config Defaults**  
  - RapidOCR models auto-download from Hugging Face & cache locally  

- **Cross-Platform**  
  - Works on **Windows**, **macOS**, and **Linux**  

- **Extensible Codebase**  
  - Core logic lives in `core.py`  
  - CLI interface in `cli.py`  
  - Easily add new engines or pipeline options  

---

## 🚀 Installation

From **PyPI**:

```bash
pip install ocrguru
```

From your **GitHub clone**:

```bash
git clone https://github.com/yourusername/ocrguru.git
cd ocrguru
pip install .
```

> **Note:**  
> - `docling` and `huggingface-hub` will install automatically.  
> - For GPU-accelerated EasyOCR, install PyTorch with CUDA support:  
>   ```bash
>   pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu118
>   ```

---

## ⚡ Quick Start

Perform OCR on a PDF using the **default RapidOCR** engine, export to **Markdown**:

```bash
docling-ocr   --engine rapidocr   --input ./scanned_document.pdf   --format md   --output ./scanned_document.md
```

_No extra flags needed!_

---

## 🛠️ CLI Reference

```plain
Usage: docling-ocr [OPTIONS]

Options:
  -e, --engine [easyocr|tesseract_py|tesseract_cli|rapidocr]
                                  OCR engine (default: rapidocr)
  -i, --input PATH                 Input file path (.pdf, image)
  -f, --format [md|json|html]      Output format (default: md)
  -o, --output PATH                Output file path
  -h, --help                       Show this message and exit
```

---

## 🎯 Examples

### 1. EasyOCR on an Image

```bash
docling-ocr   --engine easyocr   --input invoice.jpg   --format json   --output invoice.json
```

### 2. Tesseract CLI on PDF → hOCR

```bash
docling-ocr   --engine tesseract_cli   --input contract.pdf   --format html   --output contract.hocr.html
```

### 3. Batch Processing (RapidOCR default)

```bash
for pdf in reports/*.pdf; do
  out="${pdf%.pdf}.md"
  docling-ocr     --input "$pdf"     --output "$out"
done
```

---

## 📂 Project Structure

```text
ocrguru/
├── src/
│   └── ocrguru/
│       ├── cli.py        # CLI entry point
│       └── core.py       # OCR conversion logic
├── tests/                # pytest test suite
├── pyproject.toml        # build & metadata
└── README.md             # this file
```

---

## 🤝 Contributing

We welcome your ideas and pull requests!  

1. **Fork** the repo & create a feature branch  
2. **Install** dev dependencies:  
   ```bash
   pip install -e .[test]
   ```  
3. **Write** tests in `tests/` and implement your feature in `src/ocrguru/`  
4. **Run** the test suite:  
   ```bash
   pytest
   ```  
5. **Open** a pull request against `main`  

Please adhere to **PEP 8** and write clear commit messages.

---

## ✅ Testing

We use **pytest** for automated testing. Coverage reporting is encouraged:

```bash
pytest --cov=ocrguru
```

Ensure new features include corresponding tests.

---

## 📜 License

Released under the **MIT License**. See [LICENSE](LICENSE) for full text.

---

<p align="center">
  ❤️ Happy OCR’ing with <strong>ocrguru</strong>! ❤️
</p>
