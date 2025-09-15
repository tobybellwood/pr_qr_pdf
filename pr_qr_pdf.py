import sys
import re
from pathlib import Path
import segno
from cairosvg import svg2png
from PIL import Image
import argparse

SVG_DIR = Path("qr_svgs")
PNG_DIR = Path("qr_pngs")
PDF_FILE = "qr_codes.pdf"
SIZE_W, SIZE_H, QR_SIZE = 400, 600, 300
DPI = 300
A4_WIDTH_PX = int(210 / 25.4 * DPI)
A4_HEIGHT_PX = int(297 / 25.4 * DPI)
COLS, ROWS = 5, 5
IMAGES_PER_PAGE = COLS * ROWS

def generate_qr_svg(code: str, size_w=SIZE_W, size_h=SIZE_H, qr_size=QR_SIZE):
    y_offset = 100
    qr_x = (size_w - qr_size) // 2
    qr_y = (size_h - qr_size) // 2 + y_offset
    label_font_size = int(size_w * 0.10)
    label_y = qr_y + qr_size
    qr = segno.make(code, error='m', micro=False)
    scale = qr_size / qr.symbol_size(1)[0]
    qr_svg = qr.svg_inline(scale=scale, omitsize=True, dark='black', light='white')
    if qr_svg.startswith('<?xml'):
        qr_svg = qr_svg.split('?>', 1)[1]
    inner = re.sub(r'^.*?<svg[^>]*>', '', qr_svg, flags=re.DOTALL)
    inner = re.sub(r'</svg>\s*$', '', inner, flags=re.DOTALL)
    return f'''<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size_w}" height="{size_h}" viewBox="0 0 {size_w} {size_h}">
    <rect width="100%" height="100%" fill="white"/>
    <rect x="1" y="1" width="{size_w-2}" height="{size_h-2}" fill="none" stroke="black" stroke-width="2"/>
    <circle cx="{size_w*0.5}" cy="{size_h*0.1}" r="{size_w*0.05}" fill="none" stroke="black" stroke-width="2"/>
    <g transform="translate({qr_x},{qr_y})">{inner.strip()}</g>
    <text x="{size_w//2}" y="{label_y}" font-size="{label_font_size}" font-family="Helvetica, Arial, sans-serif" text-anchor="middle" fill="black">{code}</text>
</svg>'''

def code_generator(start, end):
    for i in range(start, end + 1):
        yield f"P{i:04d}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start", nargs="?", type=int, default=301)
    parser.add_argument("end", nargs="?", type=int, default=500)
    args = parser.parse_args()

    SVG_DIR.mkdir(exist_ok=True)
    PNG_DIR.mkdir(exist_ok=True)

    png_paths = []
    for code in code_generator(args.start, args.end):
        svg_path = SVG_DIR / f"{code}.svg"
        png_path = PNG_DIR / f"{code}.png"
        svg_data = generate_qr_svg(code)
        svg_path.write_text(svg_data, encoding='utf-8')
        svg2png(bytestring=svg_data.encode('utf-8'), write_to=str(png_path), output_width=SIZE_W, output_height=SIZE_H)
        png_paths.append(png_path)

    images = []
    for p in png_paths:
        with Image.open(p) as img:
            images.append(img.convert('RGB'))

    if images:
        h_space = (A4_WIDTH_PX - (COLS * SIZE_W)) // (COLS + 1)
        v_space = (A4_HEIGHT_PX - (ROWS * SIZE_H)) // (ROWS + 1)
        pages = []
        for i in range(0, len(images), IMAGES_PER_PAGE):
            page = Image.new('RGB', (A4_WIDTH_PX, A4_HEIGHT_PX), 'white')
            for j, img in enumerate(images[i:i+IMAGES_PER_PAGE]):
                row, col = divmod(j, COLS)
                x = h_space + col * (SIZE_W + h_space)
                y = v_space + row * (SIZE_H + v_space)
                page.paste(img, (x, y))
            pages.append(page)
        pages[0].save(PDF_FILE, save_all=True, append_images=pages[1:], resolution=DPI)
        print(f"✅ Created {PDF_FILE} with {len(pages)} page(s), {len(images)} QR codes.")
    else:
        print("No PNGs generated!")

if __name__ == "__main__":
    main()
