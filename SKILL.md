---
name: video-summary
description: Watch and analyze any video — a YouTube link or a local file. Reads the actual frames and audio, not just the transcript, and returns a scene-by-scene breakdown with timestamps, a full transcript, on-screen captions, structure, and pacing. Use whenever a video link or file path is given and the request is to understand, summarize, or break down what's in it.
argument-hint: <youtube-url-or-file-path> [--clip 0:00-0:05] [--fps 8] [--prompt "..."]
allowed-tools: Bash, Read
---

# Video Summary

Turn any YouTube link or local video file into a real breakdown: what is on screen, what is said, why it works, and how to use it.

## Prerequisites

- Python 3.9 or newer, which is already on every Mac.
- GEMINI_API_KEY set in the shell. Free key at https://aistudio.google.com/apikey
- Nothing to pip install. The script uses only the Python standard library.

## Steps

1. Read the arguments I gave you:
   - **source** (required): a YouTube URL, or a path to a local video file
   - **--clip** (optional): analyze only part of it, like `0:00-0:05`
   - **--fps** (optional): how many frames per second to actually look at, default 1
   - **--prompt** (optional): ask one specific thing instead of the full report
   - **--model** (optional): defaults to the current Gemini Flash

2. Decide the frame rate BEFORE you run it. This is the part that matters most:
   - **Short-form video** (Reels, TikToks, Shorts, ads) cuts every half second or faster. At the default of 1 frame per second you will miss most of the cuts and report the edit wrong. Use `--fps 6` to `--fps 10`.
   - **If I am asking about the hook**, use `--clip 0:00-0:05 --fps 10`. That reads the opening frame by frame.
   - **Long talking-head video**, tutorial, podcast, webinar, screen recording: leave the default. Raising it wastes quota and adds nothing.
   - **Never** put a high `--fps` on a long video. Always pair a high `--fps` with a `--clip`.

3. Run it:

```bash
python3 ~/.claude/skills/video-summary/video_summary.py "<source>" [flags]
```

4. Show me the report as it came back. Do not summarize it away, do not renumber or round the timestamps, and do not add anything the analysis did not actually return.

5. If it errors, the script prints the exact fix underneath the error. Give me that one command instead of guessing at it.

## Rules, do not break these

- Only describe what is actually in the video. Never invent a creator, a speaker, a brand, a statistic, or a quote.
- Never invent a voiceover. Plenty of videos are silent, music only, or ambient noise only, and that is normal. Say so instead of filling the gap.
- Use only the timestamps the analysis returned. Never estimate or round one to look tidy.
- A private, unlisted, or age-restricted link cannot be read from the URL. Tell me to download the file and pass the path instead.
- Keep my local video files local. Never upload anything I did not point you at.
