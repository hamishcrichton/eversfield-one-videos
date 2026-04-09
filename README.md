# Eversfield One Video Production Pipeline

AI-powered video production pipeline for creating demo videos of the [Eversfield One](https://field-ops-frontend-79922828091.europe-west2.run.app) fire door compliance platform.

Uses a fully open-source toolchain running on cloud GPUs (RunPod) to generate animated cartoon presenter videos with lip-synced narration overlaid on application screen recordings.

## Toolchain

| Tool | Purpose | Cost |
|------|---------|------|
| [Flux](https://github.com/black-forest-labs/flux) | Character image generation | Free |
| [Wan 2.2](https://github.com/Wan-AI/Wan2.2) | Animated scene clips | Free |
| [MuseTalk](https://github.com/TMElyrawormo/MuseTalk) | Lip-synced talking head | Free |
| [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | Image/video upscaling | Free |
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | AI workflow orchestration | Free |
| [RunPod](https://runpod.io) | Cloud GPU (RTX 4090) | ~$0.40/hr |
| [ElevenLabs](https://elevenlabs.io) | AI voice generation | $5/mo |
| [OBS Studio](https://obsproject.com) | Screen recording | Free |
| [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) | Video editing | Free |

**Total cost per video: ~$7-12**

## Quick Start

### 1. Set up RunPod

1. Create a [RunPod](https://runpod.io) account
2. Launch a GPU pod: RTX 4090 (24GB VRAM), ~$0.40/hr
3. SSH into the pod and run the setup script:

```bash
git clone <this-repo> /workspace/eversfield-one-videos
cd /workspace/eversfield-one-videos
bash scripts/setup-runpod.sh
```

This installs ComfyUI and downloads all AI models (~30GB total, ~20 min).

### 2. Generate Character Pack

```bash
# Start ComfyUI in background
cd /workspace/ComfyUI && python main.py --listen 0.0.0.0 --port 8188 &

# Generate all character poses
cd /workspace/eversfield-one-videos
python scripts/generate-character.py --comfyui-url http://localhost:8188
```

Review images in `assets/character-pack/`. Re-run with different `--seed` values until consistent.

### 3. Generate Voice Audio

1. Sign up for [ElevenLabs](https://elevenlabs.io) ($5/mo Starter plan)
2. Choose a British male voice (e.g., "Daniel")
3. Paste each section from `videos/01-platform-demo/script.md`
4. Download WAV files to `videos/01-platform-demo/voice/` named per section:
   - `01-hook.wav`, `02-intro.wav`, `03-dashboard.wav`, etc.

### 4. Record Screen Captures

1. Install [OBS Studio](https://obsproject.com)
2. Follow the shot list in `videos/01-platform-demo/storyboard.md`
3. Record against the live app at 1920x1080, 30fps
4. Save to `videos/01-platform-demo/screen-recordings/`

### 5. Generate Animations

```bash
# Lip-synced talking head (all sections)
python scripts/generate-lipsync.py --comfyui-url http://localhost:8188

# Dynamic scene clips (opening, transition, closing)
python scripts/generate-scenes.py --comfyui-url http://localhost:8188

# Upscale scene clips to 1080p
python scripts/upscale.py --input-dir videos/01-platform-demo/animations --video
```

### 6. Composite in DaVinci Resolve

1. Install [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve) (free)
2. Import all assets into the project
3. Follow the timeline structure in `videos/01-platform-demo/storyboard.md`
4. Export: H.264, 1920x1080, 30fps, YouTube preset

## Project Structure

```
eversfield-one-videos/
├── scripts/                      # Automation scripts for RunPod/ComfyUI
├── comfyui-workflows/            # ComfyUI workflow JSON files
├── videos/01-platform-demo/      # First video production assets
│   ├── script.md                 # Full narration script
│   ├── storyboard.md             # Visual plan + shot list
│   ├── voice/                    # ElevenLabs audio (per section)
│   ├── screen-recordings/        # OBS app captures
│   ├── character/                # Generated character images
│   ├── animations/               # MuseTalk + Wan 2.2 clips
│   └── export/                   # Final rendered video
├── assets/                       # Shared assets (character pack, fonts, music)
└── docs/                         # Guides and checklists
```

## Production Guides

- [RunPod Setup Guide](docs/runpod-guide.md)
- [Production Checklist](docs/production-checklist.md)
