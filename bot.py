import os
import asyncio
import re
import feedparser
import datetime
from datetime import time
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

START_DATE = datetime.date(2026, 4, 20)

# ================================
# 7 ТЕМ — 3 РІВНІ СКЛАДНОСТІ
# Місяць 1 = рівень 0 (A2)
# Місяць 2-3 = рівень 1 (A2+)
# Місяць 4-6 = рівень 2 (B1)
# ================================

WEEKLY_PLAN = {
    0: {  # Понеділок — Я і моє життя
        "theme": "Я і моє життя",
        "emoji": "👤",
        "levels": [
            {
                "grammar": "Präsens — теперішній час",
                "grammar_task": (
                    "Дієслова: sein, haben, wohnen, arbeiten, lernen, heißen\n\n"
                    "Напиши 10 речень про себе:\n"
                    "• Ich heiße...\n"
                    "• Ich wohne in...\n"
                    "• Ich lerne Deutsch, weil..."
                ),
                "words": (
                    "wohnen — жити (десь)\narbeiten — працювати\nlernen — вчитися\n"
                    "heißen — називатися\nkommen aus — походити з\nsprechen — говорити\n"
                    "verstehen — розуміти\nbrauchen — потребувати\nsuchen — шукати\nfinden — знаходити"
                ),
                "speaking": "Розкажи про себе: Хто ти? Звідки? Чому в Німеччині? Що вчиш?",
                "writing": "Напиши 10 речень про свій день сьогодні.",
            },
            {
                "grammar": "Präsens + weil / denn",
                "grammar_task": (
                    "Поєднуй речення з weil і denn:\n\n"
                    "• Ich lerne Deutsch, weil ich in Deutschland wohne.\n"
                    "• Ich lerne Deutsch, denn ich brauche die Sprache.\n\n"
                    "Напиши 10 речень — 5 з weil, 5 з denn.\n"
                    "Увага: після weil дієслово йде в кінець!"
                ),
                "words": (
                    "die Ausbildung — навчання / учнівство\ndie Zukunft — майбутнє\n"
                    "der Erfolg — успіх\ndie Möglichkeit — можливість\nentscheiden — вирішувати\n"
                    "verbessern — покращувати\nverstehen — розуміти\nerreichen — досягати\n"
                    "bleiben — залишатися\nverändern — змінювати"
                ),
                "speaking": "Розкажи чому ти в Німеччині і що хочеш досягти. Використовуй weil і denn.",
                "writing": "Напиши 12 речень про свої цілі в Німеччині.",
            },
            {
                "grammar": "Präsens + weil / obwohl / trotzdem",
                "grammar_task": (
                    "Складні конструкції з контрастом:\n\n"
                    "• Obwohl es schwer ist, lerne ich jeden Tag.\n"
                    "• Ich lerne Deutsch, obwohl ich wenig Zeit habe.\n"
                    "• Es ist schwer. Trotzdem mache ich weiter.\n\n"
                    "Напиши 12 речень — по 4 з кожним сполучником."
                ),
                "words": (
                    "die Herausforderung — виклик\ndie Geduld — терпіння\nanstrengend — виснажливий\n"
                    "trotzdem — попри це\nobwohl — хоча\ndennoch — проте\nschaffen — справлятися\n"
                    "weitermachen — продовжувати\naufgeben — здаватися\nüberwinden — долати"
                ),
                "speaking": "Розкажи про труднощі і як ти з ними справляєшся. Використовуй obwohl і trotzdem.",
                "writing": "Напиши 15 речень — есе про себе і свої цілі.",
            },
        ],
    },
    1: {  # Вівторок — Плани і обов'язки
        "theme": "Плани і обов'язки",
        "emoji": "📋",
        "levels": [
            {
                "grammar": "Modalverben — kann, muss, soll, darf, will, möchte",
                "grammar_task": (
                    "Кожне модальне дієслово — 2 речення:\n\n"
                    "• Ich muss heute Deutsch lernen.\n"
                    "• Ich kann gut Englisch sprechen.\n"
                    "• Ich möchte in Deutschland arbeiten.\n\n"
                    "Разом 12 речень."
                ),
                "words": (
                    "müssen — мусити\nkönnen — могти\nsollen — слід\ndürfen — мати дозвіл\n"
                    "wollen — хотіти\nmöchten — хотіти (ввічливо)\nder Plan — план\n"
                    "die Aufgabe — завдання\npünktlich — вчасно\nregelmäßig — регулярно"
                ),
                "speaking": "Розкажи що ти мусиш зробити сьогодні і що хочеш зробити цього тижня.",
                "writing": "Напиши план на завтра — 10 речень з модальними дієсловами.",
            },
            {
                "grammar": "Modalverben + Infinitiv + damit / um...zu",
                "grammar_task": (
                    "Мета дії:\n\n"
                    "• Ich lerne Deutsch, um in Deutschland zu arbeiten.\n"
                    "• Ich spare Geld, damit ich eine Wohnung mieten kann.\n\n"
                    "Напиши 10 речень — 5 з um...zu, 5 з damit.\n"
                    "Увага: um...zu — один підмет, damit — різні підмети!"
                ),
                "words": (
                    "sparen — заощаджувати\nmieten — орендувати\nbewerben — подавати заяву\n"
                    "vorbereiten — готуватися\nbestehen — скласти (іспит)\ndie Bewerbung — заява\n"
                    "der Lebenslauf — резюме\ndie Stelle — посада\ndie Erfahrung — досвід\nerfolgreich — успішний"
                ),
                "speaking": "Розкажи про свої плани на наступні 6 місяців. Використовуй um...zu і damit.",
                "writing": "Напиши 12 речень про те, що ти робиш і навіщо.",
            },
            {
                "grammar": "Modalverben Konjunktiv II — könnte, müsste, sollte",
                "grammar_task": (
                    "Ввічливі і гіпотетичні висловлювання:\n\n"
                    "• Ich könnte mehr lernen. (міг би)\n"
                    "• Du solltest jeden Tag üben. (слід було б)\n"
                    "• Wir müssten früher anfangen. (мали б)\n\n"
                    "Напиши 12 речень з könnte, sollte, müsste."
                ),
                "words": (
                    "vorschlagen — пропонувати\nempfehlen — рекомендувати\nraten — радити\n"
                    "überlegen — обдумувати\nentscheiden — вирішувати\ndie Entscheidung — рішення\n"
                    "abwägen — зважувати\nder Vorteil — перевага\nder Nachteil — недолік\nvergleichen — порівнювати"
                ),
                "speaking": "Що ти міг би зробити краще? Що тобі слід змінити? Говори 5 хвилин.",
                "writing": "Напиши 15 речень — що б ти зробив інакше і чому.",
            },
        ],
    },
    2: {  # Середа — Місто і транспорт
        "theme": "Місто і транспорт",
        "emoji": "🏙️",
        "levels": [
            {
                "grammar": "Akkusativ + Trennbare Verben",
                "grammar_task": (
                    "Артиклі в Akkusativ: den / einen / die / eine / das / ein\n\n"
                    "Дієслова з префіксом — префікс в кінець:\n"
                    "• Ich steige in den Bus ein.\n"
                    "• Ich kaufe eine Fahrkarte.\n"
                    "• Ich steige an der Haltestelle aus.\n\n"
                    "Напиши 10 речень про поїздку містом."
                ),
                "words": (
                    "die Haltestelle — зупинка\neinsteigen — сідати (в транспорт)\naussteigen — виходити\n"
                    "umsteigen — пересідати\ndie Fahrkarte — квиток\nder Bahnhof — вокзал\n"
                    "die U-Bahn — метро\ndie Straßenbahn — трамвай\npünktlich — вчасно\ndie Verspätung — запізнення"
                ),
                "speaking": "Опиши як ти добираєшся до центру міста. Яким транспортом? Скільки часу?",
                "writing": "Напиши 10 речень про транспорт у Дортмунді.",
            },
            {
                "grammar": "Wechselpräpositionen — Akkusativ vs Dativ",
                "grammar_task": (
                    "Рух (Akkusativ) vs Місце (Dativ):\n\n"
                    "• Ich fahre in die Stadt. (куди? → Akkusativ)\n"
                    "• Ich bin in der Stadt. (де? → Dativ)\n"
                    "• Ich gehe an den Fluss. / Ich stehe an dem Fluss.\n\n"
                    "Прийменники: in, an, auf, über, unter, vor, hinter, neben, zwischen\n\n"
                    "Напиши 12 речень — по 6 Akkusativ і Dativ."
                ),
                "words": (
                    "das Rathaus — ратуша\ndie Innenstadt — центр міста\nder Marktplatz — ринкова площа\n"
                    "die Umgebung — околиці\nentfernt — на відстані\nin der Nähe — поруч\ngegenüber — навпроти\n"
                    "entlang — вздовж\nüberqueren — перетинати\ndie Kreuzung — перехрестя"
                ),
                "speaking": "Опиши де ти живеш — що є поруч, далеко, навпроти. Використовуй Dativ і Akkusativ.",
                "writing": "Напиши 12 речень — опис свого району в Дортмунді.",
            },
            {
                "grammar": "Relativsätze — відносні речення",
                "grammar_task": (
                    "Відносні займенники: der, die, das (який/яка/яке)\n\n"
                    "• Das ist der Bus, der zum Hauptbahnhof fährt.\n"
                    "• Die Stadt, in der ich wohne, heißt Dortmund.\n"
                    "• Das Ticket, das ich gekauft habe, ist günstig.\n\n"
                    "Напиши 12 речень з відносними реченнями."
                ),
                "words": (
                    "verbinden — з'єднувати\ndie Verbindung — з'єднання / зв'язок\nerreichbar — доступний\n"
                    "das Netz — мережа\ndie Linie — лінія\ndie Richtung — напрямок\n"
                    "abfahren — відправлятися\nankommen — прибувати\ndie Abfahrt — відправлення\ndie Ankunft — прибуття"
                ),
                "speaking": "Опиши місто використовуючи відносні речення. Наприклад: Dortmund ist eine Stadt, die...",
                "writing": "Напиши 15 речень — опис Дортмунда з відносними реченнями.",
            },
        ],
    },
    3: {  # Четвер — Запитання і відповіді
        "theme": "Запитання і відповіді",
        "emoji": "❓",
        "levels": [
            {
                "grammar": "W-Fragen + kein...sondern",
                "grammar_task": (
                    "Питальні слова: Wer? Was? Wo? Wann? Wie? Warum? Wohin? Womit?\n\n"
                    "kein...sondern = не... а (заперечення + корекція):\n"
                    "• Das ist kein Problem, sondern eine Chance.\n"
                    "• Ich lerne nicht Französisch, sondern Deutsch.\n\n"
                    "Напиши 5 W-Fragen з відповідями і 5 речень з kein...sondern."
                ),
                "words": (
                    "die Frage — запитання\ndie Antwort — відповідь\nfragen — питати\nantworten — відповідати\n"
                    "erklären — пояснювати\nverstehen — розуміти\nmeinen — мати на увазі\n"
                    "bedeuten — означати\nwiederholen — повторювати\nbestätigen — підтверджувати"
                ),
                "speaking": "Уяви що ти на співбесіді. Відповідай на запитання: Wer sind Sie? Was möchten Sie? Warum Deutsch?",
                "writing": "Напиши діалог 10 реплік — запитання і відповіді про себе.",
            },
            {
                "grammar": "Indirekte Fragen — непрямі запитання",
                "grammar_task": (
                    "Пряме → Непряме запитання:\n\n"
                    "• Wo ist der Bahnhof? → Ich möchte wissen, wo der Bahnhof ist.\n"
                    "• Wann kommt der Zug? → Kannst du mir sagen, wann der Zug kommt?\n"
                    "• Ist das richtig? → Ich frage mich, ob das richtig ist.\n\n"
                    "Увага: дієслово в кінець!\n\n"
                    "Напиши 10 непрямих запитань."
                ),
                "words": (
                    "möchte wissen — хотів би знати\nkannst du sagen — чи можеш сказати\n"
                    "ich frage mich — я питаю себе\nob — чи\nherausfinden — з'ясовувати\n"
                    "nachfragen — уточнювати\nklarstellen — прояснювати\nzweifeln — сумніватися\n"
                    "sicher sein — бути впевненим\nüberzeugen — переконувати"
                ),
                "speaking": "Постав 10 непрямих запитань про Ausbildung або роботу в Німеччині.",
                "writing": "Напиши 12 речень з непрямими запитаннями.",
            },
            {
                "grammar": "Konzessivsätze — obwohl, auch wenn, selbst wenn",
                "grammar_task": (
                    "Поступові речення:\n\n"
                    "• Obwohl ich müde bin, lerne ich weiter.\n"
                    "• Auch wenn es schwer ist, gebe ich nicht auf.\n"
                    "• Selbst wenn ich keine Zeit habe, übe ich täglich.\n\n"
                    "Напиши 12 речень — по 4 з кожною конструкцією."
                ),
                "words": (
                    "aufgeben — здаватися\nweitermachen — продовжувати\nbeharrlich — наполегливий\n"
                    "die Ausdauer — витривалість\nüberwinden — долати\ndie Schwierigkeit — труднощі\n"
                    "trotz — незважаючи на\nder Widerstand — опір\nstandhalten — витримувати\nsiegen — перемагати"
                ),
                "speaking": "Розкажи про труднощі у вивченні мови. Використовуй obwohl, auch wenn, selbst wenn.",
                "writing": "Напиши 15 речень — есе про наполегливість.",
            },
        ],
    },
    4: {  # П'ятниця — Минуле
        "theme": "Минуле",
        "emoji": "⏳",
        "levels": [
            {
                "grammar": "Perfekt з haben і sein",
                "grammar_task": (
                    "З haben: kaufen→gekauft, machen→gemacht, lernen→gelernt\n"
                    "З sein: gehen→gegangen, fahren→gefahren, kommen→gekommen\n\n"
                    "Напиши 10 речень про вчора — 5 з haben, 5 з sein:\n"
                    "• Ich habe gestern Deutsch gelernt.\n"
                    "• Ich bin heute in die Stadt gefahren."
                ),
                "words": (
                    "gestern — вчора\nvorgestern — позавчора\nletzte Woche — минулого тижня\n"
                    "letztes Jahr — минулого року\nfrüher — раніше\ndamals — тоді\n"
                    "schon — вже\nnoch nicht — ще не\nnie — ніколи\nimmer — завжди"
                ),
                "speaking": "Розкажи що ти робив вчора — від ранку до вечора. Тільки Perfekt.",
                "writing": "Напиши 10 речень про минулий тиждень.",
            },
            {
                "grammar": "Perfekt + Präteritum (sein/haben/Modalverben)",
                "grammar_task": (
                    "Präteritum використовують для: sein→war, haben→hatte, Modalverben:\n"
                    "• Ich war gestern müde.\n"
                    "• Ich hatte keine Zeit.\n"
                    "• Ich musste arbeiten. / Ich konnte nicht kommen.\n\n"
                    "Напиши 12 речень — 6 Perfekt + 6 Präteritum."
                ),
                "words": (
                    "war — був (sein)\nhatte — мав (haben)\nmusste — мусив\nkonnte — міг\n"
                    "wollte — хотів\ndurfte — мав дозвіл\ndie Vergangenheit — минуле\n"
                    "die Erfahrung — досвід\nprägen — формувати\nbeeinflussen — впливати"
                ),
                "speaking": "Розкажи про важливу подію у своєму житті. Використовуй Perfekt і Präteritum.",
                "writing": "Напиши 12 речень про те як ти опинився в Німеччині.",
            },
            {
                "grammar": "Plusquamperfekt — давноминулий час",
                "grammar_task": (
                    "Дія яка відбулась ДО іншої дії в минулому:\n\n"
                    "• Nachdem ich gegessen hatte, ging ich spazieren.\n"
                    "• Als ich ankam, hatte der Zug schon abgefahren.\n\n"
                    "hatte/war + Partizip II\n\n"
                    "Напиши 10 речень з Plusquamperfekt."
                ),
                "words": (
                    "nachdem — після того як\nals — коли (одноразово)\nbevor — перед тим як\n"
                    "bereits — вже (до того)\nzuvor — до цього\ndaraufhin — після цього\n"
                    "infolgedessen — внаслідок цього\nschließlich — врешті-решт\nzuletzt — наостанок\nendlich — нарешті"
                ),
                "speaking": "Розкажи про день коли ти переїхав до Дортмунда — що відбулось до і після.",
                "writing": "Напиши 15 речень використовуючи Perfekt, Präteritum і Plusquamperfekt.",
            },
        ],
    },
    5: {  # Субота — Складні думки
        "theme": "Складні думки",
        "emoji": "🧠",
        "levels": [
            {
                "grammar": "dass + sowohl...als auch",
                "grammar_task": (
                    "dass — що (підрядне речення):\n"
                    "• Ich denke, dass Deutsch wichtig ist.\n"
                    "• Es ist klar, dass ich jeden Tag üben muss.\n\n"
                    "sowohl...als auch — як... так і:\n"
                    "• Ich lerne sowohl Grammatik als auch Vokabeln.\n\n"
                    "Напиши 5 речень з dass і 5 з sowohl...als auch."
                ),
                "words": (
                    "denken — думати\nglauben — вважати\nmeinen — мати на увазі\nwissen — знати\n"
                    "verstehen — розуміти\nannehmen — припускати\nbehaupten — стверджувати\n"
                    "bezweifeln — сумніватися\nbeweisen — доводити\nakzeptieren — приймати"
                ),
                "speaking": "Розкажи що ти думаєш про вивчення мов. Використовуй dass і sowohl...als auch.",
                "writing": "Напиши 10 речень зі своїми думками про життя в Німеччині.",
            },
            {
                "grammar": "Zweiteilige Konnektoren — парні сполучники",
                "grammar_task": (
                    "• sowohl...als auch — як... так і\n"
                    "• weder...noch — ні... ні\n"
                    "• entweder...oder — або... або\n"
                    "• nicht nur...sondern auch — не тільки... але й\n\n"
                    "Напиши по 3 речення з кожним сполучником (разом 12)."
                ),
                "words": (
                    "einerseits — з одного боку\nandererseits — з іншого боку\nzudem — крім того\n"
                    "außerdem — до того ж\ndabei — при цьому\njedoch — однак\nallerdings — щоправда\n"
                    "immerhin — принаймні\nzumindest — щонайменше\ninsgesamt — загалом"
                ),
                "speaking": "Порівняй Україну і Німеччину. Використовуй парні сполучники.",
                "writing": "Напиши 12 речень — порівняння двох варіантів твого майбутнього.",
            },
            {
                "grammar": "Argumentieren auf Deutsch — аргументація",
                "grammar_task": (
                    "Структура аргументу:\n\n"
                    "Твердження: Ich bin der Meinung, dass...\n"
                    "Аргумент: Das liegt daran, dass... / Ein Grund dafür ist...\n"
                    "Приклад: Zum Beispiel...\n"
                    "Висновок: Deshalb / Daher / Folglich...\n\n"
                    "Напиши 2 повних аргументи на тему: 'Warum ist Deutsch wichtig für mich?'"
                ),
                "words": (
                    "der Standpunkt — точка зору\ndie Meinung — думка\ndas Argument — аргумент\n"
                    "überzeugen — переконувати\nwidersprechen — заперечувати\nzustimmen — погоджуватися\n"
                    "folglich — отже\ndaher — тому\ndemzufolge — відповідно\nzusammenfassend — підсумовуючи"
                ),
                "speaking": "Аргументуй чому ти хочеш залишитись в Німеччині. 5 хвилин без зупинки.",
                "writing": "Напиши есе 15+ речень: 'Warum lerne ich Deutsch?'",
            },
        ],
    },
    6: {  # Неділя — Контраст і повторення
        "theme": "Контраст і повторення",
        "emoji": "🔄",
        "levels": [
            {
                "grammar": "kein...sondern + aber + obwohl",
                "grammar_task": (
                    "• kein...sondern — не... а (виправлення):\n"
                    "  Das ist kein Fehler, sondern eine Chance.\n\n"
                    "• aber — але (проте):\n"
                    "  Deutsch ist schwer, aber ich lerne es.\n\n"
                    "• obwohl — хоча (попри те що):\n"
                    "  Obwohl ich müde bin, übe ich weiter.\n\n"
                    "Напиши по 4 речення з кожним (разом 12)."
                ),
                "words": (
                    "der Fehler — помилка\ndie Chance — шанс\nder Unterschied — різниця\n"
                    "dagegen — натомість\nim Gegenteil — навпаки\nstattdessen — замість цього\n"
                    "hingegen — тоді як\nwohingegen — тоді як\neinerseits — з одного боку\nandererseits — з іншого боку"
                ),
                "speaking": "Повторення тижня: розкажи про себе, плани, місто, і минуле — все разом. 5 хвилин.",
                "writing": "Напиши 15 речень — підсумок тижня. Що вивчив? Що важко? Що далі?",
            },
            {
                "grammar": "Повторення A2+ — змішана граматика",
                "grammar_task": (
                    "Сьогодні — вільне повторення. Напиши текст 15 речень на тему:\n\n"
                    "'Mein Leben in Deutschland'\n\n"
                    "Використай обов'язково:\n"
                    "• Perfekt (мин. час)\n"
                    "• Modalverben (kann, muss, möchte)\n"
                    "• weil або obwohl\n"
                    "• sowohl...als auch або kein...sondern"
                ),
                "words": (
                    "die Integration — інтеграція\ndie Gesellschaft — суспільство\nder Alltag — повсякдення\n"
                    "sich anpassen — адаптуватися\ndie Kultur — культура\nder Wert — цінність\n"
                    "die Gemeinschaft — спільнота\nbeitragen — робити внесок\ndie Teilnahme — участь\ngehören — належати"
                ),
                "speaking": "Вільна розмова 10 хвилин — будь-яка тема яку ти хочеш обговорити.",
                "writing": "Напиши есе 'Mein Leben in Deutschland' — мінімум 15 речень.",
            },
            {
                "grammar": "Повторення B1 — складний текст",
                "grammar_task": (
                    "Напиши структурований текст 20 речень:\n\n"
                    "'Meine Zukunft in Deutschland'\n\n"
                    "Структура:\n"
                    "1. Вступ — хто ти і де зараз (3-4 речення)\n"
                    "2. Теперішнє — що робиш зараз (4-5 речень)\n"
                    "3. Плани — що хочеш досягти (4-5 речень)\n"
                    "4. Труднощі — obwohl, trotzdem (3-4 речення)\n"
                    "5. Висновок — Deshalb / Daher (2-3 речення)"
                ),
                "words": (
                    "die Perspektive — перспектива\ndie Karriere — кар'єра\nambitioniert — амбітний\n"
                    "verwirklichen — реалізовувати\ndie Vision — бачення\nanstreben — прагнути\n"
                    "langfristig — довгостроковий\nnachhaltig — сталий\ndie Eigenverantwortung — особиста відповідальність\ngestalten — формувати"
                ),
                "speaking": "Презентуй себе і свої цілі як на офіційній зустрічі. 10 хвилин. Без нотаток.",
                "writing": "Напиши офіційний текст 'Meine Zukunft in Deutschland' — 20+ речень.",
            },
        ],
    },
}


