import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from datetime import datetime, timedelta
from googletrans import Translator

# ТВОИ ДАННЫЕ (Будь осторожен с токеном, не свети его в паблике!)
API_TOKEN = '7948707539:AAHKky9CjUz-T-9zI43bvQ1by5JTe1VlV2Y'
ADMIN_ID = 7978414708 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
translator = Translator()
user_warns = {}

# РАСШИРЕННЫЙ СПИСОК (Добавлены основные корни и вариации)
BAD_WORDS_PATTERN = r"(сук[а-я]|блять|бля|хуй|пид[оа]р|ебл[а-я]|муд[а-я]|хуя|пизд[а-я]|г[оа]вн[оа]|чмо|ублюд|сучк)"

# Функция проверки: есть ли в тексте НЕ русские буквы?
def is_foreign(text):
    # Убираем цифры, смайлы и знаки препинания
    clean_text = re.sub(r'[^a-zA-Zа-яА-ЯёЁ\s]', '', text)
    # Если есть латиница
    has_latin = bool(re.search(r'[a-zA-Z]', text))
    # Проверка на иероглифы/арабский
    has_strange_chars = bool(re.search(r'[^\u0000-\u007F\u0400-\u04FF]', text))
    return has_latin or has_strange_chars

@dp.message(F.text)
async def handle_msg(message: types.Message):
    text = message.text.lower()
    user_id = message.from_user.id

    # 1. МОДЕРАЦИЯ (МАТЫ ЧЕРЕЗ РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ)
    # Это ловит "сука", "сучки", "суку" и т.д. одной проверкой
    if re.search(BAD_WORDS_PATTERN, text):
        if user_id == ADMIN_ID and "тест" not in text: 
            return
            
        user_warns[user_id] = user_warns.get(user_id, 0) + 1
        
        try:
            await message.delete()
        except Exception:
            pass # Если нет прав на удаление

        kb = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(text="🚫 Снять варн (Admin)", callback_data=f"unwarn_{user_id}")
        ]])
        
        await message.answer(
            f"⚠️ **Нарушение правил чата!**\n"
            f"Пользователь: ID {user_id}\n"
            f"Предупреждения: {user_warns[user_id]}/3\n"
            f"Причина: Нецензурная лексика",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        
        if user_warns[user_id] >= 3:
            # Тут можно добавить логику бана
            await message.answer(f"🚫 Пользователь {user_id} достиг лимита варнов.")
        return

    # 2. АНТИСПАМ
    if "http" in text or "t.me/" in text:
        if user_id != ADMIN_ID:
            await message.delete()
            return

    # 3. КНОПКА ПЕРЕВОДА
    if is_foreign(text) and len(text) > 2:
        kb_trans = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(text="🌐 Перевести на русский", callback_data="translate")
        ]])
        await message.reply("☁️ **Aria OS:** Обнаружен иностранный язык", reply_markup=kb_trans, parse_mode="Markdown")

@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    if "unwarn_" in call.data:
        if call.from_user.id != ADMIN_ID:
            return await call.answer("❌ У вас нет прав администратора Galaxy Ultra", show_alert=True)
        
        user_to_unwarn = int(call.data.split("_")[1])
        user_warns[user_to_unwarn] = 0
        await call.message.edit_text(f"✅ Варны пользователя {user_to_unwarn} обнулены.")

    elif call.data == "translate":
        await call.answer("Перевожу через систему Aria...")
        try:
            target_text = call.message.reply_to_message.text
            result = translator.translate(target_text, dest='ru')
            await call.message.edit_text(
                f"📝 **Перевод:**\n`{result.text}`\n\n"
                f"**Язык:** {result.src.upper()}", 
                parse_mode="Markdown"
            )
        except Exception as e:
            await call.message.edit_text("❌ Ошибка перевода. Возможно, текст слишком короткий или защищен.")

async def main():
    print("--- Бот Aria OS запущен и фильтрует маты ---")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
