#!/bin/bash
# =============================================================================
# Full pipeline: generate voice + lip-sync on RunPod
# Paste this single command in RunPod terminal and walk away.
# =============================================================================
set -e

ELEVENLABS_KEY="sk_ed59f263dd029b33c3a9e4bfd466f7f3885991d1f402dbd4"
VOICE_ID="L0Dsvb3SLTyegXwtm47J"
WORKDIR="/workspace/eversfield-one-videos"

echo "============================================="
echo "  Step 1: Pulling latest code"
echo "============================================="
cd /workspace
if [ -d "eversfield-one-videos" ]; then
    cd eversfield-one-videos && git pull || true
else
    git clone https://github.com/hamishcrichton/eversfield-one-videos.git
    cd eversfield-one-videos
fi

echo ""
echo "============================================="
echo "  Step 2: Generating voice audio (ElevenLabs)"
echo "============================================="
python3 scripts/generate-voice.py --api-key "$ELEVENLABS_KEY" --voice-id "$VOICE_ID"

echo ""
echo "============================================="
echo "  Step 3: Starting ComfyUI"
echo "============================================="
# Kill any existing ComfyUI instance
pkill -f "main.py.*8188" 2>/dev/null || true
sleep 2

cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 &
COMFY_PID=$!

echo "Waiting for ComfyUI to start..."
for i in $(seq 1 60); do
    if curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
        echo "ComfyUI ready!"
        break
    fi
    sleep 2
done

echo ""
echo "============================================="
echo "  Step 4: Running MuseTalk lip-sync"
echo "============================================="
cd "$WORKDIR"
python3 scripts/generate-lipsync.py --comfyui-url http://localhost:8188

echo ""
echo "============================================="
echo "  Step 5: Generating scene clips (Wan 2.2)"
echo "============================================="
python3 scripts/generate-scenes.py --comfyui-url http://localhost:8188

echo ""
echo "============================================="
echo "  Pipeline complete!"
echo "============================================="
echo ""
echo "Output files:"
echo "  Voice:      $WORKDIR/videos/01-platform-demo/voice/"
echo "  Lip-sync:   $WORKDIR/videos/01-platform-demo/animations/"
echo ""
echo "Download via Jupyter Lab (port 8888) or tar:"
echo "  cd $WORKDIR && tar czf /workspace/outputs.tar.gz videos/01-platform-demo/voice/ videos/01-platform-demo/animations/ assets/character-pack/"
