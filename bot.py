import os
import logging
import json
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
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

approved_users = set()
pending_users = set()

# ================== الصور ==================
uploaded_images = {}

# تحميل الصور من JSON
if os.path.exists("images.json") and os.path.getsize("images.json") > 0:
    try:
        with open("images.json", "r", encoding="utf-8") as f:
            uploaded_images = json.load(f)
    except json.JSONDecodeError:
        uploaded_images = {}

# ================== بنك الأسئلة ==================
subjects = {
    "bio": {
        "taaleel": [
            {
                "question": "لماذا عظم الفك السفلي متحرك؟",
                "options": ["لتسهيل المضغ والنطق", "لحماية الدماغ", "لتخفيف الوزن"],
                "answer": "لتسهيل المضغ والنطق"
            },
            {
                "question": "لماذا توجد أقراص غضروفية بين الفقرات؟",
                "options": ["لمنع الاحتكاك", "لزيادة الطول", "لتقوية العضلات"],
                "answer": "لمنع الاحتكاك"
            }
        ],

        "images": [
            {
                "type": "image",
                "image": "الهيكل العظمي",
                "question": "ما هذا العظم؟",
                "options": ["جمجمة", "فخذ", "ترقوة"],
                "answer": "جمجمة"
            }
        ]
    }
}

# ================== بيانات المستخدم ==================
user_data = {}
leaderboard = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in approved_users:
        pending_users.add(user_id)
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid")
        return

    user_data[user_id] = {
        "score": 0,
        "q_index": 0,
        "subject": None,
        "category": None
    }

    keyboard = [
        [InlineKeyboardButton("📘 تعاليل", callback_data="bio_taaleel")],
        [InlineKeyboardButton("🖼 صور", callback_data="bio_images")],
        [InlineKeyboardButton("🏆 النتائج", callback_data="leaderboard")]
    ]

    await update.message.reply_text(
        "🎯 اختر:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الدفع ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in approved_users:
        await update.message.reply_text("✅ أنت مشترك")
        return

    pending_users.add(user_id)

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

    # 🏁 نهاية الاختبار
    if index >= len(q_list):
        score = user_data[user_id]["score"]

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎉 انتهيت!\n📊 نتيجتك: {score} من {len(q_list)*10}"
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

    if data == "leaderboard":
        await query.edit_message_text("🏆 لا يوجد نتائج")
        return

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

    # ================== الإجابة ==================
    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q = subjects[subject][category][index]

    selected = q["options"][int(data)]

    if selected == q["answer"]:
        user_data[user_id]["score"] += 10
        result = "✅ صحيح"
    else:
        result = f"❌ خطأ\nالإجابة: {q['answer']}"

    user_data[user_id]["q_index"] += 1

    await query.edit_message_text(result)
    await asyncio.sleep(1)

    await send_question(update, context)

# ================== رفع الصور ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    file_id = update.message.photo[-1].file_id
    context.user_data["pending_file_id"] = file_id

    await update.message.reply_text("✍️ أرسل اسم الصورة")
    await update.message.reply_text(update.message.photo[-1].file_id)
# ================== حفظ الصورة ==================
async def save_image_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if "pending_file_id" not in context.user_data:
        return

    name = update.message.text
    file_id = context.user_data["pending_file_id"]

    uploaded_images[name] = file_id

    with open("images.json", "w", encoding="utf-8") as f:
        json.dump(uploaded_images, f, ensure_ascii=False, indent=4)

    await update.message.reply_text(f"✅ تم حفظ: {name}")

    del context.user_data["pending_file_id"]

# ================== تشغيل البوت ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("approve", approve))

app.add_handler(CallbackQueryHandler(button))

app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_image_name))

if __name__ == "__main__":
    app.run_polling()
