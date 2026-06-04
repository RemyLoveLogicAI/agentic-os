#!/usr/bin/env bash
# Anything Remixathon submission — ffmpeg recipe.
#
# Inputs (place yourself before running):
#   source/master.mp4    Screen recording, 1920x1080, 30fps. Aim for ~2:42 of
#                        live demo footage (00:18 to 03:00 in the EDL leaves
#                        00:18 of pre-roll/post-roll for title/end cards).
#   source/voiceover.wav OPTIONAL. If absent, the master.mp4 audio is used.
#   source/music.wav     OPTIONAL. Soft underscore mixed at -18 dB.
#
# Outputs:
#   out/submission-1080p.mp4
#
# Usage:
#   bash ffmpeg-recipe.sh                          # full render
#   bash ffmpeg-recipe.sh --preview                # 480p draft, ~10x faster
#   bash ffmpeg-recipe.sh --section title          # render just the title card
#
# Requirements: ffmpeg >= 5.0 with libx264, libfreetype, fontconfig.
#
# Notes:
#   * All overlays are applied with `enable='between(t,A,B)'` filters, where A
#     and B come straight from EDL.md's "Insert at" / "Duration" columns.
#   * Chapter and title cards are rendered as ~6-second clips by looping the
#     PNG at 30fps; they are concatenated in front of (and behind) the live
#     footage with the concat demuxer.
#   * If you only have part of the demo footage, comment out the corresponding
#     overlay lines and re-run. The render is idempotent.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${HERE}"

SOURCE="source/master.mp4"
VO="source/voiceover.wav"
MUSIC="source/music.wav"
OUT_DIR="out"
mkdir -p "${OUT_DIR}" "source"

if [[ ! -f "${SOURCE}" ]]; then
  cat <<EOF >&2
[ffmpeg-recipe] Missing source recording at ${SOURCE}.

  Drop your screen recording there (1920x1080, 30fps), then re-run.
  Suggested capture command:

    ffmpeg -framerate 30 -f x11grab -video_size 1920x1080 -i :0.0 \\
           -c:v libx264 -preset veryfast -crf 18 -y source/master.mp4

EOF
  exit 1
fi

PREVIEW=0
SECTION="all"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --preview) PREVIEW=1; shift;;
    --section) SECTION="$2"; shift 2;;
    *) echo "[ffmpeg-recipe] Unknown arg: $1" >&2; exit 2;;
  esac
done

SCALE_FILTER="scale=1920:1080"
OVERLAY_SCALE="scale=1920:1080"
PRESET="medium"
CRF="18"
if [[ "${PREVIEW}" == "1" ]]; then
  SCALE_FILTER="scale=854:480"
  OVERLAY_SCALE="scale=854:480"
  PRESET="ultrafast"
  CRF="28"
fi

# ---------------------------------------------------------------------------
# 1) Build pre-roll (title) and post-roll (end) clips from PNGs.
# ---------------------------------------------------------------------------
build_card_clip() {
  local png="$1" duration="$2" out="$3"
  ffmpeg -y -loop 1 -t "${duration}" -i "${png}" \
    -vf "fps=30,${SCALE_FILTER},format=yuv420p" \
    -c:v libx264 -preset "${PRESET}" -crf "${CRF}" -an "${out}"
}

if [[ "${SECTION}" == "title" || "${SECTION}" == "all" ]]; then
  build_card_clip "jam-title-card.png" 8 "${OUT_DIR}/_title.mp4"
fi
if [[ "${SECTION}" == "end" || "${SECTION}" == "all" ]]; then
  build_card_clip "jam-end-card.png" 10 "${OUT_DIR}/_end.mp4"
fi

if [[ "${SECTION}" == "title" || "${SECTION}" == "end" ]]; then
  echo "[ffmpeg-recipe] Section ${SECTION} rendered — see ${OUT_DIR}/."
  exit 0
fi

