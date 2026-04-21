import os
import logging
import asyncio
from telegram.ext import MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN is missing")

ADMIN_ID = 8491023024

approved_users = set()
pending_users = set()

INTRO_VIDEO = "PUT_VIDEO_FILE_ID"

uploaded_images = {
    "الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ",
}

subjects = {
    "bio": {
        "u1_taaleel": [
            {
                "question": "لماذا عظم الفك السفلي متحرك؟",
                "options": ["التنفس", "المضغ والنطق", "الحماية"],
                "answer": "المضغ والنطق"
            }
        ],
        "u1_images": [
            {
                "type": "image",
                "image": "الهيكل العظمي",
                "question": "ما هو هذا الجزء؟",
                "options": ["الجمجمة", "الهيكل المحوري", "القص"],
                "answer": "الهيكل المحوري"
            }
        ]
    }
}

user_data = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in approved_users:
        pending_users.add(user_id)
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    await update.message.reply_text("✨ نرحب بكم في منصة بوابة العلامة الكاملة ✨")

    keyboard = [
        [InlineKeyboardButton("🧬 علم الأحياء و الأرض", callback_data="bio")]
    ]

    await update.message.reply_text(
        "📚 اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الوحدة ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # اختيار المادة
    if data == "bio":
        keyboard = [
            [InlineKeyboardButton("الوحدة 1", callback_data="bio_u1")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر الوحدة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # اختيار الوحدة + فيديو
    if data.startswith("bio_u"):
        unit = data.split("_")[1]

        user_data[user_id] = {
            "subject": "bio",
            "unit": unit
        }

        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=INTRO_VIDEO,
            caption="📺 شرح الوحدة"
        )

        keyboard = [
            [InlineKeyboardButton("▶️ ابدأ الاختبار", callback_data="choose_category")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🚀 بعد مشاهدة الفيديو:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # اختيار الأقسام
    if data == "choose_category":
        unit = user_data[user_id]["unit"]

        keyboard = [
            [InlineKeyboardButton("تعاليل", callback_data=f"{unit}_taaleel")],
            [InlineKeyboardButton("صور", callback_data=f"{unit}_images")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر القسم:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # بدء الاختبار
    if data.startswith("u"):
        category = data

        user_data[user_id].update({
            "category": category,
            "score": 0,
            "q_index": 0
        })

        await send_question(update, context)
        return

    # الإجابة
    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q = subjects[subject][category][index]
    selected = q["options"][int(data)]

    if selected == q["answer"]:
        user_data[user_id]["score"] += 10
        msg = "✅ صحيح"
    else:
        msg = f"❌ خطأ\n{q['answer']}"

    user_data[user_id]["q_index"] += 1

    await context.bot.send_message(chat_id=query.message.chat_id, text=msg)

    await asyncio.sleep(1)
    await send_question(update, context)

# ================== إرسال السؤال ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q_list = subjects[subject][category]

    if index >= len(q_list):
        score = user_data[user_id]["score"]

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎉 انتهيت\n📊 {score}"
        )
        return

    q = q_list[index]

    # صورة
    if q.get("type") == "image":
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=uploaded_images[q["image"]],
            caption=q["question"]
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=q["question"]
        )

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=str(i))]
        for i, opt in enumerate(q["options"])
    ]

    await context.bot.send_message(
        chat_id=chat_id,
        text="اختر:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
