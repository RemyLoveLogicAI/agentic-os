"""Build Anything Remixathon × Agentic OS logo variants.

Outputs SVGs and rasterizes them to PNGs at all required sizes.

Brand palette (extracted from existing spec-pack diagrams):
  primary indigo  #0D32B2
  ink             #0A0F25
  paper           #F7F8FE
  white           #FFFFFF
  remix accent    #FF2BD6  (electric magenta — added for the Remixathon)
  remix accent 2  #7A29FF  (violet — used in gradient with magenta)

The glyph encodes the Agentic OS core loop:
  speak -> route -> approve -> act -> verify -> remember
as 6 arc segments around a circle, with a forward-pointing play triangle in the
center to evoke the "remix" / "press play" theme of the Anything Remixathon.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parent
LOGO_DIR = ROOT / "logo"
LOGO_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Color tokens
# ---------------------------------------------------------------------------
INDIGO = "#0D32B2"
INK = "#0A0F25"
PAPER = "#F7F8FE"
WHITE = "#FFFFFF"
ACCENT_MAGENTA = "#FF2BD6"
ACCENT_VIOLET = "#7A29FF"
GREY = "#3A3E50"


# ---------------------------------------------------------------------------
# Glyph: 6-segment loop + play triangle
# ---------------------------------------------------------------------------
def loop_glyph(
    cx: float,
    cy: float,
    r: float,
    stroke_width: float,
    color_arc: str = INDIGO,
    color_play: str = INDIGO,
    color_accent: str = ACCENT_MAGENTA,
    use_gradient: bool = True,
    gradient_id: str = "remix-grad",
) -> str:
    """Return SVG fragment for the loop glyph centered at (cx, cy) with radius r.

    The glyph is 6 arc segments forming a circle with small gaps between them
    (the 6 stages of the Agentic OS core loop), plus a forward-pointing play
    triangle in the center.  The final ("remember -> speak") arc is drawn in an
    accent color to evoke the remix/feedback loop.
    """
    parts: list[str] = []
    # 6 arcs, each spans 56° with 4° gaps between them.
    arc_span = 56.0
    gap = 4.0
    start = -90.0  # start at top
    for i in range(6):
        a0 = start + i * (arc_span + gap)
        a1 = a0 + arc_span
        x0 = cx + r * math.cos(math.radians(a0))
        y0 = cy + r * math.sin(math.radians(a0))
        x1 = cx + r * math.cos(math.radians(a1))
        y1 = cy + r * math.sin(math.radians(a1))
        large = 0
        sweep = 1
        if i == 5 and use_gradient:
            stroke = f"url(#{gradient_id})"
        elif i == 5:
            stroke = color_accent
        else:
            stroke = color_arc
        parts.append(
            f'<path d="M {x0:.2f} {y0:.2f} A {r:.2f} {r:.2f} 0 {large} {sweep} {x1:.2f} {y1:.2f}" '
            f'fill="none" stroke="{stroke}" stroke-width="{stroke_width:.2f}" stroke-linecap="round"/>'
        )
    # six small dots at the segment joints to anchor the rhythm
    for i in range(6):
        a = start + i * (arc_span + gap) + arc_span + gap / 2
        x = cx + r * math.cos(math.radians(a))
        y = cy + r * math.sin(math.radians(a))
        parts.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{stroke_width * 0.55:.2f}" fill="{color_arc}"/>'
        )
    # play triangle in the center, sized as a fraction of r
    tri_h = r * 0.78
    tri_w = tri_h * 0.86
    tx = cx - tri_w * 0.30
    parts.append(
        f'<path d="M {tx:.2f} {cy - tri_h / 2:.2f} '
        f'L {tx + tri_w:.2f} {cy:.2f} '
        f'L {tx:.2f} {cy + tri_h / 2:.2f} Z" '
        f'fill="{color_play}"/>'
    )
    return "\n".join(parts)


def gradient_def(gid: str = "remix-grad", c1: str = ACCENT_VIOLET, c2: str = ACCENT_MAGENTA) -> str:
    return (
        f'<linearGradient id="{gid}" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{c1}"/>'
        f'<stop offset="100%" stop-color="{c2}"/>'
        f"</linearGradient>"
    )


# ---------------------------------------------------------------------------
# SVG composers
# ---------------------------------------------------------------------------
def svg_doc(width: int, height: int, body: str, bg: str | None = None) -> str:
    bg_rect = f'<rect width="{width}" height="{height}" fill="{bg}"/>' if bg else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
        f"{bg_rect}{body}</svg>"
    )


def primary_horizontal(
    on_dark: bool = False,
    monochrome: str | None = None,
) -> str:
    """Glyph + 'Anything Remixathon' / 'Agentic OS' wordmark, horizontal."""
    width, height = 1600, 360
    arc_color = INDIGO if not on_dark else WHITE
    play_color = INDIGO if not on_dark else WHITE
    headline_color = INK if not on_dark else WHITE
    sub_color = GREY if not on_dark else "#B6B9C7"
    bg = WHITE if not on_dark else INK
    if monochrome:
        arc_color = monochrome
        play_color = monochrome
        headline_color = monochrome
        sub_color = monochrome
    cx, cy, r = 180, 180, 110
    grad_id = "remix-grad-h"
    glyph = loop_glyph(
        cx=cx,
        cy=cy,
        r=r,
        stroke_width=22,
        color_arc=arc_color,
        color_play=play_color,
        use_gradient=monochrome is None,
        gradient_id=grad_id,
    )
    text_x = 340
    headline = (
        f'<text x="{text_x}" y="170" font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="78" font-weight="800" fill="{headline_color}" letter-spacing="-2">'
        f"Anything Remixathon</text>"
    )
    sub_y = 240
    sub = (
        f'<text x="{text_x}" y="{sub_y}" font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="38" font-weight="500" fill="{sub_color}" letter-spacing="6">'
        f"AGENTIC&#160;&#160;OS&#160;&#160;·&#160;&#160;LOVELOGICAI</text>"
    )
    defs = "" if monochrome else f"<defs>{gradient_def(grad_id)}</defs>"
    return svg_doc(width, height, defs + glyph + headline + sub, bg=bg)


def stacked(on_dark: bool = False, monochrome: str | None = None) -> str:
    width, height = 900, 820
    arc_color = INDIGO if not on_dark else WHITE
    play_color = INDIGO if not on_dark else WHITE
    headline_color = INK if not on_dark else WHITE
    sub_color = GREY if not on_dark else "#B6B9C7"
    bg = WHITE if not on_dark else INK
    if monochrome:
        arc_color = monochrome
        play_color = monochrome
        headline_color = monochrome
        sub_color = monochrome
    grad_id = "remix-grad-s"
    glyph = loop_glyph(
        cx=450,
        cy=260,
        r=180,
        stroke_width=34,
        color_arc=arc_color,
        color_play=play_color,
        use_gradient=monochrome is None,
        gradient_id=grad_id,
    )
    headline = (
        f'<text x="450" y="600" text-anchor="middle" '
        f'font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="68" font-weight="800" fill="{headline_color}" letter-spacing="-2">'
        f"Anything Remixathon</text>"
    )
    sub = (
        f'<text x="450" y="685" text-anchor="middle" '
        f'font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="34" font-weight="600" fill="{sub_color}" letter-spacing="8">'
        f"AGENTIC&#160;&#160;OS</text>"
    )
    tagline = (
        f'<text x="450" y="755" text-anchor="middle" '
        f'font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="24" font-weight="400" fill="{sub_color}" letter-spacing="2" font-style="italic">'
        f"speak · route · approve · act · verify · remember</text>"
    )
    defs = "" if monochrome else f"<defs>{gradient_def(grad_id)}</defs>"
    return svg_doc(width, height, defs + glyph + headline + sub + tagline, bg=bg)


def glyph_only(on_dark: bool = False, monochrome: str | None = None, size: int = 512) -> str:
    arc_color = INDIGO if not on_dark else WHITE
    play_color = INDIGO if not on_dark else WHITE
    bg = WHITE if not on_dark else INK
    if monochrome:
        arc_color = monochrome
        play_color = monochrome
    grad_id = "remix-grad-g"
    cx = cy = size / 2
    r = size * 0.36
    sw = size * 0.06
    glyph = loop_glyph(
        cx=cx,
        cy=cy,
        r=r,
        stroke_width=sw,
        color_arc=arc_color,
        color_play=play_color,
        use_gradient=monochrome is None,
        gradient_id=grad_id,
    )
    defs = "" if monochrome else f"<defs>{gradient_def(grad_id)}</defs>"
    return svg_doc(size, size, defs + glyph, bg=bg)


def social_card() -> str:
    width, height = 1200, 630
    grad_id = "remix-grad-card"
    bg_grad_id = "card-bg-grad"
    body_parts = [
        f"<defs>{gradient_def(grad_id)}"
        f'<linearGradient id="{bg_grad_id}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{INK}"/>'
        f'<stop offset="100%" stop-color="#1A1F4D"/>'
        "</linearGradient></defs>",
        f'<rect width="{width}" height="{height}" fill="url(#{bg_grad_id})"/>',
        # Decorative grid lines
    ]
    # decorative concentric rings on the right
    cx, cy = 980, 315
    for i, rr in enumerate([240, 200, 160, 120, 80]):
        opacity = 0.10 + i * 0.04
        body_parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" '
            f'stroke="{ACCENT_MAGENTA}" stroke-width="1" opacity="{opacity:.2f}"/>'
        )
    # Glyph on the right
    body_parts.append(
        loop_glyph(
            cx=cx,
            cy=cy,
            r=130,
            stroke_width=24,
            color_arc=WHITE,
            color_play=WHITE,
            use_gradient=True,
            gradient_id=grad_id,
        )
    )
    # Pill: ANYTHING REMIXATHON · MAY 2026
    body_parts.append(
        f'<rect x="80" y="120" width="420" height="54" rx="27" '
        f'fill="none" stroke="{ACCENT_MAGENTA}" stroke-width="2"/>'
    )
    body_parts.append(
        f'<text x="105" y="156" font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="22" font-weight="700" fill="{ACCENT_MAGENTA}" letter-spacing="4">'
        f"ANYTHING REMIXATHON · MAY 2026</text>"
    )
    # Headline
    body_parts.append(
        f'<text x="80" y="265" font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="60" font-weight="800" fill="{WHITE}" letter-spacing="-2">'
        f"Speak. Route. Approve.</text>"
    )
    body_parts.append(
        f'<text x="80" y="345" font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="60" font-weight="800" fill="url(#{grad_id})" letter-spacing="-2">'
        f"Act. Verify. Remember.</text>"
    )
    body_parts.append(
        f'<text x="80" y="420" font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="26" font-weight="500" fill="#B6B9C7">'
        f"A voice-native operating system for the Agentic Web.</text>"
    )
    # Footer line
    body_parts.append(
        f'<line x1="80" y1="540" x2="1120" y2="540" stroke="{ACCENT_MAGENTA}" stroke-width="1" opacity="0.4"/>'
    )
    body_parts.append(
        f'<text x="80" y="585" font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="22" font-weight="600" fill="{WHITE}" letter-spacing="3">'
        f"AGENTIC OS · LOVELOGICAI</text>"
    )
    body_parts.append(
        f'<text x="1120" y="585" text-anchor="end" '
        f'font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="22" font-weight="400" fill="#B6B9C7">'
        f"github.com/RemyLoveLogicAI/agentic-os</text>"
    )
    return svg_doc(width, height, "".join(body_parts))


def submission_badge() -> str:
    """1080x1080 square submission badge for socials."""
    size = 1080
    grad_id = "remix-grad-sub"
    body_parts = [
        f"<defs>{gradient_def(grad_id)}</defs>",
        f'<rect width="{size}" height="{size}" fill="{INK}"/>',
    ]
    cx = cy = size / 2
    # Glyph upper third
    body_parts.append(
        loop_glyph(
            cx=cx,
            cy=420,
            r=200,
            stroke_width=36,
            color_arc=WHITE,
            color_play=WHITE,
            use_gradient=True,
            gradient_id=grad_id,
        )
    )
    body_parts.append(
        f'<text x="{cx}" y="780" text-anchor="middle" '
        f'font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="78" font-weight="800" fill="{WHITE}" letter-spacing="-2">'
        f"Anything Remixathon</text>"
    )
    body_parts.append(
        f'<text x="{cx}" y="860" text-anchor="middle" '
        f'font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="38" font-weight="600" fill="url(#{grad_id})" letter-spacing="6">'
        f"AGENTIC OS · SUBMISSION</text>"
    )
    body_parts.append(
        f'<text x="{cx}" y="940" text-anchor="middle" '
        f'font-family="DejaVu Sans, Inter, Helvetica, Arial, sans-serif" '
        f'font-size="28" font-weight="400" fill="#B6B9C7" font-style="italic">'
        f"speak · route · approve · act · verify · remember</text>"
    )
    return svg_doc(size, size, "".join(body_parts))


# ---------------------------------------------------------------------------
# Build pipeline
# ---------------------------------------------------------------------------
def write_svg(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def rasterize(svg_path: Path, png_path: Path, output_width: int | None = None) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=output_width,
    )


def main() -> None:
    targets: list[tuple[str, str, dict[str, int] | None]] = []

    # Primary horizontal — light bg
    p = write_svg(LOGO_DIR / "remixathon-logo-primary-light.svg", primary_horizontal(on_dark=False))
    rasterize(p, LOGO_DIR / "remixathon-logo-primary-light.png", output_width=1600)
    rasterize(p, LOGO_DIR / "remixathon-logo-primary-light@2x.png", output_width=2400)

    # Primary horizontal — dark bg
    p = write_svg(LOGO_DIR / "remixathon-logo-primary-dark.svg", primary_horizontal(on_dark=True))
    rasterize(p, LOGO_DIR / "remixathon-logo-primary-dark.png", output_width=1600)

    # Stacked — light + dark
    p = write_svg(LOGO_DIR / "remixathon-logo-stacked-light.svg", stacked(on_dark=False))
    rasterize(p, LOGO_DIR / "remixathon-logo-stacked-light.png", output_width=1080)
    p = write_svg(LOGO_DIR / "remixathon-logo-stacked-dark.svg", stacked(on_dark=True))
    rasterize(p, LOGO_DIR / "remixathon-logo-stacked-dark.png", output_width=1080)

    # Monochrome variants (for stickers, embroidery, single-ink print)
    p = write_svg(
        LOGO_DIR / "remixathon-logo-mono-black.svg",
        primary_horizontal(monochrome=INK),
    )
    rasterize(p, LOGO_DIR / "remixathon-logo-mono-black.png", output_width=1600)
    p = write_svg(
        LOGO_DIR / "remixathon-logo-mono-white.svg",
        primary_horizontal(on_dark=True, monochrome=WHITE),
    )
    rasterize(p, LOGO_DIR / "remixathon-logo-mono-white.png", output_width=1600)

    # Glyph-only at multiple sizes (favicon set + app-icon)
    glyph_full_color = write_svg(
        LOGO_DIR / "remixathon-glyph-color.svg", glyph_only(on_dark=False, size=512)
    )
    glyph_white_on_dark = write_svg(
        LOGO_DIR / "remixathon-glyph-on-dark.svg", glyph_only(on_dark=True, size=512)
    )
    for px in (16, 32, 48, 64, 128, 192, 256, 512):
        rasterize(
            glyph_full_color,
            LOGO_DIR / f"remixathon-glyph-{px}.png",
            output_width=px,
        )
    rasterize(glyph_white_on_dark, LOGO_DIR / "remixathon-glyph-on-dark-512.png", output_width=512)

    # Social card 1200x630 (Open Graph / Twitter card)
    p = write_svg(LOGO_DIR / "remixathon-social-1200x630.svg", social_card())
    rasterize(p, LOGO_DIR / "remixathon-social-1200x630.png", output_width=1200)

    # Submission badge 1080x1080 (Instagram / LinkedIn square)
    p = write_svg(LOGO_DIR / "remixathon-submission-badge-1080.svg", submission_badge())
    rasterize(p, LOGO_DIR / "remixathon-submission-badge-1080.png", output_width=1080)

    # Listing
    print("\nGenerated logo assets:")
    for entry in sorted(LOGO_DIR.iterdir()):
        size = entry.stat().st_size
        print(f"  {entry.name:55s} {size:>8d} bytes")


if __name__ == "__main__":
    main()
