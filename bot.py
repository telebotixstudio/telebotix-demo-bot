import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")


LANG_TEXT = {
    "en": {
        "choose_language": "Choose your language",
        "welcome": (
            "Welcome to *Telebotix*\n\n"
            "We build Telegram bots that help businesses capture and organize customer requests automatically.\n\n"
            "This demo shows how a business bot can work for your company."
        ),
        "menu": [
            ["🚀 Try Live Demo"],
            ["💼 Business Cases", "💰 Request Estimate"],
            ["📩 Contact", "🌐 Change Language"]
        ],
        "demo_intro": "Let’s simulate a real customer request. Please answer a few quick questions.",
        "business_question": "What type of business do you run?",
        "business_options": [
            "💅 Beauty / Salon",
            "🚗 Auto Service",
            "🏥 Clinic / Dental",
            "🏢 Agency / Services",
            "🛍️ E-commerce",
            "Other"
        ],
        "goal_question": "What would you like to automate?",
        "goal_options": [
            "Lead capture",
            "Appointment requests",
            "Customer support",
            "Product inquiries",
            "Internal requests"
        ],
        "contact_question": "How should we contact you? Leave your Telegram, phone number, or email.",
        "demo_success": (
            "✅ Request received.\n\n"
            "A Telebotix specialist will contact you soon.\n\n"
            "You can continue exploring more use cases below."
        ),
        "use_cases": (
            "*Business Cases*\n\n"
            "Here are examples of bots we can build:\n\n"
            "• Lead Capture Bot\n"
            "• Appointment Booking Bot\n"
            "• FAQ / Support Bot\n"
            "• Product Inquiry Bot\n"
            "• Internal Team Request Bot"
        ),
        "estimate": (
            "*Request Estimate*\n\n"
            "Every business is different, so we prepare a custom estimate based on:\n\n"
            "• your business type\n"
            "• automation complexity\n"
            "• integrations needed\n"
            "• support level\n\n"
            "Send us your request and we’ll suggest the right setup."
        ),
        "contact": (
            "*Contact Telebotix*\n\n"
            "Interested in a bot for your business?\n\n"
            "Telegram: @o_s_h_t\n"
            "Email: telebotix.studio@gmail.com"
        ),
        "back_to_menu": "Use the menu below or type /start to return to the main menu.",
        "language_changed": "Language changed successfully.",
        "new_lead": "New Demo Lead",
        "source": "telegram_bot",
        "lang_label": "EN"
    },
    "ua": {
        "choose_language": "Оберіть мову",
        "welcome": (
            "Вітаємо в *Telebotix*\n\n"
            "Ми створюємо Telegram-ботів, які допомагають бізнесу автоматично збирати та структурувати звернення клієнтів.\n\n"
            "Це демо показує, як такий бот може працювати для вашої компанії."
        ),
        "menu": [
            ["🚀 Спробувати демо"],
            ["💼 Приклади для бізнесу", "💰 Отримати оцінку"],
            ["📩 Контакти", "🌐 Змінити мову"]
        ],
        "demo_intro": "Давайте змоделюємо реальне звернення клієнта. Дайте відповіді на кілька коротких питань.",
        "business_question": "Який у вас тип бізнесу?",
        "business_options": [
            "💅 Б'юті / Салон",
            "🚗 Автосервіс",
            "🏥 Клініка / Стоматологія",
            "🏢 Агенція / Послуги",
            "🛍️ E-commerce",
            "Інше"
        ],
        "goal_question": "Що саме ви хочете автоматизувати?",
        "goal_options": [
            "Збір заявок",
            "Запис на послугу",
            "Підтримка клієнтів",
            "Запити по товарах",
            "Внутрішні звернення"
        ],
        "contact_question": "Як з вами зв’язатися? Залиште Telegram, номер телефону або email.",
        "demo_success": (
            "✅ Заявку отримано.\n\n"
            "Спеціаліст Telebotix зв’яжеться з вами найближчим часом.\n\n"
            "Нижче можете переглянути інші варіанти автоматизації."
        ),
        "use_cases": (
            "*Приклади для бізнесу*\n\n"
            "Ось які боти ми можемо створити:\n\n"
            "• Бот для збору заявок\n"
            "• Бот для запису на послугу\n"
            "• FAQ / Support бот\n"
            "• Бот для запитів по товарах\n"
            "• Бот для внутрішніх звернень команди"
        ),
        "estimate": (
            "*Отримати оцінку*\n\n"
            "Кожен бізнес індивідуальний, тому ми формуємо вартість залежно від:\n\n"
            "• типу бізнесу\n"
            "• складності автоматизації\n"
            "• потрібних інтеграцій\n"
            "• рівня підтримки\n\n"
            "Надішліть запит, і ми запропонуємо оптимальне рішення."
        ),
        "contact": (
            "*Контакти Telebotix*\n\n"
            "Хочете бота для свого бізнесу?\n\n"
            "Telegram: @yourusername\n"
            "Email: hello@telebotix.com"
        ),
        "back_to_menu": "Скористайтесь меню нижче або введіть /start, щоб повернутися в головне меню.",
        "language_changed": "Мову успішно змінено.",
        "new_lead": "Новий демо-лід",
        "source": "telegram_bot",
        "lang_label": "UA"
    }
}


