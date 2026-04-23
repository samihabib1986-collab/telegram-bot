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
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================== Token ==================
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN is missing")

ADMIN_ID = 8491023024

# ================== Videos ==================
UNIT_VIDEOS = {
    "u1": "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ"
}

SECTION_VIDEOS = {
    "dam": "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ",
    "ns": "PUT_YOUR_VIDEO_FILE_ID_HERE"
}

# ================== Images ==================
uploaded_images = {
    "الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ",
    "الاربطة والاوتار": "AgACAgQAAxkBAAIDxGnj27EBbQ7NdocwG8BMMx-pXpz0AAJvDGsb4XYhU0SlG3BDNztZAQADAgADbQADOwQ",
}

# ================== Questions ==================
subjects = {
    "bio": {
        "u1_dam_taaleel": [
            {
                "question": "لماذا توفر مفاصل القحف أقصى درجات الحماية للدماغ؟",
                "options": [
                    "لأنها مفاصل واسعة الحركة",
                    "لأنها محاطة بأوتار قوية",
                    "لأنها مفاصل ثابتة تلتحم بواسطة مسننات عظمية"
                ],
                "answer": "لأنها مفاصل ثابتة تلتحم بواسطة مسننات عظمية"
            }
        ],

        "u1_dam_images": [
            {
                "type": "image",
                "image": "الاربطة والاوتار",
                "question": "ما هو الشكل؟",
                "options": ["أوتار", "عضلة", "أربطة"],
                "answer": "أربطة"
            }
        ],

        "u1_ns_taaleel": [
            {
                "question": "لماذا توفر أغشية السحايا حماية إضافية؟",
                "options": [
                    "تحول دون وصول الأكسجين",
                    "تفصل المراكز العصبية عن العظام",
                    "تفرز هرمونات"
                ],
                "answer": "تفصل المراكز العصبية عن العظام"
            }
        ]
    }
}

# ================== User Data ==================
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
        "✨ أهلاً بك في منصة بوابة العلامة الكاملة ✨"
    )

    keyboard = [
        [InlineKeyboardButton("🧬 علم الأحياء", callback_data="bio")]
    ]

    await update.message.reply_text(
        "📚 اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== SEND QUESTION ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_data:
        return

    data = user_data[user_id]

    subject = data["subject"]
    category = data["category"]
    index = data["q_index"]

    q_list = subjects[subject][category]

    if index >= len(q_list):
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🎉 انتهيت من الاختبار!"
        )
        return

    q = q_list[index]

    text = q["question"] + "\n\n"
    for i, opt in enumerate(q["options"]):
        text += f"{chr(65+i)} - {opt}\n"

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

# ================== BUTTONS ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # المادة
    if data == "bio":
        keyboard = [[InlineKeyboardButton("الوحدة 1", callback_data="bio_u1")]]
        await query.message.reply_text("اختر الوحدة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # الوحدة
    if data == "bio_u1":
        keyboard = [
            [InlineKeyboardButton("🎬 فيديو", callback_data="unit_video")],
            [InlineKeyboardButton("الدعامي", callback_data="sec_dam")],
            [InlineKeyboardButton("العصبي", callback_data="sec_ns")]
        ]
        await query.message.reply_text("الوحدة 1:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # فيديو الوحدة
    if data == "unit_video":
        await context.bot.send_video(chat_id=query.message.chat_id, video=UNIT_VIDEOS["u1"])
        return

    # ================== القسم الدعامي ==================
    if data == "sec_dam":
        user_data[user_id] = {
            "subject": "bio",
            "unit": "u1",
            "section": "dam",
            "q_index": 0,
            "score": 0
        }

        keyboard = [[InlineKeyboardButton("ابدأ الاختبار", callback_data="start_quiz")]]
        await query.message.reply_text("قسم الدعامي", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ================== القسم العصبي ==================
    if data == "sec_ns":
        user_data[user_id] = {
            "subject": "bio",
            "unit": "u1",
            "section": "ns",
            "q_index": 0,
            "score": 0
        }

        keyboard = [[InlineKeyboardButton("ابدأ الاختبار", callback_data="start_quiz")]]
        await query.message.reply_text("قسم العصبي", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # بدء الاختبار
    if data == "start_quiz":
        await send_question(update, context)
        return

    # ================== الإجابة ==================
    if data in ["0", "1", "2"]:

        if user_id not in user_data:
            return

        info = user_data[user_id]

        subject = info["subject"]
        category = f"{info['unit']}_{info['section']}_taaleel"

        if category not in subjects[subject]:
            return

        q = subjects[subject][category][info["q_index"]]

        try:
            selected = q["options"][int(data)]
        except:
            return

        if selected == q["answer"]:
            info["score"] += 10
            result = "✔️ صحيح"
        else:
            result = f"❌ خطأ\nالإجابة: {q['answer']}"

        info["q_index"] += 1

        await query.message.reply_text(result)
        await asyncio.sleep(1)
        await send_question(update, context)

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
