from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import asyncio
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder


logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

# Команди для Telegram (щоб вони відображались у списку)
async def set_commands():
    commands = [
        types.BotCommand(command="/start", description="Привітання"),
        types.BotCommand(command="/random", description="Випадковий факт"),
        types.BotCommand(command="/gpt", description="ChatGPT інтерфейс"),
        types.BotCommand(command="/talk", description="Діалог з відомою особистістю"),
        types.BotCommand(command="/quiz", description="Квіз"),
    ]
    await bot.set_my_commands(commands)

# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привіт! Обери, що тобі потрібно:\n"
        "/start — Привітання\n"
        "/random — Випадковий факт\n"
        "/gpt — ChatGPT інтерфейс\n"
        "/talk — Діалог з відомою особистістю\n"
        "/quiz — Квіз"
    )

# Команда /random
@dp.message(Command("random"))
async def random_fact(message: types.Message):
    try:
        # 1️⃣ Відправляємо зображення
        photo_path = "images/im1.jpg"
        if os.path.exists(photo_path):
            photo = FSInputFile(photo_path)
            await message.answer_photo(photo=photo, caption="🎲 Генерую випадковий факт...")
        else:
            await message.answer("🎲 Генерую випадковий факт... (зображення не знайдено)")

        # 2️⃣ Запит до ChatGPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ти — енциклопедія цікавих фактів. Відповідай коротко українською."},
                {"role": "user", "content": "Розкажи випадковий цікавий факт."}
            ]
        )
        fact = response.choices[0].message.content

        # 3️⃣ Кнопки
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔁 Хочу ще факт", callback_data="more_fact"),
                    InlineKeyboardButton(text="🏁 Закінчити", callback_data="end_random"),
                ]
            ]
        )

        # 4️⃣ Відправляємо факт з кнопками
        await message.answer(f"✨ {fact}", reply_markup=keyboard)

    except Exception as e:
        logging.error(f"Помилка у /random: {e}")
        await message.answer("⚠️ Не вдалося отримати факт. Спробуй пізніше.")

# ---------- CALLBACK: Хочу ще факт ----------
@dp.callback_query(F.data == "more_fact")
async def more_fact(callback: types.CallbackQuery):
    await callback.answer()  # прибрати "годинник"
    await random_fact(callback.message)

# ---------- CALLBACK: Закінчити ----------
@dp.callback_query(F.data == "end_random")
async def end_random(callback: types.CallbackQuery):
    await callback.answer()
    await start(callback.message)


# Команда /gpt
@dp.message(Command("gpt"))
async def chatgpt_command(message: types.Message):
    user_input = message.text.replace("/gpt", "").strip()

    if not user_input:
        await message.answer("Будь ласка, напиши повідомлення після команди, наприклад:\n`/gpt розкажи анекдот`")
        return

    await message.answer("💭 Думаю над відповіддю...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ти — дружній Telegram-асистент."},
                {"role": "user", "content": user_input}
            ]
        )

        answer = response.choices[0].message.content
        await message.answer(answer)

    except Exception as e:
        logging.error(f"Помилка OpenAI: {e}")
        await message.answer("⚠️ Сталася помилка при зверненні до ChatGPT. Перевір API ключ.")



async def main():
    logging.info("🤖 Бот запущено!")
    await set_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
