"""Build Agent OS demonstration graphics for the Anything Remixathon.

Outputs:
  demo/agentic-os-one-loop-hero.svg / .png         (1920x1080 hero diagram)
  demo/agentic-os-nine-layers.svg  / .png          (1080x1500 vertical stack)
  demo/agentic-os-governance-gate.svg / .png       (1600x900 approval-gate close-up)
  demo/agentic-os-system-contract.svg / .png       (1600x900 input/processing/output)
  demo/agentic-os-three-gaps.svg / .png            (1600x900 comparison)
  demo/agentic-os-evidence-flow.svg / .png         (1600x900 evidence + memory loop)

All graphics share the brand palette and the loop-glyph from build_logos.py.
"""
from __future__ import annotations

import math
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
DEMO = ROOT / "demo"
DEMO.mkdir(parents=True, exist_ok=True)

FONT = "DejaVu Sans, Inter, Helvetica, Arial, sans-serif"


def _t(x: float, y: float, txt: str, *, size: int, weight: int = 500,
       fill: str = INK, anchor: str = "start", italic: bool = False,
       letter_spacing: float = 0) -> str:
    style = "italic" if italic else "normal"
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
        f'font-style="{style}" letter-spacing="{letter_spacing}">{txt}</text>'
    )


def _box(x: float, y: float, w: float, h: float, *, fill: str = WHITE,
         stroke: str = INDIGO, sw: float = 2, rx: float = 12) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def _arrow_marker(mid: str = "arrow", color: str = INDIGO) -> str:
    return (
        f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/></marker>'
    )


