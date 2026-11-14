#!/usr/bin/env python3
"""Generate Cover Image for Week 8 using the Full-Bleed Rayls Signature Gradient (#B49AFF -> #ECFB3E)."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "cover_image_post_quantum.png"
OUT.parent.mkdir(parents=True, exist_ok=True)
LOGO_PATH = ROOT.parent / "Brand_Guide" / "Rayls_Logo_Pack" / "PNG" / "Rayls_Logo_Black.png"

W, H = 1600, 900

C_PURPLE = (180, 154, 255, 255)   # #B49AFF
C_YELLOW = (236, 251, 62, 255)    # #ECFB3E
C_GREEN = (140, 247, 139, 255)    # #8CF78B
C_BLACK = (17, 17, 20, 255)       # #111114
C_CARD = (24, 24, 28, 255)        # #18181C
C_BORDER = (55, 55, 65, 255)
C_WHITE = (255, 255, 255, 255)
C_MUTED = (205, 205, 218, 255)

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"


def make_signature_gradient(width: int, height: int, left_rgba, right_rgba) -> Image.Image:
    base = Image.new("RGBA", (width, height), left_rgba)
    top = Image.new("RGBA", (width, height), right_rgba)
    row = [int(255 * (x / (width - 1))) for x in range(width)]
    mask = Image.new("L", (width, height))
    mask.putdata(row * height)
    base.paste(top, (0, 0), mask)
    return base


def main() -> int:
    img = make_signature_gradient(W, H, C_PURPLE, C_YELLOW)
    draw = ImageDraw.Draw(img)

    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_h = 46
        logo_w = int(logo_h * logo.width / logo.height)
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        img.paste(logo, (W - logo_w - 76, 46), logo)

    f_pill = ImageFont.truetype(FONT_BOLD, 16)
    f_title = ImageFont.truetype(FONT_BOLD, 50)
    f_sub = ImageFont.truetype(FONT_REG, 23)
    f_label = ImageFont.truetype(FONT_BOLD, 15)
    f_stat = ImageFont.truetype(FONT_BOLD, 38)
    f_stat_lbl = ImageFont.truetype(FONT_REG, 15)
    f_body = ImageFont.truetype(FONT_REG, 15)
    f_badge = ImageFont.truetype(FONT_BOLD, 14)

    # Main title (Top pill removed per design refinement)
    draw.text((76, 90), "Post-Quantum Banking: Neutralizing", fill=C_BLACK, font=f_title)
    draw.text((76, 152), "Harvest-Now-Decrypt-Later (HNDL) Attacks", fill=C_BLACK, font=f_title)

    draw.text((76, 230), "NIST FIPS 203 ML-KEM-768, Lattice-to-ZK Field Reductions, and EVM Calldata Economics on Rayls", fill=C_BLACK, font=f_sub)

    # 3 Metrics Cards
    card_y0, card_y1 = 330, 770
    card_w = 448
    gap = 22

    cards = [
        {
            "tag": "RAYLS MAINNET (CHAIN 72957)",
            "stat": "1.341s Mean",
            "stat_lbl": "Canonical Cadence (N = 1,000 blocks)",
            "lines": [
                "1,000 canonical blocks (#14,547,826 - #14,548,825)",
                "999/999 unbroken parent links, 0-block finalized lag",
                "500M gas ceiling; 57.60 Gwei baseline gasPrice",
                "ConsensusRegistry (21,929 B), FeeAggregator (122 B)"
            ],
            "accent": C_YELLOW,
        },
        {
            "tag": "NIST FIPS 203 ML-KEM-768",
            "stat": "257 us Encap",
            "stat_lbl": "26.8% faster than classical X25519 (N=500)",
            "lines": [
                "1,184 B Encapsulation Key (public view key)",
                "1,088 B Ciphertext (KEM ciphertext payload)",
                "Warm Median: Keygen=223.6 us, Decap=232.0 us",
                "Sub-millisecond latency preserves banking SLAs"
            ],
            "accent": C_PURPLE,
        },
        {
            "tag": "ENYGMA LATTICE-TO-ZK PIPELINE",
            "stat": "1.30 us Field",
            "stat_lbl": "Baby Jubjub scalar reduction (curveP)",
            "lines": [
                "toFieldElement maps 32B shared secret to curveP",
                "Fix M-11: mutual confirmation hash id verifies peer",
                "Enygma.sol strictly enforces 1184-byte view keys",
                "Foundry: 8/8 invariant passes (CRIT-PQ1 to PQ4)"
            ],
            "accent": C_GREEN,
        },
    ]

    for i, c in enumerate(cards):
        cx0 = 76 + i * (card_w + gap)
        cx1 = cx0 + card_w
        draw.rounded_rectangle([cx0, card_y0, cx1, card_y1], radius=18, fill=C_CARD, outline=C_BORDER, width=2)

        draw.rounded_rectangle([cx0 + 20, card_y0 + 20, cx0 + 20 + 12, card_y0 + 36], radius=3, fill=c["accent"])
        draw.text((cx0 + 40, card_y0 + 20), c["tag"], fill=C_MUTED, font=f_label)

        draw.text((cx0 + 22, card_y0 + 58), c["stat"], fill=C_WHITE, font=f_stat)
        draw.text((cx0 + 24, card_y0 + 104), c["stat_lbl"], fill=C_YELLOW, font=f_stat_lbl)

        draw.line([cx0 + 22, card_y0 + 134, cx1 - 22, card_y0 + 134], fill=C_BORDER, width=1)

        y_text = card_y0 + 154
        for line in c["lines"]:
            draw.text((cx0 + 24, y_text), f"- {line}", fill=C_MUTED, font=f_body)
            y_text += 48

    # Bottom pill
    draw.rounded_rectangle([76, 804, 340, 848], radius=10, fill=C_BLACK)
    draw.text((92, 815), "Verified Empirical Research", fill=C_YELLOW, font=f_badge)

    img.save(OUT, "PNG")
    print(f"Cover image saved to: {OUT}")
    return 0


if __name__ == "__main__":
    main()
