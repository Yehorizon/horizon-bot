import os
import asyncio
import re
from datetime import time, datetime
import anthropic
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

THEMES = {
    0: ('Переговори та дипломатія', '🤝'),
    1: ('Держбудівництво та інституції', '🏛'),
    2: ('Геополітика та альянси', '🌍'),
    3: ('Економіка як інструмент влади', '📊'),
    4: ('Історичні уроки та стратегія', '📜'),
    5: ('Лідерство та прийняття рішень', '⚡️'),
    6: ('Найважливіше за тиждень', '🔭'),
}

DAYS = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя']

MAX_CONTENT_LENGTH = 3600


def build_prompt(theme_name: str) -> str:
    today = datetime.now().strftime('%d.%m.%Y')
    return f"""Ти — експерт з геополітики та державного управління. Пишеш для амбітної людини, яка прагне стати політиком або дипломатом.

Сьогодні {today}. Тема дня: {theme_name}.

Знайди 10 найважливіших реальних новин і подій СЬОГОДНІ на тему "{theme_name}" з усього світу.

Формат відповіді:

10 ІНСАЙТІВ ДНЯ
(кожен інсайт — це не переказ новини, а думка або висновок з неї)

1. [1-2 речення — стислий інсайт з конкретною подією, іменем або цифрою]
2. [те саме]
...і так до 10.

Кожен інсайт має бути:
- Конкретним: реальна подія, країна, особа, цифра
- Стислим: максимум 2-3 речення
- Корисним: не просто факт, а думка або висновок з нього

Потім з нового рядка:

ПИТАННЯ ДНЯ
1. [Питання для роздумів і самоаналізу читача — пов'язане з темою дня]
2. [Друге питання]

Суворі правила:
- Лише українська мова — жодних іноземних слів без перекладу, жодних технічних символів
- Жодних китайських, японських або інших нелатинських/некириличних символів
- Стиль живий і конкретний — без академічного пафосу
- Весь текст має вміститись у 3500 символів
- Лише текст відповіді, без вступів і коментарів від себе"""


def clean_text(text: str) -> str:
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u0400-\u04FF\u2014\u2013\u2019\u201C\u201D\u2018]', '', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def trim_to_limit(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    trimmed = text[:limit]
    last_sentence = max(
        trimmed.rfind('.'),
        trimmed.rfind('!'),
        trimmed.rfind('?'),
    )
    if last_sentence > 0:
        return trimmed[:last_sentence + 1]
    return trimmed


def fetch_briefing(theme_name: str) -> str:
    r = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=4000,
        messages=[{
            'role': 'user',
            'content': build_prompt(theme_name)
        }],
        tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
    )
    text = ''.join(b.text for b in r.content if b.type == 'text')
    text = clean_text(text)
    text = trim_to_limit(text, MAX_CONTENT_LENGTH)
    return text


async def post_briefing(context):
    weekday = datetime.now().weekday()
    theme_name, theme_icon = THEMES[weekday]
    today = datetime.now().strftime('%d.%m.%Y')

    try:
        raw = await asyncio.get_event_loop().run_in_executor(
            None, fetch_briefing, theme_name
        )
    except Exception as e:
        print(f'Помилка fetch: {e}')
        return

    if not raw.strip():
        print('Порожня відповідь')
        return

    header = (
        f"{theme_icon} ВЕЧІРНІЙ БРИФІНГ\n"
        f"{DAYS[weekday]}, {today}\n"
        f"Тема: {theme_name}\n"
        f"{'─' * 30}\n\n"
    )
    footer = f"\n\n{'─' * 30}\nОБРІЙ. Щовечора о 19:00"

    full_text = header + raw + footer

    if len(full_text) <= 4096:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=full_text)
        except Exception as e:
            print(f'Помилка надсилання: {e}')
    else:
        chunks = [full_text[i:i+4096] for i in range(0, len(full_text), 4096)]
        for chunk in chunks:
            try:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=chunk)
            except Exception as e:
                print(f'Помилка надсилання: {e}')


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Генерую брифінг...')
    await post_briefing(context)
    await update.message.reply_text('Опубліковано в канал.')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        'ОБРІЙ — Вечірній брифінг\n\n'
        'Щовечора о 19:00 — 10 інсайтів дня на основі свіжих подій '
        'і два питання для роздумів.\n\n'
        'Розклад тем:\n'
        '🤝 Пн — Переговори та дипломатія\n'
        '🏛 Вт — Держбудівництво\n'
        '🌍 Ср — Геополітика\n'
        '📊 Чт — Економіка як влада\n'
        '📜 Пт — Історичні уроки\n'
        '⚡️ Сб — Лідерство\n'
        '🔭 Нд — Найважливіше за тиждень\n\n'
        '/now — опублікувати зараз'
    )
    await update.message.reply_text(msg)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('now', now))
    app.job_queue.run_daily(post_briefing, time=time(hour=19, minute=0))
    print('ОБРІЙ started')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
