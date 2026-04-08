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
TRUSTED_SOURCES = [
'Reuters', 'AP News', 'BBC', 'Politico', 'Financial Times',
'Kyiv Independent', 'Ukrainian Pravda', 'Ukrinform', 'Suspilne',
'The Economist', 'Foreign Policy', 'ISW', 'DW', 'Euronews'
]
subscribers = set()
def fetch_ukraine_digest():
sources_str = ', '.join(TRUSTED_SOURCES)
response = client.messages.create(
model='claude-haiku-4-5-20251001',
max_tokens=2000,
system='You are a Ukraine news monitor. Search for the 7 most important Ukraine-relat
messages=[{'role': 'user', 'content': 'Find the 7 most important Ukraine news today f
tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
)
text = ''.join(b.text for b in response.content if b.type == 'text')
s, e = text.find('['), text.rfind(']')
if s == -1:
return []
return json.loads(text[s:e+1])
async def send_digest(context):
if not subscribers:
return
loop = asyncio.get_event_loop()
try:
articles = await loop.run_in_executor(None, fetch_ukraine_digest)
except Exception:
return
if not articles:
return
text = 'Вечірній дайджест новин про Україну\n'
text += 'Джерела: Reuters, BBC, AP, Kyiv Independent, ISW та інші\n'
text += '----------------------------------------\n\n'
for i, a in enumerate(articles, 1):
icon = 'ВАЖЛИВО' if a.get('urgency') == 'high' else str(i)
text += icon + '. ' + a.get('title', '') + '\n'
text += 'Джерело: ' + a.get('source', '') + '\n'
text += a.get('summary', '') + '\n\n'
for chat_id in list(subscribers):
try:
await context.bot.send_message(chat_id=chat_id, text=text[:4096])
except Exception:
subscribers.discard(chat_id)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
chat_id = update.effective_chat.id
subscribers.add(chat_id)
await update.message.reply_text(
'GEOINT Monitor\n\n'
'Ви підписані на щоденний дайджест новин про Україну о 19:00.\n\n'
'Тільки перевірені джерела:\n'
'Reuters, AP, BBC, Kyiv Independent,\n'
'Ukrainian Pravda, ISW, Politico та інші.\n\n'
'Команди:\n'
'/start - підписатись\n'
'/stop - відписатись\n'
'/now - отримати дайджест зараз'
)
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
chat_id = update.effective_chat.id
subscribers.discard(chat_id)
await update.message.reply_text('Ви відписались від дайджесту.')
async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text('Збираю новини, зачекайте...')
loop = asyncio.get_event_loop()
try:
articles = await loop.run_in_executor(None, fetch_ukraine_digest)
except Exception:
await update.message.reply_text('Помилка завантаження.')
return
if not articles:
await update.message.reply_text('Новини не знайдено.')
return
text = 'Дайджест новин про Україну\n'
text += '----------------------------------------\n\n'
for i, a in enumerate(articles, 1):
icon = 'ВАЖЛИВО' if a.get('urgency') == 'high' else str(i)
text += icon + '. ' + a.get('title', '') + '\n'
text += 'Джерело: ' + a.get('source', '') + '\n'
text += a.get('summary', '') + '\n\n'
await update.message.reply_text(text[:4096])
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
