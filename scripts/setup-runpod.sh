#!/bin/bash
# =============================================================================
# RunPod Setup Script for Eversfield One Video Production Pipeline
# =============================================================================
# Run this on a fresh RunPod instance with an RTX 4090 (24GB VRAM).
# Installs ComfyUI + all required models for character design, scene generation,
# lip-sync animation, and upscaling.
#
# Usage:
#   ssh into your RunPod instance, then:
#   curl -sL <raw-github-url>/scripts/setup-runpod.sh | bash
#   OR: bash setup-runpod.sh
#
# Estimated setup time: ~20-30 minutes (mostly model downloads)
# =============================================================================

set -euo pipefail

WORKSPACE="/workspace"
COMFYUI_DIR="${WORKSPACE}/ComfyUI"
MODELS_DIR="${COMFYUI_DIR}/models"
CUSTOM_NODES_DIR="${COMFYUI_DIR}/custom_nodes"

echo "============================================="
echo "  Eversfield One Video Pipeline - RunPod Setup"
echo "============================================="

# --- System Dependencies ---
echo "[1/7] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq git git-lfs ffmpeg libgl1-mesa-glx libglib2.0-0 aria2 > /dev/null 2>&1
git lfs install --skip-smudge

# --- ComfyUI ---
echo "[2/7] Installing ComfyUI..."
if [ ! -d "${COMFYUI_DIR}" ]; then
    cd "${WORKSPACE}"
    git clone https://github.com/comfyanonymous/ComfyUI.git
    cd "${COMFYUI_DIR}"
    pip install -r requirements.txt -q
else
    echo "  ComfyUI already installed, updating..."
    cd "${COMFYUI_DIR}"
    git pull
    pip install -r requirements.txt -q
fi

# --- ComfyUI Manager (for easy node installation) ---
echo "[3/7] Installing ComfyUI Manager + Custom Nodes..."
cd "${CUSTOM_NODES_DIR}"

if [ ! -d "ComfyUI-Manager" ]; then
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
fi

# ComfyUI-VideoHelperSuite (for video output nodes)
if [ ! -d "ComfyUI-VideoHelperSuite" ]; then
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
    cd ComfyUI-VideoHelperSuite && pip install -r requirements.txt -q && cd ..
fi

# ComfyUI-WanVideoWrapper (for Wan 2.2 integration)
if [ ! -d "ComfyUI-WanVideoWrapper" ]; then
    git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git
    cd ComfyUI-WanVideoWrapper && pip install -r requirements.txt -q 2>/dev/null || true && cd ..
fi

# ComfyUI-MuseTalk (for lip-sync)
if [ ! -d "ComfyUI-MuseTalk" ]; then
    git clone https://github.com/TMElyrawormo/ComfyUI-MuseTalk.git
    cd ComfyUI-MuseTalk && pip install -r requirements.txt -q 2>/dev/null || true && cd ..
fi

# --- Flux Model (Character Design) ---
echo "[4/7] Downloading Flux model for character design..."
mkdir -p "${MODELS_DIR}/unet" "${MODELS_DIR}/clip" "${MODELS_DIR}/vae"

# Flux-dev (diffusion model)
if [ ! -f "${MODELS_DIR}/unet/flux1-dev.safetensors" ]; then
    echo "  Downloading flux1-dev (~12GB)..."
    aria2c -x 16 -s 16 --dir="${MODELS_DIR}/unet" --out="flux1-dev.safetensors" \
        "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors" \
        2>/dev/null || {
        echo "  Direct download failed. You may need to accept the licence at:"
        echo "  https://huggingface.co/black-forest-labs/FLUX.1-dev"
        echo "  Then set HF_TOKEN and retry."
    }
else
    echo "  Flux model already downloaded."
fi

# CLIP text encoders for Flux
if [ ! -f "${MODELS_DIR}/clip/clip_l.safetensors" ]; then
    echo "  Downloading CLIP-L text encoder..."
    aria2c -x 16 -s 16 --dir="${MODELS_DIR}/clip" --out="clip_l.safetensors" \
        "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors" \
        2>/dev/null