def get_lang(context):
    return context.user_data.get("lang", "en")


def get_text(context, key):
    lang = get_lang(context)
    return LANG_TEXT[lang][key]


def build_main_menu(lang):
    return ReplyKeyboardMarkup(LANG_TEXT[lang]["menu"], resize_keyboard=True)


def send_to_google_sheet(data: dict):
    if not GOOGLE_SCRIPT_URL:
        print("GOOGLE_SCRIPT_URL is missing")
        return

    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json=data, timeout=10)
        print("Google Sheets response:", response.status_code, response.text)
    except Exception as e:
        print("Error sending to Google Sheets:", e)


async def show_language_picker(update: Update):
    keyboard = ReplyKeyboardMarkup(
        [["🇬🇧 English", "🇺🇦 Українська"]],
        resize_keyboard=True
    )
    await update.message.reply_text("Choose your language / Оберіть мову", reply_markup=keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["step"] = None
    await show_language_picker(update)


async def show_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(
        LANG_TEXT[lang]["welcome"],
        parse_mode="Markdown",
        reply_markup=build_main_menu(lang)
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    lang = get_lang(context)

    if user_text == "🇬🇧 English":
        context.user_data["lang"] = "en"
        context.user_data["step"] = None
        await update.message.reply_text(
            LANG_TEXT["en"]["language_changed"],
            reply_markup=build_main_menu("en")
        )
        await show_welcome(update, context)
        return

    if user_text == "🇺🇦 Українська":
        context.user_data["lang"] = "ua"
        context.user_data["step"] = None
        await update.message.reply_text(
            LANG_TEXT["ua"]["language_changed"],
            reply_markup=build_main_menu("ua")
        )
        await show_welcome(update, context)
        return

    if user_text in ["🌐 Change Language", "🌐 Змінити мову"]:
        context.user_data["step"] = None
        await show_language_picker(update)
        return

    if user_text in ["🚀 Try Live Demo", "🚀 Спробувати демо"]:
        context.user_data["step"] = "business"

        business_keyboard = ReplyKeyboardMarkup(
            [[option] for option in LANG_TEXT[lang]["business_options"]],
            resize_keyboard=True
        )

        await update.message.reply_text(LANG_TEXT[lang]["demo_intro"])
        await update.message.reply_text(
            LANG_TEXT[lang]["business_question"],
            reply_markup=business_keyboard
        )
        return

    if context.user_data.get("step") == "business":
        context.user_data["business"] = user_text
        context.user_data["step"] = "goal"

        goal_keyboard = ReplyKeyboardMarkup(
            [[option] for option in LANG_TEXT[lang]["goal_options"]],
            resize_keyboard=True
        )

        await update.message.reply_text(
            LANG_TEXT[lang]["goal_question"],
            reply_markup=goal_keyboard
        )
        return

    if context.user_data.get("step") == "goal":
        context.user_data["goal"] = user_text
        context.user_data["step"] = "contact"

        await update.message.reply_text(
            LANG_TEXT[lang]["contact_question"],
            reply_markup=build_main_menu(lang)
        )
        return

    if context.user_data.get("step") == "contact":
        context.user_data["contact"] = user_text
        context.user_data["step"] = None

        username = update.message.from_user.username
        username_text = f"@{username}" if username else "No username"

        message = (
            f"{LANG_TEXT[lang]['new_lead']}\n\n"
            f"Business: {context.user_data['business']}\n"
            f"Goal: {context.user_data['goal']}\n"
            f"Contact: {context.user_data['contact']}\n"
            f"User: {username_text}\n"
            f"Language: {LANG_TEXT[lang]['lang_label']}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message
        )

        lead_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "language": LANG_TEXT[lang]["lang_label"],
            "telegram_user": username_text,
            "business_type": context.user_data["business"],
            "automation_goal": context.user_data["goal"],
            "contact_channel": "telegram",
            "biggest_issue": "",
            "contact_details": context.user_data["contact"],
            "lead_status": "new",
            "source": LANG_TEXT[lang]["source"],
            "notes": ""
        }

        send_to_google_sheet(lead_data)

        await update.message.reply_text(
            LANG_TEXT[lang]["demo_success"],
            reply_markup=build_main_menu(lang)
        )
        return

    if user_text in ["💼 Business Cases", "💼 Приклади для бізнесу"]:
        await update.message.reply_text(
            LANG_TEXT[lang]["use_cases"],
            parse_mode="Markdown",
            reply_markup=build_main_menu(lang)
        )
        return

    if user_text in ["💰 Request Estimate", "💰 Отримати оцінку"]:
        await update.message.reply_text(
            LANG_TEXT[lang]["estimate"],
            parse_mode="Markdown",
            reply_markup=build_main_menu(lang)
        )
        return

    if user_text in ["📩 Contact", "📩 Контакти"]:
        await update.message.reply_text(
            LANG_TEXT[lang]["contact"],
            parse_mode="Markdown",
            reply_markup=build_main_menu(lang)
        )
        return

    await update.message.reply_text(
        LANG_TEXT[lang]["back_to_menu"],
        reply_markup=build_main_menu(lang)
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing in .env")

    if not ADMIN_CHAT_ID:
        raise ValueError("ADMIN_CHAT_ID is missing in .env")

    print("Bot is running...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()


if __name__ == "__main__":
    main()