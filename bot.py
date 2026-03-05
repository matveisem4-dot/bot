import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from datetime import datetime, timedelta

# Получаем данные из секретов GitHub
API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID')) if os.getenv('ADMIN_ID') else 0
BAD_WORDS = ["мат1", "мат2", "плохоеслово"] # Добавь свои через запятую

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_warns = {} # На GitHub Actions варны сбрасываются при перезапуске

@dp.message(F.text)
async def handle_msg(message: types.Message):
    if message.from_user.id == ADMIN_ID: return
    
    text = message.text.lower()
    if any(word in text for word in BAD_WORDS):
        uid = message.from_user.id
        user_warns[uid] = user_warns.get(uid, 0) + 1
        await message.delete()
        
        if user_warns[uid] >= 3:
            until = datetime.now() + timedelta(hours=3)
            await bot.restrict_chat_member(message.chat.id, uid, 
                permissions=types.ChatPermissions(can_send_messages=False), until_date=until)
            user_warns[uid] = 0
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[
                types.InlineKeyboardButton(text="✅ Размутить (Матвей)", callback_data=f"un_{uid}")
            ]])
            await message.answer(f"🚫 {message.from_user.full_name} в муте на 3 часа (3/3)!", reply_markup=kb)
        else:
            await message.answer(f"⚠️ {message.from_user.full_name}, предупреждение {user_warns[uid]}/3!")

@dp.callback_query(F.data.startswith("un_"))
async def unmute(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return await call.answer("❌ Доступ запрещен!", show_alert=True)
    
    uid = int(call.data.split("_")[1])
    await bot.restrict_chat_member(call.message.chat.id, uid, 
        permissions=types.ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
    await call.message.edit_text("✅ Пользователь размучен!")

async def main():
    print("Бот Matvey OS запущен в облаке!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
