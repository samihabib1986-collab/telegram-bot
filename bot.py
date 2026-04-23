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
    "dam": "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ"
}

# ================== الصور ==================
uploaded_images = {
    "الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ"
}

# ================== بنك الأسئلة ==================
subjects = {
    "bio": {

        "u1_dam_taaleel": [
            {
                "question": "لماذا العظام صلبة؟",
                "options": ["لوجود الكالسيوم", "لوجود الماء", "لوجود الدهون"],
                "answer": "لوجود الكالسيوم"
            }
        ],

        "u1_dam_images": [
            {
                "image": "الهيكل العظمي",
                "question": "ما هذا؟",
                "options": ["الهيكل العظمي", "عضلة", "عصب"],
                "answer": "الهيكل العظمي"
            }
        ],

        "u1_dam_where": [],
        "u1_dam_level": [],
        "u1_dam_result1": [],
        "u1_dam_function": []
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

    await update.message.reply_text(
        "✨ نرحب بكم في منصة بوابة العلامة الكاملة ✨\n"
        "✨إشراف الاستاذ :احمد نور الدين  939138720✨\n"
        "✨ برمجة وتصميم المهندس :سامي حبيب  943512782✨/"
    )

    keyboard = [
        [InlineKeyboardButton("🧬 علم الأحياء و الأرض", callback_data="bio")]
    ]

    await update.message.reply_text(
        "📚 اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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

    # ✅ حل مشكلة الصور
    if "image" in q:
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

        if user_id not in user_data:
            return

        unit = user_data[user_id]["unit"]
        section = user_data[user_id]["section"]

        category = f"{unit}_{section}_{data}"

        if category not in subjects["bio"]:
            await query.message.reply_text("❌ لا يوجد أسئلة لهذا القسم")
            return

        user_data[user_id]["category"] = category

        keyboard = [[
            InlineKeyboardButton("▶️ بدء الاختبار", callback_data="start_quiz")
        ]]

        await query.message.reply_text("ابدأ 👇", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # بدء الاختبار
    if data == "start_quiz":
        await send_question(update, context)
        return

    # الإجابة
    if user_id not in user_data:
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
