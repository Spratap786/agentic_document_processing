"""
CREATE_SAMPLE_INVOICE.PY — Makes a test PDF.
Run: python create_sample_invoice.py  → documents/invoice.pdf
"""

import os

import fitz

os.makedirs("documents", exist_ok=True)

doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), """
    INVOICE

    Invoice Number : INV-2026-00417
    Invoice Date   : 20 July 2026

    BILL TO: Acme Corporation
    FROM:    Tech Solutions Pvt Ltd

    ITEM              QTY    TOTAL
    Web Development    1     50,000
    UI/UX Design       1     20,000
                    TOTAL:   70,000
""", fontsize=11)
doc.save("documents/invoice.pdf")
doc.close()
print("✅ Created documents/invoice.pdf (invoice number: INV-2026-00417)")
