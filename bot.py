import sqlite3
from datetime import datetime
from aiogram import Bot, types, Dispatcher, executor
from config import token
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

bot = Bot(token)
dp = Dispatcher(bot)

database = sqlite3.connect('dodo_pizza.db')
cursor = database.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR (999),
        last_name VARCHAR (999),
        username VARCHAR,
        id_user INT,
        phone_number VARCHAR (999)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS address (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_user INT,
        address_longitude FLOAT,
        address_latitude FLOAT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR (999),
        address_destination VARCHAR(999),
        date_time_order VARCHAR (999)
    )
""")

database.commit()

inline_buttons = [
    InlineKeyboardButton("Отправить номер", callback_data='send_phone_number'),
        InlineKeyboardButton("Отправить локацию", callback_data='send_location'),
        InlineKeyboardButton("Заказать еду", callback_data='order_food')
]
inline_keyboard = InlineKeyboardMarkup().add(*inline_buttons)

@dp.message_handler(commands='start')
async def start_command(message: types.Message):
    cursor.execute(f"SELECT * FROM users WHERE id_user= {message.from_user.id};")
    result = cursor.fetchall()
    if result == []:
        
        cursor.execute(f"""INSERT INTO users (first_name, last_name, username, id_user) VALUES ({message.from_user.id},
                       '{message.from_user.first_name}', '{message.from_user.last_name}', '{message.from_user.username});
                        )
                        """)
    cursor.connection.commit()
    await message.answer(f"Здравствуйте {message.from_user.full_name}", reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda call: call.data == 'send_phone_number')
async def send_phone_number(callback_query: types.CallbackQuery):
    # Запрашиваем у пользователя номер телефона
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введите номер телефона', reply_markup=types.ReplyKeyboardRemove())

    # Прослушиваем ответ пользователя
    @dp.message_handler(content_types=types.ContentType.CONTACT)
    async def process_contact(message: types.Message):
        cursor.execute("UPDATE users SET phone_number=? WHERE id_user=?", (message.contact.phone_number, message.from_user.id))
        conn.commit()

        await bot.send_message(message.chat.id, "Спасибо, ваш номер телефона добавлен", reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(lambda call: call.data == 'send_location')
async def send_location(callback_query: types.CallbackQuery):
    
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Отправьте вашу локацию', reply_markup=types.ReplyKeyboardRemove())

    
    @dp.message_handler(content_types=types.ContentType.LOCATION)
    async def process_location(message: types.Message): 
        cursor.execute("INSERT INTO address (id_user, address_longitude, address_latitude) VALUES (?, ?, ?)",
                       (message.from_user.id, message.location.longitude, message.location.latitude))
        conn.commit()
        await bot.send_message(message.chat.id, "Спасибо, ваша локация добавлена", reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(lambda call: call.data == 'order_food')
async def order_food(callback_query: types.CallbackQuery):  
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введите ваш заказ', reply_markup=types.ReplyKeyboardRemove())

    
    @dp.message_handler(content_types=types.ContentType.TEXT)
    async def process_order(message: types.Message):
       
        cursor.execute(f"""INSERT INTO orders (title, address_destination, date_time_order) VALUES
                       (message.text, "", datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                       """)
        conn.commit()

        await bot.send_message(message.chat.id, "Спасибо, ваш заказ добавлен", reply_markup=types.ReplyKeyboardRemove())

executor.start_polling(dp)