# ---------------------------------------------------------------------------
# 1. One-loop hero
# ---------------------------------------------------------------------------
def one_loop_hero() -> str:
    W, H = 1920, 1080
    grad_id = "loop-grad"
    parts: list[str] = [
        f'<defs>{gradient_def(grad_id)}{_arrow_marker("arrow-i", INDIGO)}'
        f'{_arrow_marker("arrow-m", ACCENT_MAGENTA)}</defs>',
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        # title strip
        _t(80, 95, "The One Loop", size=64, weight=800, fill=INK, letter_spacing=-1),
        _t(80, 145,
           "Agentic OS converts spoken intent into verified action — and remembers.",
           size=28, weight=400, fill=GREY),
        # pill: ANYTHING REMIXATHON · MAY 2026
        f'<rect x="1380" y="60" width="460" height="56" rx="28" '
        f'fill="none" stroke="{ACCENT_MAGENTA}" stroke-width="2"/>',
        _t(1610, 96, "ANYTHING REMIXATHON · MAY 2026",
           size=18, weight=700, fill=ACCENT_MAGENTA, letter_spacing=3, anchor="middle"),
    ]

    # six stages laid out on an ellipse so bottom and top boxes don't crowd
    # the central glyph
    cx, cy = W / 2, 590
    Rx, Ry = 540, 340
    stages = [
        ("Speak",     "Spokenly MCP\nask_user_dictation"),
        ("Route",     "Voice Orion\ndeterministic router"),
        ("Approve",   "Aegis · Violet Covenant\napproval + TTL"),
        ("Act",       "DLAM / R1 / API\nsafe execution"),
        ("Verify",    "Evidence ledger\nfile-backed receipts"),
        ("Remember",  "R.I.P. · Knowledge Graph\ncanonical memory"),
    ]
    positions: list[tuple[float, float]] = []
    for i in range(6):
        # start at top, go clockwise
        angle = -90 + i * 60
        x = cx + Rx * math.cos(math.radians(angle))
        y = cy + Ry * math.sin(math.radians(angle))
        positions.append((x, y))

    box_w, box_h = 300, 132
    for i, (name, sub) in enumerate(stages):
        x, y = positions[i]
        bx = x - box_w / 2
        by = y - box_h / 2
        parts.append(_box(bx, by, box_w, box_h, fill=WHITE, stroke=INDIGO, sw=3, rx=18))
        parts.append(_t(x, by + 50, name, size=28, weight=800, fill=INK, anchor="middle"))
        for j, line in enumerate(sub.split("\n")):
            parts.append(_t(x, by + 84 + j * 24, line, size=18, weight=500,
                            fill=GREY, anchor="middle"))
        parts.append(_t(bx + 16, by + 28, f"0{i+1}", size=16, weight=700,
                        fill=ACCENT_MAGENTA, letter_spacing=2))

    # arrows between consecutive stages along the perimeter
    hw, hh = box_w / 2, box_h / 2
    for i in range(6):
        x0, y0 = positions[i]
        x1, y1 = positions[(i + 1) % 6]
        dx, dy = x1 - x0, y1 - y0
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        # Distance from box center to edge along this direction (rectangle).
        eps = 1e-6
        t_box = min(hw / max(abs(ux), eps), hh / max(abs(uy), eps))
        clear = t_box + 12  # small clearance from the rounded edge
        sx, sy = x0 + ux * clear, y0 + uy * clear
        ex, ey = x1 - ux * clear, y1 - uy * clear
        color = ACCENT_MAGENTA if i == 5 else INDIGO
        marker = "arrow-m" if i == 5 else "arrow-i"
        parts.append(
            f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
            f'stroke="{color}" stroke-width="3" marker-end="url(#{marker})"/>'
        )

    # central glyph (smaller so it doesn't fight the surrounding boxes)
    parts.append(loop_glyph(cx=cx, cy=cy, r=110, stroke_width=20,
                            color_arc=INDIGO, color_play=INDIGO,
                            use_gradient=True, gradient_id=grad_id))
    parts.append(_t(cx, cy + 165, "speak · route · approve · act · verify · remember",
                    size=20, weight=400, fill=GREY, anchor="middle", italic=True))

    # footer principles
    parts.append(
        f'<line x1="80" y1="1000" x2="1840" y2="1000" stroke="{INDIGO}" '
        f'stroke-width="1" opacity="0.25"/>'
    )
    parts.append(_t(80, 1045, "No proof, no claim.", size=20, weight=700, fill=INDIGO))
    parts.append(_t(380, 1045, "Approval before action.", size=20, weight=700, fill=INDIGO))
    parts.append(_t(760, 1045, "Evidence with every action.", size=20, weight=700, fill=INDIGO))
    parts.append(_t(1200, 1045, "Memory is canonical.", size=20, weight=700, fill=INDIGO))
    parts.append(_t(1840, 1045, "AGENTIC OS · LOVELOGICAI",
                    size=16, weight=600, fill=GREY, anchor="end", letter_spacing=3))

    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# 2. Nine-layer stack