# ---------------------------------------------------------------------------
# 2) Apply overlays + corner bug to the master demo footage.
#    Timestamps below are RELATIVE to the start of master.mp4 (which begins at
#    00:08 in the final cut, so subtract 8s from each EDL timestamp).
# ---------------------------------------------------------------------------
# (EDL t)  -> (master t)
#   00:14  ->  00:06  callout-no-proof
#   00:20  ->  00:12  chapter-1-speak
#   00:30  ->  00:22  lower-third-1
#   00:46  ->  00:38  chapter-2-route
#   00:54  ->  00:46  lower-third-2
#   01:06  ->  00:58  chapter-3-approve
#   01:14  ->  01:06  lower-third-3
#   01:18  ->  01:10  callout-approval-gate
#   01:30  ->  01:22  chapter-4-act
#   01:38  ->  01:30  lower-third-4
#   01:54  ->  01:46  chapter-5-verify
#   02:02  ->  01:54  lower-third-5
#   02:14  ->  02:06  chapter-6-remember
#   02:22  ->  02:14  lower-third-6
#   02:24  ->  02:16  callout-memory-canonical
#   00:20-02:42 ->    persistent corner bug

OVERLAYS=(
  "jam-callout-no-proof.png:6:6"
  "jam-chapter-1-speak.png:12:8"
  "jam-lower-third-1-spokenly-mcp.png:22:14"
  "jam-chapter-2-route.png:38:6"
  "jam-lower-third-2-voice-orion.png:46:12"
  "jam-chapter-3-approve.png:58:6"
  "jam-lower-third-3-aegis-violet-covenant.png:66:14"
  "jam-callout-approval-gate.png:70:8"
  "jam-chapter-4-act.png:82:6"
  "jam-lower-third-4-dlam-r1-zo-api.png:90:14"
  "jam-chapter-5-verify.png:106:6"
  "jam-lower-third-5-evidence-ledger.png:114:10"
  "jam-chapter-6-remember.png:126:6"
  "jam-lower-third-6-rip-knowledge-graph.png:134:12"
  "jam-callout-memory-canonical.png:136:8"
)

# Build the input list and the filter graph dynamically.
INPUTS=( -i "${SOURCE}" )
FILTER="[0:v]${SCALE_FILTER},format=yuva420p[base];"
PREV="base"
IDX=1

for spec in "${OVERLAYS[@]}"; do
  IFS=':' read -r FILE START DUR <<<"${spec}"
  END=$(awk -v s="${START}" -v d="${DUR}" 'BEGIN{printf "%d", s+d}')
  INPUTS+=( -i "${FILE}" )
  PRE="ov${IDX}p"
  LABEL="ov${IDX}"
  # Pre-scale every overlay to the base resolution so overlay coords line up.
  FILTER+="[${IDX}:v]${OVERLAY_SCALE},format=rgba[${PRE}];"
  FILTER+="[${PREV}][${PRE}]overlay=0:0:enable='between(t,${START},${END})'[${LABEL}];"
  PREV="${LABEL}"
  IDX=$((IDX + 1))
done

# Persistent corner bug across the whole demo.
INPUTS+=( -i "jam-corner-bug.png" )
PRE="ov${IDX}p"
LABEL="ov${IDX}"
FILTER+="[${IDX}:v]${OVERLAY_SCALE},format=rgba[${PRE}];"
FILTER+="[${PREV}][${PRE}]overlay=0:0[${LABEL}]"
PREV="${LABEL}"

# ---------------------------------------------------------------------------
# 3) Render the demo body with overlays.
# ---------------------------------------------------------------------------
ffmpeg -y "${INPUTS[@]}" \
  -filter_complex "${FILTER}" \
  -map "[${PREV}]" -map 0:a? \
  -c:v libx264 -preset "${PRESET}" -crf "${CRF}" -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest \
  "${OUT_DIR}/_body.mp4"

# ---------------------------------------------------------------------------
# 4) Concat title + body + end into the final submission.
# ---------------------------------------------------------------------------
CONCAT_LIST="${OUT_DIR}/_concat.txt"
{
  echo "file '_title.mp4'"
  echo "file '_body.mp4'"
  echo "file '_end.mp4'"
} > "${CONCAT_LIST}"

ffmpeg -y -f concat -safe 0 -i "${CONCAT_LIST}" \
  -c:v libx264 -preset "${PRESET}" -crf "${CRF}" \
  -c:a aac -b:a 192k -movflags +faststart \
  "${OUT_DIR}/submission-1080p.mp4"

echo "[ffmpeg-recipe] Done — ${OUT_DIR}/submission-1080p.mp4"
