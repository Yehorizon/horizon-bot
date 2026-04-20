import os
import asyncio
import datetime
from datetime import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

START_DATE = datetime.date(2026, 4, 20)

# ================================
# 7 ТЕМ + РІВНІ
# ================================

WEEKLY_THEMES = {
    0: {"theme": "Я і моє життя", "emoji": "👤"},
    1: {"theme": "Плани і обов'язки", "emoji": "📋"},
    2: {"theme": "Місто і транспорт", "emoji": "🏙️"},
    3: {"theme": "Запитання і відповіді", "emoji": "❓"},
    4: {"theme": "Минуле", "emoji": "⏳"},
    5: {"theme": "Складні думки", "emoji": "🧠"},
    6: {"theme": "Контраст і повторення", "emoji": "🔄"},
}

LEVEL_CONFIG = {
    0: {
        "label": "A2",
        "description": "Базовий рівень A2. Прості речення, основна граматика, повсякденна лексика.",
        "grammar_focus": "Präsens, Modalverben, Akkusativ, Perfekt — базове використання.",
        "word_count": 10,
        "sentence_count": 10,
    },
    1: {
        "label": "A2+",
        "description": "Рівень A2+. Складніші конструкції, більше сполучників, розширена лексика.",
        "grammar_focus": "weil, obwohl, dass, sowohl...als auch, Perfekt + Präteritum.",
        "word_count": 10,
        "sentence_count": 12,
    },
    2: {
        "label": "B1",
        "description": "Рівень B1. Складний синтаксис, аргументація, офіційна і розмовна мова.",
        "grammar_focus": "Konjunktiv II, Relativsätze, Plusquamperfekt, складна аргументація.",
        "word_count": 10,
        "sentence_count": 15,
    },
}


def get_level(day: int) -> int:
    if day < 30:
        return 0
    elif day < 90:
        return 1
    else:
        return 2


def generate_lesson(theme: str, emoji: str, level: dict, day: int) -> tuple[str, str, str]:
    """Генерує 3 повідомлення уроку через Claude API."""

    today = datetime.date.today().strftime('%A, %d.%m.%Y')

    system_prompt = """Ти — досвідчений викладач німецької мови для українців.
Ти генеруєш щоденні уроки для студента який вчить німецьку в Німеччині.
Відповідай ТІЛЬКИ у вказаному форматі. Без зайвих коментарів.
Пояснення — українською. Приклади — німецькою з українським перекладом."""

    user_prompt = f"""Згенеруй урок німецької мови.

ТЕМА ДНЯ: {theme}
РІВЕНЬ: {level['label']} — {level['description']}
ГРАМАТИЧНИЙ ФОКУС: {level['grammar_focus']}
ДЕНЬ НАВЧАННЯ: {day + 1}
ДАТА: {today}

Згенеруй РІВНО 3 блоки — розділені рядком ===BLOCK===

БЛОК 1 — СЛОВА (повідомлення 1):
Формат:
{emoji} ДЕНЬ {day + 1} [{level['label']}] — {theme}
{datetime.date.today().strftime('%d.%m.%Y')}
{'─' * 30}

📚 СЛОВА — {theme}

[{level['word_count']} слів пов'язаних з темою "{theme}"]
Формат кожного слова:
N. слово — переклад
   📌 Приклад речення німецькою. — Переклад українською.

{'─' * 30}
💡 Порада: [корисна порада про одне зі слів або типову помилку]

🔁 Повтори кожне слово вголос 3 рази!

===BLOCK===

БЛОК 2 — ГРАМАТИКА (повідомлення 2):
Формат:
📝 ГРАМАТИКА — [назва теми]

{'─' * 30}

[Детальне пояснення граматики пов'язаної з темою "{theme}" на рівні {level['label']}]
Включи:
- Пояснення правила українською
- Схему або таблицю
- 3-4 приклади з перекладом
- Типові помилки (❌ → ✅)

{'─' * 30}

ЗАВДАННЯ 1 — [назва]
[5 вправ з пропусками або трансформаціями]
✅ Відповіді: [відповіді]

ЗАВДАННЯ 2 — [назва]
[Завдання на написання {level['sentence_count']} речень]

ЗАВДАННЯ 3 — [переклад або творче завдання]
[5 речень для перекладу з української на німецьку]
✅ Відповіді: [відповіді]

===BLOCK===

БЛОК 3 — ПРАКТИКА (повідомлення 3):
Формат:
💬 ПРАКТИКА — {theme}

{'─' * 30}

🗣️ ГОВОРІННЯ — 60 хв

[Конкретні інструкції для говоріння по темі "{theme}"]
[5-6 питань з підказками як відповідати]

{'─' * 30}

✍️ ПИСЬМО — 30 хв

[Назва тексту для написання]
[Чітка структура — скільки речень, що включити]

{'─' * 30}

🧠 Цікавий факт: [цікавий факт про німецьку мову або культуру пов'язаний з темою]

{'─' * 30}
Viel Erfolg heute! 💪🇩🇪"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        system=system_prompt,
    )

    full_text = response.content[0].text
    blocks = full_text.split("===BLOCK===")

    msg1 = blocks[0].strip() if len(blocks) > 0 else "Помилка генерації блоку 1."
    msg2 = blocks[1].strip() if len(blocks) > 1 else "Помилка генерації блоку 2."
    msg3 = blocks[2].strip() if len(blocks) > 2 else "Помилка генерації блоку 3."

    return msg1, msg2, msg3


async def send_long(bot, text: str):
    if len(text) <= 4096:
        await bot.send_message(chat_id=CHANNEL_ID, text=text)
    else:
        for chunk in [text[i:i+4096] for i in range(0, len(text), 4096)]:
            await bot.send_message(chat_id=CHANNEL_ID, text=chunk)
            await asyncio.sleep(0.5)


async def post_german(context):
    day = max(0, (datetime.date.today() - START_DATE).days)
    weekday = day % 7
    level_idx = get_level(day)

    theme_data = WEEKLY_THEMES[weekday]
    level = LEVEL_CONFIG[level_idx]

    theme = theme_data["theme"]
    emoji = theme_data["emoji"]

    try:
        msg1, msg2, msg3 = await asyncio.get_event_loop().run_in_executor(
            None, generate_lesson, theme, emoji, level, day
        )

        await send_long(context.bot, msg1)
        await asyncio.sleep(1)
        await send_long(context.bot, msg2)
        await asyncio.sleep(1)
        await send_long(context.bot, msg3)

    except Exception as e:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"⚠️ Помилка генерації уроку: {e}"
        )


async def german(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('⏳ Генерую урок через Claude... (~10 сек)')
    await post_german(context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        '🇩🇪 НІМЕЦЬКА — Щоденні уроки\n\n'
        'Щодня о 13:00 — 3 повідомлення:\n'
        '📚 Слова з прикладами\n'
        '📝 Граматика з завданнями\n'
        '💬 Говоріння і письмо\n\n'
        '7 тем — кожного дня нові завдання!\n\n'
        'Місяць 1 — A2\n'
        'Місяці 2-3 — A2+\n'
        'Місяці 4-6 — B1\n\n'
        '/german — отримати урок зараз'
    )
    await update.message.reply_text(msg)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('german', german))
    # 13:00 CET = 11:00 UTC (літо)
    app.job_queue.run_daily(post_german, time=time(hour=11, minute=0))
    print('Бот запущено')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