# ---------------------------------------------------------------------------
def nine_layers() -> str:
    W, H = 1080, 1500
    parts: list[str] = [
        f'<defs>{gradient_def("nine-grad")}</defs>',
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        _t(60, 90, "Nine Layers", size=58, weight=800, fill=INK, letter_spacing=-1),
        _t(60, 135, "From human voice to canonical truth.",
           size=24, weight=400, fill=GREY),
    ]
    layers = [
        ("9", "Ambient state · storytelling", "glyphy pets · CYOA",                 "#FBE3F3", ACCENT_MAGENTA),
        ("8", "Productization · packaging",   "zopack · portable bundles",          "#EEE0FF", ACCENT_VIOLET),
        ("7", "Governance · verification",    "Aegis · Violet Covenant",            "#DCE2FF", INDIGO),
        ("6", "Memory · identity",            "R.I.P. · Knowledge Graph",           "#DCE2FF", INDIGO),
        ("5", "Orchestration mesh",           "OpenClaw · peer coordination",       "#DCE2FF", INDIGO),
        ("4", "Execution edge",               "DLAM / R1 · API adapters · Zo",      "#E1ECFF", INDIGO),
        ("3", "Command edge",                 "Voice Orion · Command Palette",      "#E1ECFF", INDIGO),
        ("2", "Desktop edge",                 "tmux · VS Code browser · SSH",       "#E9F0FF", INDIGO),
        ("1", "Voice edge",                   "Spokenly MCP",                       "#E9F0FF", INDIGO),
    ]
    box_x, box_y, box_w, box_h, gap = 60, 200, 960, 120, 16
    for i, (num, name, sub, fill, accent) in enumerate(layers):
        y = box_y + i * (box_h + gap)
        parts.append(_box(box_x, y, box_w, box_h, fill=fill, stroke=accent, sw=2, rx=14))
        # number badge
        parts.append(
            f'<rect x="{box_x + 22}" y="{y + 22}" width="76" height="76" rx="16" '
            f'fill="{accent}"/>'
        )
        parts.append(_t(box_x + 60, y + 75, num, size=44, weight=800,
                        fill=WHITE, anchor="middle"))
        # text
        parts.append(_t(box_x + 130, y + 55, name, size=30, weight=700, fill=INK))
        parts.append(_t(box_x + 130, y + 92, sub, size=22, weight=400, fill=GREY))
    parts.append(_t(60, 1465, "AGENTIC OS · LOVELOGICAI",
                    size=18, weight=600, fill=GREY, letter_spacing=3))
    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# 3. Governance / approval gate close-up
# ---------------------------------------------------------------------------
def governance_gate() -> str:
    W, H = 1600, 900
    parts: list[str] = [
        f'<defs>{_arrow_marker("g-arrow-i", INDIGO)}'
        f'{_arrow_marker("g-arrow-m", ACCENT_MAGENTA)}'
        f'{_arrow_marker("g-arrow-g", "#1F8F4F")}</defs>',
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        _t(60, 90, "Governance Gate", size=56, weight=800, fill=INK, letter_spacing=-1),
        _t(60, 135,
           "Risky paths require approval. Safe paths execute. Both are evidenced.",
           size=24, weight=400, fill=GREY),
    ]
    # Router
    parts.append(_box(120, 240, 280, 130, fill=WHITE, stroke=INDIGO, sw=3, rx=14))
    parts.append(_t(260, 295, "Router", size=30, weight=800, fill=INK, anchor="middle"))
    parts.append(_t(260, 330, "intent · trust score", size=20, weight=500,
                    fill=GREY, anchor="middle"))
    # safe path  — top branch
    parts.append(_box(560, 130, 320, 130, fill="#E8F6EE", stroke="#1F8F4F", sw=3, rx=14))
    parts.append(_t(720, 185, "Safe path", size=28, weight=800,
                    fill="#0E5C32", anchor="middle"))
    parts.append(_t(720, 220, "low risk · whitelisted",
                    size=20, weight=500, fill="#1F8F4F", anchor="middle"))
    # risky path → approval gate (middle)
    parts.append(_box(560, 320, 320, 130, fill="#FFE8F5",
                      stroke=ACCENT_MAGENTA, sw=3, rx=14))
    parts.append(_t(720, 375, "Approval gate", size=28, weight=800,
                    fill="#84106F", anchor="middle"))
    parts.append(_t(720, 410, "operator approves · TTL expires",
                    size=18, weight=500, fill=ACCENT_MAGENTA, anchor="middle"))
    # blocked path
    parts.append(_box(560, 510, 320, 130, fill="#FCE8E8", stroke="#C02525", sw=3, rx=14))
    parts.append(_t(720, 565, "Blocked", size=28, weight=800,
                    fill="#7A1212", anchor="middle"))
    parts.append(_t(720, 600, "denied · timeout", size=20, weight=500,
                    fill="#C02525", anchor="middle"))
    # action
    parts.append(_box(1040, 240, 280, 130, fill=WHITE, stroke=INDIGO, sw=3, rx=14))
    parts.append(_t(1180, 295, "Action", size=30, weight=800, fill=INK, anchor="middle"))
    parts.append(_t(1180, 330, "CLI · Desktop · API", size=20, weight=500,
                    fill=GREY, anchor="middle"))
    # evidence
    parts.append(_box(1040, 510, 280, 130, fill=WHITE, stroke=INDIGO, sw=3, rx=14))
    parts.append(_t(1180, 565, "Evidence", size=30, weight=800, fill=INK, anchor="middle"))
    parts.append(_t(1180, 600, "ledger · receipts · diff", size=20, weight=500,
                    fill=GREY, anchor="middle"))
    # arrows
    def line(x1, y1, x2, y2, color, marker, label=None, label_y=None):
        out = [
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="3" marker-end="url(#{marker})"/>'
        ]
        if label:
            mx = (x1 + x2) / 2
            my = label_y if label_y is not None else (y1 + y2) / 2 - 8
            out.append(_t(mx, my, label, size=18, weight=600,
                          fill=color, anchor="middle", italic=True))
        return "".join(out)
    parts.append(line(400, 280, 560, 195, "#1F8F4F", "g-arrow-g", "safe", 230))
    parts.append(line(400, 305, 560, 385, ACCENT_MAGENTA, "g-arrow-m", "risky", 360))
    parts.append(line(400, 330, 560, 575, "#C02525", "g-arrow-i", "denied", 510))
    parts.append(line(880, 195, 1040, 280, "#1F8F4F", "g-arrow-g"))
    parts.append(line(880, 385, 1040, 305, ACCENT_MAGENTA, "g-arrow-m",
                      "approved", 330))
    # action -> evidence
    parts.append(line(1180, 370, 1180, 510, INDIGO, "g-arrow-i", "logged", 440))
    # blocked -> evidence (audit trail)
    parts.append(line(880, 575, 1040, 575, "#C02525", "g-arrow-i",
                      "audited", 565))
    # principles
    parts.append(_t(60, 800, "·  No proof, no claim.",
                    size=24, weight=700, fill=INDIGO))
    parts.append(_t(60, 838, "·  High-risk actions must be approved.",
                    size=24, weight=700, fill=INDIGO))
    parts.append(_t(60, 876, "·  Evidence must accompany every action — including denials.",
                    size=24, weight=700, fill=INDIGO))
    parts.append(_t(W - 60, 876, "AGENTIC OS · LOVELOGICAI",
                    size=18, weight=600, fill=GREY, anchor="end", letter_spacing=3))
    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# 4. System contract triad
