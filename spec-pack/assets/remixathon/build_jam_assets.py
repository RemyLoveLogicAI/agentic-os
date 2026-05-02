"""Build jam screen-recording assets for the Anything Remixathon submission.

Outputs (all 1920x1080 except as noted):
  jam/jam-title-card.svg       / .png    Opening title card
  jam/jam-end-card.svg         / .png    Closing CTA card
  jam/jam-chapter-{1..6}.svg   / .png    Chapter / segment dividers
  jam/jam-lower-third.svg      / .png    Lower-third overlay (transparent bg)
  jam/jam-callout-overlay.svg  / .png    Approval-gate callout (transparent bg)
  jam/jam-corner-bug.svg       / .png    Persistent corner bug (transparent bg)

These cards are designed to be dropped into a video editor or applied with
ffmpeg overlays — see jam/EDL.md and jam/ffmpeg-recipe.sh.
"""
from __future__ import annotations

from pathlib import Path

import cairosvg

from build_logos import (
    ACCENT_MAGENTA,
    ACCENT_VIOLET,
    GREY,
    INDIGO,
    INK,
    PAPER,
    WHITE,
    gradient_def,
    loop_glyph,
    svg_doc,
)

ROOT = Path(__file__).resolve().parent
JAM = ROOT / "jam"
JAM.mkdir(parents=True, exist_ok=True)

FONT = "DejaVu Sans, Inter, Helvetica, Arial, sans-serif"


def _t(x, y, txt, *, size, weight=500, fill=INK, anchor="start",
       italic=False, letter_spacing=0):
    style = "italic" if italic else "normal"
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
        f'font-style="{style}" letter-spacing="{letter_spacing}">{txt}</text>'
    )


def _bg_dark_gradient() -> str:
    return (
        '<defs>'
        '<linearGradient id="bg-grad" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="{INK}"/>'
        f'<stop offset="100%" stop-color="#1A1F4D"/>'
        '</linearGradient>'
        + gradient_def("remix-grad-jam") +
        '</defs>'
    )


def _decor_rings(cx, cy, color=ACCENT_MAGENTA):
    return "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
        f'stroke="{color}" stroke-width="1" opacity="{0.07 + i * 0.04:.2f}"/>'
        for i, r in enumerate([460, 380, 300, 220, 150])
    )


# ---------------------------------------------------------------------------
# Title card
# ---------------------------------------------------------------------------
def title_card() -> str:
    W, H = 1920, 1080
    parts = [
        _bg_dark_gradient(),
        f'<rect width="{W}" height="{H}" fill="url(#bg-grad)"/>',
        _decor_rings(1500, 540),
        loop_glyph(cx=1500, cy=540, r=200, stroke_width=34,
                   color_arc=WHITE, color_play=WHITE,
                   use_gradient=True, gradient_id="remix-grad-jam"),
        # pill
        f'<rect x="120" y="200" width="540" height="64" rx="32" '
        f'fill="none" stroke="{ACCENT_MAGENTA}" stroke-width="2"/>',
        _t(390, 244, "ANYTHING REMIXATHON · MAY 2026",
           size=24, weight=700, fill=ACCENT_MAGENTA, letter_spacing=4,
           anchor="middle"),
        # headline (3 lines, gradient on third)
        _t(120, 380, "Speak.", size=132, weight=800, fill=WHITE,
           letter_spacing=-3),
        _t(120, 510, "Route. Approve.", size=132, weight=800, fill=WHITE,
           letter_spacing=-3),
        _t(120, 640, "Act. Verify.", size=132, weight=800,
           fill="url(#remix-grad-jam)", letter_spacing=-3),
        _t(120, 770, "Remember.", size=132, weight=800,
           fill="url(#remix-grad-jam)", letter_spacing=-3),
        # tagline
        _t(120, 850, "A voice-native operating system for the Agentic Web.",
           size=32, weight=400, fill="#B6B9C7"),
        # footer
        f'<line x1="120" y1="950" x2="1800" y2="950" '
        f'stroke="{ACCENT_MAGENTA}" stroke-width="1" opacity="0.4"/>',
        _t(120, 1010, "AGENTIC OS · LOVELOGICAI",
           size=24, weight=700, fill=WHITE, letter_spacing=4),
        _t(1800, 1010, "github.com/RemyLoveLogicAI/agentic-os",
           size=24, weight=400, fill="#B6B9C7", anchor="end"),
    ]
    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# End card
