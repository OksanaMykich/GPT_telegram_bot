from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from credentials import TOKEN, OPENAI_API_KEY
import asyncio
import os
import logging
import json
from openai import OpenAI
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter


# Створення станів
class GPTMode(StatesGroup):
    active = State()

class TALKMode(StatesGroup):
    active = State()

class RANDOMMode(StatesGroup):
    active = State()

class QUIZMode(StatesGroup):
    active = State()

class TRANSLATEMode(StatesGroup):
    active = State()

class ROLLMode(StatesGroup):
    active = State()

# Логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальні змінні
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
client = OpenAI(api_key=OPENAI_API_KEY)
user_gpt_mode = set()
user_talk_persona = {}
user_quiz_question = {}
user_talk_translator = {}


# Команди для Telegram (щоб вони відображались у списку)
async def set_commands():
    commands = [
        types.BotCommand(command="/start", description="Вибрати команду"),
        types.BotCommand(command="/random", description="Випадковий факт"),
        types.BotCommand(command="/gpt", description="ChatGPT інтерфейс"),
        types.BotCommand(command="/talk", description="Діалог з відомою особистістю"),
        types.BotCommand(command="/quiz", description="Квіз"),
        types.BotCommand(command="/translate", description="Перекладач"),
        types.BotCommand(command="/roll", description="Гра-кубик"),
    ]
    await bot.set_my_commands(commands)


# Команда /start ------------------------------------------------------------------------------------------
@dp.message(Command("start"), StateFilter("*"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    # Відправляю зображення
    photo_path = "images/im0.jpg"
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo, caption="")
    else:
        await message.answer("Зображення не знайдено")

    await message.answer(
        "Привіт! Обери, що тобі потрібно:\n"
        "/start — Вибір команди\n"
        "/random — Випадковий факт\n"
        "/gpt — ChatGPT інтерфейс\n"
        "/talk — Діалог з відомою особистістю\n"
        "/quiz — Квіз\n"
        "/translate - Перекладач\n"
        "/roll - Гра-кубик"
    )


# Команда /random ------------------------------------------------------------------------------------------
@dp.message(Command("random"), StateFilter("*"))
async def random_fact(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(RANDOMMode.active)
    try:
        # Відправляю зображення
        photo_path = "images/im1.jpg"
        if os.path.exists(photo_path):
            photo = FSInputFile(photo_path)
            await message.answer_photo(photo=photo, caption="🎲 Генерую випадковий факт...")
        else:
            await message.answer("🎲 Генерую випадковий факт... (зображення не знайдено)")

        # Запит ChatGPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ти — енциклопедія цікавих фактів. Відповідай коротко українською."},
                {"role": "user", "content": "Розкажи випадковий цікавий факт."}
            ]
        )
        fact = response.choices[0].message.content

        # Кнопки
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔁 Хочу ще факт", callback_data="more_fact"),
                    InlineKeyboardButton(text="🏁 Закінчити", callback_data="end_random"),
                ]
            ]
        )

        # Відправляю факт з кнопками
        await message.answer(f"✨ {fact}", reply_markup=keyboard)

    except Exception as e:
        logging.error(f"Помилка у /random: {e}")
        await message.answer("⚠️ Не вдалося отримати факт. Спробуй пізніше.")


# Коли тисну кнопку: Хочу ще факт
@dp.callback_query(F.data == "more_fact")
async def more_fact(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await random_fact(callback.message, state)


# Коли тисну кнопку: Закінчити
@dp.callback_query(F.data == "end_random")
async def end_random(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await start(callback.message, state)


# Команда /gpt ------------------------------------------------------------------------------------------
@dp.message(Command("gpt"), StateFilter("*"))
async def start_gpt_mode(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(GPTMode.active)
    photo_path = "images/im2.jpg"
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo)
    else:
        await message.answer("🎲 зображення не знайдено")

    await message.answer("Привіт! Давай спілкуватись!\n Напиши своє запитання 👇")


@dp.message(GPTMode.active, F.text & ~F.text.startswith("/"))
async def chatgpt_command(message: types.Message, state: FSMContext):
    user_gpt_mode.add(message.from_user.id)  # додаю користувача у “режим GPT”
    await message.answer("💭 Думаю над відповіддю...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ти — дружній Telegram-асистент."},
                {"role": "user", "content": message.text}
            ]
        )
        answer = response.choices[0].message.content
        await message.answer(answer)

    except Exception as e:
        logging.error(f"Помилка OpenAI: {e}")
        await message.answer("⚠️ Сталася помилка при зверненні до ChatGPT. Перевір API ключ.")


