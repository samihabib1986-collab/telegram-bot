import os
import logging
import asyncio
from pymongo import MongoClient

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ================== إعدادات ==================
TOKEN = os.environ.get("TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")

if not TOKEN:
    raise ValueError("TOKEN is missing")

# ================== قاعدة البيانات ==================
client = MongoClient(MONGO_URL)
db = client["quiz_bot"]
users = db["users"]

# ================== Logging ==================
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================== الأدمن ==================
ADMIN_ID = 8491023024

# ================== بيانات مؤقتة ==================
user_data = {}

# ================== فيديو ==================
INTRO_VIDEO = "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ"

# ================== الصور ==================
uploaded_images = {
    "الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ",
    "عظام الوجه": "AgACAgQAAxkBAAIDgmnjuaxzSVnHSg-Ht5sh8MLSRxgDAAJEDGsb4XYhUyf_4zNepyt6AQADAgADbQADOwQ",
}

# ================== الأسئلة ==================
subjects = {
    "bio": {
        "u1_taaleel": [
            {
                "question": "لماذا عظم الفك السفلي متحرك؟",
                "options": ["لتسهيل التنفس", "لتسهيل المضغ والنطق", "لحماية الدماغ"],
                "answer": "لتسهيل المضغ والنطق"
            },
            {
                "question": "لماذا توجد أقراص غضروفية بين الفقرات؟",
                "options": ["لمنع الاحتكاك", "لزيادة الطول", "لتقوية العضلات"],
                "answer": "لمنع الاحتكاك"
            }
        ]
    }
}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_data.setdefault(user_id, {
        "approved": False,
        "q_index": 0,
        "score": 0
    })

    if not user_data[user_id].get("approved"):
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    keyboard = [
        [InlineKeyboardButton("🧬 أحياء", callback_data="bio")]
    ]

    await update.message.reply_text(
        "📚 اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الدفع ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    users.update_one(
        {"user_id": user_id},
        {"$set": {"pending": True}},
        upsert=True
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💳 طلب اشتراك: /approve {user_id}"
    )

    await update.message.reply_text("⏳ تم إرسال الطلب")

# ================== الموافقة ==================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])

    user_data.setdefault(user_id, {})
    user_data[user_id]["approved"] = True

    await update.message.reply_text("✅ تم التفعيل")
    await context.bot.send_message(chat_id=user_id, text="🎉 تم قبولك")

# ================== إرسال السؤال ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_data:
        await query.message.reply_text("⚠️ ابدأ من جديد /start")
        return

    if "category" not in user_data[user_id]:
        await query.message.reply_text("⚠️ اختر نوع الأسئلة أولاً")
        return

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id].get("q_index", 0)

    q_list = subjects[subject][category]

    if index >= len(q_list):
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"🎉 انتهيت! النتيجة: {user_data[user_id]['score']}"
        )
        return

    q = q_list[index]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=str(i))]
        for i, opt in enumerate(q["options"])
    ]

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=q["question"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الأزرار ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    user_data.setdefault(user_id, {"q_index": 0, "score": 0})

    # اختيار المادة
    if data == "bio":
        user_data[user_id]["subject"] = "bio"

        keyboard = [
            [InlineKeyboardButton("الوحدة 1", callback_data="u1")]
        ]

        await query.message.reply_text(
            "اختر الوحدة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # اختيار الوحدة
    if data == "u1":
        user_data[user_id]["unit"] = "u1"

        keyboard = [
            [InlineKeyboardButton("تعليل", callback_data="taaleel")]
        ]

        await query.message.reply_text(
            "اختر النوع:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # اختيار نوع الأسئلة
    if data == "taaleel":
        user_data[user_id]["category"] = "u1_taaleel"
        user_data[user_id]["q_index"] = 0
        user_data[user_id]["score"] = 0

        keyboard = [
            [InlineKeyboardButton("▶️ ابدأ", callback_data="start")]
        ]

        await query.message.reply_text(
            "جاهز؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # زر البداية (هذا كان المشكلة عندك)
    if data == "start":
        user_data[user_id]["q_index"] = 0
        user_data[user_id]["score"] = 0

        await send_question(update, context)
        return

    # الإجابة
    if user_id not in user_data:
        return

    subject = user_data[user_id].get("subject")
    category = user_data[user_id].get("category")
    index = user_data[user_id].get("q_index", 0)

    if not subject or not category:
        return

    q = subjects[subject][category][index]
    selected = q["options"][int(data)]

    if selected == q["answer"]:
        user_data[user_id]["score"] += 10
        msg = "✅ صحيح"
    else:
        msg = f"❌ خطأ\nالإجابة: {q['answer']}"

    user_data[user_id]["q_index"] += 1

    await query.message.reply_text(msg)

    await asyncio.sleep(1)
    await send_question(update, context)

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(button))

if __name__ == "__main__":
    app.run_polling()
