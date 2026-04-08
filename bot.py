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

SYS = 'You are a Ukraine news monitor. Find 7 important Ukraine news today from: ' + SOURCES + '. Return ONLY JSON array. Format: [{"title":"...","summary":"2 sentences","source":"...","urgency":"high|normal"}]'
USR = 'Find 7 most important Ukraine news today from trusted sources only.'

subscribers = set()


def fetch_digest():
    r = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=2000,
        system=SYS,
        messages=[{'role': 'user', 'content': USR}],
        tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
    )
    text = ''.join(b.text for b in r.content if b.type == 'text')
    s, e = text.find('['), text.rfind(']')
    if s == -1:
        return []
    return json.loads(text[s:e+1])


def fmt(articles):
    lines = ['Дайджест новин про Україну', 'Джерела: ' + SOURCES, '---']
    for i, a in enumerate(articles, 1):
        icon = 'ВАЖЛИВО' if a.get('urgency') == 'high' else str(i)
        lines.append(icon + '. ' + a.get('title', ''))
        lines.append('Джерело: ' + a.get('source', ''))
        lines.append(a.get('summary', ''))
        lines.append('')
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
            await context.bot.send_message(chat_id=cid, text=text[:4096])
        except Exception:
            subscribers.discard(cid)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.add(update.effective_chat.id)
    msg = 'GEOINT Monitor\n\nПідписані на дайджест о 19:00\nДжерела: ' + SOURCES + '\n\n/stop - відписатись\n/now - отримати зараз'
    await update.message.reply_text(msg)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribers.discard(update.effective_chat.id)
    await update.message.reply_text('Відписались.')


async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Збираю новини...')
    loop = asyncio.get_event_loop()
    try:
        articles = await loop.run_in_executor(None, fetch_digest)
    except Exception:
        await update.message.reply_text('Помилка.')
        return
    if not articles:
        await update.message.reply_text('Не знайдено.')
        return
    await update.message.reply_text(fmt(articles)[:4096])


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
