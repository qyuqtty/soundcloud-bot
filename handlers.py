import asyncio
import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import DOWNLOADS_DIR, MAX_FILE_SIZE
from downloader import download_audio, search_tracks

router = Router()

user_search_results = {}


def main_menu():
    kb = [
        [InlineKeyboardButton(text="٩(^‿^)۶ Поиск по тексту", callback_data="search_text")],
        [InlineKeyboardButton(text="٩(^‿^)۶ Скачать по ссылке", callback_data="search_link")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def back_to_menu_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« В меню", callback_data="back_to_menu")]
    ])


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "<b>SoundCloud Music Bot</b>\n\n"
        "(｡◕‿◕｡) Выбери режим:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>SoundCloud Music Bot</b>\n\n"
        "(｡◕‿◕｡) Выбери режим:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "search_text")
async def start_text_search(callback: CallbackQuery):
    await callback.message.edit_text(
        "(◕‿◕) Введи название трека или исполнителя:",
        reply_markup=back_to_menu_button()
    )
    await callback.answer()


@router.callback_query(F.data == "search_link")
async def start_link_search(callback: CallbackQuery):
    await callback.message.edit_text(
        "(◕‿◕) Отправь ссылку на трек SoundCloud:",
        reply_markup=back_to_menu_button()
    )
    await callback.answer()


@router.message(F.text & ~F.text.startswith("http"))
async def handle_text_search(message: Message):
    query = message.text.strip()
    status = await message.answer("(✿◠‿◠) Ищу треки...")

    try:
        results = await asyncio.to_thread(search_tracks, query, limit=8)

        if not results:
            await status.edit_text("(╥﹏╥) Ничего не найдено.\nПопробуй другой запрос.", 
                                 reply_markup=back_to_menu_button())
            return

        user_search_results[message.from_user.id] = results

        kb = []
        for i, track in enumerate(results):
            button_text = f"{track['title'][:45]}"
            if track['uploader']:
                button_text += f" — {track['uploader'][:20]}"
            kb.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"download_track:{i}"
            )])

        kb.append([InlineKeyboardButton(text="« В меню", callback_data="back_to_menu")])

        await status.edit_text(
            f"🔍 Найдено {len(results)} треков по запросу:\n<b>{query}</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
            parse_mode="HTML"
        )

    except Exception as e:
        await status.edit_text(f"(╥﹏╥) Ошибка поиска:\n{str(e)[:200]}", 
                             reply_markup=back_to_menu_button())


@router.callback_query(F.data.startswith("download_track:"))
async def download_selected_track(callback: CallbackQuery):
    user_id = callback.from_user.id
    track_index = int(callback.data.split(":")[1])

    results = user_search_results.get(user_id, [])
    if not results or track_index >= len(results):
        await callback.answer("(╥﹏╥) Трек не найден", show_alert=True)
        return

    track = results[track_index]
    url = track['url']
    
    status_msg = await callback.message.edit_text(f"(｡◕‿‿◕｡) Скачиваю:\n{track['title']}")

    try:
        info = await asyncio.to_thread(download_audio, url, DOWNLOADS_DIR)

        if info["filesize"] > MAX_FILE_SIZE:
            await status_msg.edit_text("(╥﹏╥) Файл слишком большой (>50 МБ).", 
                                     reply_markup=back_to_menu_button())
            return

        audio = FSInputFile(info["filename"])

        await callback.message.answer_audio(
            audio=audio,
            title=info["title"],
            performer=info["uploader"],
            duration=info["duration"],
            caption="(^-^)\/ Скачано успешно",
        )

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"(╥﹏╥) Ошибка скачивания:\n{str(e)[:200]}", 
                                 reply_markup=back_to_menu_button())
    finally:
        if 'info' in locals() and os.path.exists(info.get("filename", "")):
            try:
                os.remove(info["filename"])
            except:
                pass


@router.message(F.text.regexp(r"https?://"))
async def handle_music_link(message: Message):
    url = message.text.strip()
    if "soundcloud.com" not in url.lower():
        await message.reply("(^-^)\/ Поддерживаются только ссылки SoundCloud.", 
                          reply_markup=back_to_menu_button())
        return

    status_msg = await message.answer("(｡◕‿‿◕｡) Скачиваю...")

    try:
        info = await asyncio.to_thread(download_audio, url, DOWNLOADS_DIR)

        if info["filesize"] > MAX_FILE_SIZE:
            await status_msg.edit_text("(╥﹏╥) Файл слишком большой (>50 МБ).", 
                                     reply_markup=back_to_menu_button())
            return

        audio = FSInputFile(info["filename"])

        await message.answer_audio(
            audio=audio,
            title=info["title"],
            performer=info["uploader"],
            duration=info["duration"],
            caption="(^-^)\/ Скачано успешно",
        )

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"(╥﹏╥) Ошибка:\n{str(e)[:250]}", 
                                 reply_markup=back_to_menu_button())
    finally:
        if 'info' in locals() and os.path.exists(info.get("filename", "")):
            try:
                os.remove(info["filename"])
            except:
                pass