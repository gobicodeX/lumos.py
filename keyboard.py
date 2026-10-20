from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
        (InlineKeyboardButton(text="☀️", callback_data="sunny"))
    ],
    [
        (InlineKeyboardButton(text="🌧️", callback_data="rainy"))
    ],
    ]
)                                                          