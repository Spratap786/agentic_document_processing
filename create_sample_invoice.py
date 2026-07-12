"""
CREATE_SAMPLE_INVOICE.PY — Generates a test invoice PDF.

Run this once to create a sample PDF you can test with:
    python create_sample_invoice.py

This creates: documents/invoice.pdf
"""

import fitz  # PyMuPDF
import os

os.makedirs("documents", exist_ok=True)

doc = fitz.open()
page = doc.new_page()

invoice_text = """
    INVOICE

    Invoice Number : INV-2024-00891
    Invoice Date   : 12 July 2026
    Due Date       : 26 July 2026

    BILL TO:
    Acme Corporation
    123 Business Street
    Bengaluru, Karnataka 560001

    FROM:
    Tech Solutions Pvt Ltd
    456 Startup Avenue
    Bengaluru, Karnataka 560002

    ─────────────────────────────────────────────
    ITEM              QTY    UNIT PRICE    TOTAL
    ─────────────────────────────────────────────
    Web Development    1     ₹50,000       ₹50,000
    UI/UX Design       1     ₹20,000       ₹20,000
    Hosting Setup      1     ₹10,000       ₹10,000
    ─────────────────────────────────────────────
                                 TOTAL:  ₹80,000
    ─────────────────────────────────────────────

    Payment Terms: Net 14 days
    Bank: HDFC Bank | Account: 1234567890 | IFSC: HDFC0001234
"""

page.insert_text((50, 50), invoice_text, fontsize=11)
doc.save("documents/invoice.pdf")
doc.close()

print("✅ Sample invoice created at: documents/invoice.pdf")
print("   Invoice Number in the PDF: INV-2024-00891")
print("\nNow run: python app.py")
