"""
Generate voice audio for all script sections using the ElevenLabs API.

Usage:
    # List available voices:
    python scripts/generate-voice.py --api-key YOUR_KEY --list-voices

    # Generate all sections with a specific voice:
    python scripts/generate-voice.py --api-key YOUR_KEY --voice-id VOICE_ID

    # Generate a single section to test:
    python scripts/generate-voice.py --api-key YOUR_KEY --voice-id VOICE_ID --section 01-hook

    # Use a voice by name:
    python scripts/generate-voice.py --api-key YOUR_KEY --voice-name "Daniel"

Get your API key from: https://elevenlabs.io/app/settings/api-keys
"""

import argparse
import json
import urllib.request
from pathlib import Path

API_BASE = "https://api.elevenlabs.io/v1"

OUTPUT_DIR = "videos/01-platform-demo/voice"

# Narration text for each section, extracted from script.md
SECTIONS = {
    "01-hook": (
        "If you manage fire doors across multiple buildings, you know the burden. "
        "Paper checklists that get lost. Spreadsheets no one trusts. "
        "Inspections overdue because no one spotted them in time. "
        "And when the regulator asks for your Golden Thread — that sinking feeling. "
        "The Fire Safety Act and Building Safety Act have raised the bar. "
        "But the tools most teams rely on haven't kept up."
    ),
    "02-intro": (
        "Eversfield One changes that. It's a single platform built for field operations teams — "
        "and it starts with the thing that matters most: getting your fire door compliance right. "
        "Let me show you how it works."
    ),
    "03-dashboard": (
        "This is your Fire Doors Dashboard. At a glance, you can see your total door count, "
        "how many are compliant, how many aren't, and how many inspections are overdue. "
        "Below that, analytics show you inspection trends over time, your most common failure types, "
        "and a breakdown by scheme — so you know exactly where to focus your attention."
    ),
    "04-start-inspection": (
        "Starting an inspection takes seconds. Select your door — you can search by reference, "
        "location, or scheme. Choose your inspection type: Routine, Post-Remediation, or Installation. "
        "Set the date, and you're straight into the checklist. "
        "If there's a previous survey on record, you'll see the last inspector's notes and recommendation "
        "right here — so nothing gets missed between visits."
    ),
    "05-checklist": (
        "The checklist is tailored to each door type. Items are grouped by category, "
        "and for each one you simply mark Pass, Fail, or Not Applicable. "
        "Need to capture evidence? Tap the camera icon and the photo is attached to that specific check item. "
        "Some items require measurements — the app validates them in real time so nothing gets submitted incomplete."
    ),
    "06-complete": (
        "When you're done, the summary shows your results at a glance: "
        "how many items passed, how many failed, and the overall outcome. "
        "Hit submit and it's recorded instantly. And here's the key: "
        "this entire workflow works offline. No signal on site? No problem. "
        "The inspection queues locally and syncs automatically when you're back online."
    ),
    "07-golden-thread": (
        "Every inspection feeds directly into the door's compliance history. "
        "You can drill into any door and see every check that's ever been carried out, "
        "with photos, measurements, and outcomes. "
        "When you need to demonstrate compliance, the Golden Thread Export generates "
        "a BSA 2022-ready report — covering every door, every inspection, across your entire portfolio. One click."
    ),
    "08-remediation": (
        "When doors fail inspection, the remediation workflow picks up automatically. "
        "Your repair managers see exactly what's outstanding, what's in progress, and what's overdue. "
        "Contractors get a Statement of Work PDF with every door, every issue, and every photo — "
        "so there's no ambiguity about what needs fixing. "
        "Once repairs are done, the re-inspection loop closes the chain."
    ),
    "09-transition": (
        "But fire doors are just one part of managing your buildings. "
        "Let me show you what else the platform can do."
    ),
    "10-lifecycle": (
        "The Lifecycle module gives you long-term cost visibility across your entire estate. "
        "Each project shows a full cost breakdown by BCIS construction element — "
        "from mechanical services to internal finishes to external walls. "
        "You can filter by building, adjust the year range, and switch between maintenance strategies "
        "to see how different approaches affect your total spend over time."
    ),
    "11-analytics": (
        "The analytics dashboard surfaces the insights that matter. "
        "The 80/20 analysis shows you which handful of elements drive the majority of your costs — "
        "so you know where investment has the biggest impact. "
        "The budget forecast breaks down your annual spend year by year, "
        "with a cumulative cost curve so you can plan ahead with confidence. "
        "And you can compare strategies side by side — reactive versus planned maintenance — "
        "to see the long-term cost difference in real terms. "
        "Everything exports to PDF or CSV, ready for board presentations or procurement planning."
    ),
    "12-highlights": (
        "Eversfield One is built for the field. It's a progressive web app — "
        "install it on any phone, tablet, or desktop. It works offline by default, "
        "with automatic sync when connectivity returns. "
        "Role-based access means inspectors, repair technicians, managers, and administrators "
        "each see exactly what they need. Every action is logged. Every inspection is traceable. "
        "Every document is part of your Golden Thread."
    ),
    "13-cta": (
        "If you're managing fire doors across housing, healthcare, education, or commercial property — "
        "and you need a system that actually works on site, not just in the office — "
        "we'd love to show you Eversfield One with your own data. "
        "Book a demo at the link below. We'll have you up and running in days, not months."
    ),
}


