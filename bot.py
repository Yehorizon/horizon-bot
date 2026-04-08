import os
import json
import asyncio
import anthropic
from datetime import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SOURCES = 'Reuters, AP News, BBC, Kyiv Independent, Ukrainian Pravda, ISW, Politico, DW'

SYS = (
    'Ти — монітор новин про Україну. Знайди 7 найважливіших новин про Україну сьогодні з джерел: '
    + SOURCES +
    '. Поверни ТІЛЬКИ JSON масив без жодного додаткового тексту. '
    'Формат кожного елементу: '
    '{"title": "заголовок українською", '
    '"summary": "2 речення українською", '
    '"source": "назва джерела", '
    '"urgency": "high" або "normal"}. '
    'Всі поля title та summary — виключно українською мовою.'
)

USR = (
    'Знайди 7 найважливіших новин про Україну сьогодні. '
    'Заголовки та резюме — тільки українською мовою. '
    'Поверни тільки JSON масив.'
)

subscribers = set()


def fetch_digest():
    r = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=2500,
        system=SYS,
        messages=[{'role': 'user', 'content': USR}],
        tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
    )
    text = ''.join(b.text for b in r.content if b.type == 'text')
    s, e = text.find('['), text.rfind(']')
    if s == -1:
        return []
    try:
        return json.loads(text[s:e+1])
    except Exception:
        return []


def fmt(articles):
    lines = [
        '🇺🇦 *ДАЙДЖЕСТ НОВИН ПРО УКРАЇНУ*',
        f'_Джерела: {SOURCES}_',
        '',
    ]
    for i, a in enumerate(articles, 1):
        urgency = a.get('urgency') == 'high'
        icon = '🔴' if urgency else '🔵'
        title = a.get('title', '').replace('.', '\\.').replace('-', '\\-').replace('!', '\\!').replace('(', '\\(').replace(')', '\\)').replace('>', '\\>').replace('#', '\\#')
        source = a.get('source', '')
        summary = a.get('summary', '').replace('.', '\\.').replace('-', '\\-').replace('!', '\\!').replace('(', '\\(').replace(')', '\\)').replace('>', '\\>').replace('#', '\\#')

        lines.append(f"{icon} *{i}\\. {title}*")
        lines.append(f"_{source}_")
        lines.append(summary)
        lines.append('')

    lines.append('——')
    lines.append('🔔 _Щодня о 19:00_')
    return '\n'.join(lines)


async def send_digest(context):
    if not subscribers:
        return
    loop = asyncio.get_event_loop()
    try:
        articles = await loop.run_in_executor(None, fetch_digest)
    except Exception:
        return
    if not articles:
        return
    text = fmt(articles)
    for cid in list(subscribers):
        try:
            await context.bot.send_message(
                chat_id=cid,
                text=text[:4096],
                parse_mode='MarkdownV2'
            )
        except Exception:
            subscribers.discard(cid)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.add(update.effective_chat.id)
    msg = (
        '🇺🇦 *GEOINT Monitor*\n\n'
        'Ви підписані на щоденний дайджест о 19:00\\.\n\n'
        f'_Джерела: {SOURCES}_\n\n'
        '/now \\— отримати дайджест зараз\n'
        '/stop \\— відписатись'
    )
    await update.message.reply_text(msg, parse_mode='MarkdownV2')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.discard(update.effective_chat.id)
    await update.message.reply_text('Відписались\\.', parse_mode='MarkdownV2')


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('⏳ Збираю новини\\.\\.\\.',  parse_mode='MarkdownV2')
    loop = asyncio.get_event_loop()
    try:
        articles = await loop.run_in_executor(None, fetch_digest)
    except Exception:
        await update.message.reply_text('❌ Помилка\\.', parse_mode='MarkdownV2')
        return
    if not articles:
        await update.message.reply_text('❌ Не знайдено\\.', parse_mode='MarkdownV2')
        return
    await update.message.reply_text(
        fmt(articles)[:4096],
        parse_mode='MarkdownV2'
    )


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stop', stop))
    app.add_handler(CommandHandler('now', now))
    app.job_queue.run_daily(send_digest, time=time(hour=19, minute=0))
    print('GEOINT Monitor started')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
