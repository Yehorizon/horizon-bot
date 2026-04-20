import os
import asyncio
import datetime
from datetime import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

START_DATE = datetime.date(2026, 4, 20)

WEEKLY_PLAN = {
    0: {
        "theme": "Я і моє життя", "emoji": "👤",
        "levels": [
            {
                "grammar": "Präsens — теперішній час",
                "grammar_task": "Дієслова: sein, haben, wohnen, arbeiten, lernen, heißen\n\nНапиши 10 речень про себе:\n• Ich heiße...\n• Ich wohne in...\n• Ich lerne Deutsch, weil...",
                "words": "wohnen — жити\narbeiten — працювати\nlernen — вчитися\nheißen — називатися\nkommen aus — походити з\nsprechen — говорити\nverstehen — розуміти\nbrauchen — потребувати\nsuchen — шукати\nfinden — знаходити",
                "speaking": "Розкажи про себе: Хто ти? Звідки? Чому в Німеччині? Що вчиш?",
                "writing": "Напиши 10 речень про свій день сьогодні.",
            },
            {
                "grammar": "Präsens + weil / denn",
                "grammar_task": "• Ich lerne Deutsch, weil ich in Deutschland wohne.\n• Ich lerne Deutsch, denn ich brauche die Sprache.\n\nНапиши 10 речень — 5 з weil, 5 з denn.\nУвага: після weil дієслово йде в кінець!",
                "words": "die Zukunft — майбутнє\nder Erfolg — успіх\ndie Möglichkeit — можливість\nentscheiden — вирішувати\nverbessern — покращувати\nerreichen — досягати\nbleiben — залишатися\nverändern — змінювати\ndie Ausbildung — навчання\nschaffen — справлятися",
                "speaking": "Розкажи чому ти в Німеччині і що хочеш досягти. Використовуй weil і denn.",
                "writing": "Напиши 12 речень про свої цілі в Німеччині.",
            },
            {
                "grammar": "Präsens + weil / obwohl / trotzdem",
                "grammar_task": "• Obwohl es schwer ist, lerne ich jeden Tag.\n• Ich lerne Deutsch, obwohl ich wenig Zeit habe.\n• Es ist schwer. Trotzdem mache ich weiter.\n\nНапиши 12 речень — по 4 з кожним.",
                "words": "die Herausforderung — виклик\ndie Geduld — терпіння\nanstrengend — виснажливий\ntrotzdem — попри це\nobwohl — хоча\ndennoch — проте\nweitermachen — продовжувати\naufgeben — здаватися\nüberwinden — долати\nbeharrlich — наполегливий",
                "speaking": "Розкажи про труднощі і як ти з ними справляєшся.",
                "writing": "Напиши есе 15+ речень про себе і свої цілі.",
            },
        ],
    },
    1: {
        "theme": "Плани і обов'язки", "emoji": "📋",
        "levels": [
            {
                "grammar": "Modalverben — kann, muss, soll, darf, will, möchte",
                "grammar_task": "Кожне модальне дієслово — 2 речення:\n• Ich muss heute Deutsch lernen.\n• Ich kann gut Englisch sprechen.\n• Ich möchte in Deutschland arbeiten.\n\nРазом 12 речень.",
                "words": "müssen — мусити\nkönnen — могти\nsollen — слід\ndürfen — мати дозвіл\nwollen — хотіти\nmöchten — хотіти (ввічливо)\nder Plan — план\ndie Aufgabe — завдання\npünktlich — вчасно\nregelmäßig — регулярно",
                "speaking": "Розкажи що ти мусиш зробити сьогодні і що хочеш зробити цього тижня.",
                "writing": "Напиши план на завтра — 10 речень з модальними дієсловами.",
            },
            {
                "grammar": "Modalverben + um...zu / damit",
                "grammar_task": "• Ich lerne Deutsch, um in Deutschland zu arbeiten.\n• Ich spare Geld, damit ich eine Wohnung mieten kann.\n\nНапиши 10 речень — 5 з um...zu, 5 з damit.",
                "words": "sparen — заощаджувати\nmieten — орендувати\nbewerben — подавати заяву\nvorbereiten — готуватися\nbestehen — скласти іспит\ndie Bewerbung — заява\nder Lebenslauf — резюме\ndie Stelle — посада\ndie Erfahrung — досвід\nerfolgreich — успішний",
                "speaking": "Розкажи про свої плани на наступні 6 місяців. Використовуй um...zu і damit.",
                "writing": "Напиши 12 речень про те, що ти робиш і навіщо.",
            },
            {
                "grammar": "Konjunktiv II — könnte, müsste, sollte",
                "grammar_task": "• Ich könnte mehr lernen.\n• Du solltest jeden Tag üben.\n• Wir müssten früher anfangen.\n\nНапиши 12 речень з könnte, sollte, müsste.",
                "words": "vorschlagen — пропонувати\nempfehlen — рекомендувати\nraten — радити\nüberlegen — обдумувати\ndie Entscheidung — рішення\nabwägen — зважувати\nder Vorteil — перевага\nder Nachteil — недолік\nvergleichen — порівнювати\nüberzeugen — переконувати",
                "speaking": "Що ти міг би зробити краще? Що тобі слід змінити? Говори 5 хвилин.",
                "writing": "Напиши 15 речень — що б ти зробив інакше і чому.",
            },
        ],
    },
    2: {
        "theme": "Місто і транспорт", "emoji": "🏙️",
        "levels": [
            {
                "grammar": "Akkusativ + Trennbare Verben",
                "grammar_task": "Артиклі в Akkusativ: den / einen / die / eine / das / ein\n\nПрефікс в кінець:\n• Ich steige in den Bus ein.\n• Ich kaufe eine Fahrkarte.\n\nНапиши 10 речень про поїздку містом.",
                "words": "die Haltestelle — зупинка\neinsteigen — сідати\naussteigen — виходити\numsteigen — пересідати\ndie Fahrkarte — квиток\nder Bahnhof — вокзал\ndie U-Bahn — метро\ndie Straßenbahn — трамвай\npünktlich — вчасно\ndie Verspätung — запізнення",
                "speaking": "Опиши як ти добираєшся до центру міста. Яким транспортом? Скільки часу?",
                "writing": "Напиши 10 речень про транспорт у Дортмунді.",
            },
            {
                "grammar": "Wechselpräpositionen — Akkusativ vs Dativ",
                "grammar_task": "Рух (Akkusativ) vs Місце (Dativ):\n• Ich fahre in die Stadt. (куди?)\n• Ich bin in der Stadt. (де?)\n\nПрийменники: in, an, auf, über, unter, vor, hinter, neben, zwischen\n\nНапиши 12 речень — по 6 Akkusativ і Dativ.",
                "words": "das Rathaus — ратуша\ndie Innenstadt — центр міста\nder Marktplatz — площа\ndie Umgebung — околиці\nentfernt — на відстані\nin der Nähe — поруч\ngegenüber — навпроти\nentlang — вздовж\nüberqueren — перетинати\ndie Kreuzung — перехрестя",
                "speaking": "Опиши де ти живеш — що є поруч, далеко, навпроти.",
                "writing": "Напиши 12 речень — опис свого району в Дортмунді.",
            },
            {
                "grammar": "Relativsätze — відносні речення",
                "grammar_task": "• Das ist der Bus, der zum Hauptbahnhof fährt.\n• Die Stadt, in der ich wohne, heißt Dortmund.\n• Das Ticket, das ich gekauft habe, ist günstig.\n\nНапиши 12 речень з відносними реченнями.",
                "words": "verbinden — з'єднувати\ndie Verbindung — з'єднання\nerreichbar — доступний\ndas Netz — мережа\ndie Linie — лінія\ndie Richtung — напрямок\nabfahren — відправлятися\nankommen — прибувати\ndie Abfahrt — відправлення\ndie Ankunft — прибуття",
                "speaking": "Опиши місто з відносними реченнями: Dortmund ist eine Stadt, die...",
                "writing": "Напиши 15 речень — опис Дортмунда з відносними реченнями.",
            },
        ],
    },
    3: {
        "theme": "Запитання і відповіді", "emoji": "❓",
        "levels": [
            {
                "grammar": "W-Fragen + kein...sondern",
                "grammar_task": "Wer? Was? Wo? Wann? Wie? Warum? Wohin?\n\nkein...sondern — не... а:\n• Das ist kein Problem, sondern eine Chance.\n\nНапиши 5 W-Fragen з відповідями і 5 речень з kein...sondern.",
                "words": "die Frage — запитання\ndie Antwort — відповідь\nfragen — питати\nantworten — відповідати\nerklären — пояснювати\nmeinen — мати на увазі\nbedеuten — означати\nwiederholen — повторювати\nbestätigen — підтверджувати\nverstehen — розуміти",
                "speaking": "Уяви що ти на співбесіді. Відповідай: Wer sind Sie? Was möchten Sie? Warum Deutsch?",
                "writing": "Напиши діалог 10 реплік — запитання і відповіді про себе.",
            },
            {
                "grammar": "Indirekte Fragen — непрямі запитання",
                "grammar_task": "• Wo ist der Bahnhof? → Ich möchte wissen, wo der Bahnhof ist.\n• Ist das richtig? → Ich frage mich, ob das richtig ist.\n\nУвага: дієслово в кінець!\n\nНапиши 10 непрямих запитань.",
                "words": "möchte wissen — хотів би знати\nkannst du sagen — чи можеш сказати\nich frage mich — я питаю себе\nob — чи\nherausfinden — з'ясовувати\nnachfragen — уточнювати\nklarstellen — прояснювати\nzweifeln — сумніватися\nsicher sein — бути впевненим\nüberzeugen — переконувати",
                "speaking": "Постав 10 непрямих запитань про Ausbildung або роботу в Німеччині.",
                "writing": "Напиши 12 речень з непрямими запитаннями.",
            },
            {
                "grammar": "obwohl / auch wenn / selbst wenn",
                "grammar_task": "• Obwohl ich müde bin, lerne ich weiter.\n• Auch wenn es schwer ist, gebe ich nicht auf.\n• Selbst wenn ich keine Zeit habe, übe ich täglich.\n\nНапиши 12 речень — по 4 з кожною конструкцією.",
                "words": "aufgeben — здаватися\nweitermachen — продовжувати\ndie Ausdauer — витривалість\nüberwinden — долати\ndie Schwierigkeit — труднощі\ntrotz — незважаючи на\nder Widerstand — опір\nstandhalten — витримувати\nsiegen — перемагати\nbeharrlich — наполегливий",
                "speaking": "Розкажи про труднощі у вивченні мови. Використовуй obwohl, auch wenn, selbst wenn.",
                "writing": "Напиши 15 речень — есе про наполегливість.",
            },
        ],
    },
    4: {
        "theme": "Минуле", "emoji": "⏳",
        "levels": [
            {
                "grammar": "Perfekt з haben і sein",
                "grammar_task": "З haben: kaufen→gekauft, machen→gemacht, lernen→gelernt\nЗ sein: gehen→gegangen, fahren→gefahren, kommen→gekommen\n\nНапиши 10 речень — 5 з haben, 5 з sein:\n• Ich habe gestern Deutsch gelernt.\n• Ich bin heute in die Stadt gefahren.",
                "words": "gestern — вчора\nvorgestern — позавчора\nletzte Woche — минулого тижня\nletztes Jahr — минулого року\nfrüher — раніше\ndamals — тоді\nschon — вже\nnoch nicht — ще не\nnie — ніколи\nimmer — завжди",
                "speaking": "Розкажи що ти робив вчора — від ранку до вечора. Тільки Perfekt.",
                "writing": "Напиши 10 речень про минулий тиждень.",
            },
            {
                "grammar": "Perfekt + Präteritum",
                "grammar_task": "Präteritum для: sein→war, haben→hatte, Modalverben:\n• Ich war gestern müde.\n• Ich hatte keine Zeit.\n• Ich musste arbeiten.\n\nНапиши 12 речень — 6 Perfekt + 6 Präteritum.",
                "words": "war — був\nhatte — мав\nmusste — мусив\nkonnte — міг\nwollte — хотів\ndurfte — мав дозвіл\ndie Vergangenheit — минуле\ndie Erfahrung — досвід\nprägen — формувати\nbeeinflussen — впливати",
                "speaking": "Розкажи про важливу подію у своєму житті. Perfekt і Präteritum.",
                "writing": "Напиши 12 речень про те як ти опинився в Німеччині.",
            },
            {
                "grammar": "Plusquamperfekt",
                "grammar_task": "Дія яка відбулась ДО іншої:\n• Nachdem ich gegessen hatte, ging ich spazieren.\n• Als ich ankam, hatte der Zug schon abgefahren.\n\nhatte/war + Partizip II\n\nНапиши 10 речень з Plusquamperfekt.",
                "words": "nachdem — після того як\nals — коли\nbevor — перед тим як\nbereits — вже\nzuvor — до цього\ndaraufhin — після цього\nschließlich — врешті-решт\nzuletzt — наостанок\nendlich — нарешті\ninfolgedessen — внаслідок",
                "speaking": "Розкажи про день коли ти переїхав до Дортмунда.",
                "writing": "Напиши 15 речень — Perfekt, Präteritum і Plusquamperfekt разом.",
            },
        ],
    },
    5: {
        "theme": "Складні думки", "emoji": "🧠",
        "levels": [
            {
                "grammar": "dass + sowohl...als auch",
                "grammar_task": "dass — що:\n• Ich denke, dass Deutsch wichtig ist.\n\nsowohl...als auch — як... так і:\n• Ich lerne sowohl Grammatik als auch Vokabeln.\n\nНапиши 5 речень з dass і 5 з sowohl...als auch.",
                "words": "denken — думати\nglauben — вважати\nmeinen — мати на увазі\nwissen — знати\nverstehen — розуміти\nannehmen — припускати\nbehaupten — стверджувати\nbezweifeln — сумніватися\nbeweisen — доводити\nakzeptieren — приймати",
                "speaking": "Розкажи що ти думаєш про вивчення мов. Використовуй dass і sowohl...als auch.",
                "writing": "Напиши 10 речень зі своїми думками про життя в Німеччині.",
            },
            {
                "grammar": "Парні сполучники",
                "grammar_task": "• sowohl...als auch — як... так і\n• weder...noch — ні... ні\n• entweder...oder — або... або\n• nicht nur...sondern auch — не тільки... але й\n\nНапиши по 3 речення з кожним (разом 12).",
                "words": "einerseits — з одного боку\nandererseits — з іншого боку\nzudem — крім того\naußerdem — до того ж\ndabei — при цьому\njedoch — однак\nallerdings — щоправда\nimmerhin — принаймні\nzumindest — щонайменше\ninsgesamt — загалом",
                "speaking": "Порівняй Україну і Німеччину. Використовуй парні сполучники.",
                "writing": "Напиши 12 речень — порівняння двох варіантів твого майбутнього.",
            },
            {
                "grammar": "Argumentieren — аргументація",
                "grammar_task": "Структура:\nТвердження: Ich bin der Meinung, dass...\nАргумент: Das liegt daran, dass...\nПриклад: Zum Beispiel...\nВисновок: Deshalb / Daher...\n\nНапиши 2 повних аргументи: 'Warum ist Deutsch wichtig für mich?'",
                "words": "der Standpunkt — точка зору\ndie Meinung — думка\ndas Argument — аргумент\nüberzeugen — переконувати\nwidersprechen — заперечувати\nzustimmen — погоджуватися\nfolglich — отже\ndaher — тому\ndemzufolge — відповідно\nzusammenfassend — підсумовуючи",
                "speaking": "Аргументуй чому ти хочеш залишитись в Німеччині. 5 хвилин без зупинки.",
                "writing": "Напиши есе 15+ речень: 'Warum lerne ich Deutsch?'",
            },
        ],
    },
    6: {
        "theme": "Контраст і повторення", "emoji": "🔄",
        "levels": [
            {
                "grammar": "kein...sondern + aber + obwohl",
                "grammar_task": "• kein...sondern:\n  Das ist kein Fehler, sondern eine Chance.\n• aber:\n  Deutsch ist schwer, aber ich lerne es.\n• obwohl:\n  Obwohl ich müde bin, übe ich weiter.\n\nНапиши по 4 речення з кожним (разом 12).",
                "words": "der Fehler — помилка\ndie Chance — шанс\nder Unterschied — різниця\ndagegen — натомість\nim Gegenteil — навпаки\nstattdessen — замість цього\nhingegen — тоді як\neinerseits — з одного боку\nandererseits — з іншого боку\ntrotzdem — попри це",
                "speaking": "Повторення тижня: розкажи про себе, плани, місто, минуле — все разом. 5 хвилин.",
                "writing": "Напиши 15 речень — підсумок тижня. Що вивчив? Що важко? Що далі?",
            },
            {
                "grammar": "Повторення A2+ — змішана граматика",
                "grammar_task": "Напиши текст 15 речень: 'Mein Leben in Deutschland'\n\nВикористай обов'язково:\n• Perfekt\n• Modalverben\n• weil або obwohl\n• sowohl...als auch або kein...sondern",
                "words": "die Integration — інтеграція\ndie Gesellschaft — суспільство\nder Alltag — повсякдення\nsich anpassen — адаптуватися\ndie Kultur — культура\nder Wert — цінність\ndie Gemeinschaft — спільнота\nbeitragen — робити внесок\ngehören — належати\ndie Teilnahme — участь",
                "speaking": "Вільна розмова 10 хвилин — будь-яка тема.",
                "writing": "Напиши есе 'Mein Leben in Deutschland' — мінімум 15 речень.",
            },
            {
                "grammar": "Повторення B1 — складний текст",
                "grammar_task": "Напиши структурований текст 20 речень: 'Meine Zukunft in Deutschland'\n\nСтруктура:\n1. Вступ — хто ти і де зараз\n2. Теперішнє — що робиш\n3. Плани — що хочеш досягти\n4. Труднощі — obwohl, trotzdem\n5. Висновок — Deshalb / Daher",
                "words": "die Perspektive — перспектива\ndie Karriere — кар'єра\nambitioniert — амбітний\nverwirklichen — реалізовувати\ndie Vision — бачення\nanstreben — прагнути\nlangfristig — довгостроковий\nnachhaltig — сталий\ngestalten — формувати\nverantwortlich — відповідальний",
                "speaking": "Презентуй себе і свої цілі як на офіційній зустрічі. 10 хвилин. Без нотаток.",
                "writing": "Напиши 'Meine Zukunft in Deutschland' — 20+ речень.",
            },
        ],
    },
}