fi

if [ ! -f "${MODELS_DIR}/clip/t5xxl_fp16.safetensors" ]; then
    echo "  Downloading T5-XXL text encoder (~10GB)..."
    aria2c -x 16 -s 16 --dir="${MODELS_DIR}/clip" --out="t5xxl_fp16.safetensors" \
        "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors" \
        2>/dev/null
fi

# Flux VAE
if [ ! -f "${MODELS_DIR}/vae/ae.safetensors" ]; then
    echo "  Downloading Flux VAE..."
    aria2c -x 16 -s 16 --dir="${MODELS_DIR}/vae" --out="ae.safetensors" \
        "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors" \
        2>/dev/null || true
fi

# --- Wan 2.2 Model (Scene Generation) ---
echo "[5/7] Downloading Wan 2.2 model for scene generation..."
mkdir -p "${MODELS_DIR}/diffusion_models"

if [ ! -f "${MODELS_DIR}/diffusion_models/wan2.2_t2v_720p.safetensors" ]; then
    echo "  Downloading Wan 2.2 T2V 720p (~8GB)..."
    aria2c -x 16 -s 16 --dir="${MODELS_DIR}/diffusion_models" --out="wan2.2_t2v_720p.safetensors" \
        "https://huggingface.co/Wan-AI/Wan2.2-T2V-14B-720P/resolve/main/diffusion_pytorch_model.safetensors" \
        2>/dev/null || {
        echo "  Wan 2.2 download may require HF_TOKEN."
    }
else
    echo "  Wan 2.2 model already downloaded."
fi

# --- MuseTalk Models (Lip-Sync) ---
echo "[6/7] Downloading MuseTalk models..."
MUSETALK_DIR="${CUSTOM_NODES_DIR}/ComfyUI-MuseTalk/models"
mkdir -p "${MUSETALK_DIR}"

# MuseTalk downloads its own models on first run if not present.
# We pre-download the face parsing and audio encoder models for speed.
echo "  MuseTalk models will auto-download on first use."
echo "  Pre-downloading face detection model..."
mkdir -p "${MODELS_DIR}/facedetection"
if [ ! -f "${MODELS_DIR}/facedetection/detection_Resnet50_Final.pth" ]; then
    aria2c -x 16 -s 16 --dir="${MODELS_DIR}/facedetection" --out="detection_Resnet50_Final.pth" \
        "https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth" \
        2>/dev/null || true
fi

# --- Real-ESRGAN (Upscaling) ---
echo "[7/7] Downloading Real-ESRGAN upscaling model..."
mkdir -p "${MODELS_DIR}/upscale_models"

if [ ! -f "${MODELS_DIR}/upscale_models/RealESRGAN_x4plus.pth" ]; then
    aria2c -x 16 -s 16 --dir="${MODELS_DIR}/upscale_models" --out="RealESRGAN_x4plus.pth" \
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth" \
        2>/dev/null
else
    echo "  Real-ESRGAN already downloaded."
fi

# --- Final Setup ---
echo ""
echo "============================================="
echo "  Setup complete!"
echo "============================================="
echo ""
echo "Models downloaded to: ${MODELS_DIR}"
echo ""
echo "To start ComfyUI:"
echo "  cd ${COMFYUI_DIR}"
echo "  python main.py --listen 0.0.0.0 --port 8188"
echo ""
echo "Then access ComfyUI at: http://<your-runpod-ip>:8188"
echo ""
echo "To run Python scripts directly:"
echo "  cd /workspace/eversfield-one-videos"
echo "  python scripts/generate-character.py --comfyui-url http://localhost:8188"
echo ""
echo "Estimated VRAM usage:"
echo "  Flux character generation: ~18GB"
echo "  Wan 2.2 scene generation:  ~16GB"
echo "  MuseTalk lip-sync:         ~8GB"
echo "  Real-ESRGAN upscaling:     ~4GB"
echo ""
echo "NOTE: Run one pipeline at a time to stay within 24GB VRAM."
