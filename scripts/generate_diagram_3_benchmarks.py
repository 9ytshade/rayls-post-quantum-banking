#!/usr/bin/env python3
"""Generate Diagram 3: Post-Quantum vs Classical Empirical Benchmarks & Calldata Economics."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "diagram_3_pq_empirical_benchmarks.png"
OUT.parent.mkdir(parents=True, exist_ok=True)
LOGO_PATH = ROOT.parent / "Brand_Guide" / "Rayls_Logo_Pack" / "PNG" / "Rayls_Logo_Black.png"

W, H = 1600, 900

C_PURPLE = (180, 154, 255, 255)   # #B49AFF
C_YELLOW = (236, 251, 62, 255)    # #ECFB3E
C_GREEN = (140, 247, 139, 255)    # #8CF78B
C_BLUE = (120, 200, 255, 255)     # #78C8FF
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
        logo_h = 42
        logo_w = int(logo_h * logo.width / logo.height)
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        img.paste(logo, (W - logo_w - 76, 44), logo)

    f_pill = ImageFont.truetype(FONT_BOLD, 15)
    f_title = ImageFont.truetype(FONT_BOLD, 42)
    f_sub = ImageFont.truetype(FONT_REG, 21)
    f_card_hdr = ImageFont.truetype(FONT_BOLD, 22)
    f_stat = ImageFont.truetype(FONT_BOLD, 36)
    f_stat_lbl = ImageFont.truetype(FONT_REG, 15)
    f_th = ImageFont.truetype(FONT_BOLD, 15)
    f_td = ImageFont.truetype(FONT_REG, 15)
    f_mono = ImageFont.truetype(FONT_MONO, 14)
    f_body = ImageFont.truetype(FONT_REG, 15)

    # Top pill (dynamic width to prevent overflow)
    pill_text = "EMPIRICAL BENCHMARK | N = 500 ITERATIONS"
    pill_w = int(f_pill.getlength(pill_text)) + 36
    draw.rounded_rectangle([76, 40, 76 + pill_w, 78], radius=8, fill=C_BLACK)
    draw.text((92, 48), pill_text, fill=C_YELLOW, font=f_pill)

    # Title
    draw.text((76, 96), "Post-Quantum vs Classical Performance & Calldata Costs", fill=C_BLACK, font=f_title)
    draw.text((76, 148), "Measured on Consumer Hardware (i3-3110M @ 2.40 GHz) and Live Rayls Mainnet 72957", fill=C_BLACK, font=f_sub)

    # Left Container: Latency & Benchmark Table
    left_x0, left_x1 = 76, 880
    c_y0, c_y1 = 205, 820
    draw.rounded_rectangle([left_x0, c_y0, left_x1, c_y1], radius=16, fill=C_CARD, outline=C_BORDER, width=2)

    draw.text((left_x0 + 24, c_y0 + 20), "Cryptographic Operations Latency (Warm Median, N = 500)", fill=C_WHITE, font=f_card_hdr)
    draw.line([left_x0 + 24, c_y0 + 56, left_x1 - 24, c_y0 + 56], fill=C_BORDER, width=1)

    # Table Headers
    cols = [
        ("Primitive", 180),
        ("Keygen (us)", 110),
        ("Encap (us)", 110),
        ("Decap (us)", 110),
        ("Total (us)", 110),
        ("Quantum?", 130),
    ]

    th_y = c_y0 + 72
    tx = left_x0 + 24
    for title, width in cols:
        draw.text((tx, th_y), title, fill=C_YELLOW, font=f_th)
        tx += width
    draw.line([left_x0 + 24, th_y + 28, left_x1 - 24, th_y + 28], fill=C_BORDER, width=1)

    rows = [
        ("ML-KEM-768", "223.6 us", "257.0 us", "232.0 us", "712.6 us", "SAFE (FIPS 203)", C_GREEN),
        ("X25519", "172.3 us", "350.9 us", "169.1 us", "692.3 us", "BROKEN (Shor)", C_MUTED),
        ("P-256 (ECDH)", "44.9 us", "191.4 us", "150.4 us", "386.7 us", "BROKEN (Shor)", C_MUTED),
    ]

    tr_y = th_y + 44
    for name, kg, enc, dec, tot, qsafe, col in rows:
        tx = left_x0 + 24
        draw.text((tx, tr_y), name, fill=col, font=f_th)
        tx += 180
        draw.text((tx, tr_y), kg, fill=C_WHITE, font=f_td)
        tx += 110
        draw.text((tx, tr_y), enc, fill=C_YELLOW if name == "ML-KEM-768" else C_WHITE, font=f_td)
        tx += 110
        draw.text((tx, tr_y), dec, fill=C_WHITE, font=f_td)
        tx += 110
        draw.text((tx, tr_y), tot, fill=C_WHITE, font=f_td)
        tx += 110
        draw.text((tx, tr_y), qsafe, fill=col, font=f_th)
        tr_y += 38

    draw.line([left_x0 + 24, tr_y + 10, left_x1 - 24, tr_y + 10], fill=C_BORDER, width=1)

    # Key finding banner
    tr_y += 24
    draw.rounded_rectangle([left_x0 + 24, tr_y, left_x1 - 24, tr_y + 90], radius=8, fill=(35, 30, 42, 255), outline=C_YELLOW, width=1)
    draw.text((left_x0 + 40, tr_y + 16), "COUNTER-INTUITIVE DISCOVERY: ML-KEM-768 IS 26.8% FASTER IN ENCAPSULATION", fill=C_YELLOW, font=f_th)
    draw.text((left_x0 + 40, tr_y + 42), "Lattice matrix multiplications over polynomial rings execute faster on standard CPUs", fill=C_WHITE, font=f_td)
    draw.text((left_x0 + 40, tr_y + 64), "than classical elliptic curve scalar point multiplication (257.0 us vs 350.9 us).", fill=C_WHITE, font=f_td)

    # Micro-benchmarks
    tr_y += 115
    draw.text((left_x0 + 24, tr_y), "Auxiliary Cryptographic Operations (N = 500):", fill=C_WHITE, font=f_card_hdr)
    draw.text((left_x0 + 24, tr_y + 36), "- Baby Jubjub Scalar Field Reduction (toFieldElement): 1.30 us median (3.3 us p95)", fill=C_GREEN, font=f_td)
    draw.text((left_x0 + 24, tr_y + 64), "- Mutual Confirmation ID SHA-256 Hash (Fix M-11):     1.40 us median (2.6 us p95)", fill=C_BLUE, font=f_td)
    draw.text((left_x0 + 24, tr_y + 92), "- Memory Allocations per ML-KEM-768 Exchange:           17,315 Bytes per operation", fill=C_MUTED, font=f_td)

    # Right Container: Calldata & On-Chain Economics
    right_x0, right_x1 = 905, 1524
    draw.rounded_rectangle([right_x0, c_y0, right_x1, c_y1], radius=16, fill=C_CARD, outline=C_BORDER, width=2)

    draw.text((right_x0 + 24, c_y0 + 20), "On-Chain Calldata & Gas Economics (Rayls L1)", fill=C_WHITE, font=f_card_hdr)
    draw.line([right_x0 + 24, c_y0 + 56, right_x1 - 24, c_y0 + 56], fill=C_BORDER, width=1)

    r_y = c_y0 + 74
    draw.text((right_x0 + 24, r_y), "VIEW KEY REGISTRATION GAS", fill=C_MUTED, font=f_th)
    draw.text((right_x0 + 24, r_y + 24), "308,164 Gas", fill=C_WHITE, font=f_stat)
    draw.text((right_x0 + 24, r_y + 68), "Live Mainnet 72957 fork measured gas (Enygma.sol line 529)", fill=C_YELLOW, font=f_stat_lbl)

    draw.line([right_x0 + 24, r_y + 102, right_x1 - 24, r_y + 102], fill=C_BORDER, width=1)

    r_y += 120
    draw.text((right_x0 + 24, r_y), "PAIRWISE AGREEMENT LIVE FORK GAS", fill=C_MUTED, font=f_th)
    draw.text((right_x0 + 24, r_y + 24), "251,561 Gas", fill=C_WHITE, font=f_stat)
    draw.text((right_x0 + 24, r_y + 68), "1,088 B Ciphertext + Fix M-11 confirmation tag verification", fill=C_GREEN, font=f_stat_lbl)

    draw.line([right_x0 + 24, r_y + 102, right_x1 - 24, r_y + 102], fill=C_BORDER, width=1)

    r_y += 120
    draw.text((right_x0 + 24, r_y), "PAYLOAD SIZE vs CALLDATA TRADEOFF", fill=C_MUTED, font=f_th)

    items = [
        ("Public Key Size:", "1,184 Bytes (ML-KEM) vs 32 Bytes (X25519)"),
        ("Ciphertext Size:", "1,088 Bytes (ML-KEM) vs 32 Bytes (X25519)"),
        ("Calldata Gas Cost:", "18,944 gas (ML-KEM) vs 512 gas (X25519)"),
        ("Net USD Cost (48 Gwei):", "$0.0019 USDr (less than 2/10ths of a cent)"),
    ]

    r_y += 30
    for lbl, val in items:
        draw.text((right_x0 + 24, r_y), lbl, fill=C_YELLOW, font=f_th)
        draw.text((right_x0 + 24, r_y + 22), val, fill=C_WHITE, font=f_td)
        r_y += 50

    # Bottom footer
    draw.text((76, 848), "All metrics recorded via verify_datasets.py | Pinned Upstream @ a9b06c00 | Rayls Mainnet 72957", fill=C_BLACK, font=f_body)

    img.save(OUT, "PNG")
    print(f"Diagram 3 saved to: {OUT}")
    return 0


if __name__ == "__main__":
    main()
