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


def build_prompt(theme_name: str) -> str:
    today = datetime.now().strftime('%d.%m.%Y')
    return f"""Ти — експерт з геополітики та державного управління. Пишеш для амбітної молоді, яка хоче стати політиком або дипломатом.

Сьогодні {today}. Тема: {theme_name}.

Знайди 5 реальних подій цього тижня на тему "{theme_name}" і створи брифінг.

Кожен з 5 пунктів має таку структуру:

**[Коротка назва — до 8 слів]**
Подія: що сталось (2 речення, просто і конкретно).
Контекст: чому це важливо стратегічно (2 речення).
Паралель: схожа історична ситуація і чим закінчилась (2-3 речення).
Висновок: урок для майбутнього політика (2 речення, спонукай до роздумів).

Пункт 5 — завершується двома реченнями у форматі питання або думки для самоаналізу читача.

Правила:
- Тільки українська мова
- Жодних службових позначок, технічних символів або нелатинських/некириличних знаків
- Стиль: розумний, але живий — без зайвого академізму
- Короткі речення, конкретні факти, реальні імена і дати
- Тільки сам текст брифінгу — без вступів, пояснень і коментарів від себе"""


def clean_text(text: str) -> str:
    # Залишаємо кирилицю, латиницю, цифри, розділові знаки і форматування
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u0400-\u04FF\u2014\u2013\u2019\u201C\u201D]', '', text)
    # Прибираємо зайві порожні рядки (більше двох поспіль)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def fetch_briefing(theme_name: str) -> str:
    r = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=4000,
        messages=[{
            'role': 'user',
            'content': build_prompt(theme_name)
        }],
        tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
    )
    text = ''.join(b.text for b in r.content if b.type == 'text')
    return clean_text(text)


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
        f"{theme_icon} РАНКОВИЙ БРИФІНГ\n"
        f"{DAYS[weekday]}, {today}\n"
        f"Тема: {theme_name}\n"
        f"{'─' * 30}\n\n"
    )
    footer = f"\n\n{'─' * 30}\nОБРІЙ. Щоранку о 08:00"
    text = header + raw + footer

    chunks = [text[i:i+4096] for i in range(0, len(text), 4096)]
    for chunk in chunks:
        try:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=chunk
            )
        except Exception as e:
            print(f'Помилка надсилання: {e}')


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Генерую брифінг...')
    await post_briefing(context)
    await update.message.reply_text('Опубліковано в канал.')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        'ОБРІЙ — Ранковий брифінг\n\n'
        'Щоранку о 08:00 в канал виходить глибокий навчальний матеріал '
        'на основі свіжих подій тижня.\n\n'
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
    app.job_queue.run_daily(post_briefing, time=time(hour=8, minute=0))
    print('ОБРІЙ started')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
