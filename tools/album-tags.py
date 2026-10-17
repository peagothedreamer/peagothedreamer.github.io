#!/usr/bin/env python3
"""扫 static/audio/<专辑文件夹>/*.mp3，用 ffprobe 读 ID3，写 data/audio.json。

加歌、改标签之后跑一次，再照常 hugo：

    python tools/album-tags.py

为什么要这个：Hugo 自己不会读 mp3 标签，构建时只看得见文件名。data/audio.json
是生成出来的，但**要提交**——曲目表跟着仓库走，构建就不再依赖那些没进仓库的 mp3
（换机器、上 CI 都能构建）。没提交、或者没跑过脚本、又没有本地文件夹的三重情况下，
album 短代码会退回读文件名。

需要 ffprobe 在 PATH 里（装了 ffmpeg 就有）。
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "static" / "audio"
OUT = ROOT / "data" / "audio.json"


def probe(path):
    """ffprobe 的 format 段：时长和标签都在这里。"""
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True,
        text=True,
    )
    if r.returncode:
        sys.exit(f"ffprobe 读不了 {path}：{r.stderr.strip() or '（装了 ffmpeg 吗？）'}")
    return json.loads(r.stdout).get("format", {})


def tags(fmt):
    return {k.lower(): v for k, v in (fmt.get("tags") or {}).items()}


def filename_title(path, folder):
    """没标签就拿文件名顶上：削掉专辑前缀和 01 / 01- / 01. / 01_ 这种序号前缀。
    文件名惯例是 counting-stars-01-secrets.mp3。"""
    name = re.sub(rf"^{re.escape(folder)}[-_ .]+", "", path.stem)
    return re.sub(r"^\d+[ ._-]+", "", name).strip() or path.stem


def main():
    if not AUDIO.is_dir():
        sys.exit(f"没有 {AUDIO}")

    albums = {}
    for folder in sorted(p for p in AUDIO.iterdir() if p.is_dir()):
        tracks, artist = [], ""
        album = ""
        for mp3 in sorted(folder.glob("*.mp3")):
            fmt = probe(mp3)
            t = tags(fmt)
            album = album or t.get("album", "")
            # 专辑歌手先用 album_artist（合集里每首歌的 artist 不一样），退到第一首的 artist
            artist = artist or t.get("album_artist") or t.get("artist") or ""
            tracks.append({
                "file": mp3.name,
                "title": t.get("title") or filename_title(mp3, folder.name),
                "seconds": round(float(fmt.get("duration") or 0)),
            })
        if tracks:
            albums[folder.name] = {"album": album, "artist": artist, "tracks": tracks}

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        json.dumps(albums, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    n = sum(len(a["tracks"]) for a in albums.values())
    print(f"{OUT.relative_to(ROOT)}: {len(albums)} 张专辑 {n} 首")


if __name__ == "__main__":
    main()