# ---------------------------------------------------------------------------
def end_card() -> str:
    W, H = 1920, 1080
    parts = [
        _bg_dark_gradient(),
        f'<rect width="{W}" height="{H}" fill="url(#bg-grad)"/>',
        _decor_rings(960, 540),
        loop_glyph(cx=960, cy=400, r=160, stroke_width=28,
                   color_arc=WHITE, color_play=WHITE,
                   use_gradient=True, gradient_id="remix-grad-jam"),
        _t(960, 720, "Thanks for watching.", size=84, weight=800,
           fill=WHITE, letter_spacing=-2, anchor="middle"),
        _t(960, 800, "Remix the loop.", size=64, weight=800,
           fill="url(#remix-grad-jam)", letter_spacing=-2, anchor="middle"),
        # CTA buttons
        f'<rect x="540" y="870" width="380" height="80" rx="40" '
        f'fill="{WHITE}"/>',
        _t(730, 925, "Read the Spec", size=28, weight=700, fill=INK,
           anchor="middle"),
        f'<rect x="1000" y="870" width="380" height="80" rx="40" '
        f'fill="none" stroke="{ACCENT_MAGENTA}" stroke-width="2"/>',
        _t(1190, 925, "Star on GitHub", size=28, weight=700,
           fill=ACCENT_MAGENTA, anchor="middle"),
        # Footer
        _t(960, 1020, "github.com/RemyLoveLogicAI/agentic-os    ·    AGENTIC OS · LOVELOGICAI",
           size=20, weight=500, fill="#B6B9C7", anchor="middle", letter_spacing=2),
    ]
    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# Chapter card
# ---------------------------------------------------------------------------
def chapter_card(num: int, label: str, sub: str) -> str:
    W, H = 1920, 1080
    parts = [
        _bg_dark_gradient(),
        f'<rect width="{W}" height="{H}" fill="url(#bg-grad)"/>',
        _decor_rings(1500, 540),
        loop_glyph(cx=1500, cy=540, r=170, stroke_width=28,
                   color_arc=WHITE, color_play=WHITE,
                   use_gradient=True, gradient_id="remix-grad-jam"),
        _t(120, 380, f"{num:02d}", size=240, weight=800,
           fill="url(#remix-grad-jam)", letter_spacing=-6),
        _t(120, 530, "CHAPTER", size=28, weight=700, fill="#B6B9C7",
           letter_spacing=8),
        _t(120, 660, label, size=104, weight=800, fill=WHITE,
           letter_spacing=-3),
        _t(120, 740, sub, size=32, weight=400, fill="#B6B9C7"),
        f'<line x1="120" y1="950" x2="1300" y2="950" '
        f'stroke="{ACCENT_MAGENTA}" stroke-width="1" opacity="0.4"/>',
        _t(120, 1010, "AGENTIC OS · LOVELOGICAI",
           size=22, weight=700, fill=WHITE, letter_spacing=4),
    ]
    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# Lower-third overlay (transparent bg)
# ---------------------------------------------------------------------------
def lower_third(headline: str = "Approval Gate", sub: str = "Aegis · Violet Covenant",
                step: int = 3) -> str:
    W, H = 1920, 1080
    body = [
        # bar
        f'<rect x="80" y="900" width="1240" height="120" rx="60" '
        f'fill="{INK}" fill-opacity="0.92"/>',
        # mini glyph badge on left
        f'<circle cx="160" cy="960" r="44" fill="{ACCENT_MAGENTA}"/>',
        _t(160, 974, f"{step:02d}", size=32, weight=800, fill=WHITE,
           anchor="middle"),
        # text
        _t(232, 950, headline, size=36, weight=800, fill=WHITE),
        _t(232, 992, sub, size=24, weight=500, fill="#B6B9C7"),
        # right pill
        f'<rect x="1170" y="930" width="130" height="60" rx="30" '
        f'fill="none" stroke="{ACCENT_MAGENTA}" stroke-width="2"/>',
        _t(1235, 968, "LIVE", size=22, weight=700, fill=ACCENT_MAGENTA,
           anchor="middle", letter_spacing=4),
    ]
    return svg_doc(W, H, "".join(body))


