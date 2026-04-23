import os
import logging
import asyncio
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ================== إعدادات ==================
MONGO_URL = os.environ.get("MONGO_URL")
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 8491023024

if not MONGO_URL:
    raise ValueError("MONGO_URL is missing")

if not TOKEN:
    raise ValueError("TOKEN is missing")

# ================== MongoDB ==================
client = MongoClient(MONGO_URL)
db = client["quiz_bot"]
users = db["users"]

# ================== Logging ==================
logging.basicConfig(level=logging.INFO)

# ================== الصور ==================
uploaded_images = {
    "الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ",
    "عظام الوجه": "AgACAgQAAxkBAAIDgmnjuaxzSVnHSg-Ht5sh8MLSRxgDAAJEDGsb4XYhUyf_4zNepyt6AQADAgADbQADOwQ",
    "القفص الصدري": "AgACAgQAAxkBAAIDvGnj2wKHWoZd-Fnq6VTgtbr_26cXAAJrDGsb4XYhU6gEI1EyrwWmAQADAgADbQADOwQ",
}

# ================== DB ==================
def get_user(user_id):
    return users.find_one({"_id": user_id})

def create_user(user_id):
    users.update_one(
        {"_id": user_id},
        {"$setOnInsert": {"approved": False}},
        upsert=True
    )

def approve_user(user_id):
    users.update_one(
        {"_id": user_id},
        {"$set": {"approved": True}},
        upsert=True
    )

# ================== الفيديوهات ==================
UNIT1_VIDEO = "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ"
SECTION1_VIDEO = "VIDEO_S1"

# ================== الأسئلة ==================

section1_questions = {
    "function": [
        {
            "question": "ما وظيفة الهيكل العظمي؟",
            "options": ["الحماية", "الهضم", "التنفس"],
            "answer": "الحماية"
        }
    ],

    "taaleel": [
        {
            "question": "علل: أهمية الهيكل العظمي؟",
            "options": ["للحماية", "للهضم", "للتنفس"],
            "answer": "للحماية"
        }
    ],

    "images": [
        {
            "image": "الهيكل العظمي",
            "question": "اختر الجزء الصحيح",
            "options": ["العمود الفقري", "الهيكل الطرفي", "القفص الصدري"],
            "answer": "العمود الفقري"
        }
    ],

    "where": [
        {
            "question": "أين يوجد الهيكل العظمي؟",
            "options": ["داخل الجسم", "خارج الجسم", "في الدم"],
            "answer": "داخل الجسم"
        }
    ],

    "level": [
        {
            "question": "رتب مراحل الحماية",
            "options": ["عظام → حماية", "دم → حماية", "هواء → حماية"],
            "answer": "عظام → حماية"
        }
    ]
}

# ================== الهيكل ==================
subjects = {
    "science": {
        "units": {
            "u1": {
                "video": UNIT1_VIDEO,
                "sections": {
                    "s1": {
                        "video": SECTION1_VIDEO,
                        "questions": section1_questions
                    }
                }
            }
        }
    }
}

# ================== بيانات المستخدم ==================
user_data = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not get_user(user_id):
        create_user(user_id)
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    if not get_user(user_id).get("approved"):
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    keyboard = [
        [InlineKeyboardButton("📚 كتاب العلوم", callback_data="science")]
    ]

    await update.message.reply_text(
        "اختر الكتاب:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== إرسال سؤال ==================
async def send_question(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    data = user_data[user_id]

    q_list = subjects["science"]["units"]["u1"]["sections"]["s1"]["questions"][data["quiz_type"]]
    q = q_list[data["q_index"]]

    # ================== عرض صورة إن وجدت ==================
    if "image" in q:
        img_id = uploaded_images.get(q["image"])
        if img_id:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=img_id
            )

    # ================== نص السؤال ==================
    text = q["question"] + "\n\n"
    for i, opt in enumerate(q["options"]):
        text += f"{chr(65+i)}- {opt}\n"

    keyboard = [
        [
            InlineKeyboardButton("A", callback_data="0"),
            InlineKeyboardButton("B", callback_data="1"),
            InlineKeyboardButton("C", callback_data="2")
        ]
    ]

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

    # اختيار الكتاب
    if data == "science":
        user_data[user_id] = {
            "quiz_type": "function",
            "q_index": 0
        }

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="تم اختيار الكتاب"
        )

        await send_question(update, context)
        return

    # اختيار الإجابة
    q_data = user_data[user_id]

    q_list = subjects["science"]["units"]["u1"]["sections"]["s1"]["questions"][q_data["quiz_type"]]
    q = q_list[q_data["q_index"]]

    chosen = q["options"][int(data)]

    if chosen == q["answer"]:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="✅ صحيح"
        )
    else:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"❌ خطأ\nالإجابة الصحيحة: {q['answer']}"
        )

    # السؤال التالي
    user_data[user_id]["q_index"] += 1
    await asyncio.sleep(1)
    await send_question(update, context)

# ================== تشغيل البوت ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
