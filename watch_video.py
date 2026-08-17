#!/usr/bin/env python3
"""
watch_video.py - let your AI watch a YouTube video or a local video file.

Usage:
    python3 watch_video.py <youtube-url-or-file> [--prompt "..."] [--clip 0:00-0:05] [--fps N] [--model ...]

Env:
    GEMINI_API_KEY - required. Free key at https://aistudio.google.com/apikey

Standard library only. No pip install.
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://generativelanguage.googleapis.com/v1beta"
UPLOAD_API = "https://generativelanguage.googleapis.com/upload/v1beta"
DEFAULT_MODEL = "gemini-flash-latest"
INLINE_LIMIT = 100 * 1024 * 1024
UPLOAD_TIMEOUT_SEC = 300
POLL_SEC = 3

MIME = {
    ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm",
    ".avi": "video/avi", ".mpeg": "video/mpeg", ".mpg": "video/mpg",
    ".flv": "video/x-flv", ".wmv": "video/wmv", ".3gp": "video/3gpp",
    ".3gpp": "video/3gpp",
}

DEFAULT_PROMPT = """Analyze this video and return a structured markdown report using the exact sections below.

ACCURACY RULES - these override everything else:
1. Report only what is actually in the video. Do not infer, guess, or fill in plausible-sounding detail.
2. Never invent a creator, presenter, narrator, or speaker name. If no name is shown on screen or clearly spoken, say the video has no identified creator.
3. Never fabricate a voiceover, dialogue, or transcript. Many videos are silent or have music only, and that is normal. If there is no speech, say "No speech detected."
4. Separate what you SEE from what you INFER. Label anything inferred with "(inferred)".
5. Use only real timestamps taken from the video. Never estimate or invent one.

## Summary
Two to four sentences on what actually happens and who the video is for.

## Scene-by-Scene Breakdown
Walk the video in order with `MM:SS` timestamps for every distinct cut, scene, or beat. For each one give:
- what is on screen (people, setting, b-roll, product, UI)
- what is said, if anything
- any on-screen text or caption, quoted verbatim
- the cut or transition that ends the beat

## Audio
Report only what you actually hear. Valid answers include "No audio track present", "Silent - no speech, music, or effects detected", "Music only: [describe]", or a verbatim transcript with `MM:SS` timestamps if speech is genuinely present.

## On-Screen Text and Visuals
Every caption, title card, or overlay, quoted verbatim with its timestamp. Then the caption style, the text placement, and any branding or products actually shown.

## Structure
Identify these four beats with timestamps, and say plainly if one is missing:
- The hook: the first 3 seconds, what is said and what is shown
- The turn: where the video shifts or the tension is introduced
- The payoff: the moment the promise is delivered
- The close: how it ends and what the viewer is asked to do

## Pacing
Average seconds per cut, the total number of cuts, and where the pace changes.

## Key Moments
Three to seven `[MM:SS] Description` bullets a viewer would actually remember.

