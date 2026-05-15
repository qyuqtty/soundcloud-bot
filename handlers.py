import asyncio
import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from config import DOWNLOADS_DIR, MAX_FILE_SIZE
from downloader import download_audio

router = Router()

SUPPORTED_DOMAINS = (
    "soundcloud.com",
)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🎵 <b>Музыкальный бот</b>"
        " SoundCloud\n"
        "Просто отправь ссылку на трек.",
        parse_mode="HTML",
    )


@router.message(F.text)
async def handle_music_link(message: Message):
    url = message.text.strip()
    text_lower = url.lower()

    if not any(domain in text_lower for domain in SUPPORTED_DOMAINS):
        await message.reply(
            "\\(^-^)\/ Я поддерживаю только музыку с "
            "♫ SoundCloud\n"
            "◕_◕ Пожалуйста, пришли корректную ссылку."
        )
        return

    status_msg = await message.answer(
        "(｡◕‿‿◕｡) Скачиваю аудио..."
    )

    info = None

    try:
        info = await asyncio.to_thread(
            download_audio,
            url,
            DOWNLOADS_DIR,
        )

        if info["filesize"] > MAX_FILE_SIZE:
            await status_msg.edit_text(
                "(╥﹏╥) Файл слишком большой (>50 МБ).\n"
                "Попробуй другой трек."
            )

            if os.path.exists(info["filename"]):
                os.remove(info["filename"])

            return

        audio = FSInputFile(info["filename"])

        await message.answer_audio(
            audio=audio,
            title=info["title"],
            performer=info["uploader"],
            duration=info["duration"],
            caption="\\(^-^)\/ Скачано успешно",
        )

        await status_msg.delete()

    except Exception as e:
        error_text = str(e)[:300]

        await status_msg.edit_text(
            f"(╥﹏╥) Ошибка при скачивании:\n{error_text}"
        )

    finally:
        if info and os.path.exists(info["filename"]):
            try:
                os.remove(info["filename"])
            except Exception:
                pass