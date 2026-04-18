import os
import logging

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

# ================== الاشتراك ==================
ADMIN_ID = 123456789  # 🔴 ضع ايديك هنا

approved_users = set()
pending_users = set()

# ================== تخزين الصور ==================
uploaded_images = {}

# ================== بنك الأسئلة (تصنيفات) ==================
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
"image": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Human_skull_side_simplified.png",
"question": "الهيكل المحوري",
"options": ["1,2,3,4,5,6,7,8,9,10,11"],
"answer": "1"
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

        await update.message.reply_text(
            "💰 هذا البوت مدفوع\n\n"
            "1️⃣ ادفع\n"
            "2️⃣ ثم اكتب /paid"
        )
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
        [InlineKeyboardButton("🏆 أفضل الطلاب", callback_data="leaderboard")]
    ]

    await update.message.reply_text(
        "🎯 اختر التصنيف:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الدفع ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in approved_users:
        await update.message.reply_text("✅ أنت مشترك بالفعل")
        return

    pending_users.add(user_id)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💳 طلب اشتراك:\nUser ID: {user_id}\n/approve {user_id}"
    )

    await update.message.reply_text("⏳ تم إرسال طلبك")

# ================== الموافقة ==================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("استخدم: /approve USER_ID")
        return

    user_id = int(context.args[0])
    approved_users.add(user_id)
    pending_users.discard(user_id)

    await update.message.reply_text("✅ تم التفعيل")

    await context.bot.send_message(
        chat_id=user_id,
        text="🎉 تم قبول اشتراكك"
    )

# ================== إرسال سؤال ==================
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
        leaderboard[user_id] = score

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

    # 📸 صورة
    if q.get("type") == "image":
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=q["image"],
            caption=q["question"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
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

    # leaderboard
    if data == "leaderboard":
        if not leaderboard:
            await query.edit_message_text("لا يوجد نتائج")
            return

        text = "🏆 النتائج:\n\n"
        sorted_board = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

        for i, (uid, score) in enumerate(sorted_board[:10], 1):
            text += f"{i}. {uid} - {score}\n"

        await query.edit_message_text(text)
        return

    # اختيار تصنيف
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

    # إجابة
    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q = subjects[subject][category][index]
    selected = q["options"][int(data)]

    if selected == q["answer"]:
        user_data[user_id]["score"] += 10
        text = "✅ صحيح!"
    else:
        text = f"❌ خطأ! الإجابة: {q['answer']}"

    user_data[user_id]["q_index"] += 1

    await query.edit_message_text(text)
    await send_question(update, context)

# ================== رفع الصور من الموبايل ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    photo = update.message.photo[-1]
    file_id = photo.file_id

    context.user_data["pending_file_id"] = file_id

    await update.message.reply_text("✏️ أرسل اسم الصورة")

# ================== حفظ اسم الصورة ==================
async def save_image_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    if "pending_file_id" not in context.user_data:
        return

    name = update.message.text
    file_id = context.user_data["pending_file_id"]

    uploaded_images[name] = file_id

    await update.message.reply_text(f"✅ تم حفظ الصورة باسم: {name}")

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