def api_request(endpoint: str, api_key: str, data: dict | None = None, method: str = "GET") -> bytes:
    """Make an ElevenLabs API request."""
    url = f"{API_BASE}/{endpoint}"
    headers = {"xi-api-key": api_key}

    if data:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)

    with urllib.request.urlopen(req) as resp:
        return resp.read()


def list_voices(api_key: str):
    """List available voices with their IDs."""
    result = json.loads(api_request("voices", api_key))
    voices = result.get("voices", [])

    print(f"Found {len(voices)} voices:\n")
    print(f"  {'Name':<25} {'ID':<25} {'Labels'}")
    print(f"  {'-'*25} {'-'*25} {'-'*30}")

    for v in sorted(voices, key=lambda x: x.get("name", "")):
        labels = v.get("labels", {})
        accent = labels.get("accent", "")
        gender = labels.get("gender", "")
        use_case = labels.get("use_case", "")
        desc = ", ".join(filter(None, [accent, gender, use_case]))
        print(f"  {v['name']:<25} {v['voice_id']:<25} {desc}")


def find_voice_by_name(api_key: str, name: str) -> str | None:
    """Find a voice ID by name (case-insensitive partial match)."""
    result = json.loads(api_request("voices", api_key))
    for v in result.get("voices", []):
        if name.lower() in v["name"].lower():
            print(f"Using voice: {v['name']} ({v['voice_id']})")
            return v["voice_id"]
    return None


def generate_speech(api_key: str, voice_id: str, text: str, output_path: Path):
    """Generate speech audio and save to file."""
    data = {
        "text": text,
        "model_id": "eleven_v3",
        "voice_settings": {
            "stability": 0.15,
            "similarity_boost": 0.65,
            "style": 0.80,
        },
    }

    audio_bytes = api_request(f"text-to-speech/{voice_id}", api_key, data, method="POST")
    output_path.write_bytes(audio_bytes)


def main():
    parser = argparse.ArgumentParser(description="Generate voice audio via ElevenLabs API")
    parser.add_argument("--api-key", required=True, help="ElevenLabs API key")
    parser.add_argument("--voice-id", help="Voice ID to use")
    parser.add_argument("--voice-name", help="Find voice by name (e.g., 'Daniel')")
    parser.add_argument("--list-voices", action="store_true", help="List available voices and exit")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--section", help="Generate a single section (e.g., '01-hook')")
    parser.add_argument("--format", default="mp3", choices=["mp3", "wav"], help="Audio format")
    args = parser.parse_args()

    if args.list_voices:
        list_voices(args.api_key)
        return

    voice_id = args.voice_id
    if not voice_id and args.voice_name:
        voice_id = find_voice_by_name(args.api_key, args.voice_name)
        if not voice_id:
            print(f"No voice found matching '{args.voice_name}'. Use --list-voices to see options.")
            return

    if not voice_id:
        print("Provide --voice-id or --voice-name. Use --list-voices to see options.")
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sections = {args.section: SECTIONS[args.section]} if args.section else SECTIONS
    if args.section and args.section not in SECTIONS:
        print(f"Section '{args.section}' not found. Available: {list(SECTIONS.keys())}")
        return

    total_chars = sum(len(t) for t in sections.values())
    print(f"Generating {len(sections)} audio files ({total_chars} characters total)...")
    print()

    for name, text in sections.items():
        output_path = output_dir / f"{name}.{args.format}"
        print(f"  [{name}] {len(text)} chars...", end=" ", flush=True)
        generate_speech(args.api_key, voice_id, text, output_path)
        print(f"saved to {output_path}")

    print()
    print(f"Voice generation complete! {len(sections)} files in {output_dir}/")
    print()
    print("Next steps:")
    print("  1. Listen to each file and check pacing/pronunciation")
    print("  2. Re-generate any sections that need adjustment")
    print("  3. Upload to RunPod for lip-sync: scp voice/*.mp3 runpod:/workspace/eversfield-one-videos/videos/01-platform-demo/voice/")


if __name__ == "__main__":
    main()
