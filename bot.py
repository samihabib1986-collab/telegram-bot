import json
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

# ================== الأدمن ==================
ADMIN_ID = 8491023024

# ================== KV ==================
# سيتم ربطه من Worker
KV = None

approved_users = set()
pending_users = set()

# ================== تحميل المستخدمين من KV ==================
async def load_users():
    global approved_users, pending_users

    data = await KV.get("users")

    if data:
        obj = json.loads(data)
        approved_users = set(obj.get("approved_users", []))
        pending_users = set(obj.get("pending_users", []))
    else:
        approved_users = set()
        pending_users = set()

# ================== حفظ المستخدمين في KV ==================
async def save_users():
    data = {
        "approved_users": list(approved_users),
        "pending_users": list(pending_users)
    }

    await KV.put("users", json.dumps(data))

# ================== الصور ==================
uploaded_images = {
    "الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ",
}

# ================== بنك الأسئلة ==================
subjects = {
    "bio": {
        "taaleel": [
            {
                "question": "1. لماذا عظم الفك السفلي متحرك؟",
                "options": [" لتسهيل التنفس"," لتسهيل المضغ والنطق "," لحماية الدماغ"],
                "answer": " لتسهيل المضغ والنطق "
            }
        ],
        "images": [
            {
                "type": "image",
                "image": "الهيكل العظمي",
                "question": "ما هذا؟",
                "options": ["الجمجمة","الهيكل المحوري","القص"],
                "answer": "الهيكل المحوري"
            }
        ]
    }
}

# ================== بيانات المستخدم ==================
user_data = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in approved_users:
        pending_users.add(user_id)
        await save_users()

        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    keyboard = [
        [InlineKeyboardButton("📘 تعاليل", callback_data="bio_taaleel")],
        [InlineKeyboardButton("🖼 صور", callback_data="bio_images")]
    ]

    await update.message.reply_text(
        "🎯 اختر:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الدفع ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    pending_users.add(user_id)
    await save_users()

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💳 طلب اشتراك:\n/approve {user_id}"
    )

    await update.message.reply_text("⏳ تم الإرسال")

# ================== الموافقة ==================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])

    approved_users.add(user_id)
    pending_users.discard(user_id)

    await save_users()

    await update.message.reply_text("✅ تم التفعيل")
    await context.bot.send_message(chat_id=user_id, text="🎉 تم قبولك")

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
            text=f"🎉 انتهيت!\n📊 نتيجتك: {score}"
        )
        return

    q = q_list[index]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=str(i))]
        for i, opt in enumerate(q["options"])
    ]

    if q.get("type") == "image":
        file_id = uploaded_images.get(q["image"])

        if file_id:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=file_id,
                caption=q["question"],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await context.bot.send_message(chat_id, "❌ الصورة غير موجودة")
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=q["question"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ================== الأزرار ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if "_" in data:
        subject, category = data.split("_")

        user_data[user_id] = {
            "score": 0,
            "q_index": 0,
            "subject": subject,
            "category": category
        }

        await query.edit_message_text("🚀 بدأ الاختبار")
        await send_question(update, context)
        return

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q = subjects[subject][category][index]
    selected = q["options"][int(data)]

    if selected == q["answer"]:
        user_data[user_id]["score"] += 10
        text = "✅ صحيح"
    else:
        text = f"❌ خطأ\nالإجابة: {q['answer']}"

    user_data[user_id]["q_index"] += 1

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=text
    )

    await asyncio.sleep(1)
    await send_question(update, context)

# ================== تشغيل البوت ==================
app = ApplicationBuilder().token(TOKEN).build()

# 🔥 ربط KV من Worker
app.bot_data["KV"] = KV_NAMESPACE

# تحميل المستخدمين عند التشغيل
asyncio.get_event_loop().run_until_complete(load_users())

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(button))

if __name__ == "__main__":
    app.run_polling()
