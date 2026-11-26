#!/usr/bin/env python3
"""Draw the social sharing image (assets/img/og.png) once. Skipped when the file exists."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

out = Path(__file__).resolve().parent.parent / "assets" / "img" / "og.png"
if not out.exists():
    INK, YEL, WHITE, BLUE = "#1D2327", "#FFD21F", "#FFFFFF", "#1857C4"
    im = Image.new("RGB", (1200, 630), "#E9EDEE")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 40, 1160, 590), 36, fill=YEL, outline=INK, width=10)
    d.text((100, 110), "Know it fits", font=ImageFont.load_default(size=104), fill=INK)
    d.text((100, 225), "before you lift it.", font=ImageFont.load_default(size=104), fill=INK)
    d.text((100, 372), "Free load calculators: truck size, payload,", font=ImageFont.load_default(size=40), fill=INK)
    d.text((100, 424), "towing, tie-downs, fuel, pallets, freight class", font=ImageFont.load_default(size=40), fill=INK)
    d.rounded_rectangle((100, 492, 470, 556), 10, fill=INK)
    d.text((124, 504), "LoadandGo.com", font=ImageFont.load_default(size=40), fill=WHITE)
    d.rounded_rectangle((860, 140, 1060, 280), 6, fill=WHITE, outline=INK, width=8)
    d.rectangle((868, 148, 1000, 272), fill=BLUE)
    d.polygon([(1064, 180), (1110, 180), (1144, 220), (1144, 280), (1064, 280)], fill=WHITE, outline=INK, width=8)
    for cx in (910, 1104):
        d.ellipse((cx - 26, 264, cx + 26, 316), fill=INK)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, optimize=True)
    print("wrote", out)
