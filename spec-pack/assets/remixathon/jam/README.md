# Anything Remixathon — Jam Recording Edits

This folder contains everything needed to edit the Remixathon submission video
without writing any new graphics or animation.

## What's here

| File                                       | Purpose                                          |
| ------------------------------------------ | ------------------------------------------------ |
| `EDL.md`                                   | Edit decision list — exact timestamps, voiceover beats, asset map |
| `ffmpeg-recipe.sh`                         | One-shot renderer; consumes `source/master.mp4` and emits `out/submission-1080p.mp4` |
| `jam-title-card.{svg,png}`                 | 8s opening title (1920×1080)                     |
| `jam-end-card.{svg,png}`                   | 10s closing CTA card (1920×1080)                 |
| `jam-chapter-{1..6}-{name}.{svg,png}`      | 6s chapter dividers, one per loop stage           |
| `jam-lower-third-{1..6}-{slug}.{svg,png}`  | Lower-third overlays (transparent BG)             |
| `jam-callout-{slug}.{svg,png}`             | Mid-frame callout pill overlays (transparent BG)  |
| `jam-corner-bug.{svg,png}`                 | Persistent watermark overlay (transparent BG)     |

All overlays are 1920×1080 with transparent backgrounds — drop them straight
on top of your screen recording.

## Quick render

1. Drop your screen recording at `source/master.mp4` (1920×1080, 30 fps).
   Aim for ~2:42 of demo footage (the title and end cards add ~0:18).
2. Optionally add `source/voiceover.wav` and `source/music.wav`.
3. Run:

   ```bash
   bash ffmpeg-recipe.sh --preview     # 480p draft, ~30s render
   bash ffmpeg-recipe.sh               # 1080p final
   ```

4. Final cut lands at `out/submission-1080p.mp4`.

## Capture suggestion

```bash
ffmpeg -framerate 30 -f x11grab -video_size 1920x1080 -i :0.0 \
       -f pulse -i default \
       -c:v libx264 -preset veryfast -crf 18 \
       -c:a aac -b:a 192k \
       -y source/master.mp4
```

Stop with `q` once you've completed the demo.

## Editor (NLE) workflow

If you'd rather cut in DaVinci Resolve / Premiere / Final Cut:

1. Import the screen recording onto V1.
2. Drop `jam-title-card.png` on V2 as 0:00→0:08; key its alpha (it's opaque, so set its V1 cut to start at 0:08).
3. Drop chapter cards on V2 at the master timestamps in `EDL.md`.
4. Drop lower-thirds and callouts on V3/V4 over the live footage at the EDL
   times — they have transparent backgrounds, so no keying needed.
5. Drop `jam-corner-bug.png` on V5 spanning the whole demo (00:20 → 02:50 in
   the master cut) for the persistent watermark.
6. Place `jam-end-card.png` on V1 at 02:50→03:00.
7. Export 1080p H.264, CRF 18, AAC 192k, 30 fps.

Voiceover beats are in `EDL.md`, "Master Timeline" table.
