"""
TOOLS/TESSERACT_TOOL.PY — OCR for scanned PDFs.

How OCR works here:
  Step 1: Convert each PDF page into a high-resolution image (via PyMuPDF)
  Step 2: Feed that image into Tesseract (an open-source OCR engine)
  Step 3: Tesseract reads the text from the image pixel by pixel
  Step 4: We collect all the text and return it

NOTE: Tesseract must be installed on your system separately:
  - Windows: https://github.com/UB-Mannheim/tesseract/wiki
  - Mac:     brew install tesseract
  - Linux:   sudo apt install tesseract-ocr
"""

import fitz           # PyMuPDF
import pytesseract    # Python wrapper around the Tesseract engine
from PIL import Image # Pillow — for image handling
import io


def ocr_pdf(pdf_path: str) -> str:
    """
    Convert each page of the PDF to an image and run OCR on it.
    Returns all extracted text combined.
    """
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Render the page as a pixmap (a raw image in memory)
        # Matrix(2, 2) = 2× zoom → better resolution = better OCR accuracy
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)

        # Convert the pixmap bytes to a PIL Image that Tesseract understands
        img_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_bytes))

        # Run Tesseract OCR
        text = pytesseract.image_to_string(image)
        full_text += text + "\n"

    doc.close()
    return full_text.strip()
