"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
import sqlite3
import os
import io
import uuid


from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from peewee import *
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from PIL import Image
from database import create_connection, close_connection, Product, Complaint
from order_states import (
    OrderStates,
    AdminAddProductStates,
    CategoryListStates,
    ComplainStates,
)

from buttons import (
    button,
    phone_number_share_button,
    category_button,
    admin_category_add_button,
    cancel_pack,
)


from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
ADMIN_LOG_GROUP = os.getenv("ADMIN_LOG_GROUP")
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


DATABASE_NAME = os.getenv("PGDATABASE")
DATBASE_USER = os.getenv("PGUSER")
DATABASE_PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")

db = PostgresqlDatabase(
    DATABASE_NAME, user=DATBASE_USER, password=DATABASE_PASSWORD, host=HOST, port=PORT
)


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    logging.info("ADMIN USER ID is %r", ADMIN_USER_ID)
    logging.info("Admin log group is   %r", ADMIN_LOG_GROUP)
    
    
    if message.from_user.id == ADMIN_USER_ID:
        await AdminAddProductStates.press_buttun_stair.set()
        await message.reply(
            "Salom Admin aka,",
            reply_markup=admin_category_add_button,
        )
        print("helllllloooo")
    else:
        """
        This handler will be called when user sends `/start` or `/help` command
        """
        await message.answer(
            "Salom  👋, \nWooden kompaniyasining mijozlar botiga \nXush kelibsiz,",
            reply_markup=button,
        )


# Cancel all states


# BACK into prevoius State


