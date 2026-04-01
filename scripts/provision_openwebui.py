#!/usr/bin/env python3
"""Provision Open-WebUI model presets from ai-tutor-prompts system.yml files.

Reads each prompts/<subject>/system.yml, extracts the system prompt, and creates
(or updates) an Open-WebUI model that wraps the base vLLM model with that prompt.

Rishaan just sees "📐 Math Teacher", "🔬 Science Teacher", etc. in his model
dropdown — no configuration needed.

Usage:
    # Set your admin API key (create in Open-WebUI → Settings → Account → API Keys)
    export OPENWEBUI_API_KEY="sk-..."

    # Default: provision to chat.balikai.org
    python provision_openwebui.py

    # Or specify a different URL (e.g. local dev)
    python provision_openwebui.py --url http://localhost:3000

    # Dry-run: print what would be created without making API calls
    python provision_openwebui.py --dry-run
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
import yaml

# ── Teacher model definitions ─────────────────────────────────────────────────
# Maps subject folder → display name + emoji + model params
TEACHERS = {
    "math": {
        "id": "math-teacher",
        "name": "📐 Math Teacher",
        "description": "Patient math tutor — AMC, SASMO, AP Calculus, IB Math AA HL",
        "temperature": 0.6,
        "top_p": 0.95,
    },
    "science": {
        "id": "science-teacher",
        "name": "🔬 Science Teacher",
        "description": "Enthusiastic science teacher — AP Physics, Chemistry, Science Olympiad",
        "temperature": 0.6,
        "top_p": 0.95,
    },
    "english": {
        "id": "english-teacher",
        "name": "📝 English Teacher",
        "description": "Writing-focused English teacher — AP English, IB English A HL",
        "temperature": 0.7,
        "top_p": 0.9,
    },
    "chinese": {
        "id": "chinese-teacher",
        "name": "🀄 Chinese Teacher",
        "description": "Conversation-first Mandarin teacher — HSK, IB Chinese B SL",
        "temperature": 0.7,
        "top_p": 0.9,
    },
    "history": {
        "id": "history-teacher",
        "name": "📜 History Teacher",
        "description": "Engaging history teacher — AP World/US/Euro, IB History HL",
        "temperature": 0.7,
        "top_p": 0.9,
    },
}

# Base model served by vLLM on GX10
BASE_MODEL = "nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4"

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_system_prompt(subject: str) -> str:
    """Read system_prompt from prompts/<subject>/system.yml."""
    path = PROMPTS_DIR / subject / "system.yml"
    if not path.exists():
        print(f"  ⚠ {path} not found, skipping", file=sys.stderr)
        return ""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("system_prompt", "")


def create_or_update_model(
    base_url: str, api_key: str, model_def: dict, system_prompt: str, dry_run: bool
) -> bool:
    """Create or update a model in Open-WebUI."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    model_id = model_def["id"]
    payload = {
        "id": model_id,
        "name": model_def["name"],
        "meta": {
            "description": model_def["description"],
            "profile_image_url": "",
        },
        "base_model_id": BASE_MODEL,
        "params": {
            "system": system_prompt,
            "temperature": model_def["temperature"],
            "top_p": model_def["top_p"],
            "max_tokens": 32768,
            "stream": True,
        },
    }

    if dry_run:
        print(f"  [DRY-RUN] Would create/update model '{model_id}'")
        print(f"    Name: {model_def['name']}")
        print(f"    Base: {BASE_MODEL}")
        print(f"    Prompt: {len(system_prompt)} chars")
        return True

    # Try to get existing model first
    resp = requests.get(
        f"{base_url}/api/v1/models/{model_id}",
        headers=headers,
        timeout=10,
    )

    if resp.status_code == 200:
        # Model exists → update
        resp = requests.post(
            f"{base_url}/api/v1/models/update",
            headers=headers,
            json=payload,
            timeout=30,
        )
        action = "Updated"
    else:
        # Model doesn't exist → create
        resp = requests.post(
            f"{base_url}/api/v1/models/create",
            headers=headers,
            json=payload,
            timeout=30,
        )
        action = "Created"

    if resp.status_code in (200, 201):
        print(f"  ✅ {action} '{model_def['name']}'")
        return True

    print(
        f"  ❌ Failed to provision '{model_id}': {resp.status_code} {resp.text}",
        file=sys.stderr,
    )
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Provision Open-WebUI teacher model presets"
    )
    parser.add_argument(
        "--url",
        default="https://chat.balikai.org",
        help="Open-WebUI base URL (default: https://chat.balikai.org)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without making API calls",
    )
    args = parser.parse_args()

    api_key = os.environ.get("OPENWEBUI_API_KEY", "")
    if not api_key and not args.dry_run:
        print(
            "Error: Set OPENWEBUI_API_KEY environment variable.\n"
            "Create one in Open-WebUI → Settings → Account → API Keys",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Provisioning teacher models to {args.url}")
    print(f"Reading prompts from {PROMPTS_DIR}\n")

    success = 0
    for subject, model_def in TEACHERS.items():
        print(f"[{subject}]")
        prompt = load_system_prompt(subject)
        if not prompt:
            continue
        if create_or_update_model(args.url, api_key, model_def, prompt, args.dry_run):
            success += 1
        print()

    total = len(TEACHERS)
    print(f"Done: {success}/{total} teachers provisioned.")
    sys.exit(0 if success == total else 1)


if __name__ == "__main__":
    main()
