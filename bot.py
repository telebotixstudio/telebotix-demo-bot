from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ====== CONFIG ======
ADMIN_CHAT_ID = "YOUR_CHAT_ID"

# ====== STATE ======
user_data_store = {}

# ====== TEXTS ======
TEXTS = {
    "en": {
        "welcome": "👋 Welcome to Telebotix Studio\n\nWe build Telegram bots that help businesses capture leads, automate requests and respond faster.\n\nWhat would you like to explore?",
        "menu": [["🚀 Try demo", "📦 Use cases"], ["💼 Get a bot", "ℹ️ About"], ["🌐 Change language"]],
        "demo_start": "Great. Let's simulate a real client request.\n\nWhat type of business do you have?",
        "business_types": [["💅 Beauty / Salon", "🚗 Auto service"], ["🏥 Clinic", "⬅️ Back"]],
        "need": "What would you like to automate?",
        "needs": [["📅 Booking", "📥 Lead collection"], ["💬 Customer requests", "⬅️ Back"]],
        "name": "Please enter your name:",
        "contact": "Now enter your contact (Telegram / phone):",
        "done": "✅ Done!\n\nThis is how your future clients will interact with your bot.\n\nWe capture structured requests automatically.",
        "about": "We create simple and effective Telegram bots for businesses.\n\nFocus: lead capture, booking flows, automation.",
        "cases": "Examples:\n\n• Beauty salons\n• Auto services\n• Clinics\n• Local businesses",
        "get_bot": "Tell us briefly about your business:",
        "fallback": "Sorry, I didn't understand that.\nPlease use the buttons below 👇",
    },
    "ua": {
        "welcome": "👋 Вітаємо в Telebotix Studio\n\nМи створюємо Telegram-боти, які допомагають бізнесу збирати заявки, автоматизувати запити та швидше відповідати клієнтам.\n\nЩо вас цікавить?",
        "menu": [["🚀 Спробувати демо", "📦 Приклади"], ["💼 Замовити бота", "ℹ️ Про нас"], ["🌐 Змінити мову"]],
        "demo_start": "Супер. Змоделюємо реальний запит клієнта.\n\nЯкий у вас бізнес?",
        "business_types": [["💅 Салон краси", "🚗 СТО"], ["🏥 Клініка", "⬅️ Назад"]],
        "need": "Що хочете автоматизувати?",
        "needs": [["📅 Запис", "📥 Заявки"], ["💬 Запити клієнтів", "⬅️ Назад"]],
        "name": "Введіть ваше ім’я:",
        "contact": "Введіть контакт (Telegram / телефон):",
        "done": "✅ Готово!\n\nТак виглядатиме взаємодія ваших клієнтів з ботом.\n\nЗаявки автоматично структуруються.",
        "about": "Ми створюємо прості та ефективні Telegram-боти для бізнесу.\n\nОсновне: заявки, записи, автоматизація.",
        "cases": "Приклади:\n\n• Салони\n• СТО\n• Клініки\n• Локальний бізнес",
        "get_bot": "Коротко опишіть ваш бізнес:",
        "fallback": "Вибачте, я не зрозумів.\nСкористайтесь кнопками нижче 👇",
    }
}

# ====== HELPERS ======
def get_lang(user_id):
    return user_data_store.get(user_id, {}).get("lang", "en")

def set_lang(user_id, lang):
    user_data_store.setdefault(user_id, {})["lang"] = lang

def get_text(user_id, key):
    lang = get_lang(user_id)
    return TEXTS[lang][key]

def get_menu(user_id):
    lang = get_lang(user_id)
    return ReplyKeyboardMarkup(TEXTS[lang]["menu"], resize_keyboard=True)

# ====== HANDLERS ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    set_lang(user_id, "en")
    await update.message.reply_text(get_text(user_id, "welcome"), reply_markup=get_menu(user_id))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    lang = get_lang(user_id)

    # ===== MENU =====
    if "demo" in text.lower() or "демо" in text.lower():
        await update.message.reply_text(get_text(user_id, "demo_start"),
            reply_markup=ReplyKeyboardMarkup(TEXTS[lang]["business_types"], resize_keyboard=True))
        return

    if "use" in text.lower() or "приклади" in text.lower():
        await update.message.reply_text(get_text(user_id, "cases"), reply_markup=get_menu(user_id))
        return

    if "about" in text.lower() or "про" in text.lower():
        await update.message.reply_text(get_text(user_id, "about"), reply_markup=get_menu(user_id))
        return

    if "get bot" in text.lower() or "замовити" in text.lower():
        user_data_store[user_id]["state"] = "lead"
        await update.message.reply_text(get_text(user_id, "get_bot"))
        return

    if "language" in text.lower() or "мова" in text.lower():
        new_lang = "ua" if lang == "en" else "en"
        set_lang(user_id, new_lang)
        await update.message.reply_text(get_text(user_id, "welcome"), reply_markup=get_menu(user_id))
        return

    if "beauty" in text.lower() or "салон" in text.lower() or "auto" in text.lower() or "сто" in text.lower():
        await update.message.reply_text(get_text(user_id, "need"),
            reply_markup=ReplyKeyboardMarkup(TEXTS[lang]["needs"], resize_keyboard=True))
        return

    if "booking" in text.lower() or "запис" in text.lower():
        user_data_store[user_id]["state"] = "name"
        await update.message.reply_text(get_text(user_id, "name"))
        return

    if user_data_store.get(user_id, {}).get("state") == "name":
        user_data_store[user_id]["name"] = text
        user_data_store[user_id]["state"] = "contact"
        await update.message.reply_text(get_text(user_id, "contact"))
        return

    if user_data_store.get(user_id, {}).get("state") == "contact":
        name = user_data_store[user_id].get("name")
        contact = text

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🔥 New lead\n\nName: {name}\nContact: {contact}"
        )

        user_data_store[user_id]["state"] = None
        await update.message.reply_text(get_text(user_id, "done"), reply_markup=get_menu(user_id))
        return

    # ===== FALLBACK =====
    await update.message.reply_text(get_text(user_id, "fallback"), reply_markup=get_menu(user_id))

# ====== MAIN ======
app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot running...")
app.run_polling()