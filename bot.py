import os
import asyncio
import re
import feedparser
from datetime import time, datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

RSS_FEEDS = [
    'https://www.chathamhouse.org/rss.xml',
    'https://ecfr.eu/feed/',
    'https://foreignaffairs.com/rss.xml',
    'https://cepa.org/feed/',
    'https://warontherocks.com/feed/',
    'https://www.atlanticcouncil.org/feed/',
    'https://www.csis.org/rss.xml',
    'https://www.stimson.org/feed/',
    'https://www.newsecuritybeat.org/feed/',
    'https://www.ukrinform.net/rss/block-lastnews',
    'https://rss.dw.com/xml/rss-ukr-all',
    'https://www.bpb.de/rss/',
]

YEHOR_PROFILE = """
Єгор, 23 роки, українець у Дортмунді. Цілі: кар'єра в дипломатії та держуправлінні,
внесок у майбутнє України. Інтереси: геополітика, міжнародні відносини, торгові шляхи,
стратегічні інтереси країн, переговори з позиції сили, держбудівництво.
"""


def clean_text(text: str) -> str:
    text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u0400-\u04FF\u2014\u2013\u2019\u201C\u201D\u2018\u2022\u2026]', '', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def fetch_rss_articles() -> list:
    articles = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', '')[:300]
                source = feed.feed.get('title', url)
                articles.append({
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'source': source
                })
        except Exception as e:
            print(f'RSS помилка {url}: {e}')
    return articles


def select_top_articles(articles: list) -> str:
    if not articles:
        return 'Статей не знайдено.'

    articles_text = '\n'.join([
        f"{i+1}. [{a['source']}] {a['title']}\n{a['summary']}"
        for i, a in enumerate(articles[:80])
    ])

    prompt = f"""Ти аналітик який допомагає Єгору відбирати найважливіші статті.

Профіль Єгора:
{YEHOR_PROFILE}

Ось список статей з різних джерел:
{articles_text}

Відбери TOP 8 найрелевантніших для Єгора.
Для кожної напиши:
- Назву українською (коротко)
- Джерело
- 1 речення чому це важливо для його цілей
- Посилання

Формат — нумерований список, без markdown."""

    r = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=1500,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return r.content[0].text


async def post_digest(context):
    articles = await asyncio.get_event_loop().run_in_executor(
        None, fetch_rss_articles
    )
    if not articles:
        print('Статей не знайдено')
        return

    top = await asyncio.get_event_loop().run_in_executor(
        None, select_top_articles, articles
    )

    top = clean_text(top)
    today = datetime.now().strftime('%d.%m.%Y')

    msg = (
        f"📰 ОБРІЙ — ДАЙДЖЕСТ\n"
        f"{today}\n"
        f"{'─' * 30}\n\n"
        f"{top}\n\n"
        f"{'─' * 30}\n"
        f"ОБРІЙ. Щодня о 09:00"
    )

    if len(msg) <= 4096:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
    else:
        chunks = [msg[i:i+4096] for i in range(0, len(msg), 4096)]
        for chunk in chunks:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=chunk)


async def digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Збираю статті...')
    await post_digest(context)
    await update.message.reply_text('Дайджест опубліковано.')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        'ОБРІЙ — Щоденний дайджест\n\n'
        'Щодня о 09:00 — топ-8 найважливіших статей\n'
        'з провідних аналітичних джерел світу.\n\n'
        'Джерела: Chatham House, Foreign Affairs, ECFR,\n'
        'CEPA, War on the Rocks, Atlantic Council,\n'
        'CSIS, Stimson, DW, Ukrinform та інші.\n\n'
        '/digest — отримати дайджест зараз'
    )
    await update.message.reply_text(msg)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('digest', digest))
    app.job_queue.run_daily(post_digest, time=time(hour=9, minute=0))
    print('ОБРІЙ started')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
