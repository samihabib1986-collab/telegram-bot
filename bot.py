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

# ================== صور جاهزة ==================
uploaded_images = {
    "الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ",
    "عظام الوجه": "AgACAgQAAxkBAAIDgmnjuaxzSVnHSg-Ht5sh8MLSRxgDAAJEDGsb4XYhUyf_4zNepyt6AQADAgADbQADOwQ",
    "مفصل العضد الكتفي": "AgACAgQAAxkBAAIDrGnj2XkC5s_14i-8Zr11ICic-ImxAAJjDGsb4XYhU7x_C70kw-VnAQADAgADbQADOwQ",
    "مفاصل العمود الفقري": "AgACAgQAAxkBAAIDrmnj2cFsc9BTuUF_6SBSJ5AolzFXAAJkDGsb4XYhU52j6bbeUJdeAQADAgADbQADOwQ",
    "عظام الطرف العلوي": "AgACAgQAAxkBAAIDsmnj2gsFww-fBb8XMXywean-d5bSAAJmDGsb4XYhU71hPZ-to5faAQADAgADeAADOwQ",
    "عظام الطرف السفلي": "AgACAgQAAxkBAAIDtGnj2i6b24ki0cgork2CXiRUPyZkAAJnDGsb4XYhU-tRzckix1dGAQADAgADeAADOwQ",
    "عظام الجمجمة": "AgACAgQAAxkBAAIDtmnj2kzpampZCzzZG1R3ukMhOA_LAAJoDGsb4XYhU90RtQhjryIZAQADAgADbQADOwQ",
    "بنية العظم الطويل": "AgACAgQAAxkBAAIDuGnj2qP11IFHNmIsBybhHIJnHnhlAAJpDGsb4XYhU4jukApSAAF2JgEAAwIAA20AAzsE",
    "القناة الفقرية": "AgACAgQAAxkBAAIDumnj2s3d7FdxX6ek83h2ICL058HGAAJqDGsb4XYhU44UTT9-9Q3TAQADAgADbQADOwQ",
    "القفص الصدري": "AgACAgQAAxkBAAIDvGnj2wKHWoZd-Fnq6VTgtbr_26cXAAJrDGsb4XYhU6gEI1EyrwWmAQADAgADbQADOwQ",
    "الفقرة": "AgACAgQAAxkBAAIDvmnj2y7tdQIvOj1m2vpCtZYG73CTAAJsDGsb4XYhUwAB9a5PVNtyWQEAAwIAA20AAzsE",
    "العمود الفقري": "AgACAgQAAxkBAAIDwGnj2098LBlyy3stztvcZro8wYe8AAJtDGsb4XYhU2P4mddgYBUPAQADAgADbQADOwQ",
    "الزنار الحوضي": "AgACAgQAAxkBAAIDwmnj22kphW_UdDwCxYEXZ1QEEvr6AAJuDGsb4XYhU9ARG08G-TgLAQADAgADbQADOwQ",
    "الاربطة والاوتار": "AgACAgQAAxkBAAIDxGnj27EBbQ7NdocwG8BMMx-pXpz0AAJvDGsb4XYhU0SlG3BDNztZAQADAgADbQADOwQ",
}

# ================== DB ==================
def get_user(user_id):
    return users.find_one({"_id": user_id})

def create_user(user_id):
    users.update_one({"_id": user_id}, {"$setOnInsert": {"approved": False}}, upsert=True)

def approve_user(user_id):
    users.update_one({"_id": user_id}, {"$set": {"approved": True}}, upsert=True)

# ================== أسئلة الصور (تم تعديلها) ==================
section1_questions = {
    "images": [
        {
            "question": "ما هي هذه الصورة؟",
            "image": uploaded_images["الهيكل العظمي"],
            "options": ["الهيكل العظمي", "القلب", "الرئة"],
            "answer": "الهيكل العظمي"
        },
        {
            "question": "حدد الصورة الصحيحة لعظام الجمجمة",
            "image": uploaded_images["عظام الجمجمة"],
            "options": ["عظام الجمجمة", "عظام اليد", "العمود الفقري"],
            "answer": "عظام الجمجمة"
        }
    ]
}

# ================== باقي الأنواع ==================
section1_questions.update({
    "function": [
        {
            "question": "ما وظيفة الهيكل العظمي؟",
            "options": ["الحماية", "الهضم", "التنفس"],
            "answer": "الحماية"
        }
    ]
})

# ================== الهيكل ==================
subjects = {
    "science": {
        "title": "📚 كتاب العلوم",
        "units": {
            "u1": {
                "title": "📘 الوحدة الأولى",
                "video": "UNIT1_VIDEO",
                "sections": {
                    "s1": {
                        "title": "📂 الجهاز الدعامي",
                        "video": "SECTION1_VIDEO",
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

    # ================== عرض الصورة إذا موجودة ==================
    if quiz_type == "images":
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=q["image"],
            caption=q["question"]
        )
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text=q["question"])

    keyboard = [
        [InlineKeyboardButton("A", callback_data="0"),
         InlineKeyboardButton("B", callback_data="1"),
         InlineKeyboardButton("C", callback_data="2")]
    ]

    text_options = ""
    for i, opt in enumerate(q["options"]):
        text_options += f"{chr(65+i)}- {opt}\n"

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text_options,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الأزرار ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

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

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
