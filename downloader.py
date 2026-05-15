import os
from pathlib import Path
from typing import Dict, Any

import yt_dlp


def download_audio(url: str, output_dir: Path) -> Dict[str, Any]:
    output_template = str(output_dir / "%(title).100s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
        "restrictfilenames": True,
        "windowsfilenames": True,
        "socket_timeout": 30,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            {
                "key": "FFmpegMetadata",
            },
        ],
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"(✿◠‿◠) Скачиваю: {url}")

        info = ydl.extract_info(url, download=True)

        if not info:
            raise ValueError("Не удалось получить информацию о треке")
        if "entries" in info:
            info = info["entries"][0]
            if not info:
                raise ValueError("Не удалось найти трек в плейлисте")

        filename = Path(
            ydl.prepare_filename(info)
        ).with_suffix(".mp3")

        if not filename.exists():
            raise FileNotFoundError("MP3 файл не был создан")

        return {
            "filename": str(filename),
            "title": info.get("title", "Unknown Track"),
            "uploader": info.get(
                "uploader",
                info.get("channel", "Unknown")
            ),
            "duration": int(info.get("duration") or 0),
            "filesize": filename.stat().st_size,
        }