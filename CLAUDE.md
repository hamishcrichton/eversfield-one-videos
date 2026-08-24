# CLAUDE.md

## Project Overview

Video production pipeline for Eversfield One platform demo videos. Uses open-source AI tools on RunPod cloud GPUs.

## Notion Context

| Resource     | Reference |
|--------------|-----------|
| Project      | Eversfield One — Platform — page `339f84ba-16d6-817a-afd1-e49d14f699a3` |
| Repository   | row `3c6f84ba-16d6-810d-9a48-e29ba03bc0f3` |
| Product      | Eversfield One — page `3c2f84ba-16d6-8116-bde4-cd6097463155` |
| Client       | ECL — page `3c2f84ba-16d6-817c-9861-c077bd0a34aa` |
| Tasks DS     | `4e273ca5-0803-4122-a59c-be9020486ff6` |
| Decisions DS | `dff9636f-d1bf-4272-b04d-dc8534282f06` |
| Conventions  | `33af84ba-16d6-8159-8079-e167cd4113a1` |
| Hub          | `339f84ba-16d6-81ce-8d0c-cf98d2dbae4b` |

Read this block before any Notion call; fetch by ID (never bulk). Contract: the Conventions page (v2).

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

## Working with Claude
Task routing follows the global dev cycle (global CLAUDE.md): trivial → do + verify; small → plan mode,
then `/code-review` before commit; feature/multi-session → superpowers brainstorming → writing-plans →
executing-plans (+ test-driven-development); non-obvious bugs → systematic-debugging.

Repo specifics:
- **Test:** none configured (no test suite — verify scripts manually against the RunPod ComfyUI API)
- **Lint/typecheck:** none configured
- **Done means:** scripts run cleanly end-to-end; character consistency constants stay in sync (see below)
- **Plans/specs live in:** `docs/plans/`

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
