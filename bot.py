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

# ================== DB Functions ==================
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

# ================== فيديوهات ==================
UNIT1_VIDEO = "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ"
SECTION1_VIDEO = "VIDEO_S1"
SECTION2_VIDEO = "VIDEO_S2"
SECTION3_VIDEO = "VIDEO_S3"

# ================== أسئلة ==================
section1_questions = [
    {
        "question": "ما وظيفة الهيكل العظمي؟",
        "options": ["الحماية", "الهضم", "التنفس"],
        "answer": "الحماية"
    }
]

section2_questions = [
    {
        "question": "ما وظيفة الجهاز العصبي؟",
        "options": ["الهضم", "التنسيق", "الإخراج"],
        "answer": "التنسيق"
    }
]

section3_questions = [
    {
        "question": "ما وظيفة الغدد الصماء؟",
        "options": ["إفراز هرمونات", "هضم", "تنفس"],
        "answer": "إفراز هرمونات"
    }
]

# ================== الهيكل الجديد ==================
subjects = {
    "science": {
        "title": "📚 كتاب العلوم",

        "units": {
            "u1": {
                "title": "📘 الوحدة الأولى: الدعامة والتنسيق",
                "video": UNIT1_VIDEO,

                "sections": {
                    "s1": {
                        "title": "📂 الجهاز الدعامي الحركي",
                        "video": SECTION1_VIDEO,
                        "questions": section1_questions
                    },
                    "s2": {
                        "title": "📂 الجهاز العصبي",
                        "video": SECTION2_VIDEO,
                        "questions": section2_questions
                    },
                    "s3": {
                        "title": "📂 الغدد الصماء",
                        "video": SECTION3_VIDEO,
                        "questions": section3_questions
                    }
                }
            }
        }
    }
}

# ================== User Temp ==================
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

    await update.message.reply_text("اختر الكتاب:", reply_markup=InlineKeyboardMarkup(keyboard))

# ================== Paid ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)

    await context.bot.send_message(chat_id=ADMIN_ID, text=f"/approve {user_id}")
    await update.message.reply_text("تم إرسال طلبك")

# ================== Approve ==================
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

    unit = user_data[user_id]["unit"]
    sec = user_data[user_id]["section"]
    q_type = user_data[user_id].get("quiz_type", "s1")

    q_list = subjects["science"]["units"][unit]["sections"][sec]["questions"]

    index = data["q_index"]

    if index >= len(q_list):
        await context.bot.send_message(chat_id=query.message.chat_id, text="انتهى الاختبار")
        return

    q = q_list[index]

    text = q["question"] + "\n"
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

# ================== Buttons ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # كتاب
    if data == "science":
        keyboard = [
            [InlineKeyboardButton("📘 الوحدة الأولى", callback_data="u1")]
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text="اختر الوحدة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # وحدة
    if data.startswith("u"):
        user_data[user_id] = {"unit": data, "q_index": 0}

        unit = subjects["science"]["units"][data]

        keyboard = [[InlineKeyboardButton("🎬 فيديو الوحدة", callback_data="UNIT1_VIDEO")]]

        for key, sec in unit["sections"].items():
            keyboard.append([InlineKeyboardButton(sec["title"], callback_data=f"sec_{key}")])

        await context.bot.send_message(chat_id=query.message.chat_id, text=unit["title"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # فيديو الوحدة
    if data == "UNIT1_VIDEO":
        unit = user_data[user_id]["unit"]
        video = subjects["science"]["units"][unit]["video"]

        await context.bot.send_video(chat_id=query.message.chat_id, video=video)
        return

    # قسم
    if data.startswith("sec_"):
        sec = data.split("_")[1]
        user_data[user_id]["section"] = sec
        user_data[user_id]["q_index"] = 0

        keyboard = [
            [InlineKeyboardButton("🎬 فيديو القسم", callback_data="sec_video")],
            [InlineKeyboardButton("▶️ ابدأ الاختبار", callback_data="start_quiz")]
        ]

        await context.bot.send_message(chat_id=query.message.chat_id, text="اختر:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # فيديو القسم
    if data == "sec_video":
        unit = user_data[user_id]["unit"]
        sec = user_data[user_id]["section"]

        video = subjects["science"]["units"][unit]["sections"][sec]["video"]

        await context.bot.send_video(chat_id=query.message.chat_id, video=video)
        return

    # بدء الاختبار → اختيار النوع
    if data == "start_quiz":

        keyboard = [
            [InlineKeyboardButton("🧠 تعاليل", callback_data="quiz_taaleel")],
            [InlineKeyboardButton("🖼 صور", callback_data="quiz_images")],
            [InlineKeyboardButton("📍 أين", callback_data="quiz_where")],
            [InlineKeyboardButton("🔁 ترتيب", callback_data="quiz_level")],
            [InlineKeyboardButton("⚙️ وظيفة", callback_data="quiz_function")],
            [InlineKeyboardButton("📊 نتائج", callback_data="quiz_result1")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر نوع الأسئلة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # اختيار نوع الاختبار
    if data.startswith("quiz_"):
        quiz_type = data.replace("quiz_", "")
        user_data[user_id]["quiz_type"] = quiz_type
        user_data[user_id]["q_index"] = 0

        await send_question(update, context)
        return

    # إجابة
    q_data = user_data[user_id]
    q_list = subjects["science"]["units"][q_data["unit"]]["sections"][q_data["section"]]["questions"]
    q = q_list[q_data["q_index"]]

    if q["options"][int(data)] == q["answer"]:
        await context.bot.send_message(chat_id=query.message.chat_id, text="✅ صحيح")
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"❌ خطأ\n{q['answer']}")

    user_data[user_id]["q_index"] += 1
    await asyncio.sleep(1)
    await send_question(update, context)

# ================== Run ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