# ---------------------------------------------------------------------------
# Callout overlay (transparent bg) — used to highlight key moments
# ---------------------------------------------------------------------------
def callout_overlay(headline: str = "No proof, no claim.",
                    body_text: str = "Every action carries an evidence receipt.") -> str:
    W, H = 1920, 1080
    parts = [
        # large pill on right
        f'<rect x="1180" y="200" width="660" height="220" rx="32" '
        f'fill="{INK}" fill-opacity="0.92" stroke="{ACCENT_MAGENTA}" '
        f'stroke-width="2"/>',
        _t(1210, 260, "CALLOUT", size=20, weight=700,
           fill=ACCENT_MAGENTA, letter_spacing=6),
        _t(1210, 320, headline, size=42, weight=800, fill=WHITE),
        _t(1210, 380, body_text, size=24, weight=400, fill="#B6B9C7"),
    ]
    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# Corner bug — persistent watermark
# ---------------------------------------------------------------------------
def corner_bug() -> str:
    W, H = 1920, 1080
    parts = [
        # bottom-right cluster
        loop_glyph(cx=1810, cy=1010, r=44, stroke_width=10,
                   color_arc=WHITE, color_play=WHITE,
                   use_gradient=True, gradient_id="remix-grad-jam"),
        gradient_def("remix-grad-jam"),
        _t(1750, 1018, "Anything Remixathon",
           size=22, weight=700, fill=WHITE, anchor="end"),
        _t(1750, 1044, "AGENTIC OS · LOVELOGICAI",
           size=14, weight=600, fill="#B6B9C7", anchor="end", letter_spacing=2),
    ]
    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# Build pipeline
# ---------------------------------------------------------------------------
def write_and_render(name: str, content: str, *, width: int = 1920) -> None:
    svg_path = JAM / f"{name}.svg"
    png_path = JAM / f"{name}.png"
    svg_path.write_text(content)
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path),
                     output_width=width)


def main() -> None:
    write_and_render("jam-title-card", title_card())
    write_and_render("jam-end-card", end_card())

    chapters = [
        (1, "Speak", "voice clarification with Spokenly MCP"),
        (2, "Route", "deterministic intent classification"),
        (3, "Approve", "policy gate — Aegis · Violet Covenant"),
        (4, "Act", "safe execution across CLI, desktop, and API"),
        (5, "Verify", "evidence ledger — receipts on disk"),
        (6, "Remember", "canonical memory — R.I.P. · Knowledge Graph"),
    ]
    for num, label, sub in chapters:
        write_and_render(
            f"jam-chapter-{num}-{label.lower()}",
            chapter_card(num, label, sub),
        )

    # A small library of pre-rendered lower thirds matched to each chapter
    lower_thirds = [
        ("Spokenly MCP",         "voice clarification · ask_user_dictation", 1),
        ("Voice Orion",          "deterministic command router",             2),
        ("Aegis · Violet Covenant", "approval gate · TTL expiry",            3),
        ("DLAM / R1 · Zo API",   "safe execution adapters",                  4),
        ("Evidence Ledger",      "receipts · diffs · audit trail",           5),
        ("R.I.P. · Knowledge Graph", "canonical memory + claims",            6),
    ]
    for headline, sub, step in lower_thirds:
        slug = (
            headline.lower()
            .replace(" · ", "-")
            .replace(" / ", "-")
            .replace(" ", "-")
            .replace("·", "")
            .replace("/", "")
            .replace(".", "")
        )
        # collapse repeated "-"
        while "--" in slug:
            slug = slug.replace("--", "-")
        slug = slug.strip("-")
        write_and_render(f"jam-lower-third-{step}-{slug}",
                         lower_third(headline=headline, sub=sub, step=step))

    # Generic callouts the editor can drop in
    callouts = [
        ("no-proof",  "No proof, no claim.",
         "Every action carries an evidence receipt."),
        ("approval-gate", "Approval before action.",
         "High-risk steps must be explicitly approved."),
        ("memory-canonical", "Memory is canonical.",
         "Claims live in R.I.P., context lives in the Knowledge Graph."),
    ]
    for slug, headline, body in callouts:
        write_and_render(f"jam-callout-{slug}",
                         callout_overlay(headline=headline, body_text=body))

    write_and_render("jam-corner-bug", corner_bug())

    print("\nGenerated jam recording assets:")
    for entry in sorted(JAM.iterdir()):
        size = entry.stat().st_size
        print(f"  {entry.name:55s} {size:>8d} bytes")


if __name__ == "__main__":
    main()
