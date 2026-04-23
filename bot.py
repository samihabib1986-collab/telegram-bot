import os
import logging
import asyncio
from pymongo import MongoClient
from telegram.ext import MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ================== إعداد MongoDB ==================
MONGO_URL = os.environ.get("MONGO_URL")

if not MONGO_URL:
    raise ValueError("MONGO_URL is missing")

client = MongoClient(MONGO_URL)
db = client["quiz_bot"]
users = db["users"]

# ================== لوج ==================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================== التوكن ==================
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN is missing")

# ================== الأدمن ==================
ADMIN_ID = 8491023024

# ================== قواعد البيانات ==================
def get_user(user_id):
    return users.find_one({"_id": user_id})

def create_user(user_id):
    users.update_one(
        {"_id": user_id},
        {
            "$setOnInsert": {
                "_id": user_id,
                "approved": False,
                "pending": True,
                "score": 0,
                "q_index": 0
            }
        },
        upsert=True
    )

def approve_user(user_id):
    users.update_one(
        {"_id": user_id},
        {"$set": {"approved": True, "pending": False}},
        upsert=True
    )

# ================== فيديوهات ==================
UNIT_VIDEOS = {
    "u1": "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ"
}

SECTION_VIDEOS = {
    "dam": "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ"
}

# ================== الصور ==================
uploaded_images = {
"الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ"
}

# ================== بنك الأسئلة ==================
subjects = {
    "bio": {
        "u1_taaleel": [],
        "u1_images": [],
        "u1_where": [],
        "u1_level": [],
        "u1_result1": [],
        "u1_function": []
    }
}

# ================== بيانات المستخدم ==================
user_data = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user = get_user(user_id)

    if not user:
        create_user(user_id)
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    if not user.get("approved"):
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    keyboard = [
        [InlineKeyboardButton("🧬 علم الأحياء", callback_data="bio")]
    ]

    await update.message.reply_text(
        "📚 اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الدفع ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    create_user(user_id)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"/approve {user_id}"
    )

    await update.message.reply_text("⏳ تم إرسال طلبك")

# ================== الموافقة ==================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    approve_user(user_id)

    await update.message.reply_text("تم التفعيل")

# ================== إرسال السؤال ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q_list = subjects[subject][category]

    if index >= len(q_list):
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🎉 انتهيت!"
        )
        return

    q = q_list[index]

    text = q["question"] + "\n\n"
    for i, opt in enumerate(q["options"]):
        text += f"{chr(65+i)}- {opt}\n"

    keyboard = [[
        InlineKeyboardButton("A", callback_data="0"),
        InlineKeyboardButton("B", callback_data="1"),
        InlineKeyboardButton("C", callback_data="2"),
    ]]

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الأزرار ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # المادة
    if data == "bio":
        keyboard = [
            [InlineKeyboardButton("الوحدة 1", callback_data="bio_u1")]
        ]
        await query.message.reply_text("اختر الوحدة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # الوحدة
    if data == "bio_u1":

        keyboard = [
            [InlineKeyboardButton("🎬 فيديو الوحدة", callback_data="unit_video")],
            [InlineKeyboardButton("القسم الأول: الدعامي الحركي", callback_data="sec_u1_dam")]
        ]

        await query.message.reply_text("📘 الوحدة 1:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # فيديو الوحدة
    if data == "unit_video":
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=UNIT_VIDEOS["u1"]
        )
        return

    # القسم
    if data == "sec_u1_dam":

        user_data[user_id] = {
            "subject": "bio",
            "unit": "u1",
            "section": "dam",
            "score": 0,
            "q_index": 0
        }

        keyboard = [
            [InlineKeyboardButton("🎥 فيديو القسم", callback_data="section_video")],
            [InlineKeyboardButton("📘 تعليل", callback_data="taaleel")],
            [InlineKeyboardButton("🖼️ صور", callback_data="images")],
            [InlineKeyboardButton("📍 موقع", callback_data="where")],
            [InlineKeyboardButton("📊 ترتيب", callback_data="level")],
            [InlineKeyboardButton("🧠 نتائج", callback_data="result1")],
            [InlineKeyboardButton("⚙️ وظيفة", callback_data="function")]
        ]

        await query.message.reply_text("📚 اختر:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # فيديو القسم
    if data == "section_video":
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=SECTION_VIDEOS["dam"]
        )
        return

    # نوع الأسئلة
    if data in ["taaleel", "images", "where", "level", "result1", "function"]:

        category = f"{user_data[user_id]['unit']}_{data}"
        user_data[user_id]["category"] = category

        keyboard = [[InlineKeyboardButton("▶️ بدء", callback_data="start_quiz")]]

        await query.message.reply_text("ابدأ 👇", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "start_quiz":
        await send_question(update, context)
        return

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
