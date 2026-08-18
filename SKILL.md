---
name: video-summary
description: Watch and analyze any video — a YouTube link or a local file. Reads the actual frames and audio, not just the transcript, and returns a scene-by-scene breakdown with timestamps, a full transcript, on-screen captions, structure, and pacing. Can also turn that analysis into a team brief: concrete ideas to bring to a team meeting, each traceable to a timestamp, with effort, owner, and one decision to make. Use whenever a video link or file path is given and the request is to understand, summarize, break down, or extract takeaways from what's in it.
argument-hint: <youtube-url-or-file-path> [--clip 0:00-0:05] [--fps 8] [--prompt "..."]
allowed-tools: Bash, Read
---

# Video Summary

Turn any YouTube link or local video file into a real breakdown: what is on screen, what is said, why it works, and how to use it.

This skill runs in two stages. Stage 1 observes and never infers. Stage 2 interprets, and only runs when asked. Keep them separate. Do not let Stage 2 reasoning leak into the Stage 1 report.

## Prerequisites

- Python 3.9 or newer, which is already on every Mac.
- GEMINI_API_KEY set in the shell. Free key at https://aistudio.google.com/apikey
- Nothing to pip install. The script uses only the Python standard library.

## Stage 1: watch the video

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

## Stage 2: the team brief

Run this ONLY when I ask for something actionable. Trigger phrases: "ideas for my team", "what can we action", "bring back to the team", "what should we do with this", "team brief", "takeaways we can discuss". If I only asked what is in the video, stop after Stage 1.

Before writing the brief, ask me two things if I have not already said them:
- **Which team is this for**, and what do they own? Ideas for a demand gen team are different from ideas for a content or brand team.
- **Why did I watch this?** A competitor teardown, a format I am considering, a conference talk, a customer story, or a campaign post-mortem all point at different actions.

Do not guess these. A brief aimed at the wrong team is worse than no brief, because it wastes a meeting.

### Rules for the brief

- **Every idea traces to a timestamp.** No idea appears without the `MM:SS` observation it came from. This is what makes it defensible in a room. If someone pushes back, I can scrub to the moment and show them.
- **Separate observed from recommended.** Never blur what the video did with what we should do. Label them.
- **Three to five ideas, not ten.** A list nobody can act on is a list nobody acts on. Cut to what is genuinely worth discussing.
- **Say what NOT to copy.** A brief that recommends everything is useless. Naming what you would skip, and why, is what makes the rest credible.
- **Every idea gets an honest effort estimate.** If it needs a videographer, a budget, or three weeks of someone's time, say so. Ideas that hide their cost get killed in the meeting anyway.
- **End with one decision.** Meetings need a decision, not a discussion. Name the single thing the team should decide, and what happens either way.
- **No hype.** Plain language. If a technique is common and unremarkable, say that rather than dressing it up.

### Brief format

```markdown
# Team brief: [video, in a few words]

**Watched:** [what it is, who made it if identified, length]
**Why:** [the reason I watched it]
**For:** [which team]

## What the video actually did
[Three to five bullets, observation only, each with a timestamp. No recommendations here.]

## Ideas worth discussing

### 1. [Plain name for the idea]
- **Seen at:** `[MM:SS]` [the specific observation this comes from]
- **What we would do:** [concrete action, not a theme]
- **Effort:** [Small / Medium / Large, and what it actually takes]
- **The bet:** [what has to be true for this to work, stated honestly]
- **Suggested owner:** [function, not a named person]

### 2. [...]
(three to five total)

## What I would not copy
- [thing] — [why it would not work for us]

## Questions I cannot answer alone
- [the things that genuinely need the team's input, budget, or context]

## The decision for this meeting
[One question, phrased so the answer is yes or no, or A or B. Then what happens on each branch.]
```

## Rules, do not break these

- Only describe what is actually in the video. Never invent a creator, a speaker, a brand, a statistic, or a quote.
- Never invent a voiceover. Plenty of videos are silent, music only, or ambient noise only, and that is normal. Say so instead of filling the gap.
- Use only the timestamps the analysis returned. Never estimate or round one to look tidy.
- A private, unlisted, or age-restricted link cannot be read from the URL. Tell me to download the file and pass the path instead.
- Keep my local video files local. Never upload anything I did not point you at.
- In Stage 2, never present an inference as an observation. If an idea rests on something you are guessing at, say which part is a guess.
