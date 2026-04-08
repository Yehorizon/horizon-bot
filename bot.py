import os
import json
import asyncio
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode, ChatAction

TELEGRAM_TOKEN = os.environ[“TELEGRAM_TOKEN”]
ANTHROPIC_API_KEY = os.environ[“ANTHROPIC_API_KEY”]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

REGIONS = {
“all”:      (“🌍 Всі регіони”,    “geopolitics international relations breaking news today 2026”),
“ukraine”:  (“🇺🇦 Україна”,       “Ukraine war conflict diplomacy news today 2026”),
“europe”:   (“🇪🇺 Європа / НАТО”, “Europe EU NATO security politics news today 2026”),
“usa”:      (“🇺🇸 США”,           “USA foreign policy Congress international news today 2026”),
“russia”:   (“🇷🇺 Росія”,         “Russia geopolitics sanctions war news today 2026”),
“china”:    (“🇨🇳 Китай”,         “China geopolitics Taiwan foreign policy news today 2026”),
“mideast”:  (“🕌 Близький Схід”,  “Middle East conflict Israel Iran diplomacy news today 2026”),
}

QUICK_QUESTIONS = [
“Чи можлива нейтральність України як гарантія безпеки?”,
“Роль Китаю у врегулюванні конфлікту в Україні”,
“НАТО та стаття 5: межі колективної оборони”,
“Санкції проти Росії: ефективність та наслідки”,
“Майбутнє євроатлантичної безпекової архітектури”,
“Турецька геополітика між Сходом і Заходом”,
]

def fetch_news(region_query):
response = client.messages.create(
model=“claude-sonnet-4-20250514”,
max_tokens=1000,
system=‘Ти геополітичний новинний агрегатор. Знайди 5 новин і поверни ТІЛЬКИ JSON-масив. Формат: [{“title”:”…”,“summary”:”…”,“source”:”…”,“urgency”:“high|normal”}]’,
messages=[{“role”: “user”, “content”: f”Знайди 5 актуальних геополітичних новин: {region_query}”}],
tools=[{“type”: “web_search_20250305”, “name”: “web_search”}],
)
text = “”.join(b.text for b in response.content if b.type == “text”)
s, e = text.find(”[”), text.rfind(”]”)
if s == -1:
return []
return json.loads(text[s:e+1])

def analyze_event(title, summary, source):
response = client.messages.create(
model=“claude-sonnet-4-20250514”,
max_tokens=900,
system=“Ти старший аналітик з геополітики. Відповідай українською. Будь конкретним.”,
messages=[{“role”: “user”, “content”: f”Проаналізуй подію:\nЗаголовок: {title}\nОпис: {summary}\nДжерело: {source}\n\nРозділи: КОНТЕКСТ, КЛЮЧОВІ АКТОРИ, НАСЛІДКИ, СЦЕНАРІЇ, ВИСНОВОК”}],
)
return “”.join(b.text for b in response.content if b.type == “text”)

def ask_analyst(question):
response = client.messages.create(
model=“claude-sonnet-4-20250514”,
max_tokens=1000,
system=“Ти старший аналітик з геополітики. Відповідай структуровано українською мовою.”,
messages=[{“role”: “user”, “content”: question}],
tools=[{“type”: “web_search_20250305”, “name”: “web_search”}],
)
return “”.join(b.text for b in response.content if b.type == “text”)

def main_menu_keyboard():
return InlineKeyboardMarkup([
[InlineKeyboardButton(“📰 Новини за регіоном”, callback_data=“menu_news”)],
[InlineKeyboardButton(“🤖 AI Аналітик”, callback_data=“menu_analyst”)],
[InlineKeyboardButton(“❓ Швидкі питання”, callback_data=“menu_quick”)],
])

def regions_keyboard():
buttons = [[InlineKeyboardButton(label, callback_data=f”region_{key}”)] for key, (label, _) in REGIONS.items()]
buttons.append([InlineKeyboardButton(“← Назад”, callback_data=“menu_main”)])
return InlineKeyboardMarkup(buttons)

def news_keyboard(articles):
buttons = [
[InlineKeyboardButton(
f”{‘🔴’ if a.get(‘urgency’) == ‘high’ else ‘📌’} {a[‘title’][:55]}{’…’ if len(a[‘title’]) > 55 else ‘’}”,
callback_data=f”analyze_{i}”
)]
for i, a in enumerate(articles)
]
buttons.append([InlineKeyboardButton(“← Регіони”, callback_data=“menu_news”)])
return InlineKeyboardMarkup(buttons)

