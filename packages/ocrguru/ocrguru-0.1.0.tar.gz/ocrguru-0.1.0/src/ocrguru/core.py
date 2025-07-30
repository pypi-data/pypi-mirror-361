# src/docling_ocr/core.py
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    EasyOcrOptions,
    TesseractOcrOptions,
    TesseractCliOcrOptions,
    RapidOcrOptions
)
from huggingface_hub import snapshot_download

SUPPORTED_ENGINES = {
    "easyocr": EasyOcrOptions,
    "tesseract_py": TesseractOcrOptions,
    "tesseract_cli": TesseractCliOcrOptions,
    "rapidocr": RapidOcrOptions,
}

def get_ocr_options(engine: str):
    opts_cls = SUPPORTED_ENGINES[engine]
    if engine == "rapidocr":
        path = snapshot_download("SWHL/RapidOCR")
        return RapidOcrOptions(
            det_model_path=f"{path}/PP-OCRv4/en_PP-OCRv3_det_infer.onnx",
            rec_model_path=f"{path}/PP-OCRv4/ch_PP-OCRv4_rec_server_infer.onnx",
            cls_model_path=f"{path}/PP-OCRv3/ch_ppocr_mobile_v2.0_cls_train.onnx",
        )
    return opts_cls()

def convert(input_path: Path, engine: str, out_format: str, output_path: Path):
    suffix = input_path.suffix.lower()
    ocr_opts = get_ocr_options(engine)
    if suffix == ".pdf":
        pdf_opts = PdfPipelineOptions(do_ocr=True)
        pdf_opts.ocr_options = ocr_opts
        fmt_opt = PdfFormatOption(pipeline_options=pdf_opts)
        fmt = InputFormat.PDF
    elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
        img_opts = PdfPipelineOptions(do_ocr=True)
        img_opts.ocr_options = ocr_opts
        fmt_opt = ImageFormatOption(pipeline_options=img_opts)
        fmt = InputFormat.IMAGE
    else:
        raise ValueError(f"Unsupported input: {suffix}")

    converter = DocumentConverter(format_options={fmt: fmt_opt})
    doc = converter.convert(source=input_path).document
    if out_format == "md":
        data = doc.export_to_markdown()
    elif out_format == "json":
        data = doc.json()
    elif out_format == "html":
        data = doc.export_to_hocr()
    else:
        raise ValueError(f"Unsupported output: {out_format}")
    output_path.write_text(data, encoding="utf-8")
