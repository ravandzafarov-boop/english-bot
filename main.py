import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Системный промпт для ИИ
SYSTEM_PROMPT = """
Ты — дружелюбный и умный помощник по изучению английского языка.
Твои задачи:
1. Исправлять ошибки в тексте пользователя и объяснять их простым языком.
2. Давать понятные объяснения грамматики.
3. Предлагать более естественные варианты фраз.
4. Если пользователь пишет на русском — помогать перевести и объяснить.
5. Отвечай кратко, четко и по делу. Используй эмодзи для удобства.
Всегда отвечай на русском, если пользователь пишет на русском, кроме примеров на английском.
"""

class ChatState(StatesGroup):
    waiting = State()

@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! 👋 Я твой помощник по английскому.\n\n"
        "Просто напиши мне:\n"
        "• Текст на английском — я исправлю и объясню ошибки\n"
        "• Вопрос по грамматике\n"
        "• Фразу, которую хочешь сказать красиво\n\n"
        "Напиши что-нибудь!"
    )

@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "Как пользоваться ботом:\n\n"
        "1. Отправь любое предложение на английском — я исправлю\n"
        "2. Спроси правило грамматики\n"
        "3. Попроси перевести или перефразировать\n"
        "4. Можно просто общаться на английском\n\n"
        "Гамид иди нахуй пожалуйста\n\n"
        "Команды:\n"
        "/start — начать заново\n"
        "/help — эта справка"
    )

@dp.message(F.text)
async def handle_message(message: Message, state: FSMContext):
    user_text = message.text

    # Показываем, что бот думает
    thinking = await message.answer("Думаю... 🤔")

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",        # можно заменить на gpt-4o
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=800
        )

        answer = response.choices[0].message.content
        await thinking.edit_text(answer)

    except Exception as e:
        await thinking.edit_text(f"Произошла ошибка 😔\n{str(e)}")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())