import os
import asyncio
import datetime
from datetime import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

START_DATE = datetime.date(2026, 4, 20)

# ================================
# 7 ТЕМ — ПОВНИЙ УРОК
# ================================

WEEKLY_PLAN = {
    0: {
        "theme": "Я і моє життя",
        "emoji": "👤",

        "words_title": "📚 СЛОВА — Тема: Я і моє життя",
        "words": [
            ("wohnen", "жити (десь)", "Ich wohne in Dortmund. — Я живу в Дортмунді."),
            ("arbeiten", "працювати", "Ich arbeite jeden Tag. — Я працюю щодня."),
            ("lernen", "вчитися / вчити", "Ich lerne Deutsch. — Я вчу німецьку."),
            ("heißen", "називатися / звати", "Ich heiße Yehor. — Мене звати Єгор."),
            ("kommen aus", "походити з", "Ich komme aus der Ukraine. — Я з України."),
            ("sprechen", "говорити", "Ich spreche ein bisschen Deutsch. — Я трохи говорю німецькою."),
            ("verstehen", "розуміти", "Ich verstehe das nicht. — Я цього не розумію."),
            ("brauchen", "потребувати", "Ich brauche mehr Übung. — Мені потрібно більше практики."),
            ("suchen", "шукати", "Ich suche eine Ausbildung. — Я шукаю учнівство."),
            ("finden", "знаходити / вважати", "Ich finde Deutsch interessant. — Я вважаю німецьку цікавою."),
        ],
        "words_tip": "💡 Порада: finden має два значення — 'знаходити' і 'вважати'. Ich finde es gut = Я вважаю це добрим.",

        "grammar_title": "📝 ГРАМАТИКА — Präsens (теперішній час)",
        "grammar_explanation": (
            "Präsens — це теперішній час. Використовується коли:\n"
            "• Ти говориш про те що відбувається зараз\n"
            "• Ти говориш про звички і регулярні дії\n"
            "• Ти говориш про факти\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ВІДМІНЮВАННЯ — lernen (вчити)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ich lerne       → я вчу\n"
            "du lernst       → ти вчиш\n"
            "er/sie/es lernt → він/вона вчить\n"
            "wir lernen      → ми вчимо\n"
            "ihr lernt       → ви вчите\n"
            "sie/Sie lernen  → вони/Ви вчать\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "НЕПРАВИЛЬНІ — sein і haben\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ich bin / ich habe\n"
            "du bist / du hast\n"
            "er ist / er hat\n"
            "wir sind / wir haben\n"
            "ihr seid / ihr habt\n"
            "sie sind / sie haben\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ ТИПОВІ ПОМИЛКИ:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ Ich bin heiße Yehor.\n"
            "✅ Ich heiße Yehor.\n\n"
            "❌ Ich lerne Deutsch jeden Tag.\n"
            "✅ Ich lerne jeden Tag Deutsch.\n\n"
            "❌ Er arbeite in Deutschland.\n"
            "✅ Er arbeitet in Deutschland. (er/sie/es → +t)"
        ),
        "grammar_tasks": (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 1 — Заповни пропуски\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ich ___ (heißen) Yehor.\n"
            "Er ___ (kommen) aus Polen.\n"
            "Wir ___ (lernen) Deutsch.\n"
            "Du ___ (arbeiten) viel.\n"
            "Sie ___ (sprechen) gut Englisch.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 2 — Напиши 10 речень\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Про себе — використай ці початки:\n"
            "1. Ich heiße...\n"
            "2. Ich komme aus...\n"
            "3. Ich wohne in...\n"
            "4. Ich lerne Deutsch, weil...\n"
            "5. Ich spreche...\n"
            "6. Ich arbeite / suche...\n"
            "7. Ich finde Deutsch...\n"
            "8. Ich brauche...\n"
            "9. Ich verstehe...\n"
            "10. Ich bin ... Jahre alt und...\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 3 — Переклади\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1. Я живу в Дортмунді вже рік.\n"
            "2. Він шукає роботу в Німеччині.\n"
            "3. Ми вчимо німецьку щодня.\n"
            "4. Ти розумієш це?\n"
            "5. Вона вважає це складним.\n\n"
            "✅ Відповіді завдання 1:\n"
            "heiße / kommt / lernen / arbeitest / sprechen"
        ),

        "practice_title": "💬 ПРАКТИКА — Говоріння і письмо",
        "speaking": (
            "🗣️ ГОВОРІННЯ — 60 хв\n\n"
            "Розкажи про себе вголос — як на офіційному знайомстві.\n\n"
            "Структура (говори по пунктах):\n"
            "1. Wie heißen Sie? → Ich heiße...\n"
            "2. Woher kommen Sie? → Ich komme aus...\n"
            "3. Wo wohnen Sie? → Ich wohne in...\n"
            "4. Was machen Sie? → Ich lerne / arbeite / suche...\n"
            "5. Warum lernen Sie Deutsch? → Ich lerne Deutsch, weil...\n\n"
            "Повтори мінімум 5 разів — кожен раз плавніше."
        ),
        "writing": (
            "✍️ ПИСЬМО — 30 хв\n\n"
            "Напиши текст 'Wer bin ich?' (Хто я?)\n\n"
            "Мінімум 12 речень. Структура:\n"
            "• 3 речення — хто ти і звідки\n"
            "• 3 речення — де живеш і що робиш\n"
            "• 3 речення — чому вчиш німецьку\n"
            "• 3 речення — твої плани в Німеччині"
        ),
        "fun_fact": "🧠 Цікаво: У німецькій всі іменники пишуться з великої літери — der Hund, die Stadt, das Buch. Це унікальна риса німецької мови!",
    },

    1: {
        "theme": "Плани і обов'язки",
        "emoji": "📋",

        "words_title": "📚 СЛОВА — Тема: Плани і обов'язки",
        "words": [
            ("müssen", "мусити / треба", "Ich muss jeden Tag üben. — Я мушу практикуватись щодня."),
            ("können", "могти / вміти", "Ich kann gut kochen. — Я вмію добре готувати."),
            ("wollen", "хотіти (рішуче)", "Ich will in Deutschland bleiben. — Я хочу залишитись в Німеччині."),
            ("möchten", "хотіти (ввічливо)", "Ich möchte Kaffee, bitte. — Я б хотів кави, будь ласка."),
            ("sollen", "слід / мати (за дорученням)", "Du sollst das nicht machen. — Тобі не слід цього робити."),
            ("dürfen", "мати дозвіл", "Darf ich hier warten? — Чи можна тут зачекати?"),
            ("der Plan", "план", "Ich habe einen Plan. — У мене є план."),
            ("die Aufgabe", "завдання", "Das ist meine Aufgabe. — Це моє завдання."),
            ("pünktlich", "вчасно", "Ich bin immer pünktlich. — Я завжди вчасно."),
            ("regelmäßig", "регулярно", "Ich lerne regelmäßig. — Я вчуся регулярно."),
        ],
        "words_tip": "💡 Різниця: wollen = я ХОЧУ (рішуче, для себе). möchten = я б хотів (ввічливо, прохання). Ich will ein Auto! vs Ich möchte einen Kaffee.",

        "grammar_title": "📝 ГРАМАТИКА — Modalverben (модальні дієслова)",
        "grammar_explanation": (
            "Модальні дієслова — це дієслова які змінюють значення іншого дієслова.\n"
            "Схема: Modalverb (2-га позиція) + інфінітив (в кінець)\n\n"
            "Ich muss Deutsch LERNEN. ✅\n"
            "Ich LERNEN muss Deutsch. ❌\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ТАБЛИЦЯ — всі форми\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "       müssen  können  wollen  dürfen  sollen\n"
            "ich    muss    kann    will    darf    soll\n"
            "du     musst   kannst  willst  darfst  sollst\n"
            "er/sie muss    kann    will    darf    soll\n"
            "wir    müssen  können  wollen  dürfen  sollen\n"
            "ihr    müsst   könnt   wollt   dürft   sollt\n"
            "sie    müssen  können  wollen  dürfen  sollen\n\n"
            "⚠️ Увага: ich і er/sie мають ОДНАКОВУ форму!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ ТИПОВІ ПОМИЛКИ:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ Ich muss lernen Deutsch.\n"
            "✅ Ich muss Deutsch lernen.\n\n"
            "❌ Ich kann nicht kommen heute.\n"
            "✅ Ich kann heute nicht kommen.\n\n"
            "❌ Er möchtet einen Kaffee.\n"
            "✅ Er möchte einen Kaffee. (без -t!)"
        ),
        "grammar_tasks": (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 1 — Заповни пропуски\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ich ___ heute arbeiten. (müssen)\n"
            "Er ___ gut Englisch sprechen. (können)\n"
            "Wir ___ in Deutschland bleiben. (wollen)\n"
            "Du ___ hier nicht rauchen. (dürfen)\n"
            "Sie ___ das Formular ausfüllen. (sollen)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 2 — Напиши 12 речень\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "По 2 речення з кожним дієсловом:\n"
            "müssen, können, wollen, möchten, sollen, dürfen\n\n"
            "Приклад:\n"
            "Ich muss heute Deutsch lernen.\n"
            "Ich muss morgen früh aufstehen.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 3 — Переклади\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1. Мені треба знайти роботу.\n"
            "2. Він вміє говорити трьома мовами.\n"
            "3. Чи можна тут сфотографувати?\n"
            "4. Ти маєш прийти вчасно.\n"
            "5. Ми хочемо залишитись в Дортмунді.\n\n"
            "✅ Відповіді завдання 1:\n"
            "muss / kann / wollen / darfst / sollen"
        ),

        "practice_title": "💬 ПРАКТИКА — Говоріння і письмо",
        "speaking": (
            "🗣️ ГОВОРІННЯ — 60 хв\n\n"
            "Розкажи про свої плани і обов'язки.\n\n"
            "Говори по пунктах вголос:\n"
            "1. Was musst du heute machen?\n"
            "   → Ich muss heute...\n"
            "2. Was kannst du gut?\n"
            "   → Ich kann gut...\n"
            "3. Was willst du in einem Jahr erreichen?\n"
            "   → Ich will...\n"
            "4. Was möchtest du lernen?\n"
            "   → Ich möchte...\n"
            "5. Was darfst du nicht vergessen?\n"
            "   → Ich darf nicht vergessen...\n\n"
            "Повтори мінімум 5 разів."
        ),
        "writing": (
            "✍️ ПИСЬМО — 30 хв\n\n"
            "Напиши текст 'Meine Pläne' (Мої плани)\n\n"
            "Мінімум 12 речень. Структура:\n"
            "• 3 речення — що ти мусиш зробити цього тижня (müssen)\n"
            "• 3 речення — що ти вмієш і не вмієш (können)\n"
            "• 3 речення — що ти хочеш досягти (wollen/möchten)\n"
            "• 3 речення — що тобі слід робити щодня (sollen)"
        ),
        "fun_fact": "🧠 Цікаво: Modalverben у німецькій мають окремі форми в однині — ich muss, er muss (без -t). Це виняток з правил! Звичайні дієслова: er lern-t, er arbeit-et.",
    },

    2: {
        "theme": "Місто і транспорт",
        "emoji": "🏙️",

        "words_title": "📚 СЛОВА — Тема: Місто і транспорт",
        "words": [
            ("die Haltestelle", "зупинка", "Die Haltestelle ist um die Ecke. — Зупинка за рогом."),
            ("einsteigen", "сідати (в транспорт)", "Ich steige in den Bus ein. — Я сідаю в автобус."),
            ("aussteigen", "виходити (з транспорту)", "Ich steige an der Haltestelle aus. — Я виходжу на зупинці."),
            ("umsteigen", "пересідати", "Ich muss in die U-Bahn umsteigen. — Мені треба пересісти на метро."),
            ("die Fahrkarte", "квиток", "Ich kaufe eine Fahrkarte. — Я купую квиток."),
            ("der Bahnhof", "вокзал", "Der Bahnhof ist groß. — Вокзал великий."),
            ("die U-Bahn", "метро", "Ich fahre mit der U-Bahn. — Я їду на метро."),
            ("die Straßenbahn", "трамвай", "Die Straßenbahn kommt pünktlich. — Трамвай приходить вчасно."),
            ("die Verspätung", "запізнення", "Der Zug hat Verspätung. — Поїзд запізнюється."),
            ("überqueren", "перетинати", "Ich überquere die Straße. — Я переходжу вулицю."),
        ],
        "words_tip": "💡 einsteigen / aussteigen / umsteigen — всі з префіксом! Префікс завжди йде в кінець речення: Ich steige EIN. Ich steige AUS. Ich steige UM.",

        "grammar_title": "📝 ГРАМАТИКА — Akkusativ + Trennbare Verben",
        "grammar_explanation": (
            "ЧАСТИНА 1 — Akkusativ (знахідний відмінок)\n\n"
            "Akkusativ = відповідає на питання 'кого? що?'\n"
            "Змінюється тільки чоловічий рід (der → den)!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "         Nominativ → Akkusativ\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "чол.  der Bus    → den Bus\n"
            "      ein Bus    → einen Bus\n"
            "жін.  die Bahn   → die Bahn  (не змінюється!)\n"
            "      eine Bahn  → eine Bahn\n"
            "сер.  das Auto   → das Auto  (не змінюється!)\n"
            "      ein Auto   → ein Auto\n\n"
            "Ich nehme DEN Bus. ✅ (чол. → den)\n"
            "Ich nehme DIE U-Bahn. ✅ (жін. → die)\n"
            "Ich kaufe EIN Ticket. ✅ (сер. → ein)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЧАСТИНА 2 — Trennbare Verben\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Дієслова з префіксом — префікс іде В КІНЕЦЬ:\n\n"
            "einsteigen → Ich steige in den Bus EIN.\n"
            "aussteigen → Ich steige an der Haltestelle AUS.\n"
            "umsteigen  → Ich steige in die U-Bahn UM.\n"
            "abfahren   → Der Zug fährt um 10 Uhr AB.\n\n"
            "⚠️ ТИПОВІ ПОМИЛКИ:\n"
            "❌ Ich einsteige in den Bus.\n"
            "✅ Ich steige in den Bus ein.\n\n"
            "❌ Ich kaufe einen die Fahrkarte.\n"
            "✅ Ich kaufe eine Fahrkarte. (жін. рід!)"
        ),
        "grammar_tasks": (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 1 — der/die/das → den/die/das\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ich nehme ___ Bus. (der)\n"
            "Ich kaufe ___ Fahrkarte. (die)\n"
            "Er nimmt ___ Zug. (der)\n"
            "Wir nehmen ___ Auto. (das)\n"
            "Sie kauft ___ Ticket. (das)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 2 — постав префікс правильно\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ich ___ in den Bus ___. (einsteigen)\n"
            "Er ___ an der Haltestelle ___. (aussteigen)\n"
            "Wir ___ in die U-Bahn ___. (umsteigen)\n"
            "Der Zug ___ um 9 Uhr ___. (abfahren)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 3 — опиши маршрут\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Напиши 10 речень як ти їдеш від дому до центру міста.\n"
            "Використай: einsteigen, aussteigen, umsteigen,\n"
            "kaufen, nehmen, fahren, ankommen\n\n"
            "✅ Відповіді завдання 1:\n"
            "den / eine / den / das / ein\n"
            "✅ Відповіді завдання 2:\n"
            "steige...ein / steigt...aus / steigen...um / fährt...ab"
        ),

        "practice_title": "💬 ПРАКТИКА — Говоріння і письмо",
        "speaking": (
            "🗣️ ГОВОРІННЯ — 60 хв\n\n"
            "Опиши свій маршрут містом вголос.\n\n"
            "Говори по пунктах:\n"
            "1. Wie kommst du zur Arbeit / zur Schule?\n"
            "   → Ich fahre mit dem/der...\n"
            "2. Wo steigst du ein?\n"
            "   → Ich steige an der Haltestelle... ein.\n"
            "3. Musst du umsteigen?\n"
            "   → Ja, ich steige... um. / Nein, ich fahre direkt.\n"
            "4. Wie lange dauert die Fahrt?\n"
            "   → Die Fahrt dauert... Minuten.\n"
            "5. Was kostet die Fahrkarte?\n"
            "   → Die Fahrkarte kostet...\n\n"
            "Повтори маршрут 5 разів."
        ),
        "writing": (
            "✍️ ПИСЬМО — 30 хв\n\n"
            "Напиши текст 'Mein Weg in die Stadt' (Мій шлях до міста)\n\n"
            "Мінімум 12 речень. Включи:\n"
            "• Яким транспортом їдеш\n"
            "• Де сідаєш і виходиш\n"
            "• Чи пересідаєш\n"
            "• Скільки коштує квиток\n"
            "• Що бачиш з вікна"
        ),
        "fun_fact": "🧠 Цікаво: У Дортмунді є 6 ліній U-Bahn і 4 лінії Straßenbahn. Квиток дійсний 90 хвилин і можна пересідати скільки завгодно разів!",
    },

    3: {
        "theme": "Запитання і відповіді",
        "emoji": "❓",

        "words_title": "📚 СЛОВА — Тема: Запитання і відповіді",
        "words": [
            ("fragen", "питати", "Ich frage den Lehrer. — Я питаю вчителя."),
            ("antworten", "відповідати", "Er antwortet auf meine Frage. — Він відповідає на моє питання."),
            ("erklären", "пояснювати", "Kannst du das erklären? — Ти можеш це пояснити?"),
            ("meinen", "мати на увазі / вважати", "Was meinst du damit? — Що ти маєш на увазі?"),
            ("bedeuten", "означати", "Was bedeutet dieses Wort? — Що означає це слово?"),
            ("wiederholen", "повторювати", "Können Sie das wiederholen? — Чи можете повторити?"),
            ("verstehen", "розуміти", "Ich verstehe das nicht. — Я не розумію цього."),
            ("die Frage", "питання", "Das ist eine gute Frage. — Це гарне питання."),
            ("die Antwort", "відповідь", "Ich weiß die Antwort nicht. — Я не знаю відповіді."),
            ("kein...sondern", "не... а", "Das ist kein Fehler, sondern eine Chance. — Це не помилка, а шанс."),
        ],
        "words_tip": "💡 antworten auf + Akkusativ: Ich antworte AUF die Frage. Не кажи: Ich antworte die Frage ❌",

        "grammar_title": "📝 ГРАМАТИКА — W-Fragen + kein...sondern",
        "grammar_explanation": (
            "ЧАСТИНА 1 — W-Fragen (питальні слова)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Wer?    → Хто?      Wer bist du?\n"
            "Was?    → Що?       Was machst du?\n"
            "Wo?     → Де?       Wo wohnst du?\n"
            "Wohin?  → Куди?     Wohin fährst du?\n"
            "Woher?  → Звідки?   Woher kommst du?\n"
            "Wann?   → Коли?     Wann kommst du?\n"
            "Wie?    → Як?       Wie heißt du?\n"
            "Warum?  → Чому?     Warum lernst du Deutsch?\n"
            "Wie oft?→ Як часто? Wie oft übst du?\n"
            "Wie lange?→ Як довго? Wie lange lernst du schon?\n\n"
            "⚠️ У питанні дієслово завжди на 2-му місці!\n"
            "Wo WOHNST du? ✅\n"
            "Wo du wohnst? ❌\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЧАСТИНА 2 — kein...sondern\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "kein...sondern = не... а (виправлення)\n\n"
            "Das ist kein Problem, sondern eine Chance.\n"
            "Це не проблема, а шанс.\n\n"
            "Ich lerne nicht Französisch, sondern Deutsch.\n"
            "Я вчу не французьку, а німецьку.\n\n"
            "⚠️ nicht...sondern — для дієслів і прикметників\n"
            "⚠️ kein...sondern — для іменників\n\n"
            "Er ist nicht müde, sondern krank. ✅\n"
            "Das ist kein Hund, sondern eine Katze. ✅"
        ),
        "grammar_tasks": (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 1 — правильне питальне слово\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "___ heißt du? (як)\n"
            "___ kommst du? (звідки)\n"
            "___ wohnst du? (де)\n"
            "___ lernst du Deutsch? (чому)\n"
            "___ lange lernst du schon? (як довго)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 2 — kein...sondern або nicht...sondern\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Das ist ___ Fehler, ___ eine Chance.\n"
            "Ich bin ___ müde, ___ krank.\n"
            "Er hat ___ Auto, ___ ein Fahrrad.\n"
            "Sie lernt ___ langsam, ___ regelmäßig.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 3 — склади 10 запитань\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Уяви що ти знайомишся з новою людиною.\n"
            "Напиши 10 запитань про неї і відповіді.\n"
            "Використай різні W-Wörter.\n\n"
            "✅ Відповіді завдання 1:\n"
            "Wie / Woher / Wo / Warum / Wie\n"
            "✅ Відповіді завдання 2:\n"
            "kein...sondern / nicht...sondern / kein...sondern / nicht...sondern"
        ),

        "practice_title": "💬 ПРАКТИКА — Говоріння і письмо",
        "speaking": (
            "🗣️ ГОВОРІННЯ — 60 хв\n\n"
            "Уяви що ти на офіційній зустрічі або співбесіді.\n\n"
            "Відповідай вголос на ці запитання:\n"
            "1. Wie heißen Sie?\n"
            "2. Woher kommen Sie?\n"
            "3. Wo wohnen Sie?\n"
            "4. Was machen Sie hier in Deutschland?\n"
            "5. Warum lernen Sie Deutsch?\n"
            "6. Wie lange lernen Sie schon Deutsch?\n"
            "7. Was sind Ihre Ziele in Deutschland?\n"
            "8. Was können Sie gut?\n\n"
            "Потім поміняйся ролями — задавай питання собі сам."
        ),
        "writing": (
            "✍️ ПИСЬМО — 30 хв\n\n"
            "Напиши діалог 'Erstes Kennenlernen' (Перше знайомство)\n\n"
            "Мінімум 16 реплік (8 запитань + 8 відповідей).\n"
            "Використай мінімум 6 різних W-Fragen.\n"
            "Додай 3 речення з kein...sondern або nicht...sondern."
        ),
        "fun_fact": "🧠 Цікаво: У німецькій є слово 'Fingerspitzengefühl' (букв. 'відчуття кінчиків пальців') — означає тонке чуття ситуації. Таких слів в інших мовах просто немає!",
    },

    4: {
        "theme": "Минуле",
        "emoji": "⏳",

        "words_title": "📚 СЛОВА — Тема: Минуле",
        "words": [
            ("gestern", "вчора", "Gestern war ich müde. — Вчора я був втомлений."),
            ("letzte Woche", "минулого тижня", "Letzte Woche habe ich viel gelernt. — Минулого тижня я багато вчився."),
            ("früher", "раніше", "Früher habe ich in Kyiv gewohnt. — Раніше я жив у Києві."),
            ("damals", "тоді / у той час", "Damals war alles anders. — Тоді все було інакше."),
            ("schon", "вже", "Ich habe das schon gemacht. — Я це вже зробив."),
            ("noch nicht", "ще не", "Ich habe das noch nicht gemacht. — Я цього ще не зробив."),
            ("nie", "ніколи", "Ich war nie in Berlin. — Я ніколи не був у Берліні."),
            ("plötzlich", "раптово", "Plötzlich hat es geregnet. — Раптово пішов дощ."),
            ("endlich", "нарешті", "Endlich habe ich es geschafft! — Нарешті я впорався!"),
            ("leider", "на жаль", "Leider habe ich den Bus verpasst. — На жаль я пропустив автобус."),
        ],
        "words_tip": "💡 schon vs noch nicht: Hast du gegessen? Ja, ich habe SCHON gegessen. / Nein, ich habe NOCH NICHT gegessen.",

        "grammar_title": "📝 ГРАМАТИКА — Perfekt (минулий час)",
        "grammar_explanation": (
            "Perfekt — найуживаніший минулий час у розмовній мові.\n\n"
            "Схема: haben/sein (2-га позиція) + Partizip II (в кінець)\n\n"
            "Ich HABE Deutsch GELERNT. ✅\n"
            "Ich BIN nach Hause GEGANGEN. ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "PARTIZIP II — як утворити?\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Правильні: ge + Stamm + t\n"
            "lernen → ge-lern-t\n"
            "machen → ge-mach-t\n"
            "kaufen → ge-kauf-t\n\n"
            "Неправильні (треба вчити!):\n"
            "gehen   → gegangen\n"
            "kommen  → gekommen\n"
            "fahren  → gefahren\n"
            "sehen   → gesehen\n"
            "essen   → gegessen\n"
            "schreiben → geschrieben\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "HABEN або SEIN?\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "SEIN — рух або зміна стану:\n"
            "gehen, fahren, kommen, fliegen,\n"
            "aufstehen, einschlafen, werden\n\n"
            "HABEN — все інше:\n"
            "lernen, machen, kaufen, essen,\n"
            "arbeiten, schreiben, sehen\n\n"
            "⚠️ ТИПОВІ ПОМИЛКИ:\n"
            "❌ Ich bin gegessen.\n"
            "✅ Ich habe gegessen.\n\n"
            "❌ Ich habe nach Hause gegangen.\n"
            "✅ Ich bin nach Hause gegangen."
        ),
        "grammar_tasks": (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 1 — haben чи sein?\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ich ___ gestern viel gelernt.\n"
            "Er ___ nach Berlin gefahren.\n"
            "Wir ___ einen Film gesehen.\n"
            "Sie ___ früh aufgestanden.\n"
            "Ich ___ Deutsch geübt.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 2 — утвори Partizip II\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "lernen → ___\n"
            "gehen → ___\n"
            "kaufen → ___\n"
            "kommen → ___\n"
            "machen → ___\n"
            "fahren → ___\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 3 — розкажи вчорашній день\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Напиши 12 речень у Perfekt про те\n"
            "що ти робив вчора від ранку до вечора.\n\n"
            "✅ Відповіді завдання 1:\n"
            "habe / ist / haben / ist / habe\n"
            "✅ Відповіді завдання 2:\n"
            "gelernt / gegangen / gekauft / gekommen / gemacht / gefahren"
        ),

        "practice_title": "💬 ПРАКТИКА — Говоріння і письмо",
        "speaking": (
            "🗣️ ГОВОРІННЯ — 60 хв\n\n"
            "Розкажи про вчорашній день — тільки Perfekt!\n\n"
            "Орієнтовна структура:\n"
            "1. Wann bist du aufgestanden?\n"
            "   → Ich bin um... Uhr aufgestanden.\n"
            "2. Was hast du zum Frühstück gegessen?\n"
            "   → Ich habe... gegessen.\n"
            "3. Wohin bist du gegangen/gefahren?\n"
            "   → Ich bin... gegangen.\n"
            "4. Was hast du gelernt/gemacht?\n"
            "   → Ich habe... gelernt/gemacht.\n"
            "5. Wann bist du schlafen gegangen?\n"
            "   → Ich bin um... Uhr schlafen gegangen.\n\n"
            "Повтори розповідь 5 разів — все плавніше."
        ),
        "writing": (
            "✍️ ПИСЬМО — 30 хв\n\n"
            "Напиши текст 'Mein gestriger Tag' (Мій вчорашній день)\n\n"
            "Мінімум 12 речень у Perfekt. Включи:\n"
            "• Коли прокинувся\n"
            "• Що їв і пив\n"
            "• Куди їхав\n"
            "• Що вчив або робив\n"
            "• Що дивився або читав\n"
            "• Коли ліг спати\n"
            "Використай: gestern, dann, danach, schließlich, endlich"
        ),
        "fun_fact": "🧠 Цікаво: У розмовній мові німці майже не використовують Präteritum (простий минулий) — тільки Perfekt. Präteritum — це для книжок і газет. Тому вчи Perfekt першим!",
    },

    5: {
        "theme": "Складні думки",
        "emoji": "🧠",

        "words_title": "📚 СЛОВА — Тема: Складні думки",
        "words": [
            ("denken", "думати", "Ich denke, dass das richtig ist. — Я думаю, що це правильно."),
            ("glauben", "вважати / вірити", "Ich glaube, er kommt bald. — Я вважаю, він незабаром прийде."),
            ("meinen", "мати на увазі", "Was meinst du damit? — Що ти маєш на увазі?"),
            ("sowohl...als auch", "як... так і", "Ich lerne sowohl Grammatik als auch Vokabeln."),
            ("weder...noch", "ні... ні", "Ich spreche weder Spanisch noch Französisch."),
            ("entweder...oder", "або... або", "Entweder lernst du jetzt, oder du lernst morgen."),
            ("nicht nur...sondern auch", "не тільки... але й", "Ich lerne nicht nur Deutsch, sondern auch Englisch."),
            ("einerseits...andererseits", "з одного боку... з іншого", "Einerseits ist es schwer, andererseits macht es Spaß."),
            ("außerdem", "крім того / до того ж", "Ich lerne Deutsch. Außerdem lese ich jeden Tag."),
            ("insgesamt", "загалом / в цілому", "Insgesamt bin ich zufrieden. — Загалом я задоволений."),
        ],
        "words_tip": "💡 dass-речення: після dass дієслово йде В КІНЕЦЬ! Ich denke, dass Deutsch wichtig IST. ✅ Ich denke, dass IST Deutsch wichtig. ❌",

        "grammar_title": "📝 ГРАМАТИКА — dass + парні сполучники",
        "grammar_explanation": (
            "ЧАСТИНА 1 — dass-Sätze\n\n"
            "dass = що (підрядне речення)\n"
            "Після dass дієслово ЗАВЖДИ В КІНЕЦЬ!\n\n"
            "Ich denke, dass Deutsch wichtig ist.\n"
            "Я думаю, що німецька важлива.\n\n"
            "Es ist klar, dass ich jeden Tag üben muss.\n"
            "Зрозуміло, що я маю практикуватись щодня.\n\n"
            "Ich weiß, dass er in Dortmund wohnt.\n"
            "Я знаю, що він живе в Дортмунді.\n\n"
            "Після: denken, glauben, wissen, sagen,\n"
            "finden, hoffen, meinen, es ist klar/wichtig/schön\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЧАСТИНА 2 — парні сполучники\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "sowohl...als auch (як... так і):\n"
            "Ich lerne sowohl Grammatik als auch Vokabeln.\n\n"
            "weder...noch (ні... ні):\n"
            "Ich spreche weder Russisch noch Polnisch.\n\n"
            "entweder...oder (або... або):\n"
            "Entweder lernst du jetzt, oder du schläfst.\n\n"
            "nicht nur...sondern auch (не тільки... але й):\n"
            "Ich lerne nicht nur Deutsch, sondern auch Englisch.\n\n"
            "⚠️ ТИПОВІ ПОМИЛКИ:\n"
            "❌ Ich denke, dass ist Deutsch wichtig.\n"
            "✅ Ich denke, dass Deutsch wichtig ist.\n\n"
            "❌ Sowohl ich als auch er lernen Deutsch.\n"
            "✅ Sowohl ich als auch er lernt Deutsch.\n"
            "(після sowohl...als auch — однина!)"
        ),
        "grammar_tasks": (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 1 — постав дієслово правильно\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ich denke, dass Deutsch ___ wichtig. (sein)\n"
            "Es ist klar, dass ich jeden Tag ___ muss. (üben)\n"
            "Ich weiß, dass er in Dortmund ___. (wohnen)\n"
            "Ich glaube, dass das ___ ist. (richtig)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 2 — вибери правильний сполучник\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ich lerne ___ Grammatik ___ Vokabeln. (sowohl/weder/entweder)\n"
            "Ich spreche ___ Spanisch ___ Italienisch. (sowohl/weder/entweder)\n"
            "___ lernst du jetzt, ___ du lernst morgen. (sowohl/weder/entweder)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ЗАВДАННЯ 3 — напиши свої думки\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Напиши 12 речень про вивчення мови:\n"
            "• 4 речення з dass\n"
            "• 4 речення з парними сполучниками\n"
            "• 4 речення з außerdem, einerseits, insgesamt\n\n"
            "✅ Відповіді завдання 1:\n"
            "ist / üben / wohnt / richtig\n"
            "✅ Відповіді завдання 2:\n"
            "sowohl...als auch / weder...noch / entweder...oder"
        ),

        "practice_title": "💬 ПРАКТИКА — Говоріння і письмо",
        "speaking": (
            "🗣️ ГОВОРІННЯ — 60 хв\n\n"
            "Розкажи свою думку про вивчення мов.\n\n"
            "Говори по пунктах:\n"
            "1. Was denkst du über das Deutschlernen?\n"
            "   → Ich denke, dass...\n"
            "2. Was ist schwer, was ist leicht?\n"
            "   → Sowohl... als auch... / Einerseits... andererseits...\n"
            "3. Was lernst du außer Deutsch?\n"
            "   → Ich lerne nicht nur... sondern auch...\n"
            "4. Was magst du an Deutschland?\n"
            "   → Ich finde, dass...\n"
            "5. Was ist dein Ziel?\n"
            "   → Ich glaube, dass ich... kann.\n\n"
            "Повтори 5 разів — кожен раз додавай нові деталі."
        ),
        "writing": (
            "✍️ ПИСЬМО — 30 хв\n\n"
            "Напиши текст 'Warum lerne ich Deutsch?' (Чому я вчу німецьку?)\n\n"
            "Мінімум 15 речень. Структура:\n"
            "• Вступ — загальна думка (2-3 речення з dass)\n"
            "• Причини — чому саме німецька (4-5 речень)\n"
            "• Труднощі і переваги (3-4 речення з sowohl...als auch)\n"
            "• Цілі — що хочеш досягти (3-4 речення)\n"
            "• Висновок — insgesamt, außerdem (1-2 речення)"
        ),
        "fun_fact": "🧠 Цікаво: Слово 'Schadenfreude' (радість від чужого нещастя) настільки унікальне, що його запозичили без перекладу англійська, французька та інші мови!",
    },

    6: {
        "theme": "Контраст і повторення",
        "emoji": "🔄",

        "words_title": "📚 СЛОВА — Тема: Контраст і повторення",
        "words": [
            ("obwohl", "хоча / незважаючи на те що", "Obwohl es schwer ist, lerne ich weiter. — Хоча це важко, я продовжую вчитись."),
            ("trotzdem", "попри це / проте", "Es ist schwer. Trotzdem mache ich weiter. — Це важко. Проте я продовжую."),
            ("aber", "але", "Ich bin müde, aber ich lerne. — Я втомлений, але вчуся."),
            ("jedoch", "однак (офіційніше)", "Das ist schwer. Jedoch ist es möglich. — Це складно. Однак це можливо."),
            ("dagegen", "натомість / проти цього", "Er mag Sport. Ich dagegen lese lieber. — Він любить спорт. Я натомість воліє читати."),
            ("im Gegenteil", "навпаки", "Das ist nicht schwer. Im Gegenteil, es ist einfach!"),
            ("stattdessen", "замість цього", "Ich fahre nicht mit dem Auto, stattdessen nehme ich die Bahn."),
            ("der Fehler", "помилка", "Fehler sind normal. — Помилки — це нормально."),
            ("die Chance", "шанс / можливість", "Das ist eine große Chance. — Це великий шанс."),
            ("schaffen", "справлятись / досягати", "Ich schaffe das! — Я впораюсь!"),
        ],
        "words_tip": "💡 obwohl vs trotzdem: obwohl — сполучник (в одному реченні): Obwohl es schwer IST... trotzdem — прислівник (нове речення): Es ist schwer. TROTZDEM...",

        "grammar_title": "📝 ГРАМАТИКА — Повторення тижня",
        "grammar_explanation": (
            "Сьогодні повторюємо ВСЕ за тиждень!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1. PRÄSENS — порядок слів\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Дієслово ЗАВЖДИ на 2-му місці:\n"
            "Ich lerne jeden Tag Deutsch. ✅\n"
            "Jeden Tag lerne ich Deutsch. ✅\n"
            "Jeden Tag ich lerne Deutsch. ❌\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "2. MODALVERBEN — інфінітив в кінець\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ich muss heute Deutsch LERNEN. ✅\n"
            "Ich kann gut SPRECHEN. ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "3. PERFEKT — haben/sein + Partizip II\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ich habe Deutsch GELERNT. ✅\n"
            "Ich bin nach Hause GEGANGEN. ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "4. NEBENSÄTZE — дієслово в кінець\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ich lerne, weil es wichtig IST. ✅\n"
            "Ich denke, dass er kommt. ✅\n"
            "Obwohl es schwer IST, lerne ich. ✅\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "5. OBWOHL vs TROTZDEM\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Obwohl ich müde BIN, lerne ich. ✅\n"
            "Ich bin müde. Trotzdem LERNE ich. ✅\n"
            "(після trotzdem — дієслово на 2-му місці!)"
        ),
        "grammar_tasks": (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "ФІНАЛЬНЕ ЗАВДАННЯ — змішаний тест\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Виправ помилки:\n"
            "❌ Ich bin gegessen viel gestern.\n"
            "❌ Obwohl es ist schwer, ich lerne.\n"
            "❌ Ich muss lernen jeden Tag Deutsch.\n"
            "❌ Ich denke, dass kommt er morgen.\n"
            "❌ Trotzdem lerne aber ich weiter.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "МЕГА-ЗАВДАННЯ — напиши текст\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Напиши 15 речень 'Mein Leben in Deutschland'\n\n"
            "Обов'язково використай:\n"
            "✓ Мінімум 3 речення у Perfekt\n"
            "✓ Мінімум 2 Modalverben\n"
            "✓ Мінімум 2 weil або obwohl\n"
            "✓ Мінімум 1 dass-речення\n"
            "✓ Мінімум 1 sowohl...als auch або trotzdem\n\n"
            "✅ Виправлені помилки:\n"
            "Ich habe gestern viel gegessen.\n"
            "Obwohl es schwer ist, lerne ich.\n"
            "Ich muss jeden Tag Deutsch lernen.\n"
            "Ich denke, dass er morgen kommt.\n"
            "Trotzdem lerne ich weiter."
        ),

        "practice_title": "💬 ПРАКТИКА — Фінальне повторення",
        "speaking": (
            "🗣️ ГОВОРІННЯ — 60 хв\n\n"
            "Фінальний монолог тижня — 5 хвилин без зупинки!\n\n"
            "Розкажи все разом:\n"
            "1. Хто ти і звідки (Präsens)\n"
            "2. Що ти мусиш і хочеш (Modalverben)\n"
            "3. Що ти робив цього тижня (Perfekt)\n"
            "4. Чому ти вчиш німецьку (weil/obwohl)\n"
            "5. Що ти думаєш про своє майбутнє (dass)\n\n"
            "Запиши себе на телефон і послухай.\n"
            "Повтори — виправляючи помилки."
        ),
        "writing": (
            "✍️ ПИСЬМО — 30 хв\n\n"
            "Напиши фінальний текст тижня:\n"
            "'Was habe ich diese Woche gelernt?'\n"
            "(Що я вивчив цього тижня?)\n\n"
            "Мінімум 15 речень. Включи:\n"
            "• Що вивчив нового (Perfekt)\n"
            "• Що важко і що легко (obwohl/trotzdem)\n"
            "• Що ти думаєш про прогрес (dass)\n"
            "• Що плануєш на наступний тиждень (Modalverben)\n"
            "• Загальний висновок (insgesamt/außerdem)"
        ),
        "fun_fact": "🧠 Цікаво: Середня довжина слова в німецькій — 6 букв. Найдовше офіційне слово: 'Rindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz' (63 букви) — закон про маркування яловичини. Але його скасували у 2013!",
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
    plan = WEEKLY_PLAN[weekday]
    return {"theme": plan["theme"], "emoji": plan["emoji"], **{k: v for k, v in plan.items() if k not in ("theme", "emoji")}}


def build_message_1(c: dict, day: int, level_label: str, today_str: str) -> str:
    words_lines = "\n".join(
        f"{i+1}. {w} — {t}\n   📌 {ex}"
        for i, (w, t, ex) in enumerate(c["words"])
    )
    return (
        f"{c['emoji']} ДЕНЬ {day + 1} [{level_label}] — {c['theme']}\n"
        f"{today_str}\n"
        f"{'─' * 30}\n\n"
        f"{c['words_title']}\n\n"
        f"{words_lines}\n\n"
        f"{'─' * 30}\n"
        f"{c['words_tip']}\n\n"
        f"🔁 Повтори кожне слово вголос 3 рази!"
    )


def build_message_2(c: dict) -> str:
    return (
        f"{c['grammar_title']}\n\n"
        f"{'─' * 30}\n\n"
        f"{c['grammar_explanation']}\n\n"
        f"{'─' * 30}\n\n"
        f"{c['grammar_tasks']}"
    )


def build_message_3(c: dict) -> str:
    return (
        f"{c['practice_title']}\n\n"
        f"{'─' * 30}\n\n"
        f"{c['speaking']}\n\n"
        f"{'─' * 30}\n\n"
        f"{c['writing']}\n\n"
        f"{'─' * 30}\n\n"
        f"{c['fun_fact']}\n\n"
        f"{'─' * 30}\n"
        f"Viel Erfolg heute! 💪🇩🇪"
    )


async def send_long(bot, text: str):
    if len(text) <= 4096:
        await bot.send_message(chat_id=CHANNEL_ID, text=text)
    else:
        for chunk in [text[i:i+4096] for i in range(0, len(text), 4096)]:
            await bot.send_message(chat_id=CHANNEL_ID, text=chunk)
            await asyncio.sleep(0.5)


async def post_german(context):
    day = max(0, (datetime.date.today() - START_DATE).days)
    c = get_day_content(day)
    today_str = datetime.date.today().strftime('%d.%m.%Y')
    level_labels = ["A2", "A2+", "B1"]
    level_label = level_labels[get_level(day)]

    msg1 = build_message_1(c, day, level_label, today_str)
    msg2 = build_message_2(c)
    msg3 = build_message_3(c)

    await send_long(context.bot, msg1)
    await asyncio.sleep(1)
    await send_long(context.bot, msg2)
    await asyncio.sleep(1)
    await send_long(context.bot, msg3)


async def german(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Готую урок...')
    await post_german(context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        '🇩🇪 НІМЕЦЬКА — Щоденні уроки\n\n'
        'Щодня о 13:00 — повний урок з 3 повідомлень:\n'
        '📚 Слова з прикладами\n'
        '📝 Граматика з поясненням і завданнями\n'
        '💬 Говоріння і письмо\n\n'
        'Місяць 1 — A2\n'
        'Місяці 2-3 — A2+\n'
        'Місяці 4-6 — B1\n\n'
        '/german — отримати урок зараз'
    )
    await update.message.reply_text(msg)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('german', german))
    # 13:00 CET = 12:00 UTC (літо) / 11:00 UTC (зима)
    app.job_queue.run_daily(post_german, time=time(hour=11, minute=0))
    print('Бот запущено')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
