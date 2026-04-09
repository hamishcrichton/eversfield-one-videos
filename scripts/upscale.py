"""
Upscale images and videos using Real-ESRGAN via ComfyUI API.

Upscales character pack images from 1024x1024 to 2048x2048,
and scene clips from 480p/720p to 1080p.

Usage:
    # Upscale character images:
    python scripts/upscale.py --comfyui-url http://localhost:8188 --input-dir assets/character-pack

    # Upscale video clips:
    python scripts/upscale.py --comfyui-url http://localhost:8188 --input-dir videos/01-platform-demo/animations --video

Requires ComfyUI running with Real-ESRGAN model loaded (see setup-runpod.sh).
"""

import argparse
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path


def build_image_upscale_workflow(image_name: str, scale: int = 2) -> dict:
    """Build a ComfyUI workflow for Real-ESRGAN image upscaling."""
    return {
        "1": {
            "class_type": "LoadImage",
            "inputs": {
                "image": image_name,
            },
        },
        "2": {
            "class_type": "UpscaleModelLoader",
            "inputs": {
                "model_name": "RealESRGAN_x4plus.pth",
            },
        },
        "3": {
            "class_type": "ImageUpscaleWithModel",
            "inputs": {
                "upscale_model": ["2", 0],
                "image": ["1", 0],
            },
        },
        "4": {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["3", 0],
                "upscale_method": "lanczos",
                "width": 2048,
                "height": 2048,
                "crop": "center",
            },
        },
        "5": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "upscaled",
                "images": ["4", 0],
            },
        },
    }


def queue_prompt(comfyui_url: str, workflow: dict) -> str:
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
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{comfyui_url}/history/{prompt_id}") as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"Generation timed out after {timeout}s")


def download_output(comfyui_url: str, filename: str, subfolder: str, output_path: Path):
    params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": "output"})
    with urllib.request.urlopen(f"{comfyui_url}/view?{params}") as resp:
        output_path.write_bytes(resp.read())


def upload_file(comfyui_url: str, file_path: Path) -> str:
    boundary = "----FormBoundary" + str(int(time.time()))
    import mimetypes

    content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"

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
    parser = argparse.ArgumentParser(description="Upscale images/videos using Real-ESRGAN via ComfyUI")
    parser.add_argument("--comfyui-url", default="http://localhost:8188", help="ComfyUI server URL")
    parser.add_argument("--input-dir", required=True, help="Directory containing files to upscale")
    parser.add_argument("--output-dir", help="Output directory (default: input-dir/upscaled)")
    parser.add_argument("--video", action="store_true", help="Upscale video files instead of images")
    parser.add_argument("--scale", type=int, default=2, help="Upscale factor (default: 2x)")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else input_dir / "upscaled"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.video:
        print("Video upscaling via Real-ESRGAN requires frame extraction.")
        print("Use ffmpeg for frame-by-frame upscaling:")
        print()
        for video_file in sorted(input_dir.glob("scene-*.mp4")):
            stem = video_file.stem
            print(f"  # Extract frames from {video_file.name}")
            print(f"  mkdir -p /tmp/{stem}_frames /tmp/{stem}_upscaled")
            print(f"  ffmpeg -i {video_file} /tmp/{stem}_frames/frame_%04d.png")
            print()
            print(f"  # Upscale each frame (run in ComfyUI or use realesrgan-ncnn-vulkan)")
            print(f"  # Then reassemble:")
            print(f"  ffmpeg -framerate 16 -i /tmp/{stem}_upscaled/frame_%04d.png \\")
            print(f"    -c:v libx264 -pix_fmt yuv420p {output_dir / video_file.name}")
            print()
        print("For convenience, consider using realesrgan-ncnn-vulkan CLI:")
        print("  pip install realesrgan")
        print("  realesrgan-ncnn-vulkan -i input_frames/ -o output_frames/ -n realesrgan-x4plus")
        return

    extensions = {".png", ".jpg", ".jpeg", ".webp"}
    files = sorted(f for f in input_dir.iterdir() if f.suffix.lower() in extensions)

    if not files:
        print(f"No image files found in {input_dir}")
        return

    print(f"Upscaling {len(files)} images ({args.scale}x)...")
    print(f"Output: {output_dir}")
    print()

    for file_path in files:
        output_path = output_dir / file_path.name
        print(f"  [{file_path.name}] Uploading...", end=" ", flush=True)

        server_name = upload_file(args.comfyui_url, file_path)
        workflow = build_image_upscale_workflow(server_name, args.scale)

        prompt_id = queue_prompt(args.comfyui_url, workflow)
        print("upscaling...", end=" ", flush=True)
        result = wait_for_completion(args.comfyui_url, prompt_id)

        outputs = result.get("outputs", {})
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for img in node_output["images"]:
                    download_output(
                        args.comfyui_url,
                        img["filename"],
                        img.get("subfolder", ""),
                        output_path,
                    )
                    print(f"saved to {output_path}")
                    break

    print()
    print(f"Upscaling complete! {len(files)} images in {output_dir}/")


if __name__ == "__main__":
    main()
