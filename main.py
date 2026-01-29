import asyncio
import time
import os
from aiogram import Bot, Dispatcher, types, F

# Токен берем из секретов GitHub (BOT_TOKEN)
TOKEN = '7948707539:AAHKky9CjUz-T-9zI43bvQ1by5JTe1VlV2Y'
ADMIN_IDS = [1087968824, 7978414708]

# Корни матов
BAD_WORDS = [
    'хуй', 'хуя', 'хуе', 'хуи', 'пизд', 'еба', 'ебл', 'сука', 'бля',
    'жоп', 'говно', 'гавн', 'какаш', 'деби', 'лош', 'чмо', 'арбуз', 'тест', 'поп'
]

# ТВОЙ РАСШИРЕННЫЙ БЕЛЫЙ СПИСОК
EXCEPTIONS = [
    # Слова на "лош"
    'лошадь', 'лошади', 'лошадка', 'лошадиный', 'оплошность', 'площадь', 'ложка', 'ложный',
    # Слова на "поп"
    'популярный', 'попугай', 'попкорн', 'попробовать', 'поправка', 'подпись', 'пополам', 'попутно', 'попса', 'пополнение', 'поприще',
    # Слова на "сук"
    'сукно', 'суккулент', 'рассудок', 'рассуждать', 'рисунок', 'несушка', 'посуда',
    # Слова на "еб"
    'хлеб', 'учеба', 'лебедь', 'жеребец', 'гребень', 'серебро', 'небо', 'небылица',
    # Слова на "хуи" / "хуе"
    'художник', 'художество', 'худеть', 'худой'
]

# Замены для обхода (чтобы не писали 0место вместо оместо)
REPLACEMENTS = {'0': 'о', '1': 'и', '3': 'е', '4': 'ч', '5': 'с', '6': 'б', '9': 'я', '@': 'а', '$': 'с'}

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_warns = {}

def normalize_text(text):
    text = text.lower()
    for char, replacement in REPLACEMENTS.items():
        text = text.replace(char, replacement)
    # Оставляем только буквы
    return "".join(c for c in text if c.isalpha())

@dp.message(F.text)
async def filter_logic(message: types.Message):
    if message.from_user.id in ADMIN_IDS or message.from_user.is_bot: 
        return

    words = message.text.lower().split()
    found_bad = False

    for word in words:
        # Убираем лишние знаки типа "сука!!!" -> "сука"
        clean_word = "".join(c for c in word if c.isalpha())

        # 1. Если слово целиком в белом списке — пропускаем
        if clean_word in EXCEPTIONS: continue

        # 2. Если длинное слово начинается на исключение (популярность) — пропускаем
        if any(clean_word.startswith(ex) for ex in EXCEPTIONS if len(ex) > 3): continue

        normalized = normalize_text(word)

        # 3. Проверка на мат по корням
        for bad in BAD_WORDS:
            if bad in normalized:
                # Дополнительная проверка, чтобы корень мата не был частью слова-исключения
                if not any(ex in normalized for ex in EXCEPTIONS):
                    found_bad = True
                    break
        if found_bad: break

    if found_bad:
        uid = message.from_user.id
        user_warns[uid] = user_warns.get(uid, 0) + 1
        
        try: await message.delete()
        except: pass

        if user_warns[uid] >= 3:
            user_warns[uid] = 0
            try:
                # Мут на 3 часа (10800 сек)
                await bot.restrict_chat_member(
                    message.chat.id, uid,
                    permissions=types.ChatPermissions(can_send_messages=False),
                    until_date=int(time.time()) + 10800
                )
                await message.answer(f"🤐 {message.from_user.first_name} в муте (3/3 варна).")
            except: pass
        else:
            await message.answer(f"⚠️ {message.from_user.first_name}, без мата! ({user_warns[uid]}/3)")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
