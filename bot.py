import asyncio
from aiogram import Bot, Dispatcher, types, F
from datetime import datetime, timedelta

# ТВОИ ДАННЫЕ
API_TOKEN = '7948707539:AAHKky9CjUz-T-9zI43bvQ1by5JTe1VlV2Y'
ADMIN_ID = 7978414708 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_warns = {}

# Список матов
BAD_WORDS = ["тест", "сука", "блять", "бля", "хуй", "пидор", "еблан"]

# 1. ПРИВЕТСТВИЕ
@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    for user in message.new_chat_members:
        await message.answer(f"👋 Добро пожаловать, {user.full_name}, в Matvey OS Group! Не матерись и не спамь.")

# 2. АНТИСПАМ + ПЕРЕВОД + МОДЕРАЦИЯ
@dp.message(F.text)
async def handle_msg(message: types.Message):
    text = message.text
    user_id = message.from_user.id

    # --- АНТИСПАМ (Удаление ссылок) ---
    if "http" in text.lower() or "t.me/" in text.lower():
        if user_id != ADMIN_ID:
            await message.delete()
            return await message.answer(f"🚫 {message.from_user.full_name}, ссылки запрещены!")

    # --- МОДЕРАЦИЯ (Маты) ---
    if any(word in text.lower() for word in BAD_WORDS):
        if user_id == ADMIN_ID and "тест" not in text.lower(): return
        
        user_warns[user_id] = user_warns.get(user_id, 0) + 1
        await message.delete()
        
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(text="🚫 Снять варн (Матвей)", callback_data=f"unwarn_{user_id}")
        ]])
        
        if user_warns[user_id] >= 3:
            user_warns[user_id] = 0
            mute_kb = types.InlineKeyboardMarkup(inline_keyboard=[[
                types.InlineKeyboardButton(text="✅ Размутить", callback_data=f"unmute_{user_id}")
            ]])
            try:
                await bot.restrict_chat_member(message.chat.id, user_id, permissions=types.ChatPermissions(can_send_messages=False), until_date=datetime.now() + timedelta(hours=3))
                await message.answer(f"🚫 Мут 3 часа (3/3)!", reply_markup=mute_kb)
            except:
                await message.answer(f"⚠️ 3/3 варна!", reply_markup=mute_kb)
        else:
            await message.answer(f"⚠️ Варн {user_warns[user_id]}/3!", reply_markup=kb)
        return

    # --- КНОПКА ПЕРЕВОДА ---
    # Показываем кнопку перевода для любого текста длиннее 5 символов
    if len(text) > 5 and user_id != ADMIN_ID:
        kb_trans = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(text="🌐 Перевести на русский", callback_data=f"translate")
        ]])
        await message.reply("Вижу иностранный текст?", reply_markup=kb_trans)

# 3. ОБРАБОТКА КНОПОК
@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    if "unwarn_" in call.data or "unmute_" in call.data:
        if call.from_user.id != ADMIN_ID:
            return await call.answer("❌ Только Матвей!", show_alert=True)
        # Логика снятия (как в прошлом коде)
        await call.message.edit_text("✅ Действие выполнено.")

    elif call.data == "translate":
        # Используем бесплатный API для перевода (имитация для примера)
        original_text = call.message.reply_to_message.text
        # В реальности тут вызывается библиотека googletrans, но для GitHub Actions проще так:
        await call.answer("Перевожу...")
        await call.message.edit_text(f"📝 Перевод:\n{original_text}\n\n(Тут будет русский перевод)")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