###############ADMIN##################
@dp.message_handler(
    Text(equals="Zinalar Qo'shish"), state=AdminAddProductStates.press_buttun_stair
)
async def get_image_press_button(message: types.Message, state=FSMContext):
    await AdminAddProductStates.next()

    return await message.reply(
        "Mahsulot rasmini kiriting ", reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message_handler(filters.Text, state=AdminAddProductStates.press_buttun_stair)
async def get_image_not_press_button(message: types.Message, state=FSMContext):
    return await message.reply("tugamni bosish orqali Kontakt kiriting ")


@dp.message_handler(
    content_types=types.ContentType.PHOTO, state=AdminAddProductStates.image
)
async def get_image_of_product(message: types.Message, state=FSMContext):
    filename = f"data/{uuid.uuid4()}.jpg"

    await message.photo[-1].download(destination_file=filename)

    image = Image.open(filename)

    resized_image = image.resize((800, 900))

    resized_image.save(filename)

    async with state.proxy() as data:
        data["image_path"] = filename

    await AdminAddProductStates.next()

    return await message.reply(
        "Iltimos ushbu rasmdagi mahsulot haqida ma'lumot kiriting"
    )


@dp.message_handler(filters.Text, state=AdminAddProductStates.description)
async def get_description_of_product(messege: types.Message, state=FSMContext):
    await state.update_data(description=messege.text)
    await AdminAddProductStates.next()
    return await messege.reply("Iltimos mahsulot narxini kiriting")


@dp.message_handler(filters.Text, state=AdminAddProductStates.price)
async def get_price_of_product(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data["price"] = message.text

    image_path = data["image_path"]
    description = data["description"]
    price = data["price"]

    db.connect()
    product = Product(image=image_path, description=description, price=price)
    product.save()
    db.close()

    await state.finish()

    await message.reply("Mahsulotingiz muvaffaqiyatli saqlandi")
    await send_welcome(message=message)


#####################################


@dp.message_handler(state="*", commands="Asosiy")
@dp.message_handler(Text(equals="Asosiy", ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await send_welcome(message=message)


@dp.message_handler(Text(equals="🛒 2.Buyurtma"))
async def post_order(message: types.Message):
    await OrderStates.phone_number.set()

    await message.answer(
        "Telefon Raqamingizni kiriting", reply_markup=phone_number_share_button
    )


@dp.message_handler(filters.Text, state=OrderStates.phone_number)
async def get_phone_number_in_order_by_text(message: types.Message):
    return await message.reply("Iltimos tugmani bosish orqali telefon raqam kiriting")


@dp.message_handler(
    content_types=types.ContentType.CONTACT, state=OrderStates.phone_number
)
async def get_phone_number_in_order_by_contact(
    message: types.Message, state: FSMContext
):
    if message.contact is None:
        async with state.proxy() as data:
            a = await state.get_data()
            data["phone_number"] = a["phone_number"]

    else:
        async with state.proxy() as data:
            data["phone_number"] = message.contact["phone_number"]

    await OrderStates.next()

    await message.answer("Mahsulot nomini kiriting", reply_markup=cancel_pack)


@dp.message_handler(filters.Text, state=OrderStates.product_name)
async def get_product_name_in_order(message: types.Message, state: FSMContext):
    """
    Process user name
    """

    if message.text == "Ortga":
        await post_order(message=message)

        return

    if message.text is None:
        async with state.proxy() as data:
            a = await state.get_data()
            data["product_name"] = a["product_name"]

    else:
        async with state.proxy() as data:
            a = await state.get_data()

            data["product_name"] = message.text

    await OrderStates.next()
    await message.answer(
        "Mahsulotingiz haqida qo'shimcha ma'lumot bering ", reply_markup=cancel_pack
    )
    return


@dp.message_handler(filters.Text, state=OrderStates.product_description)
async def get_product_detail_info_in_order(message: types.Message, state: FSMContext):
    if message.text == "Ortga":
        await state.set_state(OrderStates.phone_number)

        # message.contact["phone_number"] = phone_num

        await get_phone_number_in_order_by_contact(message=message, state=state)
        return

    async with state.proxy() as data:
        data["description"] = message.text

    await OrderStates.next()
    await message.answer(
        "Mahsulotingizni qaysi shaharga buyurtma qilmoqchisiz? ",
        reply_markup=cancel_pack,
    )


@dp.message_handler(filters.Text, state=OrderStates.city)
async def get_product_city_in_order(message: types.Message, state: FSMContext):
    """
    Process user name
    """

    if message.text == "Ortga":
        message.text = None
        await state.set_state(OrderStates.product_name)

        await get_product_name_in_order(message=message, state=state)

        return

    async with state.proxy() as data:
        data["city"] = message.text

    await bot.send_message(
        chat_id=ADMIN_LOG_GROUP,
        text=f"📞 1.Nomer: {data['phone_number']} \n\n📦 2.Mahsulot: {data['product_name']}\n\n\U0001F4CD 3.Shahar: {data['city']}  \n\n🗒 4.Qo'shimcha ma'lumot: {data['description']}",
    )
    await message.answer("Malumotlar Adminga jo'natildi")
    await state.finish()
    await send_welcome(message=message)


@dp.message_handler(Text(equals="😡 3.Shikoyat"))
async def complain(message: types.Message):
    await ComplainStates.phone_number.set()
    await message.answer(
        "Telefon raqamingizni kiriting", reply_markup=phone_number_share_button
    )


@dp.message_handler(
    content_types=types.ContentType.CONTACT, state=ComplainStates.phone_number
)
async def get_phone_number_for_complain(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["phone_number"] = message.contact
    await ComplainStates.next()

    await message.answer("Iltimos mahsulotdagi kamchilikni rasmga tushirib yuboring")


@dp.message_handler(content_types=types.ContentType.PHOTO, state=ComplainStates.image)
async def get_image_of_complain_product(message: types.Message, state: FSMContext):
    filename = f"complaint/{uuid.uuid4()}.jpg"

    await message.photo[-1].download(destination_file=filename)

    image = Image.open(filename)
    print(image)
    resized_image = image.resize((700, 800))

    resized_image.save(filename)

    print("what is up")
    async with state.proxy() as data:
        data["image_path"] = filename

    await ComplainStates.next()

    await message.answer("iltimos kamchilik haqida batafsilroq yozsangiz ")


@dp.message_handler(filters.Text, state=ComplainStates.description)
async def get_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        image_path = data["image_path"]
        number = data["phone_number"]
        description = message.text

    db.connect()
    product = Complaint(
        image=image_path, description=description, phone_number=number["phone_number"]
    )
    product.save()
    db.close()

    await bot.send_photo(
        chat_id=ADMIN_LOG_GROUP,
        photo=open(image_path, "rb"),
        caption=f"🔴⁉️ SHIKOYAT 🔴⁉️\n\n☎️ 1.Nomer: {number['phone_number']}\n📝 2.Batafsil: {description} ",
    )

    await message.answer("Tez orada Muammoingiz ko'rib chiqiladi,")

    await state.finish()
    await send_welcome(message=message)


@dp.message_handler(Text(equals="🕧 4.Buyurtma Holati"))
async def staus_product(message: types.Message):
    await message.answer("pressed Tovar Holati")


@dp.message_handler(Text(equals="📦 1.Mahsulot Turlari"))
async def get_all_category(message: types.Message, state: FSMContext):
    await CategoryListStates.choose_category.set()
    await message.answer(
        "Istalgan Turdagi mahsulot tanlang", reply_markup=category_button
    )


@dp.message_handler(Text(equals="Zinalar"), state=CategoryListStates.choose_category)
async def get_stairs(message: types.Message):
    db.connect()
    products = Product.select()

    images = []

    for product in products:
        images.append(product.image)

        order_product = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text="buyurtma", callback_data=product.image),
        )

        with open(product.image, "rb") as photo_path:
            await bot.send_photo(
                chat_id=message.from_user.id,
                photo=photo_path,
                caption=f"{product.description} va narxi {product.price}",
                reply_markup=order_product,
            )
    await CategoryListStates.next()
    db.close()


@dp.callback_query_handler(state=CategoryListStates.get_order)
async def handle_button_click(callback: types.CallbackQuery, state=FSMContext):
    # Answer the callback query

    dir_list = os.listdir("data")
    for x in dir_list:
        if callback.data == f"data/{x}":
            async with state.proxy() as data:
                data["image_path"] = callback.data

            await bot.answer_callback_query(
                callback.id, text="Buyurtma maahsulotingiz haqida kiriting "
            )

    await CategoryListStates.next()
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="Mahsulotni qncha hajimda buyurtma qilmoqchisiz,masalan 10 kv metr",
    )


@dp.message_handler(state=CategoryListStates.quantity)
async def get_quantity(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["quantity"] = message.text
    await CategoryListStates.next()
    await message.answer("mahsulot haqida qoshimcha ma'lumot kiriting")


@dp.message_handler(state=CategoryListStates.description)
async def get_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text

    await CategoryListStates.next()
    await message.answer(
        "telefon raqamingizni kiriting", reply_markup=phone_number_share_button
    )


@dp.message_handler(
    content_types=types.ContentTypes.CONTACT, state=CategoryListStates.phone_number
)
async def get_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["phone_number"] = message.contact

    await message.answer("Buyurtma Adminga yuborildi")

    with open(data["image_path"], "rb") as photo_path:
        await bot.send_photo(
            chat_id=ADMIN_LOG_GROUP,
            photo=photo_path,
            caption=f"📞1.Nomer: {data['phone_number']['phone_number']} \n🛠 2.Olcham: {data['quantity']}\n📊3.Qo'shimcha ma'lumot: {data['description']} ",
        )

    await state.finish()
    await send_welcome(message=message)


# And remove keyboard (just in case)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
