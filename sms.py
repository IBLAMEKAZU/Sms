from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from twilio.rest import Client

# ==============================
BOT_TOKEN = "8648834747:AAGYtbdEW8lsgFHeMbh6g2shlvT-7vAdrzE"

TWILIO_SID = "AC12d6ced239285cff9006fafa06b96b69"
TWILIO_AUTH = "26a0f418d51ac67acd4a11ba2297eca4"
TWILIO_NUMBER = "+14314502344"

ADMIN_ID = 7692722647
# ==============================

twilio_client = Client(TWILIO_SID, TWILIO_AUTH)

saved_numbers = {}
user_balance = {}

# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("💎 View Plans", callback_data="plans")]
    ]

    await update.message.reply_text(
        "👋 Welcome to Premium SMS Bot\n\n"
        "You must purchase a plan before using SMS.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================

async def set_number(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        number = context.args[0]
        saved_numbers[update.effective_user.id] = number

        await update.message.reply_text(
            f"✅ Number saved: {number}\nNow you can send SMS using /sms"
        )

    except:
        await update.message.reply_text(
            "Usage:\n/set +919876543210"
        )

# ==============================

async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("10 SMS - $5.2", callback_data="plan10")],
        [InlineKeyboardButton("21 SMS - $10.4", callback_data="plan21")],
        [InlineKeyboardButton("210 SMS - $100", callback_data="plan210")]
    ]

    await update.message.reply_text(
        "💎 Choose Your Plan",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "💰 Payment Details\n\n"
        "Network: BEP20\n\n"
        "Wallet Address:\n"
        "0xYOUR_WALLET_ADDRESS\n\n"
        "Binance ID:\n"
        "123456789\n\n"
        "Cwallet:\n"
        "your_cwallet\n\n"
        "After payment send TXID to admin.\n"
        "Admin will activate your plan."
    )

# ==============================

async def sms(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_balance.get(user_id,0) <= 0:
        await update.message.reply_text(
            "❌ Your plan is finished or not activated.\nUse /plan"
        )
        return

    if user_id not in saved_numbers:
        await update.message.reply_text(
            "⚠️ Save number first using\n/set +919876543210"
        )
        return

    try:

        number = saved_numbers[user_id]
        message = " ".join(context.args)

        msg = twilio_client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=number
        )

        user_balance[user_id] -= 1

        await update.message.reply_text(
            f"✅ SMS Sent\nNumber: {number}\nRemaining SMS: {user_balance[user_id]}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ==============================

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    bal = user_balance.get(user_id,0)

    await update.message.reply_text(
        f"📊 Your SMS Balance: {bal}"
    )

# ==============================

async def addplan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    try:

        user_id = int(context.args[0])
        sms = int(context.args[1])

        user_balance[user_id] = user_balance.get(user_id,0) + sms

        await update.message.reply_text(
            f"✅ Added {sms} SMS to {user_id}"
        )

    except:
        await update.message.reply_text(
            "Usage:\n/addplan user_id sms"
        )

# ==============================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("set", set_number))
app.add_handler(CommandHandler("plan", plan))
app.add_handler(CommandHandler("sms", sms))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("addplan", addplan))

app.add_handler(CallbackQueryHandler(button))

print("🤖 Bot Running...")

app.run_polling()