import os
import random
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

# ================== CONFIG ==================
TOKEN = os.environ.get("TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")

ADMIN_ID = 8491023024

client = MongoClient(MONGO_URL)
db = client["quiz_bot"]
users = db["users"]
questions_db = db["questions"]

logging.basicConfig(level=logging.INFO)

# ================== SAMPLE QUESTION BANK ==================
# (يمكنك لاحقًا تكبيره أو تخزينه في MongoDB)
QUESTIONS = [
    {
        "id": 1,
        "question": "لماذا عظم الفك السفلي متحرك؟",
        "options": [
            "لتسهيل التنفس",
            "لتسهيل المضغ والنطق",
            "لحماية الدماغ"
        ],
        "answer": "لتسهيل المضغ والنطق",
        "level": "easy"
    },
    {
        "id": 2,
        "question": "أين يوجد عظم الرضفة؟",
        "options": [
            "مفصل الكتف",
            "مفصل الركبة",
            "الجمجمة"
        ],
        "answer": "مفصل الركبة",
        "level": "easy"
    },
    {
        "id": 3,
        "question": "لماذا تتصلب العظام؟",
        "options": [
            "بسبب الماء",
            "بسبب أملاح الكالسيوم",
            "بسبب العضلات"
        ],
        "answer": "بسبب أملاح الكالسيوم",
        "level": "medium"
    }
]

# ================== DB HELPERS ==================
def get_user(user_id):
    return users.find_one({"_id": user_id})

def create_user(user_id):
    users.update_one(
        {"_id": user_id},
        {"$setOnInsert": {
            "_id": user_id,
            "approved": True if user_id == ADMIN_ID else False,
            "score": 0,
            "used_questions": [],
            "current_q": None,
            "in_exam": False
        }},
        upsert=True
    )

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    create_user(user_id)

    user = get_user(user_id)

    if not user["approved"]:
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    keyboard = [
        [InlineKeyboardButton("🧠 بدء امتحان", callback_data="start_exam")],
        [InlineKeyboardButton("📊 نتيجتي", callback_data="my_score")]
    ]

    await update.message.reply_text(
        "🎓 مرحباً بك في نظام الامتحان الذكي",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== PAID ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await context.bot.send_message(
        ADMIN_ID,
        f"طلب اشتراك:\n/approve {user_id}"
    )

    await update.message.reply_text("⏳ تم إرسال الطلب")

# ================== APPROVE ==================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        return

    user_id = int(context.args[0])

    users.update_one(
        {"_id": user_id},
        {"$set": {"approved": True}}
    )

    await context.bot.send_message(user_id, "✅ تم تفعيل حسابك")
    await update.message.reply_text("تم التفعيل")

# ================== GET RANDOM QUESTION ==================
def get_random_question(user):
    used = user.get("used_questions", [])

    available = [q for q in QUESTIONS if q["id"] not in used]

    if not available:
        return None

    return random.choice(available)

# ================== SEND QUESTION ==================
async def send_question(chat_id, user_id, context):
    user = get_user(user_id)

    q = get_random_question(user)

    if not q:
        await context.bot.send_message(chat_id, "🎉 انتهى الامتحان")
        return

    users.update_one(
        {"_id": user_id},
        {"$set": {"current_q": q["id"]}}
    )

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"ans|{opt}")]
        for opt in q["options"]
    ]

    await context.bot.send_message(
        chat_id,
        f"❓ {q['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== BUTTON HANDLER ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    user = get_user(user_id)

    # ================== START EXAM ==================
    if data == "start_exam":
        users.update_one(
            {"_id": user_id},
            {"$set": {
                "score": 0,
                "used_questions": [],
                "in_exam": True
            }}
        )

        await send_question(query.message.chat_id, user_id, context)
        return

    # ================== SCORE ==================
    if data == "my_score":
        await query.message.reply_text(f"📊 نتيجتك: {user['score']}")
        return

    # ================== ANSWER ==================
    if data.startswith("ans|"):
        if not user["in_exam"]:
            return

        selected = data.split("|")[1]
        qid = user["current_q"]

        q = next((x for x in QUESTIONS if x["id"] == qid), None)

        if not q:
            return

        if selected == q["answer"]:
            users.update_one(
                {"_id": user_id},
                {"$inc": {"score": 10}}
            )
            result = "✅ صحيح"
        else:
            result = f"❌ خطأ\nالإجابة: {q['answer']}"

        users.update_one(
            {"_id": user_id},
            {
                "$push": {"used_questions": qid}
            }
        )

        await query.message.reply_text(result)
        await asyncio.sleep(1)

        await send_question(query.message.chat_id, user_id, context)

# ================== ADMIN PANEL ==================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    count = users.count_documents({"approved": True})

    await update.message.reply_text(f"""
📊 لوحة الأدمن:

👥 المستخدمين المفعّلين: {count}
""")

# ================== APP ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CallbackQueryHandler(button))

if __name__ == "__main__":
    app.run_polling()
