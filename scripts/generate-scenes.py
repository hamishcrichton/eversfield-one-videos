"""
Generate dynamic scene clips using Wan 2.2 via ComfyUI API.

Produces short animated clips (4-5 seconds) of the character in different
scenarios: opening shot, module transition, and closing shot.

Usage:
    python scripts/generate-scenes.py --comfyui-url http://localhost:8188

    # Single scene:
    python scripts/generate-scenes.py --comfyui-url http://localhost:8188 --scene opening

Requires ComfyUI running with Wan 2.2 model loaded (see setup-runpod.sh).
"""

import argparse
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

CHARACTER_BASE_DESC = (
    "clean-lined digital illustration style, corporate cartoon, "
    "friendly male fire safety consultant, mid-30s, medium build, "
    "navy blue polo under high-visibility yellow safety vest, "
    "dark slate trousers, black safety boots, short brown hair"
)

SCENES = {
    "opening": {
        "prompt": (
            f"{CHARACTER_BASE_DESC}, "
            "standing in front of a modern residential apartment building, "
            "holding a clipboard, looking slightly concerned, "
            "overcast sky, professional setting, "
            "slight camera push-in, subtle wind movement, "
            "clean illustration style, flat colours with soft shadows"
        ),
        "negative_prompt": "photorealistic, 3D render, ugly, deformed, blurry, low quality",
        "filename": "scene-opening.mp4",
        "frames": 81,  # ~5s at 16fps
    },
    "transition": {
        "prompt": (
            f"{CHARACTER_BASE_DESC}, "
            "walking purposefully through a modern building corridor, "
            "turning a corner, dynamic movement, "
            "bright indoor lighting, clean modern interior, "
            "smooth walking motion, natural stride, "
            "clean illustration style, flat colours with soft shadows"
        ),
        "negative_prompt": "photorealistic, 3D render, ugly, deformed, blurry, low quality, static",
        "filename": "scene-transition.mp4",
        "frames": 65,  # ~4s at 16fps
    },
    "closing": {
        "prompt": (
            f"{CHARACTER_BASE_DESC}, "
            "facing camera directly, warm confident smile, "
            "subtle nod, inviting expression, "
            "clean neutral background with subtle gradient, "
            "gentle camera movement, professional and welcoming, "
            "clean illustration style, flat colours with soft shadows"
        ),
        "negative_prompt": "photorealistic, 3D render, ugly, deformed, blurry, low quality",
        "filename": "scene-closing.mp4",
        "frames": 81,  # ~5s at 16fps
    },
}

OUTPUT_DIR = "videos/01-platform-demo/animations"


def build_wan_workflow(
    prompt: str,
    negative_prompt: str,
    num_frames: int,
    width: int = 720,
    height: int = 480,
    seed: int = 428571,
) -> dict:
    """Build a ComfyUI workflow JSON for Wan 2.2 text-to-video generation.

    Note: Node class names depend on the ComfyUI-WanVideoWrapper plugin version.
    Adjust if the plugin has different node names in your installation.
    """
    return {
        "1": {
            "class_type": "WanT2V_ModelLoader",
            "inputs": {
                "model_name": "wan2.2_t2v_720p.safetensors",
                "precision": "fp16",
            },
        },
        "2": {
            "class_type": "WanT2V_TextEncode",
            "inputs": {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "model": ["1", 0],
            },
        },
        "3": {
            "class_type": "WanT2V_Sampler",
            "inputs": {
                "model": ["1", 0],
                "conditioning": ["2", 0],
                "width": width,
                "height": height,
                "num_frames": num_frames,
                "steps": 30,
                "cfg": 7.0,
                "seed": seed,
            },
        },
        "4": {
            "class_type": "WanT2V_Decode",
            "inputs": {
                "model": ["1", 0],
                "samples": ["3", 0],
            },
        },
        "5": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["4", 0],
                "frame_rate": 16,
                "format": "video/h264-mp4",
                "filename_prefix": "scene",
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


def wait_for_completion(comfyui_url: str, prompt_id: str, timeout: int = 900) -> dict:
    """Poll ComfyUI until the prompt completes. Long timeout for video generation."""
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{comfyui_url}/history/{prompt_id}") as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(5)
    raise TimeoutError(f"Generation timed out after {timeout}s")


def download_output(comfyui_url: str, filename: str, subfolder: str, output_path: Path):
    """Download a generated video from ComfyUI."""
    params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": "output"})
    with urllib.request.urlopen(f"{comfyui_url}/view?{params}") as resp:
        output_path.write_bytes(resp.read())


def main():
    parser = argparse.ArgumentParser(description="Generate scene clips using Wan 2.2 via ComfyUI")
    parser.add_argument("--comfyui-url", default="http://localhost:8188", help="ComfyUI server URL")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--scene", help="Generate a single scene (opening/transition/closing)")
    parser.add_argument("--seed", type=int, default=428571, help="Random seed")
    parser.add_argument("--width", type=int, default=720, help="Video width")
    parser.add_argument("--height", type=int, default=480, help="Video height (will be upscaled)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scenes = {args.scene: SCENES[args.scene]} if args.scene else SCENES
    if args.scene and args.scene not in SCENES:
        print(f"Error: Scene '{args.scene}' not found. Available: {list(SCENES.keys())}")
        return

    print(f"Generating {len(scenes)} scene clips with Wan 2.2...")
    print(f"Resolution: {args.width}x{args.height} (upscale to 1080p after)")
    print(f"Seed: {args.seed}")
    print()

    for name, scene_config in scenes.items():
        output_path = output_dir / scene_config["filename"]
        print(f"  [{name}] Generating {scene_config['frames']} frames...", end=" ", flush=True)

        workflow = build_wan_workflow(
            prompt=scene_config["prompt"],
            negative_prompt=scene_config["negative_prompt"],
            num_frames=scene_config["frames"],
            width=args.width,
            height=args.height,
            seed=args.seed,
        )

        prompt_id = queue_prompt(args.comfyui_url, workflow)
        result = wait_for_completion(args.comfyui_url, prompt_id)

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
    print("Scene generation complete!")
    print()
    print("Next steps:")
    print("  1. Review clips for character consistency and motion quality")
    print("  2. Upscale to 1080p: python scripts/upscale.py --input-dir videos/01-platform-demo/animations --video")
    print("  3. Import into DaVinci Resolve timeline")


if __name__ == "__main__":
    main()
