from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

phone_number_share_button = ReplyKeyboardMarkup(resize_keyboard=True)
phone_number_button = KeyboardButton(text="Telefen Raqam", request_contact=True)

one_state_back = KeyboardButton(text="Ortga")
cancel = KeyboardButton(text="Asosiy")
cancel_pack = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_pack.add(cancel, one_state_back)

phone_number_share_button.add(cancel, phone_number_button)

button = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="📦 1.Mahsulot Turlari"),
            KeyboardButton(text="🛒 2.Buyurtma"),
        ],
        [
            KeyboardButton(text="😡 3.Shikoyat"),
            KeyboardButton(text="🕧 4.Buyurtma Holati"),
        ],
    ],
)


category_button = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="Zinalar"),
        ],
        [KeyboardButton(text="Asosiy")],
    ],
)


admin_category_add_button = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="Admin Asosiy"), KeyboardButton(text="Zinalar Qo'shish")],
        [],
    ],
)