# ---------------------------------------------------------------------------
def system_contract() -> str:
    W, H = 1600, 900
    parts: list[str] = [
        f'<defs>{_arrow_marker("c-arrow", INDIGO)}</defs>',
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        _t(60, 90, "System Contract", size=56, weight=800, fill=INK, letter_spacing=-1),
        _t(60, 135, "Input → Processing → Output. Diffable, replayable, auditable.",
           size=24, weight=400, fill=GREY),
    ]
    cols = [
        ("INPUT", [
            "spoken request",
            "typed request",
            "clarification answer",
            "API request",
            "operator approval",
        ], INDIGO),
        ("PROCESSING", [
            "classify intent",
            "determine trust",
            "route to execution",
            "require approval",
            "log evidence",
            "update memory",
        ], ACCENT_VIOLET),
        ("OUTPUT", [
            "completed action",
            "approval request",
            "response to user",
            "evidence artifact",
            "memory update",
        ], ACCENT_MAGENTA),
    ]
    col_w, col_h, col_gap = 440, 560, 60
    start_x = (W - (col_w * 3 + col_gap * 2)) / 2
    for i, (title, items, accent) in enumerate(cols):
        x = start_x + i * (col_w + col_gap)
        y = 230
        parts.append(_box(x, y, col_w, col_h, fill=WHITE, stroke=accent, sw=3, rx=20))
        # title bar
        parts.append(
            f'<rect x="{x}" y="{y}" width="{col_w}" height="80" rx="20" fill="{accent}"/>'
        )
        # bottom rounding fix: cover bottom of bar
        parts.append(
            f'<rect x="{x}" y="{y + 50}" width="{col_w}" height="32" fill="{accent}"/>'
        )
        parts.append(_t(x + col_w / 2, y + 53, title, size=32, weight=800,
                        fill=WHITE, anchor="middle", letter_spacing=6))
        for j, item in enumerate(items):
            iy = y + 130 + j * 60
            parts.append(f'<circle cx="{x + 40}" cy="{iy - 10}" r="8" fill="{accent}"/>')
            parts.append(_t(x + 64, iy - 4, item, size=22, weight=500, fill=INK))
        # connector arrow to next column
        if i < 2:
            ax = x + col_w + 6
            parts.append(
                f'<line x1="{ax}" y1="{y + col_h / 2}" x2="{ax + col_gap - 12}" '
                f'y2="{y + col_h / 2}" stroke="{INDIGO}" stroke-width="3" '
                f'marker-end="url(#c-arrow)"/>'
            )
    parts.append(_t(W / 2, 870,
                    "Every input is observed.   Every step is logged.   Every output is verifiable.",
                    size=22, weight=600, fill=INDIGO, anchor="middle"))
    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# 5. Three-gaps comparison
