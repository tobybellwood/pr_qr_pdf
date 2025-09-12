# QR Barcode Generator

This project generates a series of QR codes (P0000 format) as SVG and PNG images, and combines them into a PDF. It is useful for creating printable barcode sheets for parkrun or similar events.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. All-in-one QR to PDF (grid layout)

```bash
python pr_qr_pdf.py
```

or for a range:
```bash
python pr_qr_pdf.py 301 400
```

## Output

- `qr_svgs/` — SVG QR codes
- `qr_pngs/` — PNG QR codes
- `qr_codes.pdf` — PDF with all QR codes (grid layout)

## Notes

- Ensure you have all dependencies installed (see requirements.txt).
- For PDF/PNG conversion, you need CairoSVG and Pillow.
