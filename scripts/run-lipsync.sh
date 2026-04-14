#!/bin/bash
# =============================================================================
# Run MuseTalk lip-sync for all voice sections
# =============================================================================
# Prerequisites:
#   1. bash scripts/setup-musetalk.sh (one-time setup)
#   2. Voice files in videos/01-platform-demo/voice/
#   3. Character image in assets/character-pack/front-facing.png
#
# Run: bash scripts/run-lipsync.sh
# =============================================================================
set -e

WORKSPACE="/workspace"
MUSETALK_DIR="${WORKSPACE}/musetalk-env"
VENV_DIR="${MUSETALK_DIR}/venv"
PROJECT_DIR="${WORKSPACE}/eversfield-one-videos"
VOICE_DIR="${PROJECT_DIR}/videos/01-platform-demo/voice"
OUTPUT_DIR="${PROJECT_DIR}/videos/01-platform-demo/animations"
CHARACTER="${PROJECT_DIR}/assets/character-pack/front-facing.png"

# Activate venv
source "${VENV_DIR}/bin/activate"
cd "${MUSETALK_DIR}/MuseTalk"

# Check prerequisites
if [ ! -f "${CHARACTER}" ]; then
    echo "Error: Character image not found at ${CHARACTER}"
    echo "Run generate-character.py first, or copy from your local machine."
    exit 1
fi

mkdir -p "${OUTPUT_DIR}"

echo "============================================="
echo "  MuseTalk Lip-Sync Generation"
echo "============================================="

# Process each voice file
SECTIONS=(
    "01-hook"
    "02-intro"
    "03-dashboard"
    "04-start-inspection"
    "05-checklist"
    "06-complete"
    "07-golden-thread"
    "08-remediation"
    "09-transition"
    "10-lifecycle"
    "11-analytics"
    "12-highlights"
    "13-cta"
)

for section in "${SECTIONS[@]}"; do
    AUDIO="${VOICE_DIR}/${section}.mp3"
    OUTPUT="${OUTPUT_DIR}/lipsync-${section}.mp4"

    if [ ! -f "${AUDIO}" ]; then
        echo "[${section}] SKIPPED — no audio file"
        continue
    fi

    if [ -f "${OUTPUT}" ]; then
        echo "[${section}] SKIPPED — output already exists"
        continue
    fi

    echo "[${section}] Generating lip-sync..."

    # MuseTalk inference
    # The exact CLI may vary by version. Try the standard approach:
    python -m scripts.inference \
        --source_image "${CHARACTER}" \
        --driven_audio "${AUDIO}" \
        --result_dir "${OUTPUT_DIR}" \
        2>&1 | tail -5

    # Rename output to our naming convention if needed
    # MuseTalk typically outputs to result_dir with auto-generated names
    LATEST=$(ls -t "${OUTPUT_DIR}"/*.mp4 2>/dev/null | head -1)
    if [ -n "${LATEST}" ] && [ "${LATEST}" != "${OUTPUT}" ]; then
        mv "${LATEST}" "${OUTPUT}"
    fi

    echo "[${section}] Done → ${OUTPUT}"
    echo ""
done

echo "============================================="
echo "  Lip-sync generation complete!"
echo "============================================="
echo ""
echo "Output: ${OUTPUT_DIR}/"
ls -la "${OUTPUT_DIR}"/*.mp4 2>/dev/null || echo "(no output files found)"
echo ""
echo "Download via Jupyter Lab or:"
echo "  tar czf /workspace/lipsync-output.tar.gz -C ${OUTPUT_DIR} ."
