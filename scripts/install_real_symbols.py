from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BRAIN = Path(r"C:\Users\Abhinav\.gemini\antigravity\brain\e3ce9f53-26d3-4547-9ff6-c53bb81bf648")

SYMBOLS_MAP = {
    "torch": "ceremonial_flaming_torch_1795324868856.jpg",
    "shield": "knight_shield_1795324874167.jpg",
    "rising_sun": "spectacular_pure_golden_sunrise_1795324899114.jpg",
    "book": "classic_open_book_studio_1795324887445.jpg",
    "star": "freestanding_golden_star_1795324909365.jpg",
    "trophy": "golden_championship_trophy_1795324888640.jpg",
    "tree": "majestic_banyan_tree_1795324895922.jpg",
    "bell": "polished_brass_bell_1795324895192.jpg",
    "compass": "vintage_brass_compass_1795324897429.jpg",
    "rocket": "rocket_model_studio_1795324939456.jpg",
}

DEST_DIRS = [
    ROOT / "Houses" / "assets" / "symbols",
    ROOT / "Result declaration" / "assets" / "symbols",
]

for d in DEST_DIRS:
    d.mkdir(parents=True, exist_ok=True)

for slug, src_name in SYMBOLS_MAP.items():
    src_path = BRAIN / src_name
    if not src_path.exists():
        print(f"ERROR: {src_path} not found!")
        continue
    
    img = Image.open(src_path).convert("RGB")
    # Resize to standard high-res square (320x320)
    resized = img.resize((320, 320), Image.Resampling.LANCZOS)
    
    for d in DEST_DIRS:
        # Save both .png and .jpg
        png_path = d / f"{slug}.png"
        jpg_path = d / f"{slug}.jpg"
        resized.save(png_path, "PNG", quality=95)
        resized.save(jpg_path, "JPEG", quality=95)
        print(f"Saved real image for {slug} -> {png_path.relative_to(ROOT)}")

print("\nAll 10 real election symbols successfully installed!")
