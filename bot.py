import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from datetime import datetime, timedelta

# ТВОИ ДАННЫЕ
API_TOKEN = '7948707539:AAHKky9CjUz-T-9zI43bvQ1by5JTe1VlV2Y'
ADMIN_ID = 7978414708 

# Список плохих слов
BAD_WORDS_LIST = [
    "сука", "блять", "бля", "хуй", "пидор", "гандон", "еблан", 
    "уебок", "пизда", "хер", "шлюха", "тварь", "мразь", "долбоеб",
    "мудак", "говно", "залупа", "дрочила", "пидорас", "сучка", "пиздец",
    "хуесос", "шалава", "курва", "гондон", "блядина", "выродок"
]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_warns = {} 

@dp.message(F.text)
async def handle_msg(message: types.Message):
    text = message.text.lower()
    user_id = message.from_user.id
    
    # ПРОВЕРКА НА СЛОВО "ТЕСТ" (Работает для всех, даже для тебя!)
    if "тест" in text:
        is_bad = True
    # ПРОВЕРКА НА МАТЫ (Для тебя - игнор, для других - бан)
    elif any(word in text for word in BAD_WORDS_LIST):
        if user_id == ADMIN_ID:
            return # Тебя за маты не трогаем
        is_bad = True
    else:
        is_bad = False

    if is_bad:
        user_warns[user_id] = user_warns.get(user_id, 0) + 1
        
        try:
            await message.delete()
        except:
            print("Ошибка: Сделай бота админом в группе!")

        if user_warns[user_id] >= 3:
            # МУТ НА 3 ЧАСА
            until = datetime.now() + timedelta(hours=3)
            try:
                await bot.restrict_chat_member(
                    message.chat.id, user_id, 
                    permissions=types.ChatPermissions(can_send_messages=False), 
                    until_date=until
                )
                user_warns[user_id] = 0
                
                kb = types.InlineKeyboardMarkup(inline_keyboard=[[
                    types.InlineKeyboardButton(text="✅ Размутить (Матвей)", callback_data=f"un_{user_id}")
                ]])
                await message.answer(f"🚫 Мут на 3 часа за проверку/маты (3/3)!", reply_markup=kb)
            except:
                await message.answer(f"⚠️ {message.from_user.full_name}, я бы тебя замутил, но ты Админ группы! (3/3)")
        else:
            await message.answer(f"⚠️ Предупреждение {user_warns[user_id]}/3! (Сработало на: {text})")

@dp.callback_query(F.data.startswith("un_"))
async def unmute(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return await call.answer("❌ Только Матвей решает!", show_alert=True)
    
    uid = int(call.data.split("_")[1])
    await bot.restrict_chat_member(
        call.message.chat.id, uid, 
        permissions=types.ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
    )
    await call.message.edit_text("✅ Размучен!")

async def main():
    print("Бот запущен! Тестируй словом 'тест'.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
