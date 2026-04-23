import os
import logging
import asyncio
from pymongo import MongoClient
from telegram.ext import MessageHandler, filters
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

# ================== قواعد البيانات ==================
def get_user(user_id):
    return users.find_one({"_id": user_id})

def create_user(user_id):
    users.update_one(
        {"_id": user_id},
        {
            "$setOnInsert": {
                "_id": user_id,
                "approved": False,
                "pending": True,
                "score": 0,
                "q_index": 0
            }
        },
        upsert=True
    )

def approve_user(user_id):
    users.update_one(
        {"_id": user_id},
        {"$set": {"approved": True, "pending": False}},
        upsert=True
    )

# ================== الفيديو ==================
INTRO_VIDEO = "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ"

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

# ================== بنك الأسئلة ==================
subjects = {
    "bio": {
        "u1_taaleel": [],
        "u1_images": [],
        "u1_where": [],
        "u1_level": [],
        "u1_result1": [],
        "u1_function": []
    }
}

# ================== بيانات المستخدم ==================
user_data = {}

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

    await update.message.reply_text(
        "✨ نرحب بكم في منصة بوابة العلامة الكاملة ✨"
    )

    keyboard = [
        [InlineKeyboardButton("🧬 علم الأحياء و الأرض", callback_data="bio")]
    ]

    await update.message.reply_text(
        "📚 اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الدفع ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    create_user(user_id)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💳 طلب اشتراك:\n/approve {user_id}"
    )

    await update.message.reply_text("⏳ تم إرسال طلبك")

# ================== الموافقة ==================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])

    approve_user(user_id)

    await update.message.reply_text("تم التفعيل")
    await context.bot.send_message(chat_id=user_id, text="اضغط /start")

# ================== إرسال السؤال ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q_list = subjects[subject][category]

    if index >= len(q_list):
        score = user_data[user_id]["score"]

        users.update_one(
            {"_id": user_id},
            {"$set": {"score": score}}
        )

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"🎉 انتهيت!\n📊 نتيجتك: {score}"
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

    # ================== المادة ==================
    if data == "bio":
        keyboard = [
            [InlineKeyboardButton("الوحدة 1", callback_data="bio_u1")]
        ]

        await query.message.reply_text(
            "🧬 اختر الوحدة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================== الوحدة ==================
    if data == "bio_u1":

        # 👇 هنا أضفنا القسم
        keyboard = [
            [InlineKeyboardButton("القسم الأول: الدعامي الحركي", callback_data="sec_u1_dam")]
        ]

        await query.message.reply_text(
            "📘 اختر القسم:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================== القسم ==================
    if data == "sec_u1_dam":

        user_data[user_id] = {
            "subject": "bio",
            "unit": "u1",
            "section": "dam",
            "score": 0,
            "q_index": 0
        }

        keyboard = [
            [InlineKeyboardButton("📘 تعليل", callback_data="taaleel")],
            [InlineKeyboardButton("🖼️ صور", callback_data="images")],
            [InlineKeyboardButton("📍 موقع", callback_data="where")],
            [InlineKeyboardButton("📊 ترتيب", callback_data="level")],
            [InlineKeyboardButton("🧠 نتائج", callback_data="result1")],
            [InlineKeyboardButton("⚙️ وظيفة", callback_data="function")]
        ]

        await query.message.reply_text(
            "📚 اختر نوع الأسئلة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================== نوع الأسئلة ==================
    if data in ["taaleel", "images", "where", "level", "result1", "function"]:

        category = f"{user_data[user_id]['unit']}_{data}"

        user_data[user_id]["category"] = category

        keyboard = [[
            InlineKeyboardButton("▶️ بدء الاختبار", callback_data="start_quiz")
        ]]

        await query.message.reply_text(
            "ابدأ الآن 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================== بدء الاختبار ==================
    if data == "start_quiz":
        await send_question(update, context)
        return

    # ================== الإجابة ==================
    if user_id not in user_data:
        return

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q = subjects[subject][category]
    selected = q[index]["options"][int(data)]

    if selected == q[index]["answer"]:
        user_data[user_id]["score"] += 10
        result = "✔️ صحيح"
    else:
        result = f"❌ خطأ\n{q[index]['answer']}"

    user_data[user_id]["q_index"] += 1

    await query.message.reply_text(result)
    await asyncio.sleep(1)
    await send_question(update, context)

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CallbackQueryHandler(button))

if __name__ == "__main__":
    app.run_polling()
