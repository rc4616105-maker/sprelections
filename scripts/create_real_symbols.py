import os
from PIL import Image, ImageDraw, ImageFont

SYMBOLS = {
    "peacock": ("🦚", "#0284c7", "#0369a1", "PEACOCK"),
    "royal_bengal_tiger": ("🐅", "#ea580c", "#c2410c", "TIGER"),
    "tiger": ("🐅", "#ea580c", "#c2410c", "TIGER"),
    "mango": ("🥭", "#f59e0b", "#d97706", "MANGO"),
    "banyan_tree": ("🌳", "#16a34a", "#15803d", "BANYAN TREE"),
    "ashoka_chakra": ("☸️", "#1d4ed8", "#1e40af", "ASHOKA CHAKRA"),
    "ashok_chakra": ("☸️", "#1d4ed8", "#1e40af", "ASHOKA CHAKRA"),
    "hockey_stick": ("🏑", "#0891b2", "#0e7490", "HOCKEY STICK"),
    "dolphin": ("🐬", "#06b6d4", "#0891b2", "DOLPHIN"),
    "pumpkin": ("🎃", "#f97316", "#ea580c", "PUMPKIN"),
    "ganga_river": ("🌊", "#3b82f6", "#2563eb", "GANGA RIVER"),
}

os.makedirs("Houses/assets/symbols", exist_ok=True)

# Find system font
font_path = "C:/Windows/Fonts/seguiemj.ttf" # Windows Segoe UI Emoji
has_emoji_font = os.path.exists(font_path)

for name, (emoji, bg1, bg2, label) in SYMBOLS.items():
    img = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer circle with subtle gradient or shadow ring
    draw.ellipse([8, 8, 248, 248], fill=bg1, outline="#ffffff", width=4)
    # Inner circular badge
    draw.ellipse([18, 18, 238, 238], fill="#ffffff")
    
    # Draw Emoji if font available
    drawn_emoji = False
    if has_emoji_font:
        try:
            e_font = ImageFont.truetype(font_path, 110)
            bbox = draw.textbbox((0, 0), emoji, font=e_font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (256 - w) / 2 - bbox[0]
            y = 45 - bbox[1]
            draw.text((x, y), emoji, font=e_font, embedded_color=True)
            drawn_emoji = True
        except Exception as e:
            pass
            
    if not drawn_emoji:
        # Fallback drawn icon / symbol
        draw.ellipse([64, 50, 192, 178], fill=bg1)
        
    # Text label banner at bottom
    try:
        t_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 20)
    except:
        t_font = ImageFont.load_default()
        
    t_bbox = draw.textbbox((0, 0), label, font=t_font)
    tw = t_bbox[2] - t_bbox[0]
    tx = (256 - tw) / 2
    ty = 195
    
    # Badge background for label
    draw.rounded_rectangle([tx - 12, ty - 4, tx + tw + 12, ty + 28], radius=8, fill=bg1)
    draw.text((tx, ty), label, fill="#ffffff", font=t_font)
    
    out_path = f"Houses/assets/symbols/{name}.png"
    img.save(out_path, "PNG")
    print(f"Generated symbol: {out_path}")