def quick_questions_keyboard():
buttons = [[InlineKeyboardButton(q[:60], callback_data=f”quick_{i}”)] for i, q in enumerate(QUICK_QUESTIONS)]
buttons.append([InlineKeyboardButton(“← Назад”, callback_data=“menu_main”)])
return InlineKeyboardMarkup(buttons)

def back_keyboard(dest=“menu_main”):
return InlineKeyboardMarkup([[InlineKeyboardButton(“← Назад”, callback_data=dest)]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
context.user_data.clear()
await update.message.reply_text(
“🌍 *GEOINT Dashboard*\n_Геополітичний моніторинг · AI-Powered_\n\nОберіть дію:”,
parse_mode=ParseMode.MARKDOWN,
reply_markup=main_menu_keyboard(),
)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
data = query.data

```
if data == "menu_main":
    await query.edit_message_text(
        "🌍 *GEOINT Dashboard*\n_Оберіть дію:_",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard(),
    )

elif data == "menu_news":
    await query.edit_message_text(
        "📰 *Новини*\nОберіть регіон:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=regions_keyboard(),
    )

elif data.startswith("region_"):
    region_key = data[len("region_"):]
    label, region_query = REGIONS[region_key]
    await query.edit_message_text(f"⏳ Завантажую новини — *{label}*…", parse_mode=ParseMode.MARKDOWN)
    loop = asyncio.get_event_loop()
    articles = await loop.run_in_executor(None, fetch_news, region_query)
    if not articles:
        await query.edit_message_text("❌ Не вдалося завантажити новини.", reply_markup=back_keyboard("menu_news"))
        return
    context.user_data["articles"] = articles
    context.user_data["region_key"] = region_key
    await query.edit_message_text(
        f"📰 *{label}* — {len(articles)} подій\n\nОберіть статтю для AI-аналізу:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=news_keyboard(articles),
    )

elif data.startswith("analyze_"):
    idx = int(data[len("analyze_"):])
    articles = context.user_data.get("articles", [])
    if idx >= len(articles):
        await query.edit_message_text("❌ Помилка.", reply_markup=back_keyboard())
        return
    article = articles[idx]
    await query.edit_message_text(f"🔍 Аналізую…")
    loop = asyncio.get_event_loop()
    analysis = await loop.run_in_executor(None, analyze_event, article["title"], article["summary"], article.get("source", ""))
    icon = "🔴" if article.get("urgency") == "high" else "📌"
    text = f"{icon} *{article['title']}*\n_{article.get('source', '')}_\n\n{analysis}"
    await query.edit_message_text(
        text[:4096],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_keyboard(f"region_{context.user_data.get('region_key', 'all')}"),
    )

elif data == "menu_quick":
    await query.edit_message_text(
        "❓ *Швидкі питання*\nОберіть тему:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=quick_questions_keyboard(),
    )

elif data.startswith("quick_"):
    idx = int(data[len("quick_"):])
    if idx >= len(QUICK_QUESTIONS):
        return
    question = QUICK_QUESTIONS[idx]
    await query.edit_message_text(f"🤖 Аналізую…")
    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, ask_analyst, question)
    await query.edit_message_text(
        f"❓ *{question}*\n\n{answer}"[:4096],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_keyboard("menu_quick"),
    )

elif data == "menu_analyst":
    context.user_data["mode"] = "analyst"
    await query.edit_message_text(
        "🤖 *AI Аналітик*\n\nНапишіть будь-яке геополітичне питання.\n\n_Напр.: Які наслідки вступу України до НАТО?_",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_keyboard("menu_main"),
    )
```

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
if context.user_data.get(“mode”) != “analyst”:
await update.message.reply_text(“Скористайся /start для навігації 👇”, reply_markup=main_menu_keyboard())
return
question = update.message.text.strip()
msg = await update.message.reply_text(“🔍 Шукаю та аналізую…”)
loop = asyncio.get_event_loop()
answer = await loop.run_in_executor(None, ask_analyst, question)
await msg.edit_text(
f”🤖 *{question[:80]}*\n\n{answer}”[:4096],
parse_mode=ParseMode.MARKDOWN,
reply_markup=back_keyboard(“menu_analyst”),
)

def main():
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler(“start”, start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
print(“GEOINT Bot запущено”)
app.run_polling(drop_pending_updates=True)

if __name__ == “__main__”:
main()
