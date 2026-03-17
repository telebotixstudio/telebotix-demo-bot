import os
from datetime import datetime
from typing import Dict, Any

import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# ENV
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
SUPPORT_TELEGRAM = os.getenv("SUPPORT_TELEGRAM", "@telebotix_contact")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "telebotix.studio@gmail.com")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

if not ADMIN_CHAT_ID:
    raise ValueError("ADMIN_CHAT_ID is not set in environment variables")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)

# =========================
# IN-MEMORY USER STATE
# =========================
user_store: Dict[int, Dict[str, Any]] = {}

# =========================
# UI / TEXTS
# =========================
TEXTS = {
    "en": {
        "lang_name": "EN",
        "choose_lang": "Choose your language",
        "welcome": (
            "Welcome to Telebotix Studio.\n\n"
            "This demo shows how a business bot can capture leads, handle booking requests, answer common questions, and organize customer communication.\n\n"
            "Choose what you want to explore."
        ),
        "main_menu": [
            ["🚀 Try demo", "🧩 Features"],
            ["📦 Use cases", "💰 Pricing"],
            ["📝 Get estimate", "📩 Contact"],
            ["🌐 Change language"],
        ],
        "features_menu": [
            ["📥 Lead capture demo", "📅 Booking demo"],
            ["💬 FAQ demo", "🏢 Internal request demo"],
            ["⬅️ Back to menu"],
        ],
        "use_cases_menu": [
            ["💅 Beauty / Salon", "🚗 Auto service"],
            ["🏥 Clinic", "🛍️ Local business"],
            ["⬅️ Back to menu"],
        ],
        "lead_intro": (
            "Let's simulate a real customer request.\n\n"
            "What type of business do you run?"
        ),
        "lead_business_menu": [
            ["💅 Beauty / Salon", "🚗 Auto service"],
            ["🏥 Clinic", "🏢 Agency / Services"],
            ["🛍️ E-commerce", "Other"],
            ["⬅️ Back to menu"],
        ],
        "lead_goal": "What would you like to automate?",
        "lead_goal_menu": [
            ["📥 Lead capture", "📅 Booking requests"],
            ["💬 Customer requests", "🧾 Product inquiries"],
            ["⬅️ Back to menu"],
        ],
        "lead_volume": "How many customer requests do you usually get per week?",
        "lead_volume_menu": [
            ["1–10", "10–30"],
            ["30–100", "100+"],
            ["⬅️ Back to menu"],
        ],
        "lead_name": "Please enter your name.",
        "lead_contact": "Please enter your contact (Telegram / phone / email).",
        "lead_done": (
            "Request received.\n\n"
            "This is how your future clients can interact with your business bot: structured, simple, and fast."
        ),
        "booking_demo": (
            "Booking flow example:\n\n"
            "• choose service\n"
            "• choose preferred date\n"
            "• leave contact\n"
            "• request goes directly to the business owner or manager\n\n"
            "This works well for salons, clinics, consultations, and local services."
        ),
        "faq_demo": (
            "FAQ flow example:\n\n"
            "A bot can instantly answer common questions like:\n"
            "• prices\n"
            "• location\n"
            "• working hours\n"
            "• how to book\n\n"
            "This reduces repetitive messages and speeds up replies."
        ),
        "internal_demo": (
            "Internal request flow example:\n\n"
            "Bots can also be built for internal teams:\n"
            "• leave a technical request\n"
            "• request access\n"
            "• submit a support task\n"
            "• collect structured internal forms"
        ),
        "features_text": (
            "Here are example bot functions you can explore.\n\n"
            "Each one can be customized for a real business."
        ),
        "pricing_text": (
            "Pricing overview:\n\n"
            "Starter — from $100\n"
            "Business — $180 to $240\n"
            "Advanced — from $320\n\n"
            "Final pricing depends on the agreed project scope.\n"
            "For clients in Ukraine, payment can be made in UAH at the exchange rate on the day of payment."
        ),
        "estimate_intro": (
            "Let's prepare a quick estimate.\n\n"
            "What type of business do you have?"
        ),
        "estimate_scope": "What do you want the bot to handle?",
        "estimate_scope_menu": [
            ["📥 Leads", "📅 Bookings"],
            ["💬 FAQ / requests", "⚙️ Custom workflow"],
            ["⬅️ Back to menu"],
        ],
        "estimate_contact": "Leave your contact and we’ll prepare a tailored estimate.",
        "estimate_done": (
            "Estimate request received.\n\n"
            "We’ll review your scope and get back to you with the best-fit option."
        ),
        "cases_intro": "Choose a niche to see how a Telegram bot could work there.",
        "case_beauty": (
            "Beauty / Salon use case:\n\n"
            "• booking requests\n"
            "• service selection\n"
            "• contact collection\n"
            "• admin notification\n"
            "• simple CRM flow"
        ),
        "case_auto": (
            "Auto service use case:\n\n"
            "• vehicle issue intake\n"
            "• preferred time\n"
            "• customer contact\n"
            "• instant admin notification"
        ),
        "case_clinic": (
            "Clinic use case:\n\n"
            "• consultation request\n"
            "• service direction\n"
            "• structured lead capture\n"
            "• faster patient communication"
        ),
        "case_local": (
            "Local business use case:\n\n"
            "• service requests\n"
            "• common questions\n"
            "• lead qualification\n"
            "• simple automation without a heavy CRM"
        ),
        "contact_text": (
            f"Contact Telebotix Studio:\n\n"
            f"Telegram: {SUPPORT_TELEGRAM}\n"
            f"Email: {SUPPORT_EMAIL}"
        ),
        "about_text": (
            "Telebotix Studio builds practical Telegram bots for businesses.\n\n"
            "Focus:\n"
            "• lead capture\n"
            "• booking flows\n"
            "• request automation\n"
            "• lightweight CRM-style organization"
        ),
        "invalid": (
            "Sorry, I didn't understand that.\n"
            "Please use one of the buttons below so I can guide you correctly."
        ),
        "back_label": "⬅️ Back to menu",
        "new_demo_lead": "New demo lead",
        "new_estimate_lead": "New estimate request",
        "source_demo": "demo_bot",
        "source_estimate": "estimate_request",
    },
    "ua": {
        "lang_name": "UA",
        "choose_lang": "Оберіть мову",
        "welcome": (
            "Вітаємо в Telebotix Studio.\n\n"
            "Це демо показує, як бізнес-бот може збирати ліди, обробляти заявки на запис, відповідати на типові питання та структурувати комунікацію з клієнтами.\n\n"
            "Оберіть, що хочете подивитися."
        ),
        "main_menu": [
            ["🚀 Спробувати демо", "🧩 Можливості"],
            ["📦 Приклади", "💰 Ціни"],
            ["📝 Отримати оцінку", "📩 Контакти"],
            ["🌐 Змінити мову"],
        ],
        "features_menu": [
            ["📥 Демо збору заявок", "📅 Демо запису"],
            ["💬 Демо FAQ", "🏢 Демо внутрішніх звернень"],
            ["⬅️ Назад у меню"],
        ],
        "use_cases_menu": [
            ["💅 Салон краси", "🚗 Автосервіс"],
            ["🏥 Клініка", "🛍️ Локальний бізнес"],
            ["⬅️ Назад у меню"],
        ],
        "lead_intro": (
            "Змоделюємо реальне звернення клієнта.\n\n"
            "Який у вас тип бізнесу?"
        ),
        "lead_business_menu": [
            ["💅 Салон краси", "🚗 Автосервіс"],
            ["🏥 Клініка", "🏢 Агенція / Послуги"],
            ["🛍️ E-commerce", "Інше"],
            ["⬅️ Назад у меню"],
        ],
        "lead_goal": "Що саме ви хочете автоматизувати?",
        "lead_goal_menu": [
            ["📥 Збір заявок", "📅 Запити на запис"],
            ["💬 Звернення клієнтів", "🧾 Запити по товарах"],
            ["⬅️ Назад у меню"],
        ],
        "lead_volume": "Скільки звернень від клієнтів ви зазвичай отримуєте за тиждень?",
        "lead_volume_menu": [
            ["1–10", "10–30"],
            ["30–100", "100+"],
            ["⬅️ Назад у меню"],
        ],
        "lead_name": "Будь ласка, введіть ваше ім’я.",
        "lead_contact": "Будь ласка, залиште контакт (Telegram / телефон / email).",
        "lead_done": (
            "Заявку отримано.\n\n"
            "Саме так ваші майбутні клієнти можуть взаємодіяти з бізнес-ботом: структуровано, просто і швидко."
        ),
        "booking_demo": (
            "Приклад флоу для запису:\n\n"
            "• вибір послуги\n"
            "• вибір бажаної дати\n"
            "• залишення контакту\n"
            "• заявка одразу йде власнику або менеджеру\n\n"
            "Це добре працює для салонів, клінік, консультацій і локальних послуг."
        ),
        "faq_demo": (
            "Приклад FAQ-флоу:\n\n"
            "Бот може миттєво відповідати на типові питання:\n"
            "• ціни\n"
            "• адреса\n"
            "• графік роботи\n"
            "• як записатися\n\n"
            "Це зменшує кількість однотипних повідомлень і пришвидшує відповіді."
        ),
        "internal_demo": (
            "Приклад флоу для внутрішніх звернень:\n\n"
            "Бот можна робити і для команди:\n"
            "• залишити технічний запит\n"
            "• подати заявку на доступ\n"
            "• надіслати support task\n"
            "• збирати внутрішні форми у структурованому вигляді"
        ),
        "features_text": (
            "Ось приклади функцій ботів, які можна переглянути.\n\n"
            "Кожну з них можна адаптувати під реальний бізнес."
        ),
        "pricing_text": (
            "Огляд цін:\n\n"
            "Starter — від $100\n"
            "Business — $180 до $240\n"
            "Advanced — від $320\n\n"
            "Фінальна вартість залежить від погодженого обсягу робіт.\n"
            "Для клієнтів з України оплата можлива в гривні за курсом на день оплати."
        ),
        "estimate_intro": (
            "Підготуємо коротку оцінку.\n\n"
            "Який у вас тип бізнесу?"
        ),
        "estimate_scope": "Що саме бот має обробляти?",
        "estimate_scope_menu": [
            ["📥 Заявки", "📅 Записи"],
            ["💬 FAQ / звернення", "⚙️ Кастомний флоу"],
            ["⬅️ Назад у меню"],
        ],
        "estimate_contact": "Залиште контакт, і ми підготуємо індивідуальну оцінку.",
        "estimate_done": (
            "Запит на оцінку отримано.\n\n"
            "Ми переглянемо ваш обсяг задач і повернемося з оптимальним варіантом."
        ),
        "cases_intro": "Оберіть нішу, щоб подивитися, як там може працювати Telegram-бот.",
        "case_beauty": (
            "Салон краси:\n\n"
            "• заявки на запис\n"
            "• вибір послуги\n"
            "• збір контактів\n"
            "• сповіщення адміну\n"
            "• простий CRM-флоу"
        ),
        "case_auto": (
            "Автосервіс:\n\n"
            "• прийом опису проблеми\n"
            "• зручний час\n"
            "• контакт клієнта\n"
            "• миттєве сповіщення адміну"
        ),
        "case_clinic": (
            "Клініка:\n\n"
            "• запит на консультацію\n"
            "• вибір напрямку послуги\n"
            "• структурований збір лідів\n"
            "• швидша комунікація з пацієнтами"
        ),
        "case_local": (
            "Локальний бізнес:\n\n"
            "• сервісні звернення\n"
            "• типові питання\n"
            "• кваліфікація ліда\n"
            "• проста автоматизація без важкої CRM"
        ),
        "contact_text": (
            f"Контакти Telebotix Studio:\n\n"
            f"Telegram: {SUPPORT_TELEGRAM}\n"
            f"Email: {SUPPORT_EMAIL}"
        ),
        "about_text": (
            "Telebotix Studio створює практичні Telegram-боти для бізнесу.\n\n"
            "Основні напрямки:\n"
            "• збір лідів\n"
            "• флоу для записів\n"
            "• автоматизація звернень\n"
            "• легка CRM-структура"
        ),
        "invalid": (
            "Вибачте, я не зрозумів цю дію.\n"
            "Будь ласка, скористайтеся кнопками нижче, і я правильно вас проведу далі."
        ),
        "back_label": "⬅️ Назад у меню",
        "new_demo_lead": "Новий демо-лід",
        "new_estimate_lead": "Новий запит на оцінку",
        "source_demo": "demo_bot",
        "source_estimate": "estimate_request",
    },
}