Be concrete. When you are unsure, say so. Reporting less with confidence beats reporting more with confabulation."""


def die(msg, hint=None):
    print(f"ERROR: {msg}", file=sys.stderr)
    if hint:
        print(hint, file=sys.stderr)
    sys.exit(1)


def log(msg):
    print(f"[info] {msg}", file=sys.stderr)


def get_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        die(
            "GEMINI_API_KEY is not set in this shell.",
            'Fix: export GEMINI_API_KEY="your-key"  (get a free key at https://aistudio.google.com/apikey)\n'
            "If you already added it to ~/.zshrc, open a new terminal or run: source ~/.zshrc",
        )
    return key


def is_youtube(s):
    return bool(re.match(r"https?://(www\.|m\.)?(youtube\.com|youtu\.be)/", s.strip(), re.I))


def to_seconds(stamp):
    """'0:05' or '1:23:45' or '90' -> '90s'"""
    parts = stamp.strip().split(":")
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        die(f"Could not read the time '{stamp}'. Use MM:SS, like 0:05.")
    total = 0.0
    for n in nums:
        total = total * 60 + n
    return f"{int(total)}s"


def parse_clip(clip):
    if "-" not in clip:
        die("--clip needs a range, like --clip 0:00-0:05")
    start, end = clip.split("-", 1)
    return to_seconds(start), to_seconds(end)


def request_json(url, payload=None, headers=None, method=None, raw=None, timeout=600):
    data = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return json.loads(body) if body else {}, dict(r.headers)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:600]
        try:
            detail = json.loads(detail)["error"]["message"]
        except Exception:
            pass
        if e.code == 400 and "API key not valid" in detail:
            die("Your GEMINI_API_KEY was rejected.", "Get a fresh key at https://aistudio.google.com/apikey")
        if e.code == 429:
            die("Rate limit hit on the free tier.", "Wait a minute and retry, or analyze a shorter clip with --clip.")
        if e.code == 404:
            die(f"Model not found. {detail}", "Try: --model gemini-2.5-flash")
        die(f"HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        die(f"Could not reach the API: {e.reason}")


def upload_large_file(path, key, mime):
    """Resumable upload for local files over the inline limit."""
    size = path.stat().st_size
    log(f"{size / 1024 / 1024:.1f} MB - uploading to the Files API...")
    _, headers = request_json(
        f"{UPLOAD_API}/files?key={key}",
        payload={"file": {"display_name": path.name}},
        headers={
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(size),
            "X-Goog-Upload-Header-Content-Type": mime,
        },
    )
    upload_url = headers.get("X-Goog-Upload-URL") or headers.get("x-goog-upload-url")
    if not upload_url:
        die("The upload did not start. Try again, or use a shorter clip.")

    result, _ = request_json(
        upload_url,
        raw=path.read_bytes(),
        headers={
            "Content-Length": str(size),
            "X-Goog-Upload-Offset": "0",
            "X-Goog-Upload-Command": "upload, finalize",
        },
    )
    info = result.get("file", {})
    name, uri = info.get("name"), info.get("uri")
    log("uploaded, waiting for processing...")

    waited = 0
    while waited < UPLOAD_TIMEOUT_SEC:
        state = info.get("state")
        if state == "ACTIVE":
            log(f"ready in {waited}s")
            return uri, info.get("mimeType", mime)
        if state == "FAILED":
            die("Gemini could not process that file.", "Try re-exporting it as an .mp4")
        time.sleep(POLL_SEC)
        waited += POLL_SEC
        info, _ = request_json(f"{API}/{name}?key={key}")
    die(f"Upload still processing after {UPLOAD_TIMEOUT_SEC}s.", "Try a shorter clip with --clip.")


def build_video_part(source, key, fps, clip):
    meta = {}
    if fps:
        meta["fps"] = fps
    if clip:
        start, end = parse_clip(clip)
        meta["start_offset"] = start
        meta["end_offset"] = end

    if is_youtube(source):
        log("reading the YouTube link directly, no download needed")
        part = {"file_data": {"file_uri": source}}
    else:
        path = Path(source).expanduser().resolve()
        if not path.is_file():
            die(f"No file at {path}")
        ext = path.suffix.lower()
        if ext not in MIME:
            die(f"'{ext}' is not a supported video format.", f"Supported: {', '.join(sorted(MIME))}")
        mime = MIME[ext]
        if path.stat().st_size <= INLINE_LIMIT:
            log(f"{path.stat().st_size / 1024 / 1024:.1f} MB - sending the file directly")
            part = {"inline_data": {"mime_type": mime, "data": base64.b64encode(path.read_bytes()).decode()}}
        else:
            uri, mime = upload_large_file(path, key, mime)
            part = {"file_data": {"file_uri": uri, "mime_type": mime}}

    if meta:
        part["video_metadata"] = meta
    return part


def main():
    p = argparse.ArgumentParser(description="Let your AI watch a video.")
    p.add_argument("source", help="A YouTube URL or a path to a local video file")
    p.add_argument("--prompt", default=DEFAULT_PROMPT, help="Ask something specific instead of the full report")
    p.add_argument("--clip", default=None, help="Analyze only part of it, like 0:00-0:05")
    p.add_argument("--fps", type=float, default=None, help="Frames sampled per second. Default 1. Use 6-10 for fast cuts.")
    p.add_argument("--model", default=DEFAULT_MODEL)
    args = p.parse_args()

    key = get_key()
    part = build_video_part(args.source, key, args.fps, args.clip)
    log(f"analyzing with {args.model}...")

    result, _ = request_json(
        f"{API}/models/{args.model}:generateContent?key={key}",
        payload={"contents": [{"parts": [part, {"text": args.prompt}]}]},
    )

    try:
        cand = result["candidates"][0]
        text = "".join(x.get("text", "") for x in cand["content"]["parts"])
    except (KeyError, IndexError):
        blocked = result.get("promptFeedback", {}).get("blockReason")
        if blocked:
            die(f"Gemini declined to analyze this video ({blocked}).")
        die(f"Unexpected response: {json.dumps(result)[:400]}")

    usage = result.get("usageMetadata", {})
    frames = next((d["tokenCount"] for d in usage.get("promptTokensDetails", []) if d.get("modality") == "VIDEO"), None)
    if frames:
        log(f"done - {frames:,} video tokens read")
    print(text)


if __name__ == "__main__":
    main()
