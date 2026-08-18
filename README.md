# video-summary

A [Claude Code](https://claude.com/claude-code) skill that watches a video — the frames and the audio, not a transcript — and returns a scene-by-scene breakdown: timestamps, on-screen captions quoted verbatim, structure, pacing, and a full transcript when speech is present.

Works on a YouTube link or a local video file. Handles anything from short-form video (ads, Reels, TikToks) to long-form talks, podcasts, tutorials, and meeting recordings.

## Requirements

| Requirement | Purpose | Source |
|---|---|---|
| Python 3.9+ | Runs the script | Already on every Mac |
| `GEMINI_API_KEY` | Does the actual video analysis | Free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

No packages to install — the script uses only the Python standard library.

## Install as a Claude Code skill

Open **Terminal** (Mac: press `Cmd + Space`, type `Terminal`, press Return) and run:

```bash
mkdir -p ~/.claude/skills/video-summary
cp SKILL.md video_summary.py ~/.claude/skills/video-summary/
```

Then get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) — it starts with `AIzaSy`, not a longer OAuth-style token — and save it so it's there every time you open Terminal, not just this session:

```bash
echo 'export GEMINI_API_KEY="AIzaSy-your-real-key-here"' >> ~/.zshrc
source ~/.zshrc
```

Replace `AIzaSy-your-real-key-here` with your actual key before running that line. Check it saved correctly:

```bash
cat ~/.zshrc
```

You should see the `export GEMINI_API_KEY=...` line printed back. If it's not there, the `echo` command above didn't run — try it again in a fresh Terminal window.

Claude Code will pick up the skill automatically. Paste a video link or file path and ask what's in it, what happened, or to turn it into a plan.

## Use it directly, without Claude Code

```bash
python3 video_summary.py "<youtube-url-or-file-path>" [--clip 0:00-0:05] [--fps 8] [--prompt "..."]
```

- `--clip` — analyze only part of it, e.g. `0:00-0:05`
- `--fps` — frames sampled per second, default 1. Short-form/fast-cut video needs 6–10, paired with `--clip` so it doesn't burn quota on a full-length video.
- `--prompt` — ask one specific thing instead of getting the full report
- `--model` — defaults to the current Gemini Flash

A private, unlisted, or age-restricted YouTube link can't be read from the URL — download the file and pass the local path instead.

## Files

| File | Contents |
|---|---|
| `video_summary.py` | The script. This is the only file required to run it standalone. |
| `SKILL.md` | The Claude Code skill definition — instructions Claude follows when you invoke this skill, including how to choose `--fps` and `--clip` correctly. |

## Accuracy

The prompt is written to refuse to fill gaps: no invented speakers, no invented voiceover on silent or music-only clips, no rounded timestamps. If something isn't in the video, the report says so instead of guessing.

## Licence

[MIT](LICENSE) — free to use, modify, and redistribute, provided the copyright notice and this license are kept with any copy.
