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
TOKEN = os.environ.get("TOKEN")

if not MONGO_URL or not TOKEN:
    raise ValueError("Missing ENV variables")

client = MongoClient(MONGO_URL)
db = client["quiz_bot"]
users = db["users"]

# ================== لوج ==================
logging.basicConfig(level=logging.INFO)

# ================== الأدمن ==================
ADMIN_ID = 8491023024

# ================== بيانات المستخدم ==================
user_data = {}

# ================== دوال DB ==================
def get_user(user_id):
    return users.find_one({"_id": user_id})

def create_user(user_id):
    users.update_one(
        {"_id": user_id},
        {"$setOnInsert": {
            "_id": user_id,
            "approved": False,
            "pending": True,
            "score": 0
        }},
        upsert=True
    )

def approve_user(user_id):
    users.update_one(
        {"_id": user_id},
        {"$set": {"approved": True, "pending": False}}
    )

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not user:
        create_user(user_id)
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    if not user.get("approved"):
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    keyboard = [[InlineKeyboardButton("🧬 علم الأحياء", callback_data="bio")]]

    await update.message.reply_text(
        "✨ أهلاً بك!\n📚 اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الدفع ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"/approve {user_id}"
    )

    await update.message.reply_text("⏳ تم إرسال طلبك")

# ================== الموافقة ==================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    approve_user(user_id)

    await update.message.reply_text("✅ تم التفعيل")
    await context.bot.send_message(chat_id=user_id, text="🎉 تم قبولك")

# ================== عرض السؤال ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    data = user_data[user_id]
    q_list = data["questions"]
    index = data["index"]

    if index >= len(q_list):
        score = data["score"]
        total = len(q_list) * 10

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎉 انتهيت!\n📊 نتيجتك: {score}/{total}"
        )
        return

    q = q_list[index]

    # ===== نص السؤال =====
    text = f"❓ {q['question']}\n\n"

    for i, opt in enumerate(q["options"]):
        text += f"{chr(65+i)}. {opt}\n"

    # ===== أزرار بسيطة =====
    keyboard = [
        [InlineKeyboardButton(chr(65+i), callback_data=str(i))]
        for i in range(len(q["options"]))
    ]

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الأزرار ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # اختيار مادة
    if data == "bio":
        user_data[user_id] = {
            "questions": SAMPLE_QUESTIONS,
            "index": 0,
            "score": 0
        }

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="▶️ ابدأ الاختبار",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ابدأ", callback_data="start_quiz")]
            ])
        )
        return

    # بدء
    if data == "start_quiz":
        await send_question(update, context)
        return

    # إجابة
    if user_id not in user_data:
        return

    user = user_data[user_id]
    q = user["questions"][user["index"]]

    selected = q["options"][int(data)]

    if selected == q["answer"]:
        user["score"] += 10
        result = "✅ صحيح"
    else:
        result = f"❌ خطأ\n✔️ الإجابة: {q['answer']}"

    user["index"] += 1

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=result
    )

    await asyncio.sleep(1)
    await send_question(update, context)

# ================== بيانات تجريبية ==================
SAMPLE_QUESTIONS = [
    {
        "question": "لماذا يزداد طول رواد الفضاء؟",
        "options": [
            "بسبب زيادة الكالسيوم",
            "بسبب غياب الجاذبية مما يقلل الضغط على الفقرات",
            "بسبب التمارين"
        ],
        "answer": "بسبب غياب الجاذبية مما يقلل الضغط على الفقرات"
    }
]

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
