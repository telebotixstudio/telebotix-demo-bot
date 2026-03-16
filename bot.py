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

menu = [
    ["🚀 Try Demo"],
    ["💼 Use Cases"],
    ["💰 Get Estimate"],
    ["📩 Contact Us"]
]


def send_to_google_sheet(data: dict):
    if not GOOGLE_SCRIPT_URL:
        print("GOOGLE_SCRIPT_URL is missing")
        return

    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json=data, timeout=10)
        print("Google Sheets response:", response.status_code, response.text)
    except Exception as e:
        print("Error sending to Google Sheets:", e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Welcome to *Telebotix Demo Bot*\n\n"
        "This demo shows how a business bot can capture and organize customer requests automatically."
    )

    keyboard = ReplyKeyboardMarkup(menu, resize_keyboard=True)

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text == "🚀 Try Demo":
        context.user_data["step"] = "business"

        await update.message.reply_text(
            "What type of business do you have?\n\n"
            "Beauty / Salon\n"
            "Auto Service\n"
            "Clinic / Dental\n"
            "Agency\n"
            "E-commerce\n"
            "Other"
        )

    elif context.user_data.get("step") == "business":
        context.user_data["business"] = user_text
        context.user_data["step"] = "goal"

        await update.message.reply_text(
            "What would you like to automate?"
        )

    elif context.user_data.get("step") == "goal":
        context.user_data["goal"] = user_text
        context.user_data["step"] = "contact"

        await update.message.reply_text(
            "Leave your Telegram username, phone number, or email."
        )

    elif context.user_data.get("step") == "contact":
        context.user_data["contact"] = user_text
        context.user_data["step"] = None

        username = update.message.from_user.username
        username_text = f"@{username}" if username else "No username"

        message = (
            "New Demo Lead\n\n"
            f"Business: {context.user_data['business']}\n"
            f"Goal: {context.user_data['goal']}\n"
            f"Contact: {context.user_data['contact']}\n"
            f"User: {username_text}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message
        )

        lead_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "language": "EN",
            "telegram_user": username_text,
            "business_type": context.user_data["business"],
            "automation_goal": context.user_data["goal"],
            "contact_channel": "telegram",
            "biggest_issue": "",
            "contact_details": context.user_data["contact"],
            "lead_status": "new",
            "source": "telegram_bot",
            "notes": ""
        }

        send_to_google_sheet(lead_data)

        await update.message.reply_text(
            "✅ Demo request captured successfully.\n\n"
            "Our team will contact you soon."
        )

    elif user_text == "💼 Use Cases":
        await update.message.reply_text(
            "Examples of bots we build:\n\n"
            "- Lead Capture Bot\n"
            "- Appointment Bot\n"
            "- FAQ Bot\n"
            "- Product Inquiry Bot\n"
            "- Internal Team Bot"
        )

    elif user_text == "💰 Get Estimate":
        await update.message.reply_text(
            "Every business is different, so pricing depends on your needs.\n\n"
            "Send us a message and we’ll prepare a custom estimate."
        )

    elif user_text == "📩 Contact Us":
        await update.message.reply_text(
            "Contact Telebotix:\n\n"
            "Telegram: @yourusername\n"
            "Email: hello@telebotix.com"
        )

    else:
        await update.message.reply_text(
            "Use the menu below or type /start to return to the main menu."
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