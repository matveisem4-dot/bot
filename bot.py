import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from datetime import datetime, timedelta
from googletrans import Translator

# ТВОИ ДАННЫЕ
API_TOKEN = '7948707539:AAHKky9CjUz-T-9zI43bvQ1by5JTe1VlV2Y'
ADMIN_ID = 7978414708 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
translator = Translator()
user_warns = {}

BAD_WORDS = ["тест", "сука", "блять", "бля", "хуй", "пидор", "еблан"]

# Функция проверки: есть ли в тексте НЕ русские буквы?
def is_foreign(text):
    # Убираем цифры, смайлы и знаки препинания
    clean_text = re.sub(r'[^a-zA-Zа-яА-ЯёЁ\s]', '', text)
    # Если есть латиница или полное отсутствие кириллицы в длинном тексте
    has_latin = bool(re.search(r'[a-zA-Z]', text))
    # Проверка на иероглифы/арабский (любые символы вне кириллицы и латиницы)
    has_strange_chars = bool(re.search(r'[^\u0000-\u007F\u0400-\u04FF]', text))
    return has_latin or has_strange_chars

@dp.message(F.text)
async def handle_msg(message: types.Message):
    text = message.text
    user_id = message.from_user.id

    # 1. МОДЕРАЦИЯ (МАТЫ)
    if any(word in text.lower() for word in BAD_WORDS):
        if user_id == ADMIN_ID and "тест" not in text.lower(): return
        user_warns[user_id] = user_warns.get(user_id, 0) + 1
        await message.delete()
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="🚫 Снять варн", callback_data=f"unwarn_{user_id}")]])
        await message.answer(f"⚠️ Предупреждение: {user_warns[user_id]}/3", reply_markup=kb)
        return

    # 2. АНТИСПАМ
    if "http" in text.lower() or "t.me/" in text.lower():
        if user_id != ADMIN_ID:
            await message.delete()
            return

    # 3. КНОПКА ПЕРЕВОДА (Для любого иностранного языка)
    if is_foreign(text) and len(text) > 2:
        kb_trans = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(text="🌐 Перевести на русский", callback_data="translate")
        ]])
        await message.reply("Обнаружен иностранный язык", reply_markup=kb_trans)

@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    if "unwarn_" in call.data or "unmute_" in call.data:
        if call.from_user.id != ADMIN_ID:
            return await call.answer("❌ Нет прав", show_alert=True)
        # Логика снятия варна...
        await call.message.edit_text("✅ Изменено.")

    elif call.data == "translate":
        await call.answer("Перевожу...")
        try:
            # Берем текст из сообщения, на которое ответил бот
            target_text = call.message.reply_to_message.text
            result = translator.translate(target_text, dest='ru')
            await call.message.edit_text(f"📝 **Перевод:**\n{result.text}\n\n(Определен язык: {result.src})", parse_mode="Markdown")
        except Exception as e:
            await call.message.edit_text("❌ Не удалось перевести. Попробуйте позже.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
