# Anything Remixathon — Jam Recording Edit Decision List

> Submission cut for Linear #17. Target runtime: **~3:00**, max 4:00.
> All overlays render at 1920×1080. Lower thirds and callouts have transparent
> backgrounds, so they composite cleanly over screen-recording footage.

---

## Tone

- Calm, declarative voiceover. Demonstrate, don't explain.
- Cuts on every action: **speak → see the loop close.** No drift, no buffering pauses.
- Color: keep desktop captures slightly desaturated; let the magenta-violet accents pop only on overlays and end card.
- Sound: soft synth pad underneath, single percussive hit on each chapter card.

## Master Timeline (target 3:00)

| t (mm:ss) | Duration | Segment                | Visual                                          | Overlay                         | Voiceover beat                                                                   |
|----------:|---------:|------------------------|-------------------------------------------------|---------------------------------|-----------------------------------------------------------------------------------|
| 00:00     | 0:08     | **Title**              | `jam-title-card.png`, gentle zoom-in (Ken Burns 1.0→1.05) | —                               | (silent) cold open + brand intro                                                  |
| 00:08     | 0:12     | **Cold thesis**        | hero shot: full-screen `agentic-os-one-loop-hero.png`     | `jam-callout-no-proof.png` from 00:14 | "Most agent stacks stop at conversation. This one closes the loop."             |
| 00:20     | 0:08     | **Chapter 01: Speak**  | `jam-chapter-1-speak.png` (0.5s) → live screen of Spokenly MCP issuing `ask_user_dictation`     | `jam-lower-third-1-spokenly-mcp.png`           | "Step one — speak. The system asks the right clarifying question."                |
| 00:28     | 0:18     | **Live Speak demo**    | screen recording of voice → transcript          | corner bug ON                   | (operator demo) "I want to deploy phase-0."                                       |
| 00:46     | 0:06     | **Chapter 02: Route**  | `jam-chapter-2-route.png`                        | `jam-lower-third-2-voice-orion.png`            | "Step two — route. Deterministic. No model drift."                                |
| 00:52     | 0:14     | **Live Route demo**    | terminal showing rule-based intent classifier outputs | callout: "Deterministic — no LLM drift." | "Voice Orion classifies intent against a fixed schema."                       |
| 01:06     | 0:06     | **Chapter 03: Approve**| `jam-chapter-3-approve.png`                      | `jam-lower-third-3-aegis-violet-covenant.png`  | "Step three — approve. High-risk actions wait for a human."                       |
| 01:12     | 0:18     | **Live Approve demo**  | UI showing approval prompt with countdown TTL   | `jam-callout-approval-gate.png` | "Approve once, expires automatically."                                            |
| 01:30     | 0:06     | **Chapter 04: Act**    | `jam-chapter-4-act.png`                          | `jam-lower-third-4-dlam-r1-zo-api.png`         | "Step four — act. Desktop, CLI, API — same governance."                           |
| 01:36     | 0:18     | **Live Act demo**      | scripted desktop action (e.g. opening a URL, pasting a snippet) | corner bug ON                   | "DLAM/R1 takes the keys, runs the action, returns the result."                    |
| 01:54     | 0:06     | **Chapter 05: Verify** | `jam-chapter-5-verify.png`                       | `jam-lower-third-5-evidence-ledger.png`        | "Step five — verify. Every action leaves a receipt."                              |
| 02:00     | 0:14     | **Live Verify demo**   | tail of `evidence/<run-id>.jsonl` rolling into terminal | callout: "Receipts on disk."  | "stdout, screenshot, diff. Append-only ledger."                                  |
| 02:14     | 0:06     | **Chapter 06: Remember** | `jam-chapter-6-remember.png`                  | `jam-lower-third-6-rip-knowledge-graph.png`    | "Step six — remember. The receipt becomes a claim."                              |
| 02:20     | 0:16     | **Live Remember demo** | open Knowledge Graph node showing the claim    | `jam-callout-memory-canonical.png`             | "Claims live in R.I.P., context lives in the Knowledge Graph."                   |
| 02:36     | 0:14     | **Loop closes**        | crossfade back to `agentic-os-one-loop-hero.png`; magenta accent arc pulses | corner bug ON                   | "Speak. Route. Approve. Act. Verify. Remember. — and ask again, smarter."        |
| 02:50     | 0:10     | **End card**           | `jam-end-card.png` with subtle parallax         | —                               | "Anything Remixathon — agentic-os. Remix the loop."                              |

Total: **3:00**.

## Caption / subtitle style

- Position: bottom-center, 2 lines max, 36px DejaVu Sans Bold, white on translucent ink (`#0A0F25CC`).
- Punctuation matches the master spec: short declarative sentences, one principle per shot.
- Avoid filler: cut "um", "uh", "kind of".

## B-roll suggestions (optional, if runtime allows)

- 1× wide of the operator at desk — under voiceover only, no narration on camera.
- 1× macro shot of the R1 / desktop edge if available.
- Animated reveal of `agentic-os-nine-layers.png` for a 5-second establishing shot before Chapter 01.

## Deliverables

After cut, export:

1. `submission-1080p.mp4` — H.264, CRF 18, AAC 192k, 30 fps.
2. `submission-vertical.mp4` — 1080×1920 cropped/letterboxed for Reels/TikTok (optional).
3. `submission-thumbnail.png` — first frame of `jam-title-card.png` rendered at 1280×720.

## Asset map (overlay file → moment)

| Overlay file                                                | Insert at | Duration |
|-------------------------------------------------------------|----------:|---------:|
| `jam-title-card.png`                                        | 00:00     | 0:08     |
| `jam-callout-no-proof.png`                                  | 00:14     | 0:06     |
| `jam-chapter-1-speak.png`                                   | 00:20     | 0:08     |
| `jam-lower-third-1-spokenly-mcp.png`                        | 00:30     | 0:14     |
| `jam-chapter-2-route.png`                                   | 00:46     | 0:06     |
| `jam-lower-third-2-voice-orion.png`                         | 00:54     | 0:12     |
| `jam-chapter-3-approve.png`                                 | 01:06     | 0:06     |
| `jam-lower-third-3-aegis-violet-covenant.png`               | 01:14     | 0:14     |
| `jam-callout-approval-gate.png`                             | 01:18     | 0:08     |
| `jam-chapter-4-act.png`                                     | 01:30     | 0:06     |
| `jam-lower-third-4-dlam-r1-zo-api.png`                      | 01:38     | 0:14     |
| `jam-chapter-5-verify.png`                                  | 01:54     | 0:06     |
| `jam-lower-third-5-evidence-ledger.png`                     | 02:02     | 0:10     |
| `jam-chapter-6-remember.png`                                | 02:14     | 0:06     |
| `jam-lower-third-6-rip-knowledge-graph.png`                 | 02:22     | 0:12     |
| `jam-callout-memory-canonical.png`                          | 02:24     | 0:08     |
| `jam-corner-bug.png`                                        | 00:28 → 02:50 (persistent during demos) | — |
| `jam-end-card.png`                                          | 02:50     | 0:10     |

## ffmpeg recipe

See `ffmpeg-recipe.sh`. It assumes a master screen recording at
`source/master.mp4` and produces `out/submission-1080p.mp4` with all overlay
images applied at the timestamps above.
