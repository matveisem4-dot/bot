import asyncio
from aiogram import Bot, Dispatcher, types, F
from datetime import datetime, timedelta

# ТВОИ ДАННЫЕ
API_TOKEN = '7948707539:AAHKky9CjUz-T-9zI43bvQ1by5JTe1VlV2Y'
ADMIN_ID = 7978414708 

# Список плохих слов
BAD_WORDS = ["тест", "сука", "блять", "бля", "хуй", "пидор", "еблан"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_warns = {} 

@dp.message(F.text)
async def handle_msg(message: types.Message):
    text = message.text.lower()
    user_id = message.from_user.id
    
    # Проверка на наличие плохого слова
    if any(word in text for word in BAD_WORDS):
        # Если админ пишет "тест" — наказываем для проверки, если маты — игнорим
        if user_id == ADMIN_ID and "тест" not in text:
            return

        user_warns[user_id] = user_warns.get(user_id, 0) + 1
        
        try:
            await message.delete() # Удаляем сообщение с матом
        except:
            pass

        # Создаем кнопку для снятия варна
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[
            types.InlineKeyboardButton(text="🚫 Снять варн (Админ)", callback_data=f"unwarn_{user_id}")
        ]])

        if user_warns[user_id] >= 3:
            # Если 3/3 — мутим и даем кнопку размута
            until = datetime.now() + timedelta(hours=3)
            user_warns[user_id] = 0
            
            mute_kb = types.InlineKeyboardMarkup(inline_keyboard=[[
                types.InlineKeyboardButton(text="✅ Размутить (Матвей)", callback_data=f"unmute_{user_id}")
            ]])

            try:
                await bot.restrict_chat_member(message.chat.id, user_id, 
                    permissions=types.ChatPermissions(can_send_messages=False), until_date=until)
                await message.answer(f"🚫 {message.from_user.full_name} замучен на 3 часа (3/3 варнов)!", reply_markup=mute_kb)
            except:
                await message.answer(f"⚠️ {message.from_user.full_name}, варны 3/3! (Не могу замутить админа)", reply_markup=mute_kb)
        else:
            # Просто варн с кнопкой "Снять"
            # Важно: здесь мы НЕ пишем само слово 'text', как ты и просил
            await message.answer(
                f"⚠️ {message.from_user.full_name}, тебе выдан варн! Всего: {user_warns[user_id]}/3. Не нарушай правила.", 
                reply_markup=kb
            )

# Обработка кнопок (Снять варн и Размутить)
@dp.callback_query(F.data.startswith("unwarn_") | F.data.startswith("unmute_"))
async def handle_buttons(call: types.CallbackQuery):
    # Проверка прав (только ты можешь нажать)
    if call.from_user.id != ADMIN_ID:
        return await call.answer("❌ У тебя нет прав админа (Матвея)!", show_alert=True)
    
    action, uid = call.data.split("_")
    uid = int(uid)

    if action == "unwarn":
        if uid in user_warns and user_warns[uid] > 0:
            user_warns[uid] -= 1
        await call.message.edit_text(f"✅ Варн снят! Текущий счет пользователя: {user_warns.get(uid, 0)}/3")
    
    elif action == "unmute":
        try:
            await bot.restrict_chat_member(call.message.chat.id, uid, 
                permissions=types.ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
        except: pass
        await call.message.edit_text("✅ Пользователь размучен!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
