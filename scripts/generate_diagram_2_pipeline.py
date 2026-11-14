#!/usr/bin/env python3
"""Generate Diagram 2: Enygma's ML-KEM-768 Lattice-to-Baby-Jubjub Zero-Knowledge Pipeline."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "diagram_2_mlkem_zk_pipeline.png"
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
    f_card_hdr = ImageFont.truetype(FONT_BOLD, 18)
    f_step_num = ImageFont.truetype(FONT_BOLD, 15)
    f_step_tag = ImageFont.truetype(FONT_BOLD, 13)
    f_mono = ImageFont.truetype(FONT_MONO, 12)
    f_body = ImageFont.truetype(FONT_REG, 14)
    f_stat = ImageFont.truetype(FONT_BOLD, 22)
    f_box_tag = ImageFont.truetype(FONT_BOLD, 12)
    f_box_desc = ImageFont.truetype(FONT_REG, 12)

    # Top pill (dynamic width to prevent overflow)
    pill_text = "CRYPTOGRAPHIC FLOW | ENYGMA ARCHITECTURE"
    pill_w = int(f_pill.getlength(pill_text)) + 36
    draw.rounded_rectangle([76, 40, 76 + pill_w, 78], radius=8, fill=C_BLACK)
    draw.text((92, 48), pill_text, fill=C_YELLOW, font=f_pill)

    # Title
    draw.text((76, 96), "Enygma's ML-KEM-768 to Zero-Knowledge Pipeline", fill=C_BLACK, font=f_title)
    draw.text((76, 148), "From Lattice Key Encapsulation to Baby Jubjub Pedersen Scalar Blinding Factors", fill=C_BLACK, font=f_sub)

    # 4 Flow Columns
    card_y0, card_y1 = 205, 820
    col_w = 347
    gap = 20

    steps = [
        {
            "num": "STEP 1",
            "tag": "ON-CHAIN REGISTRATION",
            "title": "Strict 1,184B Key Enforce",
            "accent": C_YELLOW,
            "code": [
                "// Enygma.sol (Line 529)",
                "if (viewKey.length != 0 &&",
                "    viewKey.length != 1184)",
                "    revert InvalidKeyLen();",
                "",
                "viewKeys[accountId] = key;"
            ],
            "notes": [
                "Banks register 1,184B encapsulation keys in Enygma.sol on-chain.",
                "Non-circuit relayers pass 0 bytes legitimately.",
                "Truncated classical keys (32B / 64B) strictly revert on-chain."
            ],
            "box_tag": "FOUNDRY INVARIANT PROOF",
            "box_stat": "8/8 PASS",
            "box_desc": "CRIT-PQ1: Reverts on 32B/64B (256 fuzz runs)"
        },
        {
            "num": "STEP 2",
            "tag": "PAIRWISE AGREEMENT",
            "title": "Fix M-11 Leader Direction",
            "accent": C_PURPLE,
            "code": [
                "// agreement/manager.go",
                "if !(m.bankID < peerID) {",
                "    // Fix M-11 defect 1:",
                "    // Lower ID leads",
                "    return nil, err",
                "}",
                "ct, rawSS, _ := mlkem768.",
                "    Encapsulate(peerEK)"
            ],
            "notes": [
                "Lower bankId always leads and executes encapsulation.",
                "Outputs 1,088 B ciphertext + 32 B shared secret.",
                "Eliminates race conditions where banks generate divergent keys."
            ],
            "box_tag": "UPSTREAM ENYGMA SUITE",
            "box_stat": "9/9 PASS",
            "box_desc": "Leader election and keygen determinism verified"
        },
        {
            "num": "STEP 3",
            "tag": "DESYNC MITIGATION",
            "title": "FIPS 203 Implicit Reject",
            "accent": C_BLUE,
            "code": [
                "// Fix M-11 defect 2",
                "id = SHA256(",
                "  \"enygma-view-key-confirm-v1:\",",
                "  rawSS)",
                "if subtle.ConstantTimeCompare(",
                "    want, got) != 1 {",
                "    revert BadCiphertext();",
                "}"
            ],
            "notes": [
                "FIPS 203 outputs pseudorandom key on corrupted ciphertext.",
                "Leader publishes SHA-256 confirmation ID with ciphertext.",
                "Follower verifies before caching, blocking silent state desync."
            ],
            "box_tag": "DESYNC DEFENSE VERIFIED",
            "box_stat": "1.40 us",
            "box_desc": "Constant-time tag match catches bad ciphertexts"
        },
        {
            "num": "STEP 4",
            "tag": "ZK FIELD MAPPING",
            "title": "Baby Jubjub Reduction",
            "accent": C_GREEN,
            "code": [
                "// toFieldElement (1.30 us)",
                "h = SHA256(",
                "  \"enygma-view-key-v1:\",",
                "  rawSS)",
                "fe = big.Int(h).Mod(",
                "  curveP // Baby Jubjub order",
                ")"
            ],
            "notes": [
                "Lattice shared secret mapped to Baby Jubjub scalar field.",
                "Subgroup order curveP (254-bit prime modulus).",
                "Feeds into Groth16 circuit for private balance blinding."
            ],
            "box_tag": "FIELD REDUCTION SPEED",
            "box_stat": "1.30 us",
            "box_desc": "Baby Jubjub scalar modulo curveP (N=500)"
        }
    ]

    for i, s in enumerate(steps):
        cx0 = 76 + i * (col_w + gap)
        cx1 = cx0 + col_w
        draw.rounded_rectangle([cx0, card_y0, cx1, card_y1], radius=16, fill=C_CARD, outline=C_BORDER, width=2)

        # Header tag
        step_text = s["num"]
        step_w = int(f_step_num.getlength(step_text)) + 18
        draw.rounded_rectangle([cx0 + 16, card_y0 + 14, cx0 + 16 + step_w, card_y0 + 36], radius=4, fill=C_BLACK)
        draw.text((cx0 + 25, card_y0 + 16), step_text, fill=s["accent"], font=f_step_num)
        draw.text((cx0 + 16 + step_w + 10, card_y0 + 18), s["tag"], fill=C_MUTED, font=f_step_tag)

        draw.text((cx0 + 16, card_y0 + 44), s["title"], fill=C_WHITE, font=f_card_hdr)
        draw.line([cx0 + 16, card_y0 + 72, cx1 - 16, card_y0 + 72], fill=C_BORDER, width=1)

        # Code block
        code_h = 175
        draw.rounded_rectangle([cx0 + 14, card_y0 + 82, cx1 - 14, card_y0 + 82 + code_h], radius=8, fill=(17, 17, 20, 255), outline=C_BORDER, width=1)
        cy = card_y0 + 92
        for cline in s["code"]:
            draw.text((cx0 + 22, cy), cline, fill=C_YELLOW if "revert" in cline or "Fix" in cline else C_MUTED, font=f_mono)
            cy += 19

        # Notes block (Cleanly wrapped on new lines, avoiding horizontal overflow)
        ny = card_y0 + 272
        content_w = col_w - 44  # 303px inside notes margin
        for note in s["notes"]:
            lines = wrap_text_pixels(note, f_body, content_w)
            for j, line in enumerate(lines):
                if j == 0:
                    draw.text((cx0 + 16, ny), "•", fill=s["accent"], font=f_body)
                    draw.text((cx0 + 30, ny), line, fill=C_WHITE, font=f_body)
                else:
                    draw.text((cx0 + 30, ny), line, fill=C_MUTED, font=f_body)
                ny += 21
            ny += 8  # gap between bullet points

        # Bottom Empirical Verification Callout Box (occupying lower region perfectly)
        box_y0 = card_y1 - 110
        box_y1 = card_y1 - 16
        draw.rounded_rectangle([cx0 + 14, box_y0, cx1 - 14, box_y1], radius=8, fill=(30, 30, 36, 255), outline=C_BORDER, width=1)

        draw.text((cx0 + 24, box_y0 + 12), s["box_tag"], fill=C_YELLOW, font=f_box_tag)
        draw.text((cx0 + 24, box_y0 + 32), s["box_stat"], fill=s["accent"], font=f_stat)

        # Wrap box desc
        desc_lines = wrap_text_pixels(s["box_desc"], f_box_desc, content_w)
        d_y = box_y0 + 64
        for dline in desc_lines:
            draw.text((cx0 + 24, d_y), dline, fill=C_MUTED, font=f_box_desc)
            d_y += 16

    # Bottom footer
    draw.text((76, 848), "Rayls Enygma Production Cryptography | Upstream agreement/manager.go & Enygma.sol | NIST FIPS 203", fill=C_BLACK, font=f_body)

    img.save(OUT, "PNG")
    print(f"Diagram 2 saved to: {OUT}")
    return 0


if __name__ == "__main__":
    main()
