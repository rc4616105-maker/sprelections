"""
Generate crisp, high-resolution election symbol graphic images (256x256 PNGs)
for EVM ballot strips and kiosk candidate displays.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SYMBOLS_DIR = ROOT / "Houses" / "assets" / "symbols"
RESULT_SYMBOLS_DIR = ROOT / "Result declaration" / "assets" / "symbols"

SYMBOLS_DIR.mkdir(parents=True, exist_ok=True)
RESULT_SYMBOLS_DIR.mkdir(parents=True, exist_ok=True)

CANVAS_SIZE = 512
FINAL_SIZE = 256


def create_canvas():
    return Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (255, 255, 255, 0))


def save_symbol(img, slug):
    resized = img.resize((FINAL_SIZE, FINAL_SIZE), Image.Resampling.LANCZOS)
    p1 = SYMBOLS_DIR / f"{slug}.png"
    p2 = RESULT_SYMBOLS_DIR / f"{slug}.png"
    resized.save(p1, "PNG")
    resized.save(p2, "PNG")
    print(f"Generated: {slug}.png")


def draw_torch():
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    # Background badge circle
    draw.ellipse([32, 32, 480, 480], fill="#fff7ed", outline="#ea580c", width=14)
    # Torch handle
    draw.polygon([(220, 240), (292, 240), (276, 420), (236, 420)], fill="#d97706", outline="#9a3412")
    draw.rectangle([210, 220, 302, 245], fill="#b45309", outline="#78350f", width=4)
    draw.rounded_rectangle([226, 415, 286, 435], radius=6, fill="#78350f")
    # Grip rings
    for y in [270, 310, 350, 390]:
        draw.line([(228, y), (284, y)], fill="#fed7aa", width=6)
    # Flames
    # Outer orange flame
    draw.polygon([(256, 70), (320, 150), (330, 220), (256, 225), (182, 220), (192, 150)], fill="#ea580c")
    # Middle amber flame
    draw.polygon([(256, 100), (305, 165), (295, 222), (217, 222), (207, 165)], fill="#f59e0b")
    # Inner yellow core
    draw.polygon([(256, 130), (285, 180), (280, 222), (232, 222), (227, 180)], fill="#fef08a")
    return img


def draw_shield():
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw.ellipse([32, 32, 480, 480], fill="#eff6ff", outline="#2563eb", width=14)
    # Classic shield polygon
    pts = [
        (130, 120), (382, 120), (382, 260),
        (256, 420),
        (130, 260)
    ]
    draw.polygon(pts, fill="#1d4ed8", outline="#1e3a8a", width=12)
    # Inner shield accent
    pts_inner = [
        (150, 140), (362, 140), (362, 255),
        (256, 395),
        (150, 255)
    ]
    draw.polygon(pts_inner, fill="#2563eb")
    # Shield heraldic cross / divider
    draw.rectangle([244, 140, 268, 390], fill="#fbbf24")
    draw.rectangle([150, 215, 362, 240], fill="#fbbf24")
    # Center star
    draw.polygon([
        (256, 195), (263, 217), (286, 217), (268, 230),
        (274, 252), (256, 239), (238, 252), (244, 230),
        (226, 217), (249, 217)
    ], fill="#ffffff")
    return img


def draw_rising_sun():
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw.ellipse([32, 32, 480, 480], fill="#fefce8", outline="#ca8a04", width=14)
    # Sun rays
    cx, cy = 256, 280
    ray_len = 160
    for deg in range(0, 185, 20):
        rad = math.radians(deg)
        x1 = cx + math.cos(rad) * 60
        y1 = cy - math.sin(rad) * 60
        x2 = cx + math.cos(rad) * ray_len
        y2 = cy - math.sin(rad) * ray_len
        draw.line([(x1, y1), (x2, y2)], fill="#f59e0b", width=12)
    # Half sun disc
    draw.pieslice([156, 180, 356, 380], start=180, end=360, fill="#eab308", outline="#ca8a04", width=8)
    # Mountains / Horizon in front
    draw.polygon([(80, 360), (190, 270), (280, 340), (380, 260), (440, 360)], fill="#047857")
    draw.polygon([(70, 350), (170, 290), (270, 360), (440, 360)], fill="#065f46")
    # Base sea / ground waves
    draw.rectangle([70, 350, 442, 420], fill="#0284c7")
    for y in [370, 390, 410]:
        draw.line([(85, y), (427, y)], fill="#bae6fd", width=6)
    return img


def draw_book():
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw.ellipse([32, 32, 480, 480], fill="#f8fafc", outline="#475569", width=14)
    # Book covers (open)
    draw.polygon([(256, 180), (100, 160), (90, 340), (256, 365)], fill="#0f172a", outline="#334155", width=6)
    draw.polygon([(256, 180), (412, 160), (422, 340), (256, 365)], fill="#0f172a", outline="#334155", width=6)
    # Pages (cream / white)
    draw.polygon([(256, 170), (110, 150), (100, 325), (256, 350)], fill="#ffffff", outline="#cbd5e1", width=4)
    draw.polygon([(256, 170), (402, 150), (412, 325), (256, 350)], fill="#f8fafc", outline="#cbd5e1", width=4)
    # Text lines on left page
    for y in [190, 220, 250, 280, 310]:
        draw.line([(130, y - 10), (235, y)], fill="#94a3b8", width=5)
    # Text lines on right page
    for y in [190, 220, 250, 280, 310]:
        draw.line([(275, y), (380, y - 10)], fill="#94a3b8", width=5)
    # Bookmark ribbon
    draw.polygon([(256, 170), (266, 170), (272, 300), (260, 285), (248, 300), (254, 170)], fill="#dc2626")
    return img


def draw_star():
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw.ellipse([32, 32, 480, 480], fill="#fefce8", outline="#eab308", width=14)
    cx, cy = 256, 256
    pts = []
    for i in range(10):
        r = 175 if i % 2 == 0 else 75
        angle = math.radians(i * 36 - 90)
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill="#fbbf24", outline="#d97706", width=10)
    # Inner highlight facets
    for i in range(0, 10, 2):
        tip = pts[i]
        valley1 = pts[(i + 9) % 10]
        valley2 = pts[(i + 1) % 10]
        draw.polygon([tip, (cx, cy), valley1], fill="#f59e0b")
        draw.polygon([tip, (cx, cy), valley2], fill="#fde047")
    return img


def draw_trophy():
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw.ellipse([32, 32, 480, 480], fill="#fffbeb", outline="#b45309", width=14)
    # Base pedestal
    draw.rectangle([170, 390, 342, 435], fill="#78350f", outline="#451a03", width=6)
    draw.rectangle([190, 350, 322, 390], fill="#9a3412", outline="#78350f", width=5)
    draw.polygon([(240, 280), (272, 280), (280, 350), (232, 350)], fill="#d97706")
    # Handles
    draw.arc([100, 130, 210, 260], start=90, end=270, fill="#b45309", width=18)
    draw.arc([302, 130, 412, 260], start=270, end=90, fill="#b45309", width=18)
    # Main cup
    draw.polygon([
        (160, 120), (352, 120), (330, 260),
        (256, 295), (182, 260)
    ], fill="#fbbf24", outline="#b45309", width=8)
    # Cup rim
    draw.ellipse([160, 108, 352, 132], fill="#fde047", outline="#b45309", width=6)
    # Star emblem on trophy
    draw.polygon([
        (256, 185), (261, 200), (276, 200), (264, 210),
        (268, 225), (256, 216), (244, 225), (248, 210),
        (236, 200), (251, 200)
    ], fill="#ffffff")
    return img


def draw_tree():
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw.ellipse([32, 32, 480, 480], fill="#f0fdf4", outline="#15803d", width=14)
    # Trunk
    draw.polygon([(230, 260), (282, 260), (300, 420), (212, 420)], fill="#78350f", outline="#451a03", width=6)
    # Tree ground
    draw.ellipse([140, 400, 372, 435], fill="#166534")
    # Canopy foliage clusters
    clusters = [
        (256, 150, 105, "#15803d"),
        (175, 225, 95, "#16a34a"),
        (337, 225, 95, "#16a34a"),
        (210, 275, 85, "#22c55e"),
        (302, 275, 85, "#22c55e"),
        (256, 210, 105, "#15803d"),
    ]
    for cx, cy, r, col in clusters:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline="#14532d", width=6)
    return img


def draw_bell():
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw.ellipse([32, 32, 480, 480], fill="#fefce8", outline="#ca8a04", width=14)
    # Top loop
    draw.ellipse([230, 80, 282, 135], outline="#854d0e", width=12)
    # Clapper ball
    draw.ellipse([236, 390, 276, 430], fill="#854d0e")
    # Bell body
    draw.polygon([
        (236, 125), (276, 125),
        (300, 170), (345, 330),
        (375, 365), (137, 365),
        (167, 330), (212, 170)
    ], fill="#eab308", outline="#a16207", width=10)
    # Rim band
    draw.rounded_rectangle([132, 355, 380, 385], radius=8, fill="#ca8a04", outline="#713f12", width=5)
    # Highlight
    draw.line([(200, 180), (170, 340)], fill="#fef08a", width=12)
    return img


def draw_rocket():
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw.ellipse([32, 32, 480, 480], fill="#f0f9ff", outline="#0284c7", width=14)
    # Booster exhaust flame
    draw.polygon([(256, 450), (280, 385), (232, 385)], fill="#ea580c")
    draw.polygon([(256, 420), (270, 385), (242, 385)], fill="#facc15")
    # Side fins
    draw.polygon([(170, 380), (220, 280), (220, 380)], fill="#dc2626", outline="#991b1b", width=5)
    draw.polygon([(342, 380), (292, 280), (292, 380)], fill="#dc2626", outline="#991b1b", width=5)
    # Fuselage body
    draw.polygon([
        (256, 85),
        (310, 190), (305, 385),
        (207, 385), (202, 190)
    ], fill="#f8fafc", outline="#334155", width=8)
    # Nose cone
    draw.polygon([(256, 85), (298, 170), (214, 170)], fill="#dc2626")
    # Porthole window
    draw.ellipse([228, 205, 284, 261], fill="#38bdf8", outline="#0284c7", width=8)
    draw.ellipse([238, 215, 252, 229], fill="#ffffff")
    return img


def draw_compass():
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw.ellipse([32, 32, 480, 480], fill="#f8fafc", outline="#0f172a", width=14)
    # Compass dial ring
    draw.ellipse([70, 70, 442, 442], fill="#f1f5f9", outline="#64748b", width=8)
    # Degree tick marks
    cx, cy = 256, 256
    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        x1 = cx + math.cos(rad) * 165
        y1 = cy + math.sin(rad) * 165
        x2 = cx + math.cos(rad) * 180
        y2 = cy + math.sin(rad) * 180
        draw.line([(x1, y1), (x2, y2)], fill="#475569", width=4)
    # Needle: North (Red) & South (Silver)
    # North
    draw.polygon([(256, 100), (275, 256), (256, 240), (237, 256)], fill="#dc2626", outline="#991b1b", width=4)
    # South
    draw.polygon([(256, 412), (275, 256), (256, 272), (237, 256)], fill="#94a3b8", outline="#475569", width=4)
    # Center pivot
    draw.ellipse([244, 244, 268, 268], fill="#f59e0b", outline="#b45309", width=4)
    return img


def main():
    generators = {
        "torch": draw_torch,
        "shield": draw_shield,
        "rising_sun": draw_rising_sun,
        "book": draw_book,
        "star": draw_star,
        "trophy": draw_trophy,
        "tree": draw_tree,
        "bell": draw_bell,
        "rocket": draw_rocket,
        "compass": draw_compass,
    }
    for slug, fn in generators.items():
        img = fn()
        save_symbol(img, slug)
    print("All 10 election symbols successfully generated!")


if __name__ == "__main__":
    main()
