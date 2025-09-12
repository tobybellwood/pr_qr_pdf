import os
import segno
import re
from cairosvg import svg2png
from PIL import Image
import sys

def generate_qr_svg(code: str, size=400, qr_size=300):
    """
    Generate an SVG string containing a QR code and its label.

    Args:
        code (str): The text to encode in the QR code.
        size (int): The total size of the SVG canvas (pixels).
        qr_size (int): The size of the QR code itself (pixels).

    Returns:
        str: SVG content as a string.
    """
    # Calculate position to center the QR code in the SVG
    qr_x = (size - qr_size) // 2
    qr_y = (size - qr_size) // 2
    # Set font size for the label under the QR code
    label_font_size = int(size * 0.10)
    # Y position for the label (just below the QR code)
    label_y = qr_y + qr_size

    # Generate QR code using segno
    qr = segno.make(code, error='m', micro=False)
    # Calculate scale to fit QR code into desired size
    scale = qr_size / qr.symbol_size(1)[0]
    # Generate SVG for the QR code only (no XML header, no size)
    qr_svg = qr.svg_inline(scale=scale, omitsize=True, dark='black', light='white')

    # Remove XML header if present
    if qr_svg.startswith('<?xml'):
        qr_svg = qr_svg.split('?>', 1)[1]
    # Extract only the inner SVG content (remove outer <svg> tags)
    inner = re.sub(r'^.*?<svg[^>]*>', '', qr_svg, flags=re.DOTALL)
    inner = re.sub(r'</svg>\s*$', '', inner, flags=re.DOTALL)

    # Compose the final SVG with background, QR code, and label
    svg_out = f'''<?xml version="1.0" encoding="utf-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">\n    <rect width="100%" height="100%" fill="white"/>\n    <g transform="translate({qr_x},{qr_y})">\n        {inner.strip()}\n    </g>\n    <text x="{size//2}" y="{label_y}" font-size="{label_font_size}" font-family="Helvetica, Arial, sans-serif" text-anchor="middle" fill="black">{code}</text>\n</svg>'''
    return svg_out

def main():
    # Output directories for SVG and PNG files
    SVG_DIR = "qr_svgs"
    PNG_DIR = "qr_pngs"
    # Output PDF file name
    PDF_FILE = "qr_codes.pdf"
    # Create directories if they don't exist
    os.makedirs(SVG_DIR, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)
    # Set image sizes
    SIZE = 400      # Size of the full SVG/PNG image
    QR_SIZE = 300   # Size of the QR code inside the image

    # Parse command line arguments for code range
    if len(sys.argv) == 1:
        # Default range if no arguments: 301 to 480
        start = 301
        end = 480
    elif len(sys.argv) == 3:
        # Use provided start and end values
        start = int(sys.argv[1])
        end = int(sys.argv[2])
    else:
        print("Usage: python qr_to_pdf.py <start> <end>")
        sys.exit(1)

    # Generate code strings, e.g., P0301, P0302, ..., P0500
    codes = [f"P{i:04d}" for i in range(start, end + 1)]
    png_paths = []

    # Generate SVG and PNG for each code
    for code in codes:
        svg_path = os.path.join(SVG_DIR, f"{code}.svg")
        png_path = os.path.join(PNG_DIR, f"{code}.png")
        # Generate SVG content
        svg_data = generate_qr_svg(code, SIZE, QR_SIZE)
        # Save SVG file
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_data)
        # Convert SVG to PNG using cairosvg
        svg2png(bytestring=svg_data.encode('utf-8'), write_to=png_path, output_width=SIZE, output_height=SIZE)
        png_paths.append(png_path)

    # Load all PNGs as PIL Images
    images = [Image.open(p).convert('RGB') for p in png_paths]
    if images:
        # Prepare to arrange images on A4 pages (210x297mm at 300dpi)
        DPI = 300
        MM_TO_INCH = 1 / 25.4
        A4_WIDTH_MM = 210
        A4_HEIGHT_MM = 297
        # Calculate A4 size in pixels
        A4_WIDTH_PX = int(A4_WIDTH_MM * MM_TO_INCH * DPI)
        A4_HEIGHT_PX = int(A4_HEIGHT_MM * MM_TO_INCH * DPI)

        # Set grid: 5 columns x 6 rows per page
        COLS = 5
        ROWS = 6
        IMAGES_PER_PAGE = COLS * ROWS

        # Calculate horizontal and vertical spacing between images
        img_w, img_h = SIZE, SIZE
        h_space = (A4_WIDTH_PX - (COLS * img_w)) // (COLS + 1)
        v_space = (A4_HEIGHT_PX - (ROWS * img_h)) // (ROWS + 1)

        pages = []
        # Arrange images into pages
        for i in range(0, len(images), IMAGES_PER_PAGE):
            # Create a blank white A4 page
            page = Image.new('RGB', (A4_WIDTH_PX, A4_HEIGHT_PX), 'white')
            # Place each image in its grid position
            for j, img in enumerate(images[i:i+IMAGES_PER_PAGE]):
                row = j // COLS
                col = j % COLS
                x = h_space + col * (img_w + h_space)
                y = v_space + row * (img_h + v_space)
                page.paste(img, (x, y))
            pages.append(page)

        # Save all pages as a single PDF
        pages[0].save(PDF_FILE, save_all=True, append_images=pages[1:], resolution=DPI)
        print(f"✅ Created {PDF_FILE} with {len(pages)} page(s), {len(images)} QR codes.")
    else:
        print("No PNGs generated!")

if __name__ == "__main__":
    main()
