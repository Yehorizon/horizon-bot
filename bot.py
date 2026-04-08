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


def build_prompt(theme_name: str) -> str:
    today = datetime.now().strftime('%d.%m.%Y')
    return f"""Ти — експерт з геополітики, дипломатії та державного управління.
Сьогодні {today}. Тема брифінгу: {theme_name}.

КРОК 1: Знайди через пошук 3-5 найсвіжіших подій цього тижня, що стосуються теми "{theme_name}" у світовому або українському контексті.

КРОК 2: На основі цих реальних подій створи глибокий навчальний брифінг з 5 пунктів для людини, яка прагне стати видатним політиком і переговорником.

Кожен пункт має містити:
1. Назву концепції або події (коротко, до 10 слів)
2. Пояснення — що сталось і що це означає (2-3 речення)
3. Геополітичний або стратегічний контекст — чому це важливо (2-3 речення)
4. Історична паралель — схожа ситуація з минулого і чим вона закінчилась (3-4 речення)
5. Практичний висновок — який урок має засвоїти майбутній політик (2 речення)

Вимоги:
- Тільки українською мовою
- Спирайся на РЕАЛЬНІ події цього тижня, не вигадуй
- Посилайся на конкретних діячів, країни, дати
- Глибоко і серйозно — як для студента стратегії
- Кожен пункт має бути самодостатнім уроком
- Тільки текст брифінгу, без вступу і пояснень від себе"""


def escape_md(text: str) -> str:
    chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for c in chars:
        text = text.replace(c, f'\\{c}')
    return text


def fetch_briefing(theme_name: str) -> str:
    r = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=3000,
        messages=[{
            'role': 'user',
            'content': build_prompt(theme_name)
        }],
        tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
    )
    text = ''.join(b.text for b in r.content if b.type == 'text')
    return text


def fmt(raw_text: str, theme_name: str, theme_icon: str, weekday: int) -> str:
    days = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота', 'Неділя']
    day_name = days[weekday]
    today = datetime.now().strftime('%d\\.%m\\.%Y')

    header = (
        f"*{theme_icon} РАНКОВИЙ БРИФІНГ*\n"
        f"_{day_name}, {today}_\n"
        f"*Тема: {escape_md(theme_name)}*\n\n"
    )

    parts = re.split(r'\n(?=\d+[\.\)])', raw_text.strip())

    body_lines = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split('\n', 1)
        if len(lines) == 2:
            title = escape_md(lines[0].strip())
            content = escape_md(lines[1].strip())
            body_lines.append(f"*{title}*\n{content}")
        else:
            body_lines.append(escape_md(part))

    body = '\n\n'.join(body_lines)
    footer = f"\n\n——\n_ОБРІЙ\\. Щоранку о 08:00_"

    return header + body + footer


async def post_briefing(context):
    weekday = datetime.now().weekday()
    theme_name, theme_icon = THEMES[weekday]

    try:
        raw = await asyncio.get_event_loop().run_in_executor(
            None, fetch_briefing, theme_name
        )
    except Exception as e:
        print(f'Помилка fetch: {e}')
        return

    if not raw.strip():
        print('Порожня відповідь від Claude')
        return

    text = fmt(raw, theme_name, theme_icon, weekday)
    chunks = [text[i:i+4096] for i in range(0, len(text), 4096)]

    for chunk in chunks:
        try:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=chunk,
                parse_mode='MarkdownV2'
            )
        except Exception as e:
            print(f'Помилка надсилання: {e}')


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('⏳ Генерую брифінг\\.\\.\\.', parse_mode='MarkdownV2')
    await post_briefing(context)
    await update.message.reply_text('✅ Опубліковано в канал\\.', parse_mode='MarkdownV2')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        '*🌅 ОБРІЙ — Ранковий брифінг*\n\n'
        'Щоранку о 08:00 в канал виходить глибокий навчальний матеріал на основі свіжих подій тижня\\.\n\n'
        '*Розклад тем:*\n'
        '🤝 Пн — Переговори та дипломатія\n'
        '🏛 Вт — Держбудівництво\n'
        '🌍 Ср — Геополітика\n'
        '📊 Чт — Економіка як влада\n'
        '📜 Пт — Історичні уроки\n'
        '⚡️ Сб — Лідерство\n'
        '🔭 Нд — Найважливіше за тиждень\n\n'
        '/now \\— опублікувати зараз'
    )
    await update.message.reply_text(msg, parse_mode='MarkdownV2')


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('now', now))
    app.job_queue.run_daily(post_briefing, time=time(hour=8, minute=0))
    print('ОБРІЙ started')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
