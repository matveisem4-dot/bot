import asyncio
from aiogram import Bot, Dispatcher, types, F
from datetime import datetime, timedelta

# ТВОИ ДАННЫЕ (ПРОВЕРЕНО)
API_TOKEN = '7948707539:AAHKky9CjUz-T-9zI43bvQ1by5JTe1VlV2Y'
ADMIN_ID = 7978414708 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_warns = {} 

# Команда для проверки: напиши /start в группе
@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer("🤖 Бот Matvey OS активен и готов банить за 'тест'!")

@dp.message(F.text)
async def handle_msg(message: types.Message):
    text = message.text.lower()
    user_id = message.from_user.id
    
    # Реакция на слово "тест" (для всех)
    if "тест" in text:
        user_warns[user_id] = user_warns.get(user_id, 0) + 1
        
        try:
            await message.delete() # Пытаемся удалить
        except:
            await message.answer("❌ Ошибка: Сделай меня АДМИНОМ группы!")
            return

        if user_warns[user_id] >= 3:
            user_warns[user_id] = 0
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[
                types.InlineKeyboardButton(text="✅ Размутить (Матвей)", callback_data=f"un_{user_id}")
            ]])
            await message.answer(f"🚫 Мут за тесты (3/3)!", reply_markup=kb)
        else:
            await message.answer(f"⚠️ Варн {user_warns[user_id]}/3 за слово 'тест'!")

@dp.callback_query(F.data.startswith("un_"))
async def unmute(call: types.CallbackQuery):
    if call.from_user.id == ADMIN_ID:
        await call.message.edit_text("✅ Размучено!")
    else:
        await call.answer("❌ Только Матвей!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
