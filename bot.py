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

# ================== MongoDB ==================
MONGO_URL = os.environ.get("MONGO_URL")
if not MONGO_URL:
    raise ValueError("MONGO_URL is missing")

client = MongoClient(MONGO_URL)
db = client["quiz_bot"]
users = db["users"]

# ================== Logging ==================
logging.basicConfig(level=logging.INFO)

# ================== Token ==================
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN is missing")

ADMIN_ID = 8491023024

# ================== صور ==================
uploaded_images = {
    "الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ",
    "عظام الجمجمة": "AgACAgQAAxkBAAIDtmnj2kzpampZCzzZG1R3ukMhOA_LAAJoDGsb4XYhU90RtQhjryIZAQADAgADbQADOwQ"
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

# ================== الأسئلة ==================
section1_questions = {
    "function": [
        {
            "question": "ما وظيفة الهيكل العظمي؟",
            "options": ["الحماية", "الهضم", "التنفس"],
            "answer": "الحماية"
        }
    ],
    "images": [
        {
            "question": "ما هي هذه الصورة؟",
            "image": uploaded_images["الهيكل العظمي"],
            "options": ["الهيكل العظمي", "القلب", "الرئة"],
            "answer": "الهيكل العظمي"
        },
        {
            "question": "ما هي هذه الصورة؟",
            "image": uploaded_images["عظام الجمجمة"],
            "options": ["عظام الجمجمة", "عظام اليد", "العمود الفقري"],
            "answer": "عظام الجمجمة"
        }
    ]
}

# ================== الهيكل ==================
subjects = {
    "science": {
        "title": "📚 كتاب العلوم",
        "units": {
            "u1": {
                "title": "📘 الوحدة الأولى",
                "video": "UNIT_VIDEO",
                "sections": {
                    "s1": {
                        "title": "📂 الجهاز الدعامي",
                        "video": "SECTION_VIDEO",
                        "questions": section1_questions
                    }
                }
            }
        }
    }
}

# ================== user data ==================
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
        "📌 اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== paid ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)

    await context.bot.send_message(chat_id=ADMIN_ID, text=f"/approve {user_id}")
    await update.message.reply_text("تم إرسال طلبك")

# ================== approve ==================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    approve_user(user_id)

    await context.bot.send_message(chat_id=user_id, text="تم التفعيل /start")

# ================== إرسال سؤال ==================
async def send_question(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    data = user_data[user_id]

    unit = data["unit"]
    sec = data["section"]
    quiz_type = data.get("quiz_type", "function")

    q_list = subjects["science"]["units"][unit]["sections"][sec]["questions"].get(quiz_type, [])

    index = data["q_index"]

    if index >= len(q_list):
        await context.bot.send_message(chat_id=query.message.chat_id, text="انتهى الاختبار")
        return

    q = q_list[index]

    if quiz_type == "images":
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=q["image"],
            caption=q["question"]
        )
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text=q["question"])

    keyboard = [
        [
            InlineKeyboardButton("A", callback_data="0"),
            InlineKeyboardButton("B", callback_data="1"),
            InlineKeyboardButton("C", callback_data="2")
        ]
    ]

    text = ""
    for i, opt in enumerate(q["options"]):
        text += f"{chr(65+i)}- {opt}\n"

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== buttons ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "science":
        keyboard = [
            [InlineKeyboardButton("📘 الوحدة الأولى", callback_data="u1")]
        ]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر الوحدة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("u"):
        user_data[user_id] = {
            "unit": data,
            "q_index": 0
        }

        keyboard = [
            [InlineKeyboardButton("📂 الجهاز الدعامي", callback_data="sec_s1")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر القسم:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("sec_"):
        sec = data.split("_")[1]

        user_data[user_id]["section"] = sec
        user_data[user_id]["q_index"] = 0

        keyboard = [
            [InlineKeyboardButton("🧠 أسئلة عادية", callback_data="quiz_function")],
            [InlineKeyboardButton("🖼 صور", callback_data="quiz_images")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر نوع الأسئلة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("quiz_"):
        user_data[user_id]["quiz_type"] = data.replace("quiz_", "")
        user_data[user_id]["q_index"] = 0

        await send_question(update, context)
        return

    q_data = user_data[user_id]
    q_list = subjects["science"]["units"][q_data["unit"]]["sections"][q_data["section"]]["questions"][q_data["quiz_type"]]
    q = q_list[q_data["q_index"]]

    if q["options"][int(data)] == q["answer"]:
        await context.bot.send_message(chat_id=query.message.chat_id, text="✅ صحيح")
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"❌ خطأ\n{q['answer']}")

    user_data[user_id]["q_index"] += 1
    await asyncio.sleep(1)
    await send_question(update, context)

# ================== run ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
