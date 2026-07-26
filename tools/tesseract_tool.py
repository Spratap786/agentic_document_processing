"""
TOOLS/TESSERACT_TOOL.PY — OCR for scanned PDFs.
Renders each page as an image (PyMuPDF) then reads it with Tesseract.

Tesseract must be installed on your system:
  Ubuntu:  sudo apt install tesseract-ocr
  Mac:     brew install tesseract
  Windows: https://github.com/UB-Mannheim/tesseract/wiki
"""

import io

import fitz
import pytesseract
from PIL import Image


def ocr_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom = better OCR
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        full_text += pytesseract.image_to_string(image) + "\n"
    doc.close()
    return full_text.strip()