# Команда /talk ------------------------------------------------------------------------------------------
@dp.message(Command("talk"), StateFilter("*"))
async def start_talk_mode(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(TALKMode.active)

    photo_path = "images/img3.jpg"
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo)
    else:
        await message.answer("🎲 зображення не знайдено")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍🎨 Тарас Шевченко", callback_data="talk_shevchenko")],
        [InlineKeyboardButton(text="🧠 Альберт Ейнштейн", callback_data="talk_einstein")],
        [InlineKeyboardButton(text="🚀 Ілон Маск", callback_data="talk_musk")],
        [InlineKeyboardButton(text="🦩 Клеопатра", callback_data="talk_cleopatra")]
    ])

    await message.answer("Привіт! Обери з ким спілкуватись!\n Тисни кнопку  👇", reply_markup=keyboard)


@dp.callback_query(F.data.startswith("talk_"))  # Обробка вибору особистості
async def select_person(callback: types.CallbackQuery, state: FSMContext):
    persona = callback.data.replace("talk_", "")
    user_talk_persona[callback.from_user.id] = persona

    names = {
        "shevchenko": "👨‍🎨 Тарас Шевченко",
        "einstein": "🧠 Альберт Ейнштейн",
        "musk": "🚀 Ілон Маск",
        "cleopatra": "🦩 Клеопатра"
    }

    PHOTO_PATHS = {
        "shevchenko": "images/shevchenko.jpg",
        "einstein": "images/einstein.jpg",
        "musk": "images/musk.jpg",
        "cleopatra": "images/cleopatra.jpg",
    }
    # Шлях до фото зі словника
    photo_path = PHOTO_PATHS.get(persona)

    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await callback.message.answer_photo(photo=photo, caption=f"Я {names[persona]}! Що тебе цікавить? Напиши тут 👇")
    else:
        await callback.message.answer(f"Я {names[persona]}! Що тебе цікавить? Напиши тут 👇")

    await callback.answer()


@dp.message(TALKMode.active, F.text & ~F.text.startswith("/"))  # Обробка повідомлень у режимі TALK
async def talk_mode(message: types.Message, state: FSMContext):
    persona = user_talk_persona.get(message.from_user.id, "невідомою особистістю")

    await message.answer(f"💭 {persona} думає над відповіддю...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"Ти зараз у ролі {persona}. "
                               f"Відповідай у стилі цієї особистості, доброзичливо і цікаво."
                },
                {"role": "user", "content": message.text}
            ]
        )
        answer = response.choices[0].message.content

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🏁 Закінчити", callback_data="end_talk"),
                ]
            ]
        )
        await message.answer(f"✨ {answer}", reply_markup=keyboard)

    except Exception as e:
        logging.error(f"Помилка OpenAI: {e}")
        await message.answer("⚠️ Сталася помилка при зверненні до ChatGPT.")


@dp.callback_query(F.data == "end_talk")
async def end_talk(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await start(callback.message, state)


# Команда /quiz ------------------------------------------------------------------------------------------
# Теми квізу
topic_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎬 Кіно та серіали", callback_data="quiz_movie")],
    [InlineKeyboardButton(text="🌍 Подорожі та географія", callback_data="quiz_travel")],
    [InlineKeyboardButton(text="🧠 Загальні знання", callback_data="quiz_knowledge")],
    [InlineKeyboardButton(text="🎵 Музика", callback_data="quiz_music")],
    [InlineKeyboardButton(text="🕹️ Попкультура та технології", callback_data="quiz_culture")]
])

# Кнопки після відповіді
next_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="➕ Ще питання", callback_data="next_question"),
        InlineKeyboardButton(text="🔄 Змінити тему", callback_data="change_topic"),
        InlineKeyboardButton(text="⏹ Завершити квіз", callback_data="end_quiz")
    ]
])