# ---------------------------------------------------------------------------
def three_gaps() -> str:
    W, H = 1600, 900
    parts: list[str] = [
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        _t(60, 90, "Most agent stacks fail in three places.",
           size=46, weight=800, fill=INK, letter_spacing=-1),
        _t(60, 135, "Agentic OS closes all three gaps.",
           size=28, weight=500, fill=ACCENT_MAGENTA),
    ]
    rows = [
        ("Asking",   "Cannot ask reliable clarifying questions.",
                     "Spokenly MCP — voice-native dictation as a tool."),
        ("Acting",   "Cannot execute safely across desktop and API surfaces.",
                     "DLAM/R1 + governed adapters — approval-gated, scoped."),
        ("Remembering", "Cannot remember in a canonical, auditable way.",
                        "R.I.P. + Knowledge Graph — diffable, claim-backed memory."),
    ]
    row_h = 180
    start_y = 220
    for i, (name, gap, fix) in enumerate(rows):
        y = start_y + i * (row_h + 20)
        # left: gap (red-tinted)
        parts.append(_box(60, y, 660, row_h, fill="#FFEFEF",
                          stroke="#C02525", sw=2, rx=14))
        parts.append(_t(85, y + 50, "GAP", size=18, weight=800,
                        fill="#C02525", letter_spacing=4))
        parts.append(_t(85, y + 100, name, size=32, weight=800, fill="#7A1212"))
        parts.append(_t(85, y + 145, gap, size=20, weight=500, fill="#7A1212"))
        # arrow pointing right (gap → fix)
        my = y + row_h / 2
        parts.append(
            f'<path d="M 740 {my - 18} L 740 {my - 6} L 770 {my - 6} '
            f'L 770 {my - 18} L 820 {my} L 770 {my + 18} '
            f'L 770 {my + 6} L 740 {my + 6} L 740 {my + 18} Z" '
            f'fill="{INDIGO}"/>'
        )
        # right: fix (green-tinted)
        parts.append(_box(840, y, 700, row_h, fill="#E8F6EE",
                          stroke="#1F8F4F", sw=2, rx=14))
        parts.append(_t(865, y + 50, "AGENTIC OS", size=18, weight=800,
                        fill="#0E5C32", letter_spacing=4))
        parts.append(_t(865, y + 100, name, size=32, weight=800, fill="#0E5C32"))
        parts.append(_t(865, y + 145, fix, size=20, weight=500, fill="#0E5C32"))
    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# 6. Evidence + memory feedback loop
