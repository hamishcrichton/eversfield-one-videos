#!/bin/bash
# =============================================================================
# MuseTalk Setup — Isolated venv with pre-built dependencies
# =============================================================================
# This installs MuseTalk in its own virtual environment so it cannot conflict
# with the pod's system packages. Uses openmim for pre-built mmcv/mmpose wheels
# instead of compiling from source.
#
# Run on RunPod:
#   bash scripts/setup-musetalk.sh
# =============================================================================
set -e

WORKSPACE="/workspace"
MUSETALK_DIR="${WORKSPACE}/musetalk-env"
VENV_DIR="${MUSETALK_DIR}/venv"

echo "============================================="
echo "  MuseTalk Setup (isolated environment)"
echo "============================================="

# --- Create isolated directory ---
echo "[1/6] Creating isolated environment..."
mkdir -p "${MUSETALK_DIR}"

# --- Create venv ---
echo "[2/6] Creating Python virtual environment..."
python3 -m venv "${VENV_DIR}"
# Activate
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip wheel setuptools -q

# --- Install PyTorch (locked version with pre-built CUDA support) ---
echo "[3/6] Installing PyTorch 2.1 + CUDA 12.1..."
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 \
    --index-url https://download.pytorch.org/whl/cu121 -q

# --- Install mmcv/mmpose via openmim (pre-built wheels, no compilation) ---
echo "[4/6] Installing mmcv + mmpose via openmim (pre-built wheels)..."
pip install openmim -q
mim install mmengine -q
mim install "mmcv>=2.0.1" -q
mim install "mmdet>=3.1.0" -q
mim install "mmpose>=1.1.0" -q

# --- Clone and install MuseTalk ---
echo "[5/6] Installing MuseTalk..."
cd "${MUSETALK_DIR}"
if [ ! -d "MuseTalk" ]; then
    git clone https://github.com/TMElyralab/MuseTalk.git
fi
cd MuseTalk
pip install -r requirements.txt -q 2>/dev/null || true
# Install any missing deps explicitly
pip install ffmpeg-python librosa soundfile diffusers transformers accelerate -q

# --- Download MuseTalk models ---
echo "[6/6] Downloading MuseTalk models..."
# MuseTalk needs several model files. Check if they exist first.
mkdir -p models/musetalk models/dwpose models/face-parse-bisenet models/whisper

# Download whisper model (for audio features)
if [ ! -f "models/whisper/tiny.pt" ]; then
    echo "  Downloading whisper tiny model..."
    python3 -c "import whisper; whisper.load_model('tiny', download_root='models/whisper')" 2>/dev/null || \
    pip install openai-whisper -q && python3 -c "import whisper; whisper.load_model('tiny', download_root='models/whisper')"
fi

# MuseTalk will auto-download remaining models on first run
echo ""
echo "============================================="
echo "  MuseTalk setup complete!"
echo "============================================="
echo ""
echo "Environment: ${VENV_DIR}"
echo "MuseTalk:    ${MUSETALK_DIR}/MuseTalk"
echo ""
echo "To activate: source ${VENV_DIR}/bin/activate"
echo "To run:      cd ${MUSETALK_DIR}/MuseTalk && python -m scripts.inference --help"
echo ""
echo "The lip-sync pipeline script will handle activation automatically."
