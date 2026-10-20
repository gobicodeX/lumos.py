import asyncio
import os
import random
from unicodedata import name
import aiohttp 
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import FSInputFile, Message, CallbackQuery, BufferedInputFile
from aiogram.enums import ParseMode
from keyboard import inline_keyboard
from aiogram.fsm.context import FSMContext
from states import Form 
from db import init_db, save_birthday, get_birthdays, get_tomorrow

from urllib.parse import quote
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN =os.getenv('BOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

WIDTH = 1024
HEIGHT = 1024

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Привет {message.from_user.username}! Я твой первый бот на aiogram 3.0!")
    
    
@dp.message(F.photo)
async def photo_handler(message: Message):
    photo = FSInputFile("C:\\Users\\Aser\\Desktop\\bot_lumos\\otaku.png")
    text = "<b>Вот тебе Отаку!</b>\n" \
    "<i>Надеюсь, он тебе понравится!</i>"
    await message.answer_photo(photo=photo, caption=text, parse_mode=ParseMode.HTML)
    
async def get_weather(message: Message):
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Бишкек&appid={WEATHER_API_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response: 
            print(response.status)
            if response.status == 200:
                data = await response.json()
                type = data['weather'][0]['main']
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                feel_like = data['main']['feels_like']
                
                await message.answer(f'Погода в Бишкеке:\n Температура: {temp}C \n' \
                                     f'Ощущается как: {feel_like}C \n Тип погоды: {type} \n Описание: {description}', reply_markup=inline_keyboard)
            else:
                await message.answer('Не удалось получить данные о погоде. Попробуйте позже.')
        
@dp.message(Command('weather'))
async def weather_command(message: Message):
    await get_weather(message)
    
@dp.callback_query()
async def process_callback(callback: CallbackQuery):
    if callback.data == "sunny":
        await callback.message.answer("Сегодня солнечно!")
    elif callback.data == "rainy":
        await callback.message.answer("Сегодня дождливо!")
        
        
async def generate_image(prompt: str):
    url = (f"https://image.pollinations.ai/prompt/{quote(prompt)}"
           f"?width={WIDTH}&height={HEIGHT}&nologo=true"
           f"&seed={random.randint(1, 10**6)}")
    timeout = aiohttp.ClientTimeout(total=120)
    
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.read()
                        if len(data) > 1000:
                            return data
        except Exception as e:
            print("Attempt {attempt+1} failed: {e}")
        
        
@dp.message(Command('draw'))
async def draw_command(message: Message, command: CommandObject):
    prompt = (command.args or "").strip()
    
    if not prompt:
        await message.answer("Пожалуйста, укажите описаниедля генерации изображения. Например: /draw красивый закат")
        return
    
    status = await message.answer("Генерация изображение...Пожалуйста, подождите.")
    try:
        data = await generate_image(prompt)
        await message.answer_photo(photo=BufferedInputFile(data, filename="image.png"), caption=f"Вот ваше изображение по запросу: {prompt}")
    except Exception as e:
        await message.answer(f"Произошла ошибка при генерации изображения: {e}")
    finally:
        await status.delete()
    
        

async def main():
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())
    


@dp.message(Command('add'))
async def add_birthday(message: Message, command: CommandObject):
    name, day = command.args.split()
    await save_birthday(message.from_user.id, name, day)
    await message.answer(f"День рождения {name} добавлен на {day}.")


@dp.message(Command('birthdays'))
async def list_birthdays(message: Message):
    birthdays = await get_birthdays(message.from_user.id)
    await message.answer(f"Ваши дни рождения:\n{birthdays}" if birthdays else "У вас нет сохраненных дней рождения.")

async def remind_birthdays():
    while True:
        try:
            for user_id, name, day in await get_tomorrow():
                await bot.send_message(user_id, f"Завтра день рождения у {name} ({day})!")
        except Exception as e:
            print("Ошибка в напоминании:", e)
        await asyncio.sleep(10)  



async def main():
    await init_db()
    task =asyncio.create_task(remind_birthdays())
    await dp.start_polling(bot)
