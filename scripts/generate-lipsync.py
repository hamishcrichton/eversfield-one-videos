"""
Generate lip-synced talking-head videos using MuseTalk via ComfyUI API.

Takes the front-facing character image + per-section voice audio files
and produces MP4 clips of the character speaking with synchronised lip movement.

Usage:
    python scripts/generate-lipsync.py --comfyui-url http://localhost:8188

    # Single section:
    python scripts/generate-lipsync.py --comfyui-url http://localhost:8188 --section 01-hook

Requires ComfyUI running with MuseTalk node installed (see setup-runpod.sh).
"""

import argparse
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

# Section mapping: audio filename stem -> output filename
SECTIONS = [
    ("01-hook", "lipsync-01-hook.mp4"),
    ("02-intro", "lipsync-02-intro.mp4"),
    ("03-dashboard", "lipsync-03-dashboard.mp4"),
    ("04-start-inspection", "lipsync-04-start-inspection.mp4"),
    ("05-checklist", "lipsync-05-checklist.mp4"),
    ("06-complete", "lipsync-06-complete.mp4"),
    ("07-golden-thread", "lipsync-07-golden-thread.mp4"),
    ("08-remediation", "lipsync-08-remediation.mp4"),
    ("10-lifecycle", "lipsync-10-lifecycle.mp4"),
    ("11-analytics", "lipsync-11-analytics.mp4"),
]

CHARACTER_IMAGE = "assets/character-pack/front-facing.png"
VOICE_DIR = "videos/01-platform-demo/voice"
OUTPUT_DIR = "videos/01-platform-demo/animations"


def build_musetalk_workflow(image_path: str, audio_path: str) -> dict:
    """Build a ComfyUI workflow JSON for MuseTalk lip-sync generation.

    Note: This is a simplified workflow structure. The exact node names
    and connections depend on the ComfyUI-MuseTalk plugin version.
    You may need to adjust node class names after installing the plugin.
    """
    return {
        "1": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_path,
            },
        },
        "2": {
            "class_type": "LoadAudio",
            "inputs": {
                "audio": audio_path,
            },
        },
        "3": {
            "class_type": "MuseTalkRun",
            "inputs": {
                "image": ["1", 0],
                "audio": ["2", 0],
                "fps": 30,
                "face_detect_threshold": 0.5,
            },
        },
        "4": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["3", 0],
                "audio": ["2", 0],
                "frame_rate": 30,
                "format": "video/h264-mp4",
                "filename_prefix": "lipsync",
            },
        },
    }


def queue_prompt(comfyui_url: str, workflow: dict) -> str:
    """Queue a workflow on ComfyUI and return the prompt ID."""
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{comfyui_url}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["prompt_id"]


def wait_for_completion(comfyui_url: str, prompt_id: str, timeout: int = 600) -> dict:
    """Poll ComfyUI until the prompt completes. Longer timeout for video."""
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{comfyui_url}/history/{prompt_id}") as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(3)
    raise TimeoutError(f"Generation timed out after {timeout}s")


def download_output(comfyui_url: str, filename: str, subfolder: str, output_path: Path):
    """Download a generated video from ComfyUI output."""
    params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": "output"})
    with urllib.request.urlopen(f"{comfyui_url}/view?{params}") as resp:
        output_path.write_bytes(resp.read())


def upload_file(comfyui_url: str, file_path: Path) -> str:
    """Upload a file to ComfyUI input directory and return the server filename."""
    import mimetypes

    content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    boundary = "----FormBoundary" + str(int(time.time()))

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{file_path.name}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode()
    body += file_path.read_bytes()
    body += f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{comfyui_url}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["name"]


def main():
    parser = argparse.ArgumentParser(description="Generate lip-sync videos using MuseTalk via ComfyUI")
    parser.add_argument("--comfyui-url", default="http://localhost:8188", help="ComfyUI server URL")
    parser.add_argument("--character", default=CHARACTER_IMAGE, help="Path to character front-facing image")
    parser.add_argument("--voice-dir", default=VOICE_DIR, help="Directory containing voice WAV files")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory for lip-sync videos")
    parser.add_argument("--section", help="Generate a single section (e.g., '01-hook')")
    args = parser.parse_args()

    voice_dir = Path(args.voice_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    character_path = Path(args.character)

    if not character_path.exists():
        print(f"Error: Character image not found at {character_path}")
        print("Run generate-character.py first.")
        return

    sections = [(s, o) for s, o in SECTIONS if not args.section or s == args.section]
    if not sections:
        print(f"Error: Section '{args.section}' not found. Available: {[s for s, _ in SECTIONS]}")
        return

    # Upload character image to ComfyUI
    print(f"Uploading character image: {character_path}")
    server_image_name = upload_file(args.comfyui_url, character_path)

    print(f"Generating {len(sections)} lip-sync clips...")
    print()

    for section_name, output_filename in sections:
        audio_path = voice_dir / f"{section_name}.wav"
        if not audio_path.exists():
            audio_path = voice_dir / f"{section_name}.mp3"
        if not audio_path.exists():
            print(f"  [{section_name}] SKIPPED - no audio file found ({voice_dir}/{section_name}.wav)")
            continue

        output_path = output_dir / output_filename
        print(f"  [{section_name}] Generating lip-sync...", end=" ", flush=True)

        # Upload audio to ComfyUI
        server_audio_name = upload_file(args.comfyui_url, audio_path)

        workflow = build_musetalk_workflow(
            image_path=server_image_name,
            audio_path=server_audio_name,
        )

        prompt_id = queue_prompt(args.comfyui_url, workflow)
        result = wait_for_completion(args.comfyui_url, prompt_id)

        # Extract output video
        outputs = result.get("outputs", {})
        for node_id, node_output in outputs.items():
            if "gifs" in node_output:
                for vid in node_output["gifs"]:
                    download_output(
                        args.comfyui_url,
                        vid["filename"],
                        vid.get("subfolder", ""),
                        output_path,
                    )
                    print(f"saved to {output_path}")
                    break

    print()
    print("Lip-sync generation complete!")
    print()
    print("Next steps:")
    print("  1. Review each clip for lip-sync quality")
    print("  2. Re-generate any that don't look right")
    print("  3. Import into DaVinci Resolve for compositing")


if __name__ == "__main__":
    main()
