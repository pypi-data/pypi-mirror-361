from pathlib import Path
from ocrguru.core import convert

def test_convert_md(tmp_path):
    # Prepare a minimal PDF or image fixture here...
    input_file = Path("tests/sample.pdf")
    output_file = tmp_path / "out.md"
    convert(input_file, engine="easyocr", out_format="md", output_path=output_file)
    assert output_file.exists()
