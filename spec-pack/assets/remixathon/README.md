# `spec-pack/assets/remixathon/`

Submission asset pack for the **Anything Remixathon** (Linear #17, May 2026).

```
remixathon/
├── CHECKLIST.md                # what's done vs what's still owed by the operator
├── build_logos.py              # regenerates logo/
├── build_demo_graphics.py      # regenerates demo/
├── build_jam_assets.py         # regenerates jam/ overlays + cards
├── logo/                       # 28 logo + social + favicon files
├── demo/                       # 12 system demonstration diagrams
└── jam/                        # 39 video overlays + EDL.md + ffmpeg-recipe.sh
```

Start at [`CHECKLIST.md`](./CHECKLIST.md). It tracks every artifact and the
two operator-side blockers (master recording + voiceover) that remain.

## Brand quick reference

| Token        | Hex       | Usage                                           |
|--------------|-----------|-------------------------------------------------|
| Indigo       | `#0D32B2` | primary color                                   |
| Ink          | `#0A0F25` | dark backgrounds, body text                     |
| Paper        | `#F7F8FE` | light backgrounds                               |
| White        | `#FFFFFF` | foreground on dark bg                           |
| Grey         | `#3A3E50` | secondary text                                  |
| Magenta      | `#FF2BD6` | remix accent (final arc, callouts, CTAs)        |
| Violet       | `#7A29FF` | remix accent (gradient pair with magenta)       |

The signature glyph is six arc segments around a circle (one per loop stage —
speak · route · approve · act · verify · remember), with a play triangle in
the center, and a magenta→violet gradient applied to the final arc that closes
the loop.