# ---------------------------------------------------------------------------
def evidence_flow() -> str:
    W, H = 1600, 900
    parts: list[str] = [
        f'<defs>{_arrow_marker("e-arrow", INDIGO)}'
        f'{_arrow_marker("e-arrow-m", ACCENT_MAGENTA)}</defs>',
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        _t(60, 90, "Evidence + Memory Loop", size=54, weight=800, fill=INK,
           letter_spacing=-1),
        _t(60, 135, "Action becomes receipt. Receipt becomes claim. Claim becomes truth.",
           size=24, weight=400, fill=GREY),
    ]
    # Five boxes left-to-right
    nodes = [
        ("Action",   "CLI · Desktop · API"),
        ("Receipt",  "stdout · screenshot · diff"),
        ("Ledger",   "evidence ledger\nfile-backed, rotated"),
        ("Claim",    "R.I.P.\ncanonical statement"),
        ("Memory",   "Knowledge Graph\noperational truth"),
    ]
    nx, ny, bw, bh, gap = 60, 290, 280, 200, 30
    for i, (title, sub) in enumerate(nodes):
        x = nx + i * (bw + gap)
        parts.append(_box(x, ny, bw, bh, fill=WHITE, stroke=INDIGO, sw=3, rx=18))
        parts.append(_t(x + bw / 2, ny + 70, title, size=32, weight=800,
                        fill=INK, anchor="middle"))
        for j, line in enumerate(sub.split("\n")):
            parts.append(_t(x + bw / 2, ny + 115 + j * 28, line, size=20,
                            weight=500, fill=GREY, anchor="middle"))
        parts.append(_t(x + 18, ny + 35, f"0{i+1}", size=18, weight=700,
                        fill=ACCENT_MAGENTA, letter_spacing=2))
        if i < len(nodes) - 1:
            ax = x + bw + 4
            parts.append(
                f'<line x1="{ax}" y1="{ny + bh / 2}" '
                f'x2="{ax + gap - 8}" y2="{ny + bh / 2}" '
                f'stroke="{INDIGO}" stroke-width="3" marker-end="url(#e-arrow)"/>'
            )
    # feedback arc Memory → Action (the loop)
    parts.append(
        f'<path d="M {nx + 4 * (bw + gap) + bw / 2} {ny + bh + 8} '
        f'C {nx + 4 * (bw + gap) + bw / 2} {ny + bh + 200}, '
        f'{nx + bw / 2} {ny + bh + 200}, '
        f'{nx + bw / 2} {ny + bh + 8}" fill="none" '
        f'stroke="{ACCENT_MAGENTA}" stroke-width="3" stroke-dasharray="6 6" '
        f'marker-end="url(#e-arrow-m)"/>'
    )
    parts.append(_t(W / 2, ny + bh + 230,
                    "remembered context informs the next action",
                    size=22, weight=600, fill=ACCENT_MAGENTA, anchor="middle",
                    italic=True))
    parts.append(_t(60, 870, "AGENTIC OS · LOVELOGICAI",
                    size=18, weight=600, fill=GREY, letter_spacing=3))
    return svg_doc(W, H, "".join(parts))


# ---------------------------------------------------------------------------
# Build pipeline
# ---------------------------------------------------------------------------
def write_and_render(name: str, content: str, *, width: int) -> None:
    svg_path = DEMO / f"{name}.svg"
    png_path = DEMO / f"{name}.png"
    svg_path.write_text(content)
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=width)


def main() -> None:
    write_and_render("agentic-os-one-loop-hero", one_loop_hero(), width=1920)
    write_and_render("agentic-os-nine-layers", nine_layers(), width=1080)
    write_and_render("agentic-os-governance-gate", governance_gate(), width=1600)
    write_and_render("agentic-os-system-contract", system_contract(), width=1600)
    write_and_render("agentic-os-three-gaps", three_gaps(), width=1600)
    write_and_render("agentic-os-evidence-flow", evidence_flow(), width=1600)
    print("\nGenerated demonstration graphics:")
    for entry in sorted(DEMO.iterdir()):
        size = entry.stat().st_size
        print(f"  {entry.name:50s} {size:>8d} bytes")


if __name__ == "__main__":
    main()