# =========================
# HELPERS
# =========================
def ensure_user(user_id: int) -> None:
    if user_id not in user_store:
        user_store[user_id] = {
            "lang": "en",
            "flow": None,
            "data": {},
        }


def get_lang(user_id: int) -> str:
    ensure_user(user_id)
    return user_store[user_id]["lang"]


def set_lang(user_id: int, lang: str) -> None:
    ensure_user(user_id)
    user_store[user_id]["lang"] = lang


def t(user_id: int, key: str) -> str:
    return TEXTS[get_lang(user_id)][key]


def reset_flow(user_id: int) -> None:
    ensure_user(user_id)
    user_store[user_id]["flow"] = None
    user_store[user_id]["data"] = {}


def set_flow(user_id: int, flow: str) -> None:
    ensure_user(user_id)
    user_store[user_id]["flow"] = flow


def get_flow(user_id: int):
    ensure_user(user_id)
    return user_store[user_id]["flow"]


def main_menu(user_id: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(TEXTS[get_lang(user_id)]["main_menu"], resize_keyboard=True)


def features_menu(user_id: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(TEXTS[get_lang(user_id)]["features_menu"], resize_keyboard=True)


def use_cases_menu(user_id: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(TEXTS[get_lang(user_id)]["use_cases_menu"], resize_keyboard=True)


def lead_business_menu(user_id: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(TEXTS[get_lang(user_id)]["lead_business_menu"], resize_keyboard=True)


def lead_goal_menu(user_id: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(TEXTS[get_lang(user_id)]["lead_goal_menu"], resize_keyboard=True)


def lead_volume_menu(user_id: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(TEXTS[get_lang(user_id)]["lead_volume_menu"], resize_keyboard=True)


def estimate_scope_menu(user_id: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(TEXTS[get_lang(user_id)]["estimate_scope_menu"], resize_keyboard=True)


def language_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [["🇬🇧 English", "🇺🇦 Українська"]],
        resize_keyboard=True,
    )


def send_to_google_sheet(payload: dict) -> None:
    if not GOOGLE_SCRIPT_URL:
        print("GOOGLE_SCRIPT_URL is not set; skipping sheet write")
        return

    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
        print("Google Sheets response:", response.status_code, response.text)
    except Exception as e:
        print("Error sending to Google Sheets:", e)


async def notify_admin(title: str, user_payload: dict, context: ContextTypes.DEFAULT_TYPE) -> None:
    lines = [title, ""]
    for key, value in user_payload.items():
        lines.append(f"{key}: {value}")
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text="\n".join(lines))


async def show_main(update: Update, user_id: int) -> None:
    await update.message.reply_text(t(user_id, "welcome"), reply_markup=main_menu(user_id))


# =========================
# COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ensure_user(user_id)
    reset_flow(user_id)
    await update.message.reply_text(t(user_id, "choose_lang"), reply_markup=language_menu())


# =========================
# MAIN HANDLER
# =========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    raw_text = update.message.text.strip()
    text = raw_text.lower()

    ensure_user(user_id)
    current_lang = get_lang(user_id)

    # -------- Language selection --------
    if raw_text == "🇬🇧 English":
        set_lang(user_id, "en")
        reset_flow(user_id)
        await show_main(update, user_id)
        return

    if raw_text == "🇺🇦 Українська":
        set_lang(user_id, "ua")
        reset_flow(user_id)
        await show_main(update, user_id)
        return

    # -------- Global back --------
    if raw_text in ["⬅️ Back to menu", "⬅️ Назад у меню"]:
        reset_flow(user_id)
        await show_main(update, user_id)
        return

    # -------- Main menu actions --------
    if raw_text in ["🌐 Change language", "🌐 Змінити мову"]:
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "choose_lang"), reply_markup=language_menu())
        return

    if raw_text in ["🧩 Features", "🧩 Можливості"]:
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "features_text"), reply_markup=features_menu(user_id))
        return

    if raw_text in ["📦 Use cases", "📦 Приклади"]:
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "cases_intro"), reply_markup=use_cases_menu(user_id))
        return

    if raw_text in ["💰 Pricing", "💰 Ціни"]:
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "pricing_text"), reply_markup=main_menu(user_id))
        return

    if raw_text in ["📩 Contact", "📩 Контакти"]:
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "contact_text"), reply_markup=main_menu(user_id))
        return

    if raw_text in ["ℹ️ About", "ℹ️ Про нас"]:
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "about_text"), reply_markup=main_menu(user_id))
        return

    # -------- Feature demos --------
    if raw_text in ["📥 Lead capture demo", "📥 Демо збору заявок", "🚀 Try demo", "🚀 Спробувати демо"]:
        reset_flow(user_id)
        set_flow(user_id, "lead_business")
        await update.message.reply_text(t(user_id, "lead_intro"), reply_markup=lead_business_menu(user_id))
        return

    if raw_text in ["📅 Booking demo", "📅 Демо запису"]:
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "booking_demo"), reply_markup=features_menu(user_id))
        return

    if raw_text in ["💬 FAQ demo", "💬 Демо FAQ"]:
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "faq_demo"), reply_markup=features_menu(user_id))
        return

    if raw_text in ["🏢 Internal request demo", "🏢 Демо внутрішніх звернень"]:
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "internal_demo"), reply_markup=features_menu(user_id))
        return

    # -------- Use cases --------
    if raw_text in ["💅 Beauty / Salon", "💅 Салон краси"]:
        # Could be from use-cases or from lead flow
        if get_flow(user_id) == "lead_business":
            user_store[user_id]["data"]["business_type"] = raw_text
            set_flow(user_id, "lead_goal")
            await update.message.reply_text(t(user_id, "lead_goal"), reply_markup=lead_goal_menu(user_id))
            return
        await update.message.reply_text(t(user_id, "case_beauty"), reply_markup=use_cases_menu(user_id))
        return

    if raw_text in ["🚗 Auto service", "🚗 Автосервіс", "🚗 СТО"]:
        if get_flow(user_id) == "lead_business":
            user_store[user_id]["data"]["business_type"] = raw_text
            set_flow(user_id, "lead_goal")
            await update.message.reply_text(t(user_id, "lead_goal"), reply_markup=lead_goal_menu(user_id))
            return
        await update.message.reply_text(t(user_id, "case_auto"), reply_markup=use_cases_menu(user_id))
        return

    if raw_text in ["🏥 Clinic", "🏥 Клініка"]:
        if get_flow(user_id) == "lead_business":
            user_store[user_id]["data"]["business_type"] = raw_text
            set_flow(user_id, "lead_goal")
            await update.message.reply_text(t(user_id, "lead_goal"), reply_markup=lead_goal_menu(user_id))
            return
        await update.message.reply_text(t(user_id, "case_clinic"), reply_markup=use_cases_menu(user_id))
        return

    if raw_text in ["🛍️ Local business", "🛍️ Локальний бізнес"]:
        await update.message.reply_text(t(user_id, "case_local"), reply_markup=use_cases_menu(user_id))
        return

    if raw_text in ["💼 Get a bot", "📝 Get estimate", "💼 Замовити бота", "📝 Отримати оцінку"]:
        reset_flow(user_id)
        set_flow(user_id, "estimate_business")
        await update.message.reply_text(t(user_id, "estimate_intro"), reply_markup=lead_business_menu(user_id))
        return

    # -------- LEAD DEMO FLOW --------
    flow = get_flow(user_id)

    if flow == "lead_business":
        if raw_text in ["🏢 Agency / Services", "🏢 Агенція / Послуги", "🛍️ E-commerce", "Other", "Інше"]:
            user_store[user_id]["data"]["business_type"] = raw_text
            set_flow(user_id, "lead_goal")
            await update.message.reply_text(t(user_id, "lead_goal"), reply_markup=lead_goal_menu(user_id))
            return

        await update.message.reply_text(t(user_id, "invalid"), reply_markup=lead_business_menu(user_id))
        return

    if flow == "lead_goal":
        valid_goals = [
            "📥 Lead capture", "📅 Booking requests", "💬 Customer requests", "🧾 Product inquiries",
            "📥 Збір заявок", "📅 Запити на запис", "💬 Звернення клієнтів", "🧾 Запити по товарах"
        ]
        if raw_text in valid_goals:
            user_store[user_id]["data"]["goal"] = raw_text
            set_flow(user_id, "lead_volume")
            await update.message.reply_text(t(user_id, "lead_volume"), reply_markup=lead_volume_menu(user_id))
            return

        await update.message.reply_text(t(user_id, "invalid"), reply_markup=lead_goal_menu(user_id))
        return

    if flow == "lead_volume":
        if raw_text in ["1–10", "10–30", "30–100", "100+"]:
            user_store[user_id]["data"]["volume"] = raw_text
            set_flow(user_id, "lead_name")
            await update.message.reply_text(t(user_id, "lead_name"), reply_markup=ReplyKeyboardMarkup([[t(user_id, "back_label")]], resize_keyboard=True))
            return

        await update.message.reply_text(t(user_id, "invalid"), reply_markup=lead_volume_menu(user_id))
        return

    if flow == "lead_name":
        if len(raw_text) < 2:
            await update.message.reply_text(t(user_id, "invalid"), reply_markup=ReplyKeyboardMarkup([[t(user_id, "back_label")]], resize_keyboard=True))
            return

        user_store[user_id]["data"]["name"] = raw_text
        set_flow(user_id, "lead_contact")
        await update.message.reply_text(t(user_id, "lead_contact"), reply_markup=ReplyKeyboardMarkup([[t(user_id, "back_label")]], resize_keyboard=True))
        return

    if flow == "lead_contact":
        if len(raw_text) < 3:
            await update.message.reply_text(t(user_id, "invalid"), reply_markup=ReplyKeyboardMarkup([[t(user_id, "back_label")]], resize_keyboard=True))
            return

        user_store[user_id]["data"]["contact"] = raw_text
        payload = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "language": TEXTS[current_lang]["lang_name"],
            "telegram_user": f"@{update.effective_user.username}" if update.effective_user.username else "No username",
            "business_type": user_store[user_id]["data"].get("business_type", ""),
            "automation_goal": user_store[user_id]["data"].get("goal", ""),
            "contact_channel": "telegram",
            "biggest_issue": "",
            "contact_details": raw_text,
            "lead_status": "new",
            "source": TEXTS[current_lang]["source_demo"],
            "notes": f"Volume: {user_store[user_id]['data'].get('volume', '')}; Name: {user_store[user_id]['data'].get('name', '')}",
        }

        await notify_admin(
            TEXTS[current_lang]["new_demo_lead"],
            {
                "Name": user_store[user_id]["data"].get("name", ""),
                "Business": user_store[user_id]["data"].get("business_type", ""),
                "Goal": user_store[user_id]["data"].get("goal", ""),
                "Requests/week": user_store[user_id]["data"].get("volume", ""),
                "Contact": raw_text,
                "Telegram": payload["telegram_user"],
                "Language": payload["language"],
            },
            context,
        )
        send_to_google_sheet(payload)
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "lead_done"), reply_markup=main_menu(user_id))
        return

    # -------- ESTIMATE FLOW --------
    if flow == "estimate_business":
        valid_estimate_business = [
            "💅 Beauty / Salon", "💅 Салон краси",
            "🚗 Auto service", "🚗 Автосервіс", "🚗 СТО",
            "🏥 Clinic", "🏥 Клініка",
            "🏢 Agency / Services", "🏢 Агенція / Послуги",
            "🛍️ E-commerce", "Other", "Інше"
        ]
        if raw_text in valid_estimate_business:
            user_store[user_id]["data"]["estimate_business"] = raw_text
            set_flow(user_id, "estimate_scope")
            await update.message.reply_text(t(user_id, "estimate_scope"), reply_markup=estimate_scope_menu(user_id))
            return

        await update.message.reply_text(t(user_id, "invalid"), reply_markup=lead_business_menu(user_id))
        return

    if flow == "estimate_scope":
        valid_scopes = [
            "📥 Leads", "📅 Bookings", "💬 FAQ / requests", "⚙️ Custom workflow",
            "📥 Заявки", "📅 Записи", "💬 FAQ / звернення", "⚙️ Кастомний флоу"
        ]
        if raw_text in valid_scopes:
            user_store[user_id]["data"]["estimate_scope"] = raw_text
            set_flow(user_id, "estimate_contact")
            await update.message.reply_text(t(user_id, "estimate_contact"), reply_markup=ReplyKeyboardMarkup([[t(user_id, "back_label")]], resize_keyboard=True))
            return

        await update.message.reply_text(t(user_id, "invalid"), reply_markup=estimate_scope_menu(user_id))
        return

    if flow == "estimate_contact":
        if len(raw_text) < 3:
            await update.message.reply_text(t(user_id, "invalid"), reply_markup=ReplyKeyboardMarkup([[t(user_id, "back_label")]], resize_keyboard=True))
            return

        payload = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "language": TEXTS[current_lang]["lang_name"],
            "telegram_user": f"@{update.effective_user.username}" if update.effective_user.username else "No username",
            "business_type": user_store[user_id]["data"].get("estimate_business", ""),
            "automation_goal": user_store[user_id]["data"].get("estimate_scope", ""),
            "contact_channel": "telegram",
            "biggest_issue": "Estimate request",
            "contact_details": raw_text,
            "lead_status": "new",
            "source": TEXTS[current_lang]["source_estimate"],
            "notes": "",
        }

        await notify_admin(
            TEXTS[current_lang]["new_estimate_lead"],
            {
                "Business": user_store[user_id]["data"].get("estimate_business", ""),
                "Scope": user_store[user_id]["data"].get("estimate_scope", ""),
                "Contact": raw_text,
                "Telegram": payload["telegram_user"],
                "Language": payload["language"],
            },
            context,
        )
        send_to_google_sheet(payload)
        reset_flow(user_id)
        await update.message.reply_text(t(user_id, "estimate_done"), reply_markup=main_menu(user_id))
        return

    # -------- FALLBACK --------
    await update.message.reply_text(t(user_id, "invalid"), reply_markup=main_menu(user_id))


# =========================
# MAIN
# =========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()