"""Compose the real Flutter widget captures into three feature boards.

Run after feature_screenshots_test.dart with CAPTURE_SCREENSHOTS=true.
Requires Pillow. Source logo files are read only.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "screenshots"
RAW = OUT / "raw"
WIDTH, HEIGHT = 2560, 1660
FOREST = "#002D26"
MINT = "#83F5CE"
PALE = "#B7D4C8"
FONT_DIR = Path("C:/Windows/Fonts")


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_DIR / ("segoeuib.ttf" if bold else "segoeui.ttf")), size)


def centered(draw, center, y, text, size, fill, bold=False):
    f = font(size, bold)
    box = draw.textbbox((0, 0), text, font=f)
    draw.text((center - (box[2] - box[0]) / 2, y), text, font=f, fill=fill)


def make_board(filename, number, title, account, screens):
    board = Image.new("RGB", (WIDTH, HEIGHT), "#001F1B")
    draw = ImageDraw.Draw(board)
    draw.ellipse((1680, -590, 3000, 700), fill="#043A2E")
    draw.ellipse((-650, 1210, 960, 2760), fill="#032E27")
    draw.rounded_rectangle((116, 78, 166, 128), radius=14, fill=MINT)
    centered(draw, 141, 82, f"0{number}", 25, FOREST, True)
    draw.text((187, 82), "AGAL  /  FEATURE SHOWCASE", font=font(24, True), fill=MINT)
    draw.text((116, 144), title, font=font(78, True), fill="white")
    draw.text((120, 250), account, font=font(30), fill=PALE)
    draw.rounded_rectangle((2228, 88, 2430, 136), radius=24, fill="#164D3D")
    centered(draw, 2329, 95, "MOCK DATA", 21, MINT, True)

    phone_width = 500
    phone_height = round(phone_width * 896 / 414)
    gap = 96 if len(screens) == 4 else 150
    start = (WIDTH - (phone_width * len(screens) + gap * (len(screens) - 1))) // 2
    for i, (source, caption, detail) in enumerate(screens):
        x, y = start + i * (phone_width + gap), 352
        draw.rounded_rectangle((x - 13, y - 13, x + phone_width + 13, y + phone_height + 13), radius=47, fill="#111E1B", outline="#456B5A", width=3)
        image = Image.open(RAW / f"{source}.png").convert("RGB")
        image = ImageOps.fit(image, (phone_width, phone_height), method=Image.Resampling.LANCZOS)
        mask = Image.new("L", image.size)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, phone_width - 1, phone_height - 1), radius=36, fill=255)
        board.paste(image, (x, y), mask)
        centered(draw, x + phone_width / 2, 1470, caption, 28, "white", True)
        centered(draw, x + phone_width / 2, 1515, detail, 23, PALE)

    draw.line((116, 1591, 2440, 1591), fill="#265144", width=2)
    draw.text((120, 1611), "Flutter screen captures · Demo accounts, prices, payments and verification results", font=font(20), fill=PALE)
    draw.text((2254, 1606), "AGAL", font=font(28, True), fill=MINT)
    path = OUT / filename
    board.save(path, optimize=True)
    print(f"Saved {path} ({WIDTH} × {HEIGHT})")


def main():
    if not RAW.is_dir():
        raise SystemExit("Run the Flutter screenshot capture test first.")
    make_board("01_agal_app_sms_farmer.png", 1, "Agal app + SMS", "Junrey Gonzales  ·  Farmer mock account", [
        ("farmer_dashboard", "Your offline dashboard", "Harvest records stay on your phone"),
        ("farmer_log_harvest_offline", "Log a harvest offline", "Species, weight, date and GPS"),
        ("farmer_buying_prices", "Today’s buying prices", "Compare posted offers per kilo"),
        ("farmer_sms_chat", "Keep in touch by SMS", "Open the phone’s SMS composer"),
    ])
    make_board("02_supplier_dashboard_shipments.png", 2, "Supplier dashboard", "Hamsya Igasan  ·  Trader / supplier mock account", [
        ("supplier_dashboard", "Sales & batch inventory", "A clear view of recorded trades"),
        ("supplier_bundle_shipment", "Bundle batches together", "Choose inventory and a destination"),
        ("supplier_shipment_recorded", "Record a shipment manifest", "Shared references in each batch history"),
    ])
    make_board("03_batch_verification_provenance.png", 3, "Batch verification", "Krishane Ann Remonde  ·  Exporter / buyer mock account", [
        ("exporter_marketplace", "Find a batch", "Browse available harvests"),
        ("batch_verification_origin", "Check its origin", "Farmer, harvest date and quality"),
        ("batch_verification_full_history", "Follow the handling history", "Custody, payment and shipment records"),
    ])


if __name__ == "__main__":
    main()
