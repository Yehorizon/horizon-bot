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
SYSTEM_PROMPT = (
'You are a Ukraine news monitor. '
'Find the 7 most important Ukraine-related news today. '
'Use only trusted sources: ' + SOURCES + '. '
'Return ONLY a JSON array. '
'Format: [{"title":"...","summary":"2 sentences","source":"...","urgency":"high|normal"}]
)
USER_PROMPT = 'Find the 7 most important Ukraine news today from trusted sources only.'
subscribers = set()
def fetch_digest():
response = client.messages.create(
model='claude-haiku-4-5-20251001',
max_tokens=2000,
system=SYSTEM_PROMPT,
messages=[{'role': 'user', 'content': USER_PROMPT}],
tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
)
text = ''.join(b.text for b in response.content if b.type == 'text')
s, e = text.find('['), text.rfind(']')
if s == -1:
return []
return json.loads(text[s:e+1])
def format_digest(articles):
lines = ['Вечірній дайджест новин про Україну']
lines.append('Джерела: ' + SOURCES)
lines.append('---')
for i, a in enumerate(articles, 1):
icon = 'ВАЖЛИВО' if a.get('urgency') == 'high' else str(i)
lines.append(icon + '. ' + a.get('title', ''))
lines.append('Джерело: ' + a.get('source', ''))
lines.append(a.get('summary', ''))
lines.append('')
return '
'.join(lines)
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
text = format_digest(articles)
for chat_id in list(subscribers):
try:
await context.bot.send_message(chat_id=chat_id, text=text[:4096])
except Exception:
subscribers.discard(chat_id)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
chat_id = update.effective_chat.id
subscribers.add(chat_id)
msg = (
'GEOINT Monitor
'
'Ви підписані на щоденний дайджест о 19:00.
'
'Джерела: ' + SOURCES + '
'
'Команди:
'
'/start - підписатись
'
'/stop - відписатись
'
'/now - отримати дайджест зараз'
)
await update.message.reply_text(msg)
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
subscribers.discard(update.effective_chat.id)
await update.message.reply_text('Ви відписались від дайджесту.')
async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text('Збираю новини, зачекайте...')
loop = asyncio.get_event_loop()
try:
articles = await loop.run_in_executor(None, fetch_digest)
except Exception:
await update.message.reply_text('Помилка завантаження.')
return
if not articles:
await update.message.reply_text('Новини не знайдено.')
return
await update.message.reply_text(format_digest(articles)[:4096])
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
