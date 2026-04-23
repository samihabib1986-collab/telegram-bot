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

print("BOT IS RUNNING")

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

# ================== فيديوهات ==================
UNIT_VIDEOS = {
    "u1": "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ"
}

SECTION_VIDEOS = {
    "dam": "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ",
    "ns": "PUT_YOUR_VIDEO_FILE_ID_HERE"
}

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

# صور الجهاز العصبي
"الدماغ": "PUT_FILE_ID",
"العصبون": "PUT_FILE_ID",
"النخاع الشوكي": "PUT_FILE_ID"
}

# ================== بنك الأسئلة ==================
subjects = {
    "bio": {

        # ================== الجهاز العصبي ==================
        "u1_ns_taaleel": [
            {
                "question": "1. لماذا يعد الجهاز العصبي مهماً؟",
                "options": ["لأنه مسؤول عن الهضم", "لأنه ينظم جميع أنشطة الجسم", "لأنه يخزن الطاقة"],
                "answer": "لأنه ينظم جميع أنشطة الجسم"
            }
        ],

        "u1_ns_images": [
            {
                "type": "image",
                "image": "الدماغ",
                "question": "1",
                "options": ["المخ", "المخيخ", "النخاع"],
                "answer": "المخ"
            }
        ],

        "u1_ns_where": [
            {
                "question": "أين يقع الدماغ؟",
                "options": ["في الصدر", "في الجمجمة", "في البطن"],
                "answer": "في الجمجمة"
            }
        ],

        "u1_ns_level": [
            {
                "question": "ترتيب أجزاء العصبون:",
                "options": ["محور ⬅️ جسم الخلية ⬅️ تغصنات", "تغصنات ⬅️ جسم الخلية ⬅️ محور", "جسم الخلية ⬅️ محور ⬅️ تغصنات"],
                "answer": "تغصنات ⬅️ جسم الخلية ⬅️ محور"
            }
        ],

        "u1_ns_result1": [
            {
                "question": "ماذا يحدث عند تلف النخاع الشوكي؟",
                "options": ["زيادة الذكاء", "شلل", "زيادة القوة"],
                "answer": "شلل"
            }
        ],

        "u1_ns_function": [
            {
                "question": "ما وظيفة العصبونات؟",
                "options": ["نقل السيالات العصبية", "الهضم", "التخزين"],
                "answer": "نقل السيالات العصبية"
            }
        ]
    }
}

# ================== بيانات المستخدم ==================
user_data = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user = users.find_one({"_id": user_id})

    if not user:
        users.insert_one({"_id": user_id, "approved": False})
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    if not user.get("approved"):
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    keyboard = [
        [InlineKeyboardButton("🧬 علم الأحياء", callback_data="bio")]
    ]

    await update.message.reply_text("📚 اختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))

# ================== إرسال السؤال ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q_list = subjects[subject][category]

    if index >= len(q_list):
        await context.bot.send_message(chat_id=query.message.chat_id, text="🎉 انتهيت!")
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

    if q.get("type") == "image":
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=uploaded_images[q["image"]],
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
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

    if data == "bio":
        keyboard = [
            [InlineKeyboardButton("الوحدة 1", callback_data="bio_u1")]
        ]
        await query.message.reply_text("اختر الوحدة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "bio_u1":
        keyboard = [
            [InlineKeyboardButton("🎬 فيديو الوحدة", callback_data="unit_video")],
            [InlineKeyboardButton("القسم الأول: الدعامي الحركي", callback_data="sec_u1_dam")],
            [InlineKeyboardButton("القسم الثاني: الجهاز العصبي", callback_data="sec_u1_ns")]
        ]
        await query.message.reply_text("📘 الوحدة 1:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "sec_u1_ns":
        user_data[user_id] = {
            "subject": "bio",
            "unit": "u1",
            "section": "ns",
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

        await query.message.reply_text("📚 الجهاز العصبي:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data in ["taaleel", "images", "where", "level", "result1", "function"]:
        unit = user_data[user_id]["unit"]
        section = user_data[user_id]["section"]
        category = f"{unit}_{section}_{data}"

        user_data[user_id]["category"] = category

        keyboard = [[InlineKeyboardButton("▶️ بدء", callback_data="start_quiz")]]

        await query.message.reply_text("ابدأ", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "start_quiz":
        await send_question(update, context)
        return

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q = subjects[subject][category][index]
    selected = q["options"][int(data)]

    if selected == q["answer"]:
        user_data[user_id]["score"] += 10
        result = "✔️ صحيح"
    else:
        result = f"❌ خطأ\nالإجابة: {q['answer']}"

    user_data[user_id]["q_index"] += 1

    await query.message.reply_text(result)
    await asyncio.sleep(1)
    await send_question(update, context)

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