@dp.message(Command("quiz"), StateFilter("*"))
async def start_quiz(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(QUIZMode.active)

    photo_path = "images/img4.jpg"
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo)
    else:
        await message.answer("🎲 зображення не знайдено")

    await message.answer("🎯 Привіт! Обери тему квізу 👇", reply_markup=topic_keyboard)


@dp.callback_query(F.data.startswith("quiz_"))
async def choose_topic(callback: types.CallbackQuery, state: FSMContext):
    topic_map = {
        "quiz_movie": "Кіно та серіали",
        "quiz_travel": "Подорожі та географія",
        "quiz_knowledge": "Загальні знання",
        "quiz_music": "Музика",
        "quiz_culture": "Попкультура та технології"
    }

    topic_key = callback.data
    topic_name = topic_map.get(topic_key, "Загальні знання")

    await state.update_data(topic=topic_name, score=0, total_questions=0)
    await callback.message.answer(f"🧠 Обрано тему: {topic_name}")

    # Генеруємо перше питання
    await send_new_question(callback.message, state)


@dp.message(QUIZMode.active, ~F.text.startswith("/"))
async def handle_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if "current_question" not in data or data["current_question"] is None:
        return  # Якщо користувач не у квізі

    user_answer = message.text
    correct_answer = data["correct_answer"]
    question = data["current_question"]
    topic = data.get("topic")
    score = data.get("score", 0)
    total = data.get("total_questions", 0)

    # Перевірка відповіді через GPT
    check_prompt = (
        f"Ти — ведучий вікторини. "
        f"Питання: {question}\n"
        f"Правильна відповідь: {correct_answer}\n"
        f"Відповідь користувача: {user_answer}\n\n"
        f"Відповідай ТІЛЬКИ в одному рядку у форматі JSON, наприклад:\n"
        f'{{"correct": true, "explanation": "Так, це правильна відповідь, бо ..."}}\n'
        f"Або якщо відповідь неправильна:\n"
        f'{{"correct": false, "explanation": "Ні, правильна відповідь — ..."}}'
    )

    check_response = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": check_prompt}]
    )

    result_text = check_response.choices[0].message.content.strip()

    try:
        parsed = json.loads(result_text)
        is_correct = parsed.get("correct", False)
        explanation = parsed.get("explanation", "")
    except Exception:
        # Якщо GPT щось накосячив, просто виводжу текст
        is_correct = False
        explanation = result_text

    # Якщо GPT каже, що правильна

    if is_correct:
        score += 1

    await state.update_data(score=score)

    await message.answer(
        f"{explanation}\n\n"
        f"✅ Твій рахунок: {score} з {total} правильних ✅",
        reply_markup=next_keyboard
    )

    # Чищу питання (щоб бот не приймав ще відповіді)
    await state.update_data(current_question=None, correct_answer=None)


@dp.callback_query(F.data == "next_question")
async def next_question(callback: types.CallbackQuery, state: FSMContext):
    await send_new_question(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "change_topic")
async def change_topic(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("🔄 Обери нову тему:", reply_markup=topic_keyboard)
    await callback.answer()

@dp.callback_query(F.data == "end_quiz")
async def end_quiz(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        score = data.get("score", 0)
        total = data.get("total_questions", 0)

        # Надсилаю підсумок
        await callback.message.answer(
            f"🏁 Квіз завершено!\n\n"
            f"Твій фінальний результат: {score} з {total} правильних ✅"
        )
        # Очищую стан
        await state.clear()

        # Підтверджую callback
        await callback.answer()
        await start(callback.message, state)
    except Exception as e:
        # лог і відповідь користувачу на випадок помилки
        print("ERROR in end_quiz:", e)
        await callback.answer("Сталася помилка при завершенні. Спробуйте ще раз.", show_alert=True)

async def send_new_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    topic = data.get("topic", "Загальні знання")
    total = data.get("total_questions", 0) + 1  # ✅ додаємо 1

    prompt = (
        f"Створи одне питання вікторини українською мовою на тему '{topic}'. "
        f"У форматі: 'Питання: ... Відповідь: ...'"
    )
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content.strip()
    parts = text.split("Відповідь:")
    question = parts[0].replace("Питання:", "").strip()
    correct_answer = parts[1].strip() if len(parts) > 1 else "Невідомо"
    await state.update_data(current_question=question, correct_answer=correct_answer, total_questions=total)
    await message.answer(
        f"🧩 Питання:\n{question}\n\n"
        f"Напишіть вашу відповідь 👇"
    )

# Команда /translate ------------------------------------------------------------------------------------------
translate_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Англійська", callback_data="translate_english")],
        [InlineKeyboardButton(text="Французька", callback_data="translate_french")],
        [InlineKeyboardButton(text="Німецька", callback_data="translate_german")],
        [InlineKeyboardButton(text="Польська", callback_data="translate_polish")]
    ])

