# CLAUDE.md

## Project Overview

Video production pipeline for Eversfield One platform demo videos. Uses open-source AI tools on RunPod cloud GPUs.

## Key Files

- `videos/01-platform-demo/script.md` — Narration script with timecodes
- `videos/01-platform-demo/storyboard.md` — Visual plan and shot list
- `scripts/setup-runpod.sh` — RunPod environment setup
- `scripts/generate-character.py` — Flux character generation via ComfyUI API
- `scripts/generate-lipsync.py` — MuseTalk lip-sync via ComfyUI API
- `scripts/generate-scenes.py` — Wan 2.2 scene clips via ComfyUI API
- `scripts/upscale.py` — Real-ESRGAN upscaling via ComfyUI API

## Python Guidelines

- All scripts use stdlib only (urllib, json, argparse) — no external dependencies needed locally
- Scripts talk to ComfyUI's HTTP API, so they run on any machine with network access to the RunPod pod
- Use `python3` to run scripts (not `python`)

## Character Consistency

The character is defined by prompt text in `generate-character.py`. The `CHARACTER_BASE` constant must stay consistent across all scripts. If you change the character description, update it in:
- `scripts/generate-character.py` (POSES dict)
- `scripts/generate-scenes.py` (CHARACTER_BASE_DESC)

## Video Structure

Each video lives in `videos/XX-name/` with its own script, storyboard, voice, screen recordings, and animations. Shared assets (character pack, fonts, music) live in `assets/`.

## Production App

The app being demoed is at:
- Frontend: `https://field-ops-frontend-79922828091.europe-west2.run.app`
- Source: `../ECLFireDoors/field-operations-platform/`
