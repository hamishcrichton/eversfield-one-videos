# RunPod Setup Guide

Step-by-step guide for setting up and using RunPod for the video production pipeline.

## Account Setup

1. Go to [runpod.io](https://runpod.io) and create an account
2. Add credit ($10 minimum — enough for several video production sessions)
3. Navigate to **GPU Cloud** > **Deploy**

## Launching a Pod

### Recommended Configuration

| Setting | Value |
|---------|-------|
| GPU | RTX 4090 (24GB VRAM) |
| Template | RunPod PyTorch 2.1 |
| Container Disk | 50GB (for models + outputs) |
| Volume Disk | 100GB (persistent storage) |

### Steps

1. Click **Deploy** on an available RTX 4090 pod (~$0.40/hr)
2. Select the **RunPod PyTorch 2.1** template
3. Set container disk to 50GB, volume disk to 100GB
4. Click **Deploy On-Demand**
5. Wait for pod to initialize (1-2 minutes)

## First-Time Setup

SSH into your pod (use the SSH command from the RunPod dashboard):

```bash
# Clone this repo
git clone <your-repo-url> /workspace/eversfield-one-videos
cd /workspace/eversfield-one-videos

# Run the setup script (installs ComfyUI + all models)
bash scripts/setup-runpod.sh
```

This takes ~20-30 minutes (mostly downloading models). The models are saved to the persistent volume, so you only do this once.

## Starting a Work Session

Each time you start a new pod session:

```bash
# Start ComfyUI in the background
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188 &

# Wait for it to load (~30 seconds)
sleep 30

# Navigate to your project
cd /workspace/eversfield-one-videos
```

ComfyUI is now accessible at `http://<pod-ip>:8188` (find the IP in RunPod dashboard).

## Running the Pipeline

### Character Generation (~15 min)

```bash
python scripts/generate-character.py --comfyui-url http://localhost:8188
```

Generates 8 character poses. Review in `assets/character-pack/`.

### Lip-Sync Generation (~30-60 min)

```bash
# Ensure voice files are in videos/01-platform-demo/voice/
python scripts/generate-lipsync.py --comfyui-url http://localhost:8188

# Or one section at a time:
python scripts/generate-lipsync.py --comfyui-url http://localhost:8188 --section 01-hook
```

### Scene Generation (~20 min)

```bash
python scripts/generate-scenes.py --comfyui-url http://localhost:8188
```

### Upscaling (~10 min)

```bash
# Upscale character images
python scripts/upscale.py --comfyui-url http://localhost:8188 --input-dir assets/character-pack

# For video upscaling, follow the ffmpeg instructions output by:
python scripts/upscale.py --input-dir videos/01-platform-demo/animations --video
```

## Downloading Results

Use `scp` or the RunPod file browser to download generated files to your local machine:

```bash
# From your local machine:
scp -r runpod:/workspace/eversfield-one-videos/assets/character-pack/ ./assets/character-pack/
scp -r runpod:/workspace/eversfield-one-videos/videos/01-platform-demo/animations/ ./videos/01-platform-demo/animations/
```

## Cost Management

- **Always stop your pod when done.** GPU pods charge by the hour.
- A typical production session (character + lip-sync + scenes) takes 2-4 hours = **$1-2**
- Use the persistent volume so models don't need re-downloading
- Check your RunPod billing dashboard regularly

## Troubleshooting

### ComfyUI won't start
```bash
cd /workspace/ComfyUI
pip install -r requirements.txt
python main.py --listen 0.0.0.0 --port 8188
```

### Out of VRAM
Run only one pipeline at a time (character OR lip-sync OR scenes). Kill ComfyUI and restart between tasks if needed.

### Model download failed
Some models (Flux) require accepting a licence on Hugging Face. Set your HF token:
```bash
export HF_TOKEN="your-huggingface-token"
huggingface-cli login
```
Then re-run `setup-runpod.sh`.
