"""Tekent de app-iconen (Pillow). Gebruik: python tools/iconen.py"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

UIT = Path(__file__).resolve().parent.parent / "app" / "icons"
DONKER, LICHT, WIT = (13, 59, 44), (154, 216, 176), (255, 255, 255)

def teken(maat, rond=True, schaal=1.0):
    S = maat * 4  # supersampling
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if rond: d.rounded_rectangle([0, 0, S, S], radius=S * .22, fill=DONKER)
    else: d.rectangle([0, 0, S, S], fill=DONKER)
    c, r, w = S / 2, S * .33 * schaal, S * .055 * schaal
    # drie boogsegmenten met pijlpunten (kringloop)
    for k in range(3):
        start = k * 120 + 15
        d.arc([c - r, c - r, c + r, c + r], start, start + 85, fill=LICHT, width=int(w))
        a = math.radians(start + 85)
        px, py = c + r * math.cos(a), c + r * math.sin(a)
        t = a + math.pi / 2  # raakrichting
        L = w * 1.6
        punt = (px + L * math.cos(t), py + L * math.sin(t))
        links = (px + L * .9 * math.cos(a), py + L * .9 * math.sin(a))
        rechts = (px - L * .9 * math.cos(a), py - L * .9 * math.sin(a))
        d.polygon([punt, links, rechts], fill=LICHT)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", int(S * .26 * schaal))
    d.text((c, c + S * .01), "CE", font=font, fill=WIT, anchor="mm")
    return img.resize((maat, maat), Image.LANCZOS)

UIT.mkdir(parents=True, exist_ok=True)
teken(192).save(UIT / "icon-192.png")
teken(512).save(UIT / "icon-512.png")
teken(512, rond=False, schaal=.8).save(UIT / "icon-maskable-512.png")
teken(180, rond=False).convert("RGB").save(UIT / "apple-touch-icon.png")
print("iconen klaar")