# ================================
# ВИЗНАЧЕННЯ РІВНЯ
# Місяць 1 → рівень 0
# Місяці 2-3 → рівень 1
# Місяці 4-6 → рівень 2
# ================================

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
    return {
        "theme": plan["theme"],
        "emoji": plan["emoji"],
        "weekday": weekday,
        "level": level,
        **content,
    }


# ================================
# ДОПОМІЖНІ ФУНКЦІЇ
# ================================

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


# ================================
# HANDLERS
# ================================

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
    today = datetime.datetime.now().strftime('%d.%m.%Y')

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


async def post_german(context):
    day = max(0, (datetime.date.today() - START_DATE).days)
    c = get_day_content(day)
    today_str = datetime.date.today().strftime('%d.%m.%Y')

    level_labels = ["A2", "A2+", "B1"]
    level_label = level_labels[c["level"]]

    msg = (
        f"{c['emoji']} НІМЕЦЬКА — ДЕНЬ {day + 1} [{level_label}]\n"
        f"Тема: {c['theme']}\n"
        f"{today_str}\n"
        f"{'─' * 30}\n\n"
        f"📚 СЛОВА — вивчи і повтори вголос:\n\n"
        f"{c['words']}\n\n"
        f"{'─' * 30}\n\n"
        f"📝 ГРАМАТИКА — {c['grammar']}\n\n"
        f"{c['grammar_task']}\n\n"
        f"{'─' * 30}\n\n"
        f"🎧 СЛУХАННЯ — 30 хв\n"
        f"Easy German на YouTube — тема дня: {c['theme']}\n"
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
        chunks = [msg[i:i+4096] for i in range(0, len(msg), 4096)]
        for chunk in chunks:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=chunk)


async def digest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Збираю статті...')
    await post_digest(context)
    await update.message.reply_text('Дайджест опубліковано.')


async def german(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Готую завдання...')
    await post_german(context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        'ОБРІЙ — Щоденний дайджест\n\n'
        'Щодня о 09:00 — топ-8 найважливіших статей\n'
        'з провідних аналітичних джерел світу.\n\n'
        'Щодня о 13:00 — завдання з німецької мови.\n\n'
        'Рівні:\n'
        'Місяць 1 — A2\n'
        'Місяці 2-3 — A2+\n'
        'Місяці 4-6 — B1\n\n'
        '/digest — дайджест зараз\n'
        '/german — завдання з німецької зараз'
    )
    await update.message.reply_text(msg)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('digest', digest))
    app.add_handler(CommandHandler('german', german))

    # Дайджест о 09:00 CET (08:00 UTC)
    app.job_queue.run_daily(post_digest, time=time(hour=8, minute=0))

    # Німецька о 13:00 CET (12:00 UTC)
    app.job_queue.run_daily(post_german, time=time(hour=12, minute=0))

    print('ОБРІЙ started')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
