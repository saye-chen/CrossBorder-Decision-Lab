#!/usr/bin/env python3
"""Prepare a video URL for teardown: metadata, download, frames, contact sheet."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
from pathlib import Path
from typing import Any


def ensure_package(import_name: str, package_name: str | None = None, install_missing: bool = False) -> bool:
    try:
        __import__(import_name)
        return True
    except ImportError:
        # Runtime package installation is deliberately disabled: this tool may
        # process untrusted URLs and must not execute package-manager code.
        return False


def validate_remote_url(raw: str) -> str | None:
    parsed = urlparse(raw)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return "url must use http:// or https:// and include a hostname"
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        return "local hostnames are not allowed"
    try:
        address = ipaddress.ip_address(host)
        if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
            return "private, loopback, link-local, and reserved IPs are not allowed"
    except ValueError:
        pass
    if parsed.username or parsed.password:
        return "URLs with embedded credentials are not allowed"
    return None


def slugify(text: str) -> str:
    text = re.sub(r"https?://", "", text)
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:60] or "video"


def compact_info(info: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "id",
        "title",
        "description",
        "duration",
        "view_count",
        "like_count",
        "comment_count",
        "repost_count",
        "uploader",
        "uploader_id",
        "channel",
        "channel_id",
        "timestamp",
        "upload_date",
        "webpage_url",
        "thumbnail",
        "width",
        "height",
        "fps",
        "ext",
    ]
    out = {k: info.get(k) for k in keys if info.get(k) is not None}
    out["format_count"] = len(info.get("formats") or [])
    out["has_subtitles"] = bool(info.get("subtitles"))
    out["has_automatic_captions"] = bool(info.get("automatic_captions"))
    return out


def extract_frames(video_path: Path, out_dir: Path, samples: int, install_missing: bool = False) -> dict[str, Any]:
    ok_imageio = ensure_package("imageio", "imageio", install_missing)
    ok_ffmpeg = ensure_package("imageio_ffmpeg", "imageio-ffmpeg", install_missing)
    ok_pil = ensure_package("PIL", "pillow", install_missing)
    if not (ok_imageio and ok_ffmpeg and ok_pil):
        return {"ok": False, "error": "missing imageio/imageio-ffmpeg/pillow"}

    import imageio  # type: ignore
    from PIL import Image, ImageDraw  # type: ignore

    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    reader = imageio.get_reader(str(video_path), "ffmpeg")
    try:
        meta = reader.get_meta_data()
        fps = float(meta.get("fps") or 30)
        duration = float(meta.get("duration") or 0)
        if duration <= 0:
            # Fallback: assume 8 seconds when metadata duration is unavailable or zero
            duration = 8
        times = [duration * i / max(samples - 1, 1) for i in range(samples)]
        saved: list[dict[str, Any]] = []
        thumbs = []
        for t in times:
            idx = max(0, int(t * fps))
            try:
                frame = reader.get_data(idx)
            except Exception:
                continue
            img = Image.fromarray(frame)
            frame_path = frames_dir / f"frame_{t:05.2f}s.jpg"
            img.save(frame_path, quality=90)
            saved.append({"time": round(t, 2), "path": str(frame_path)})

            thumb = img.copy()
            thumb.thumbnail((180, 320))
            canvas = Image.new("RGB", (180, 350), "white")
            canvas.paste(thumb, ((180 - thumb.width) // 2, 0))
            ImageDraw.Draw(canvas).text((8, 326), f"{t:.2f}s", fill=(0, 0, 0))
            thumbs.append(canvas)
    finally:
        reader.close()

    contact_sheet = None
    if thumbs:
        import math

        cols = min(4, len(thumbs))
        rows = math.ceil(len(thumbs) / cols)
        sheet = Image.new("RGB", (cols * 180, rows * 350), (245, 245, 245))
        for i, thumb in enumerate(thumbs):
            sheet.paste(thumb, ((i % cols) * 180, (i // cols) * 350))
        contact_sheet = out_dir / "contact_sheet.jpg"
        sheet.save(contact_sheet, quality=95)

    return {
        "ok": bool(saved),
        "metadata": meta,
        "frames": saved,
        "contact_sheet": str(contact_sheet) if contact_sheet else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--out", default=None)
    parser.add_argument("--samples", type=int, default=14)
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument(
        "--install-missing",
        action="store_true",
        help="deprecated compatibility flag; dependencies must be installed in the controlled environment",
    )
    parser.add_argument("--keep-video", action="store_true", help="keep downloaded video after frame extraction")
    args = parser.parse_args()

    url_error = validate_remote_url(args.url)
    if url_error:
        parser.error(url_error)
    if args.samples < 2 or args.samples > 120:
        parser.error("--samples must be between 2 and 120")

    out_dir = Path(args.out or tempfile.mkdtemp(prefix="video-link-breakdown."))
    out_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "url": args.url,
        "out_dir": str(out_dir),
        "needs_user_input": False,
        "keep_video": args.keep_video,
        "errors": [],
    }

    if not ensure_package("yt_dlp", "yt-dlp", args.install_missing):
        summary["needs_user_input"] = True
        summary["errors"].append(
            "yt-dlp unavailable; install it in the controlled environment or provide "
            "a local video file, screenshots, or transcript"
        )
        (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1

    import yt_dlp  # type: ignore

    meta_opts = {
        "quiet": True,
        "no_warnings": False,
        "noplaylist": True,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(meta_opts) as ydl:
            info = ydl.extract_info(args.url, download=False)
        if not isinstance(info, dict):
            summary["errors"].append("metadata extraction returned non-dict result (geo-blocked, private, or unsupported URL)")
            info = {}
        else:
            summary["info"] = compact_info(info)
            # Keep only the allow-listed compact metadata; full extractor
            # payloads may contain request headers, cookies, or signed URLs.
    except Exception as exc:
        summary["errors"].append(f"metadata extraction failed: {exc}")
        info = {}

    video_path = None
    if not args.skip_download:
        download_opts = {
            "quiet": True,
            "no_warnings": False,
            "noplaylist": True,
            "format": "bv*+ba/best",
            "outtmpl": str(out_dir / "video.%(ext)s"),
        }
        try:
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                downloaded = ydl.extract_info(args.url, download=True)
                if isinstance(downloaded, dict):
                    candidates = []
                    for item in downloaded.get("requested_downloads") or []:
                        if item.get("filepath"):
                            candidates.append(Path(item["filepath"]))
                    if downloaded.get("filepath"):
                        candidates.append(Path(downloaded["filepath"]))
                    candidates.append(Path(ydl.prepare_filename(downloaded)))
                    candidates.extend(sorted(out_dir.glob("video.*")))
                    video_path = next((path for path in candidates if path.exists()), None)
        except Exception as exc:
            summary["errors"].append(f"download failed: {exc}")

    if video_path and video_path.exists():
        summary["video_path"] = str(video_path)
        summary["downloaded_video_bytes"] = video_path.stat().st_size
        frame_result = extract_frames(video_path, out_dir, args.samples, args.install_missing)
        summary["frame_extraction"] = frame_result
        if frame_result.get("ok") and not args.keep_video:
            try:
                video_path.unlink()
                summary["video_path"] = None
                summary["video_removed_after_analysis"] = True
            except Exception as exc:
                summary["video_removed_after_analysis"] = False
                summary["errors"].append(f"video cleanup failed: {exc}")
        elif not frame_result.get("ok"):
            summary["needs_user_input"] = True
            summary["missing"] = ["extractable video frames or screenshots"]
            summary["errors"].append(
                "frame extraction failed; downloaded video was preserved for an alternate local media tool"
            )
    else:
        summary["needs_user_input"] = True
        summary["missing"] = ["downloadable video file"]

    if not summary.get("info") and not summary.get("video_path"):
        summary["needs_user_input"] = True
        summary["missing"] = ["video file", "transcript or subtitles", "screenshots"]

    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    return 0 if not summary["needs_user_input"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