@dp.message(Command("translate"), StateFilter("*"))
async def start_translate_mode(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(TRANSLATEMode.active)

    print("Translate handler triggered!")

    photo_path = "images/img5.jpg"

    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo=photo)
    else:
        await message.answer("🎲 зображення не знайдено")

    await message.answer("Привіт! Обери мову перекладу!\n Тисни кнопку  👇", reply_markup=translate_keyboard)

# 🔹 Обробка натискання кнопки
@dp.callback_query(F.data.startswith("translate_"))
async def select_language(callback: types.CallbackQuery, state: FSMContext):
    language: str = callback.data.replace("translate_", "")
    await state.update_data(language=language)
    await state.set_state(TRANSLATEMode.active)
    user_talk_translator[callback.from_user.id] = language

    names = {
        "english": "🇬🇧 Англійська",
        "french": "🇫🇷 Французька",
        "german": "🇩🇪 Німецька",
        "polish": "🇵🇱 Польська"
    }
    lang_name = names.get(language, "🌍 Невідома мова")
    await callback.message.answer(f"🔤 Обрано мову перекладу: {lang_name}\n"
                                  f"Введи текст для перекладу 👇")
    await callback.answer()

@dp.message(TRANSLATEMode.active, F.text & ~F.text.startswith("/"))  # Обробка повідомлень у режимі TRANSLATE
async def translate_mode(message: types.Message, state: FSMContext):
    translator = user_talk_translator.get(message.from_user.id, "Перекладач")
    await message.answer(f"💭 {translator} думає над відповіддю...")
    # Отримую вибрану мову
    data = await state.get_data()
    lang = data.get("language", "english")
    # Текст для перекладу
    text = message.text
    # Виклик моделі GPT або перекладача
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Переклади цей текст українською ↔ {lang}: {text}"
            }]
        )
        translated_text = response.choices[0].message.content.strip()
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🏴󠁧󠁢󠁥󠁮󠁧󠁿 Змінити мову", callback_data="change_language"),
                    InlineKeyboardButton(text="🏁 Закінчити", callback_data="end_translate"),
                ]
            ]
        )
        await message.answer(
            f"🔤 Переклад ({lang}):\n{translated_text}",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Помилка OpenAI: {e}")
        await message.answer("⚠️ Сталася помилка при зверненні до ChatGPT.")

@dp.callback_query(F.data == "end_translate")
async def end_talk(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await start(callback.message, state)

@dp.callback_query(F.data == "change_language")
async def change_language(callback: types.CallbackQuery, state: FSMContext):

    await callback.message.answer("🔄 Обери нову мову:", reply_markup=translate_keyboard)
    await callback.answer()

# Команда /roll ------------------------------------------------------------------------------------------
@dp.message(Command("roll"), StateFilter("*"))
async def start_roll_mode(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(ROLLMode.active)

    dice = await bot.send_dice(chat_id=message.chat.id )
    result = dice.dice.value
    await asyncio.sleep(4)

    # Кнопки
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=" 🧊 ще одна спроба", callback_data="more_try"),
                InlineKeyboardButton(text="🏁 Закінчити", callback_data="end_roll"),
            ]
        ]
    )

    await message.answer(f"Твій результат: {result}", reply=False, reply_markup=keyboard)

@dp.callback_query(F.data == "more_try")
async def more_try(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_roll_mode(callback.message, state)

@dp.callback_query(F.data == "end_roll")
async def end_try(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await start(callback.message, state)


async def main():
    logging.info("🤖 Бот запущено!")
    print("bot")
    await set_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
