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

MAX_CONTENT_LENGTH = 3500


def build_prompt(theme_name: str) -> str:
    today = datetime.now().strftime('%d.%m.%Y')
    return f"""Ти — розумний друг читача який глибоко розуміє світову політику. Говориш просто, але думаєш глибоко. Не журналіст і не чиновник — ти ділишся справжнім поглядом на те як влаштований світ.

Сьогодні {today}. Тема: {theme_name}.

Знайди 6-8 важливих подій СЬОГОДНІ на тему "{theme_name}" і напиши живий брифінг.

Структура — саме така, без змін:

ГОЛОВНА ДУМКА ДНЯ
[1-2 речення. Не факт — а найцікавіший висновок дня. Те що змушує задуматись.]

КАРТИНА ДНЯ
• [Спостереження 1 — реальна подія + що за нею стоїть насправді. 2 речення.]
• [Спостереження 2]
• [Спостереження 3]
• [Спостереження 4]
• [Спостереження 5]

ЯК ЦЕ ПОВ'ЯЗАНО
[2-3 речення про приховану закономірність між сьогоднішніми подіями. Те що більшість не помічає.]

ПИТАННЯ ДНЯ
1. [Питання яке змушує побачити знайоме по-новому]
2. [Питання як це стосується України або читача особисто]

Правила яких суворо дотримуйся:
- Починай одразу з "ГОЛОВНА ДУМКА ДНЯ" — жодних вступів
- Лише українська мова, жодних іноземних символів
- Говори як розумна людина в розмові — не як підручник
- Кожне спостереження: спочатку що сталось, потім що це означає
- Весь текст максимум 3200 символів
- Жодних зірочок, жирного тексту або markdown розмітки"""


def clean_text(text: str) -> str:
    # Прибираємо markdown розмітку
    text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
    text = re.sub(r'#{1,6}\s*', '', text)
    # Залишаємо лише кирилицю, латиницю, цифри, розділові знаки
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u0400-\u04FF\u2014\u2013\u2019\u201C\u201D\u2018\u2022\u2026]', '', text)
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
        f"{theme_icon} ОБРІЙ\n"
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
        'ОБРІЙ — Щоденний брифінг\n\n'
        'Щовечора о 19:00 — живий погляд на події дня.\n'
        'Не новини, а розмова про те як влаштований світ.\n\n'
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
