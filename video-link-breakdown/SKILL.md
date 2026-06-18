---
name: video-link-breakdown
description: 默认用中文拆解用户提供的视频链接，输出脚本结构、剪辑手法、内容质量、受众匹配、可复刻模板和优化建议。适用于 TikTok、YouTube Shorts、Instagram Reels、X/Twitter 视频、Bilibili、抖音等链接；当用户要求“拆解这个视频”“分析脚本/剪辑/节奏/钩子/内容质量”“复刻这个视频”“改写短视频脚本”或提供视频链接希望做内容策略分析时使用。
---

# Video Link Breakdown

Use this skill to turn an arbitrary video link into a structured content teardown. Prefer running the bundled preparation script first so metadata, local video, and keyframes are gathered consistently. The script downloads video only as a temporary analysis artifact by default, then deletes the original video after successful frame extraction.

## Quick Workflow

1. Create a task folder under the current workspace, usually `work/video-link-breakdown/<short-id>/`.
2. Run:

```bash
python3 ~/.codex/skills/video-link-breakdown/scripts/prepare_video_link.py "<video-url>" --out "<task-folder>"
```

3. Read `<task-folder>/summary.json`.
4. If `<task-folder>/contact_sheet.jpg` exists, inspect it with the image viewer before analyzing.
5. Expect the downloaded source video to be deleted after frames are extracted. Use `--keep-video` only when the user explicitly wants a local archive.
6. If downloaded video exists but no frames were extracted, try an alternate local media tool only if needed.
7. If the script reports `needs_user_input`, ask only for the missing artifact: uploaded video file, transcript/subtitles, screenshots, or a platform-accessible mirror.

## Analysis Priorities

Always separate what was observed from what is inferred. If there is no transcript or audio transcription, say that script analysis is based on visual structure, title, on-screen text, and editing flow.

Cover these sections unless the user asks for a different format:

- Basic video facts: platform, creator, title/description, duration, size, and visible engagement metrics when available.
- One-sentence strategic diagnosis: what the video is trying to achieve.
- Script structure: hook, setup, proof/demo/story beats, payoff, CTA, and what each beat does.
- Editing techniques: shot sequence, pacing, jump cuts, captions, overlays, transitions, sound/music role, camera distance, visual focus, product or subject framing.
- Content quality: topic value, clarity, novelty, credibility, emotional pull, information density, audience fit, and conversion/retention strength.
- Scores: hook, pacing, clarity, persuasion, originality, replication value, and overall score.
- Replicable template: a concise beat-by-beat formula the user can reuse.
- Upgrade suggestions: concrete changes to improve retention, trust, clarity, or conversion.
- Rewritten version: if useful, provide a short improved script or shot list in the user's language.

## Link Handling

Use `yt-dlp` through the script for supported platforms. The script can install missing Python packages into the user site when allowed by the environment. It records failures in `summary.json`; do not keep retrying the same failing method.

Default storage behavior: keep `summary.json`, `metadata.full.json`, extracted frames, and `contact_sheet.jpg`; remove the downloaded video file after successful frame extraction. This minimizes local storage use while preserving enough visual evidence for analysis.

For TikTok and short-form product videos, `oEmbed`/metadata may provide useful title, creator, thumbnail, sound, and engagement signals even when subtitles are absent. Use these as supporting context, not as a substitute for viewing frames.

For videos with speech:

- Prefer provided subtitles/transcript when available.
- If subtitles are unavailable and no transcription tool is already available, proceed with visual teardown and clearly mark spoken-word analysis as unavailable.
- Ask the user for transcript only when the missing speech materially affects the request.

## Output Style

Respond in the user's language. Be direct and practical. Favor reusable patterns over vague praise.

For Chinese users, this default template works well:

```text
一、基础信息
二、一句话判断
三、脚本结构拆解
四、剪辑手法拆解
五、内容质量评分
六、最值得复刻的点
七、问题与优化建议
八、如果重做，推荐脚本/分镜
```

Keep the teardown grounded in the actual video. If only metadata is available, give a limited analysis and state exactly what artifact would unlock a full teardown.
