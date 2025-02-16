import asyncio
import logging
import sqlite3
import datetime
from ascii_converter import image_to_ascii
from models import db_models
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ContentType
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np
import cv2
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('bot_token')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

DEFAULT_SETTINGS = {
    "new_width": 40,
    "aspect_ratio_adjust": 0.55,
    "upscale_factor": 2,
    "invert": 0,
    "gradient_mode": "Default"
}

GRADIENT_MODES = {
    "Default": "▁▂▃▄▅▆▇█",
    "simple_Blocks": "░▒▓█",
    "Blocks": ".:░▒▓█",
    "Extended": "@%#*+=-:. ",
    "Classic": "$@B%8&WM#*oahkbdpqwm",
    "Simple": " .:-=+*#%@",
    "Dense": "█▓▒░"
}

# کلاس FSM برای مدیریت وضعیت‌ها
class ImageProcess(StatesGroup):
    waiting_for_image = State()
    waiting_for_setting = State()
    waiting_for_value = State()


# Handler /start: ثبت کاربر در پایگاه داده
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user = message.from_user
    db_models.insert_or_update_user(user.id, user.username, user.first_name, user.last_name)
    if not db_models.get_user_settings(user.id):
        db_models.create_default_user_settings(user.id)
    start_text = """*Welcome to the ASCII Art Bot!* ✨

This bot transforms your images into *ASCII masterpieces* by analyzing brightness levels and mapping each pixel to a corresponding ASCII character. **ASCII art** is a form of digital art that uses text characters to represent shapes, shading, and textures. It dates back to the early days of computing and remains a creative and stylish way to share images.

Below are the main parameters you can customize. *Note:* The final **height** of the ASCII output is calculated automatically based on these settings. On devices with narrow screens, you may want to keep some values lower to ensure the art displays correctly, while higher values yield more detail.

*Parameters:*

1. *new_width*  
   Defines the width of the ASCII art in characters. The bot automatically calculates the new height based on the image’s aspect ratio and `aspect_ratio_adjust`. A higher `new_width` produces more detail but may result in a taller output that could be challenging on smaller screens.

2. *aspect_ratio_adjust*  
   Adjusts for the fact that text characters are typically taller than they are wide. A lower value creates a shorter, more compact output (ideal for mobile devices), whereas a higher value increases vertical detail, enhancing the overall clarity of the art.

3. *upscale_factor*  
   Determines how much the original image is upscaled before conversion. Increasing this value can help preserve fine details, though it might slow down the conversion process and produce larger outputs.

4. *invert*  
   Reverses the brightness mapping so that dark areas become light and vice versa. This can generate striking contrast, especially in images that are very bright or very dark.

5. *gradient_mode*  
   Lets you select the set of characters used to create the ASCII art. Different modes (such as Blocks, Classic, or Extended) can dramatically change the style and feel of the final output.

*Experiment with these settings to find the perfect balance between detail and readability.*  
Enjoy creating art! ✨
"""
    await message.reply(start_text,parse_mode='Markdown')
    await message.answer("⚠️*Remember*⚠️\nA higher `new_width` produces more detail; if your output is lacking detail, try increasing it. However, if the image appears too large and unclear, decrease `new_width` for a better balance on smaller screens.", parse_mode='Markdown')
    await state.set_state(ImageProcess.waiting_for_image)
    db_models.log_user_message(user.id, "Started conversation.")



@router.message(Command("set"))
async def cmd_set(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="new_width", callback_data="set_new_width"),
                InlineKeyboardButton(text="aspect_ratio_adjust", callback_data="set_aspect_ratio_adjust")
            ],
            [
                InlineKeyboardButton(text="upscale_factor", callback_data="set_upscale_factor"),
                InlineKeyboardButton(text="gradient_mode", callback_data="set_gradient_mode")
            ],
            [
                InlineKeyboardButton(text=f"Invert ({'ON' if db_models.get_user_settings(message.from_user.id)['invert'] else 'OFF'})", callback_data="toggle_invert")
            ]
        ]
    )
    await message.reply("Choose one of options below:", reply_markup=keyboard)
    await state.set_state(ImageProcess.waiting_for_setting)
    db_models.log_user_message(message.from_user.id, "/set command invoked.")

@router.callback_query(F.data.startswith("set_"))
async def process_setting_button(callback: types.CallbackQuery, state: FSMContext):
    setting_name = callback.data.replace("set_", "")
    await state.update_data(setting_name=setting_name)
    await callback.message.edit_text(f"Enter new value for {setting_name}:")
    await state.set_state(ImageProcess.waiting_for_value)

@router.callback_query(F.data == "toggle_invert")
async def toggle_invert(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_settings = db_models.get_user_settings(user_id)
    new_invert = 0 if user_settings["invert"] else 1
    db_models.update_user_setting(user_id, "invert", new_invert)
    await callback.message.edit_text(f"Invert mode: {'Active' if new_invert else 'Deactive'}")
    db_models.log_user_message(user_id, f"Invert set to {new_invert}")

@router.message(ImageProcess.waiting_for_value)
async def process_setting_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    setting_name = data.get("setting_name")
    user_id = message.from_user.id

    if not setting_name:
        await message.reply("error in getting Value")
        await state.clear()
        return
    
    if setting_name == "gradient_mode":
        new_value = message.text.strip()
        if new_value not in GRADIENT_MODES:
            available = ", ".join(GRADIENT_MODES.keys())
            await message.reply(f"Value is not available. Available options: {available}")
            return
    else:
        try:
            if setting_name == "aspect_ratio_adjust":
                new_value = float(message.text)
            else:
                new_value = int(message.text)
        except ValueError:
            await message.reply("please Enter number")
            return
    
    db_models.update_user_setting(user_id, setting_name, new_value)
    await message.reply(f"{setting_name} new: {new_value}")
    db_models.log_user_message(user_id, f"Updated {setting_name} to {new_value}")
    await state.clear()

@router.message(F.content_type == 'text')
async def process_image(message: types.Message, state: FSMContext):
    user = message.from_user
    db_models.log_user_message(user.id, message.text)

@router.message()
async def process_image(message: types.Message, state: FSMContext):
    user = message.from_user
    photo = message.photo[-1]
    db_models.insert_or_update_user(user.id, user.username, user.first_name, user.last_name)
    db_models.log_user_message(user.id, f"Sent a photo.\n{photo.file_id}")

    file = await bot.get_file(photo.file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"{str(user.id)}.jpg")
    
    user_settings = db_models.get_user_settings(user.id)
    if not user_settings:
        user_settings = db_models.create_default_user_settings(user.id)
    
    new_width = user_settings["new_width"]
    aspect_ratio_adjust = user_settings["aspect_ratio_adjust"]
    upscale_factor = user_settings["upscale_factor"]
    invert = bool(user_settings["invert"])
    gradient_mode = user_settings["gradient_mode"]
    
    for mode_name, gradient in GRADIENT_MODES.items():
        ascii_art = image_to_ascii(
            f"{str(user.id)}.jpg",
            new_width,
            aspect_ratio_adjust,
            upscale_factor,
            invert,
            gradient
        )
        result_text = f"<b>{mode_name} Mode:</b>\n<pre>{ascii_art}</pre>"
        await message.reply(result_text, parse_mode="HTML")
    await state.clear()
    os.remove(f"{str(user.id)}.jpg")

async def main():
    db_models.create_tables()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
