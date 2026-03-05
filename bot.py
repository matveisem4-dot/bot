import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from datetime import datetime, timedelta

# ТВОИ ДАННЫЕ
API_TOKEN = '7948707539:AAHKky9CjUz-T-9zI43bvQ1by5JTe1VlV2Y'
ADMIN_ID = 7978414708 

# ОГРОМНЫЙ СПИСОК СЛОВ (включая "тест")
BAD_WORDS_LIST = [
    "тест", "сука", "блять", "бля", "хуй", "пидор", "гандон", "еблан", 
    "уебок", "пизда", "хер", "шлюха", "тварь", "мразь", "долбоеб",
    "мудак", "говно", "залупа", "дрочила", "пидорас", "сучка"
    # Бот также будет искать эти слова внутри других слов
]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_warns = {} 

@dp.message(F.text)
async def handle_msg(message: types.Message):
    # Тебя бот НИКОГДА не трогает и не удаляет твои сообщения
    if message.from_user.id == ADMIN_ID:
        return
    
    text = message.text.lower()
    
    # Проверка: есть ли хоть одно плохое слово в сообщении
    is_bad = any(re.search(rf"\b{word}\b", text) or word in text for word in BAD_WORDS_LIST)

    if is_bad:
        uid = message.from_user.id
        user_warns[uid] = user_warns.get(uid, 0) + 1
        
        try:
            await message.delete() # Удаляем плохое слово
        except:
            pass # Если нет прав на удаление

        if user_warns[uid] >= 3:
            # МУТ НА 3 ЧАСА (3 предупреждения)
            until = datetime.now() + timedelta(hours=3)
            await bot.restrict_chat_member(
                message.chat.id, uid, 
                permissions=types.ChatPermissions(can_send_messages=False), 
                until_date=until
            )
            user_warns[uid] = 0
            
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[
                types.InlineKeyboardButton(text="✅ Размутить (Матвей)", callback_data=f"un_{uid}")
            ]])
            await message.answer(
                f"🚫 {message.from_user.full_name} замучен на 3 часа за маты (3/3)!", 
                reply_markup=kb
            )
        else:
            await message.answer(
                f"⚠️ {message.from_user.full_name}, предупреждение {user_warns[uid]}/3! "
                f"Слово '{text}' запрещено."
            )

@dp.callback_query(F.data.startswith("un_"))
async def unmute(call: types.CallbackQuery):
    # ПРОВЕРКА: только ты (ID 7978414708) можешь нажать
    if call.from_user.id != ADMIN_ID:
        return await call.answer("❌ Ты не Матвей! Только хозяин размучивает.", show_alert=True)
    
    uid = int(call.data.split("_")[1])
    await bot.restrict_chat_member(
        call.message.chat.id, uid, 
        permissions=types.ChatPermissions(
            can_send_messages=True, 
            can_send_media_messages=True, 
            can_send_other_messages=True
        )
    )
    await call.message.edit_text("✅ Пользователь размучен администратором.")

async def main():
    print(f"Бот Matvey OS активен! Админ ID: {ADMIN_ID}")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
