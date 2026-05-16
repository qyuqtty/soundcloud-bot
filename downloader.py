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
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"(✿◠‿◠) Скачиваю: {url}")

        info = ydl.extract_info(url, download=True)

        if not info:
            raise ValueError("(╥﹏╥) Не удалось получить информацию о треке")

        if "entries" in info:
            info = info["entries"][0]

        filename = Path(ydl.prepare_filename(info)).with_suffix(".mp3")

        if not filename.exists():
            raise FileNotFoundError("(╥﹏╥) MP3 файл не был создан")

        return {
            "filename": str(filename),
            "title": info.get("title", "Unknown Track"),
            "uploader": info.get("uploader", info.get("channel", "Unknown")),
            "duration": int(info.get("duration") or 0),
            "filesize": filename.stat().st_size,
        }


def search_tracks(query: str, limit: int = 8):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'ignoreerrors': True,
        'socket_timeout': 20,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_queries = [
            f"scsearch{limit}:{query}",
            f"soundcloud:{query}",
            f"scsearch{limit}:{query} official",
        ]
        
        for search_url in search_queries:
            try:
                result = ydl.extract_info(search_url, download=False)
                
                tracks = []
                if result and 'entries' in result:
                    for entry in result['entries']:
                        if entry and entry.get('url'):
                            tracks.append({
                                'title': entry.get('title', 'Без названия'),
                                'uploader': entry.get('uploader', entry.get('channel', 'Неизвестный')),
                                'url': entry.get('url', ''),
                                'duration': entry.get('duration')
                            })
                            if len(tracks) >= limit:
                                break
                
                if len(tracks) >= 3:
                    return tracks
                    
            except:
                continue
        
        return tracks if tracks else []