def get_level(day: int) -> int:
    if day < 30:
        return 0
    elif day < 90:
        return 1
    else:
        return 2


def get_day_content(day: int) -> dict:
    weekday = day % 7
    level = get_level(day)
    plan = WEEKLY_PLAN[weekday]
    content = plan["levels"][level]
    return {"theme": plan["theme"], "emoji": plan["emoji"], **content}


async def post_german(context):
    day = max(0, (datetime.date.today() - START_DATE).days)
    c = get_day_content(day)
    today_str = datetime.date.today().strftime('%d.%m.%Y')
    level_labels = ["A2", "A2+", "B1"]
    level_label = level_labels[get_level(day)]

    msg = (
        f"{c['emoji']} НІМЕЦЬКА — ДЕНЬ {day + 1} [{level_label}]\n"
        f"Тема: {c['theme']}\n"
        f"{today_str}\n"
        f"{'─' * 30}\n\n"
        f"📚 СЛОВА — повтори вголос 3 рази:\n\n"
        f"{c['words']}\n\n"
        f"{'─' * 30}\n\n"
        f"📝 ГРАМАТИКА — {c['grammar']}\n\n"
        f"{c['grammar_task']}\n\n"
        f"{'─' * 30}\n\n"
        f"🎧 СЛУХАННЯ — 30 хв\n"
        f"Easy German на YouTube — тема: {c['theme']}\n"
        f"Дивись з німецькими субтитрами. Повторюй вголос.\n\n"
        f"{'─' * 30}\n\n"
        f"💬 ГОВОРІННЯ — 60 хв\n"
        f"{c['speaking']}\n\n"
        f"{'─' * 30}\n\n"
        f"✍️ ПИСЬМО — 30 хв\n"
        f"{c['writing']}\n\n"
        f"{'─' * 30}\n"
        f"Viel Erfolg! 💪"
    )

    if len(msg) <= 4096:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
    else:
        for chunk in [msg[i:i+4096] for i in range(0, len(msg), 4096)]:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=chunk)


async def german(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Готую завдання...')
    await post_german(context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        '🇩🇪 НІМЕЦЬКА — Щоденні завдання\n\n'
        'Щодня о 13:00 — завдання з німецької.\n\n'
        'Місяць 1 — A2\n'
        'Місяці 2-3 — A2+\n'
        'Місяці 4-6 — B1\n\n'
        '/german — отримати завдання зараз'
    )
    await update.message.reply_text(msg)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('german', german))
    app.job_queue.run_daily(post_german, time=time(hour=12, minute=0))
    print('Бот запущено')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
