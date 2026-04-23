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
# ================== الصور ==================
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
# ================== أسئلة (لكل نوع بنك مستقل) ==================

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
            "question": "أي صورة تمثل الهيكل العظمي؟",
            "options": ["صورة عظام", "صورة قلب", "صورة معدة"],
            "answer": "صورة عظام"
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
            "question": "رتب مراحل حماية الجسم",
            "options": ["عظام → حماية", "دم → حماية", "هواء → حماية"],
            "answer": "عظام → حماية"
        }
    ]
}

section2_questions = {
    "function": [
        {
            "question": "ما وظيفة الجهاز العصبي؟",
            "options": ["التنسيق", "الهضم", "الإخراج"],
            "answer": "التنسيق"
        }
    ],
    "taaleel": [
        {
            "question": "علل: أهمية الجهاز العصبي؟",
            "options": ["للتنسيق", "للهضم", "للتنفس"],
            "answer": "للتنسيق"
        }
    ],
    "images": [
        {
            "question": "أي صورة تمثل الجهاز العصبي؟",
            "options": ["دماغ", "قلب", "رئة"],
            "answer": "دماغ"
        }
    ],
    "where": [
        {
            "question": "أين يوجد الجهاز العصبي؟",
            "options": ["في الجسم", "في الجلد", "في الدم"],
            "answer": "في الجسم"
        }
    ],
    "level": [
        {
            "question": "رتب انتقال الإشارات",
            "options": ["دماغ → أعصاب", "أعصاب → دم", "قلب → دماغ"],
            "answer": "دماغ → أعصاب"
        }
    ]
}

section3_questions = {
    "function": [
        {
            "question": "ما وظيفة الغدد الصماء؟",
            "options": ["إفراز هرمونات", "الهضم", "التنفس"],
            "answer": "إفراز هرمونات"
        }
    ],
    "taaleel": [
        {
            "question": "علل: أهمية الغدد الصماء؟",
            "options": ["تنظيم الجسم", "الهضم", "التنفس"],
            "answer": "تنظيم الجسم"
        }
    ],
    "images": [
        {
            "question": "أي صورة تمثل الغدد الصماء؟",
            "options": ["غدة", "قلب", "عظام"],
            "answer": "غدة"
        }
    ],
    "where": [
        {
            "question": "أين توجد الغدد الصماء؟",
            "options": ["في الجسم", "في الدم", "في الجلد"],
            "answer": "في الجسم"
        }
    ],
    "level": [
        {
            "question": "رتب تأثير الهرمونات",
            "options": ["غدة → دم → جسم", "دم → غدة → جسم", "جسم → دم → غدة"],
            "answer": "غدة → دم → جسم"
        }
    ]
}

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
# ================== add ID ==================
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    await update.message.reply_text(photo)
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
    if quiz_type == "images":
        await context.bot.send_photo(
        chat_id=query.message.chat_id,
        photo=q["options"][0],
        caption=q["question"]
    )
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

    if data == "science":
        keyboard = [
            [InlineKeyboardButton("📘 الوحدة الأولى", callback_data="u1")]
        ]
        await context.bot.send_message(chat_id=query.message.chat_id, text="اختر الوحدة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("u"):
        user_data[user_id] = {"unit": data, "q_index": 0}

        unit = subjects["science"]["units"][data]

        keyboard = [[InlineKeyboardButton("🎬 فيديو الوحدة", callback_data="UNIT1_VIDEO")]]

        for key, sec in unit["sections"].items():
            keyboard.append([InlineKeyboardButton(sec["title"], callback_data=f"sec_{key}")])

        await context.bot.send_message(chat_id=query.message.chat_id, text=unit["title"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "UNIT1_VIDEO":
        unit = user_data[user_id]["unit"]
        video = subjects["science"]["units"][unit]["video"]

        await context.bot.send_video(chat_id=query.message.chat_id, video=video)
        return

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

    if data == "sec_video":
        unit = user_data[user_id]["unit"]
        sec = user_data[user_id]["section"]

        video = subjects["science"]["units"][unit]["sections"][sec]["video"]

        await context.bot.send_video(chat_id=query.message.chat_id, video=video)
        return

    if data == "start_quiz":
        keyboard = [
            [InlineKeyboardButton("🧠 تعاليل", callback_data="quiz_taaleel")],
            [InlineKeyboardButton("🖼 صور", callback_data="quiz_images")],
            [InlineKeyboardButton("📍 أين", callback_data="quiz_where")],
            [InlineKeyboardButton("🔁 ترتيب", callback_data="quiz_level")],
            [InlineKeyboardButton("⚙️ وظيفة", callback_data="quiz_function")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر نوع الأسئلة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("quiz_"):
        quiz_type = data.replace("quiz_", "")
        user_data[user_id]["quiz_type"] = quiz_type
        user_data[user_id]["q_index"] = 0

        await send_question(update, context)
        return

    q_data = user_data[user_id]
    q_list = subjects["science"]["units"][q_data["unit"]]["sections"][q_data["section"]]["questions"].get(q_data.get("quiz_type", "function"), [])
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
app.add_handler(MessageHandler(filters.PHOTO, get_id))
app.run_polling()
