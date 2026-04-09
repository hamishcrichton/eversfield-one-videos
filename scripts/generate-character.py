"""
Generate character pack images using Flux via ComfyUI API.

Generates a consistent set of character poses for the Eversfield One
demo video presenter: a friendly male fire safety professional in PPE.

Usage:
    python scripts/generate-character.py --comfyui-url http://localhost:8188

Requires ComfyUI running with Flux model loaded (see setup-runpod.sh).
"""

import argparse
import json
import time
import urllib.request
import urllib.parse
import uuid
from pathlib import Path

# Character description - consistent across all poses
CHARACTER_BASE = (
    "clean-lined digital illustration of a friendly professional male fire safety consultant, "
    "mid-30s, medium build, warm approachable expression, slight confident smile, "
    "wearing navy blue polo shirt under high-visibility yellow safety vest, "
    "dark slate work trousers, black safety boots, "
    "clean-shaven, short brown hair, clear eyes, "
    "corporate illustration style, flat colours with subtle shading, "
    "colour palette: navy slate (#1e293b), amber yellow (#f59e0b), "
    "white background, professional and trustworthy"
)

# Pose-specific prompts
POSES = {
    "front-facing": {
        "prompt": f"{CHARACTER_BASE}, front-facing portrait, looking directly at viewer, shoulders square, head and shoulders visible, neutral white background",
        "filename": "front-facing.png",
    },
    "three-quarter": {
        "prompt": f"{CHARACTER_BASE}, three-quarter view portrait, turned slightly to the right, natural relaxed pose, head and shoulders visible, neutral white background",
        "filename": "three-quarter.png",
    },
    "full-body-standing": {
        "prompt": f"{CHARACTER_BASE}, full body standing pose, weight on both feet, arms relaxed at sides, standing straight, full figure visible from head to toe, neutral white background",
        "filename": "full-body-standing.png",
    },
    "gesturing": {
        "prompt": f"{CHARACTER_BASE}, upper body visible, right hand raised and gesturing to the side as if presenting something, open palm, engaging expression, neutral white background",
        "filename": "gesturing.png",
    },
    "holding-tablet": {
        "prompt": f"{CHARACTER_BASE}, upper body visible, holding a tablet device in both hands showing it to the viewer, looking at viewer with a smile, neutral white background",
        "filename": "holding-tablet.png",
    },
    "walking": {
        "prompt": f"{CHARACTER_BASE}, full body in mid-stride walking pose, purposeful movement to the right, dynamic but natural, full figure visible, neutral white background",
        "filename": "walking.png",
    },
    "concerned": {
        "prompt": f"{CHARACTER_BASE}, upper body visible, holding a clipboard, slightly worried expression, furrowed brow, looking at clipboard, neutral white background",
        "filename": "concerned-clipboard.png",
    },
    "confident-close": {
        "prompt": f"{CHARACTER_BASE}, close-up portrait, warm confident smile, looking directly at viewer, friendly and inviting expression, head and upper chest visible, neutral white background",
        "filename": "confident-close.png",
    },
}

# Consistent seed for character identity
DEFAULT_SEED = 428571


def build_flux_workflow(prompt: str, seed: int, width: int = 1024, height: int = 1024, steps: int = 28) -> dict:
    """Build a ComfyUI workflow JSON for Flux image generation."""
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": 3.5,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "flux1-dev.safetensors",
            },
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1,
            },
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["4", 1],
            },
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "",
                "clip": ["4", 1],
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2],
            },
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "character",
                "images": ["8", 0],
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


def wait_for_completion(comfyui_url: str, prompt_id: str, timeout: int = 300) -> dict:
    """Poll ComfyUI until the prompt completes."""
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{comfyui_url}/history/{prompt_id}") as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"Generation timed out after {timeout}s")


def download_image(comfyui_url: str, filename: str, subfolder: str, output_path: Path):
    """Download a generated image from ComfyUI."""
    params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": "output"})
    with urllib.request.urlopen(f"{comfyui_url}/view?{params}") as resp:
        output_path.write_bytes(resp.read())


def main():
    parser = argparse.ArgumentParser(description="Generate character pack using Flux via ComfyUI")
    parser.add_argument("--comfyui-url", default="http://localhost:8188", help="ComfyUI server URL")
    parser.add_argument("--output-dir", default="assets/character-pack", help="Output directory for images")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for consistency")
    parser.add_argument("--pose", help="Generate a single pose (e.g., 'front-facing'). Default: all poses")
    parser.add_argument("--width", type=int, default=1024, help="Image width")
    parser.add_argument("--height", type=int, default=1024, help="Image height")
    parser.add_argument("--steps", type=int, default=28, help="Sampling steps")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    poses = {args.pose: POSES[args.pose]} if args.pose else POSES

    print(f"Generating {len(poses)} character poses...")
    print(f"Seed: {args.seed}")
    print(f"Resolution: {args.width}x{args.height}")
    print(f"Output: {output_dir}")
    print()

    for name, pose_config in poses.items():
        output_path = output_dir / pose_config["filename"]
        print(f"  [{name}] Generating...", end=" ", flush=True)

        workflow = build_flux_workflow(
            prompt=pose_config["prompt"],
            seed=args.seed,
            width=args.width,
            height=args.height,
            steps=args.steps,
        )

        prompt_id = queue_prompt(args.comfyui_url, workflow)
        result = wait_for_completion(args.comfyui_url, prompt_id)

        # Extract output image info
        outputs = result.get("outputs", {})
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for img in node_output["images"]:
                    download_image(
                        args.comfyui_url,
                        img["filename"],
                        img.get("subfolder", ""),
                        output_path,
                    )
                    print(f"saved to {output_path}")
                    break

    print()
    print(f"Character pack complete! {len(poses)} images in {output_dir}/")
    print()
    print("Next steps:")
    print("  1. Review images for consistency")
    print("  2. Re-generate any that don't match (adjust seed or prompt)")
    print("  3. Upscale to 2048x2048: python scripts/upscale.py --input-dir assets/character-pack")


if __name__ == "__main__":
    main()
