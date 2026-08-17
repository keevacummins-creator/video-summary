# watch-video

A [Claude Code](https://claude.com/claude-code) skill that actually watches a video — the real frames and the real audio, not just a transcript — and returns a scene-by-scene breakdown: timestamps, on-screen captions quoted verbatim, the hook/turn/payoff structure, pacing, and a full transcript when speech is present.

Works on a YouTube link or a local video file. Built for pulling apart short-form video (ads, Reels, TikToks) to see why a hook or edit works, but also handles long-form talks, podcasts, and tutorials.

## Requirements

| Requirement | Purpose | Source |
|---|---|---|
| Python 3.9+ | Runs the script | Already on every Mac |
| `GEMINI_API_KEY` | Does the actual video analysis | Free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

No packages to install — the script uses only the Python standard library.

## Install as a Claude Code skill

```bash
mkdir -p ~/.claude/skills/watch-video
cp SKILL.md watch_video.py ~/.claude/skills/watch-video/
```

Then set your API key so it persists across terminal sessions:

```bash
echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

Claude Code will pick up the skill automatically. Paste a video link or file path and ask what happened, why it worked, or to turn it into a plan.

## Use it directly, without Claude Code

```bash
python3 watch_video.py "<youtube-url-or-file-path>" [--clip 0:00-0:05] [--fps 8] [--prompt "..."]
```

- `--clip` — analyze only part of it, e.g. `0:00-0:05`
- `--fps` — frames sampled per second, default 1. Short-form/fast-cut video needs 6–10, paired with `--clip` so it doesn't burn quota on a full-length video.
- `--prompt` — ask one specific thing instead of getting the full report
- `--model` — defaults to the current Gemini Flash

A private, unlisted, or age-restricted YouTube link can't be read from the URL — download the file and pass the local path instead.

## Files

| File | Contents |
|---|---|
| `watch_video.py` | The script. This is the only file required to run it standalone. |
| `SKILL.md` | The Claude Code skill definition — instructions Claude follows when you invoke this skill, including how to choose `--fps` and `--clip` correctly. |

## Accuracy

The prompt is written to refuse to fill gaps: no invented speakers, no invented voiceover on silent or music-only clips, no rounded timestamps. If something isn't actually in the video, the report says so instead of guessing.

## Licence

[MIT](LICENSE) — free to use, modify, and redistribute, provided the copyright notice and this license are kept with any copy.
