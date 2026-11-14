#!/usr/bin/env python3
"""Generate Diagram 1: The Harvest-Now-Decrypt-Later (HNDL) Threat Model in Institutional Finance."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "diagram_1_hndl_threat_model.png"
OUT.parent.mkdir(parents=True, exist_ok=True)
LOGO_PATH = ROOT.parent / "Brand_Guide" / "Rayls_Logo_Pack" / "PNG" / "Rayls_Logo_Black.png"

W, H = 1600, 900

C_PURPLE = (180, 154, 255, 255)   # #B49AFF
C_YELLOW = (236, 251, 62, 255)    # #ECFB3E
C_GREEN = (140, 247, 139, 255)    # #8CF78B
C_RED = (255, 107, 107, 255)      # #FF6B6B
C_BLACK = (17, 17, 20, 255)       # #111114
C_CARD = (24, 24, 28, 255)        # #18181C
C_BORDER = (55, 55, 65, 255)
C_WHITE = (255, 255, 255, 255)
C_MUTED = (205, 205, 218, 255)

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"


def make_signature_gradient(width: int, height: int, left_rgba, right_rgba) -> Image.Image:
    base = Image.new("RGBA", (width, height), left_rgba)
    top = Image.new("RGBA", (width, height), right_rgba)
    row = [int(255 * (x / (width - 1))) for x in range(width)]
    mask = Image.new("L", (width, height))
    mask.putdata(row * height)
    base.paste(top, (0, 0), mask)
    return base


def wrap_text_pixels(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list:
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = cur + " " + w if cur else w
        if font.getlength(test) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main() -> int:
    img = make_signature_gradient(W, H, C_PURPLE, C_YELLOW)
    draw = ImageDraw.Draw(img)

    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_h = 42
        logo_w = int(logo_h * logo.width / logo.height)
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        img.paste(logo, (W - logo_w - 76, 44), logo)

    f_pill = ImageFont.truetype(FONT_BOLD, 15)
    f_title = ImageFont.truetype(FONT_BOLD, 42)
    f_sub = ImageFont.truetype(FONT_REG, 21)
    f_lane_hdr = ImageFont.truetype(FONT_BOLD, 22)
    f_phase_tag = ImageFont.truetype(FONT_BOLD, 14)
    f_phase_hdr = ImageFont.truetype(FONT_BOLD, 18)
    f_body = ImageFont.truetype(FONT_REG, 15)

    # Top pill (dynamic width to prevent overflow)
    pill_text = "THREAT MODEL ANALYSIS | NIST FIPS 203"
    pill_w = int(f_pill.getlength(pill_text)) + 32
    draw.rounded_rectangle([76, 40, 76 + pill_w, 78], radius=8, fill=C_BLACK)
    draw.text((92, 48), pill_text, fill=C_YELLOW, font=f_pill)

    # Title
    draw.text((76, 96), "The Harvest-Now-Decrypt-Later (HNDL) Threat Vector", fill=C_BLACK, font=f_title)
    draw.text((76, 148), "Why 10-to-30 Year Institutional Contracts Require Immediate Post-Quantum Migration", fill=C_BLACK, font=f_sub)

    # Two Main Lanes (Top: Classical Vulnerability, Bottom: Rayls Post-Quantum Protection)
    lane_w = 1448
    lane_x0 = 76
    lane_x1 = lane_x0 + lane_w  # 1524

    # Symmetric card positioning inside lanes
    # Inner padding: 24px left and right. Usable width = 1448 - 48 = 1400px.
    # 3 cards * 450px = 1350px. 2 gaps * 25px = 50px. Total = 1400px.
    col_w = 450
    gap = 25
    inner_pad = 24
    content_w = col_w - 36  # 414px inside card

    # Lane 1: Classical Cryptography (X25519 / secp256k1)
    l1_y0, l1_y1 = 200, 500
    draw.rounded_rectangle([lane_x0, l1_y0, lane_x1, l1_y1], radius=16, fill=C_CARD, outline=C_BORDER, width=2)

    draw.rounded_rectangle([lane_x0 + 20, l1_y0 + 16, lane_x0 + 34, l1_y0 + 36], radius=3, fill=C_RED)
    draw.text((lane_x0 + 44, l1_y0 + 15), "CLASSICAL INFRASTRUCTURE (ECDH / secp256k1 / RSA)", fill=C_RED, font=f_lane_hdr)

    # 3 Phase Cards inside Lane 1
    p1_cards = [
        {
            "year": "PHASE 1: 2026 (EXECUTION & HARVEST)",
            "hdr": "Passive Traffic Interception",
            "text": "Banks issue 30-year TPFt bonds and syndicated credit. An adversary records encrypted calldata, public keys, and routing ciphertexts across the wire."
        },
        {
            "year": "PHASE 2: 2030s (QUANTUM EMERGENCE)",
            "hdr": "Cryptanalytic Quantum Computers",
            "text": "CRQCs running Shor's algorithm solve discrete logs and prime factorization in polynomial time, completely breaking elliptic curve cryptography."
        },
        {
            "year": "PHASE 3: RETROACTIVE BREACH",
            "hdr": "Statutory Confidentiality Failure",
            "text": "Historical trade amounts, bank client portfolios, and balances are decoded, triggering severe retroactive violations of Brazil LC 105/2001 and EU GDPR."
        }
    ]

    card_in_y0 = l1_y0 + 52
    card_in_y1 = l1_y1 - 18

    for i, c in enumerate(p1_cards):
        cx0 = lane_x0 + inner_pad + i * (col_w + gap)
        cx1 = cx0 + col_w
        draw.rounded_rectangle([cx0, card_in_y0, cx1, card_in_y1], radius=10, fill=(35, 30, 35, 255), outline=C_BORDER, width=1)
        draw.text((cx0 + 18, card_in_y0 + 16), c["year"], fill=C_YELLOW, font=f_phase_tag)
        draw.text((cx0 + 18, card_in_y0 + 42), c["hdr"], fill=C_WHITE, font=f_phase_hdr)
        draw.line([cx0 + 18, card_in_y0 + 72, cx1 - 18, card_in_y0 + 72], fill=C_BORDER, width=1)

        y = card_in_y0 + 86
        lines = wrap_text_pixels(c["text"], f_body, content_w)
        for line in lines:
            draw.text((cx0 + 18, y), line, fill=C_MUTED, font=f_body)
            y += 24

    # Lane 2: Rayls Enygma ML-KEM-768
    l2_y0, l2_y1 = 525, 825
    draw.rounded_rectangle([lane_x0, l2_y0, lane_x1, l2_y1], radius=16, fill=C_CARD, outline=C_BORDER, width=2)

    draw.rounded_rectangle([lane_x0 + 20, l2_y0 + 16, lane_x0 + 34, l2_y0 + 36], radius=3, fill=C_GREEN)
    draw.text((lane_x0 + 44, l2_y0 + 15), "RAYLS POST-QUANTUM ENCLAVE (NIST FIPS 203 ML-KEM-768)", fill=C_GREEN, font=f_lane_hdr)

    p2_cards = [
        {
            "year": "PHASE 1: 2026 (QUANTUM-SAFE SETUP)",
            "hdr": "Module-LWE Lattice Encapsulation",
            "text": "Banks register 1,184B encapsulation keys in Enygma.sol. Pairwise secrets are generated with FIPS 203 ML-KEM-768 (257 us warm encapsulation)."
        },
        {
            "year": "PHASE 2: 2030s (IMMUNE TO SHOR'S ALGO)",
            "hdr": "Lattice Hardness Holds Intact",
            "text": "Shor's algorithm cannot solve the Shortest Vector Problem (SVP) in high-dimensional lattices. Quantum computers gain no polynomial speedup."
        },
        {
            "year": "PHASE 3: PERPETUAL SECRECY",
            "hdr": "Zero Long-Term Liability",
            "text": "Banking secrecy remains mathematically sound across the entire 30-year maturity of sovereign bonds, syndicated loans, and Treasury deposits."
        }
    ]

    card2_in_y0 = l2_y0 + 52
    card2_in_y1 = l2_y1 - 18

    for i, c in enumerate(p2_cards):
        cx0 = lane_x0 + inner_pad + i * (col_w + gap)
        cx1 = cx0 + col_w
        draw.rounded_rectangle([cx0, card2_in_y0, cx1, card2_in_y1], radius=10, fill=(28, 35, 30, 255), outline=C_BORDER, width=1)
        draw.text((cx0 + 18, card2_in_y0 + 16), c["year"], fill=C_YELLOW, font=f_phase_tag)
        draw.text((cx0 + 18, card2_in_y0 + 42), c["hdr"], fill=C_WHITE, font=f_phase_hdr)
        draw.line([cx0 + 18, card2_in_y0 + 72, cx1 - 18, card2_in_y0 + 72], fill=C_BORDER, width=1)

        y = card2_in_y0 + 86
        lines = wrap_text_pixels(c["text"], f_body, content_w)
        for line in lines:
            draw.text((cx0 + 18, y), line, fill=C_MUTED, font=f_body)
            y += 24

    # Bottom footer safe zone
    draw.text((76, 848), "Rayls Enygma Security Architecture | Pinned Upstream Commit @ a9b06c00 | Deterministic Proofs", fill=C_BLACK, font=f_body)

    img.save(OUT, "PNG")
    print(f"Diagram 1 saved to: {OUT}")
    return 0


if __name__ == "__main__":
    main()
