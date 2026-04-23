import os
import logging
import asyncio
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================== إعداد MongoDB ==================
MONGO_URL = os.environ.get("MONGO_URL")

if not MONGO_URL:
    raise ValueError("MONGO_URL is missing")

client = MongoClient(MONGO_URL)
db = client["quiz_bot"]
users = db["users"]
media_db = db["media_files"]

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
}

# ================== بنك الأسئلة (كل الأنواع بدون حذف) ==================
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
                "question": "ما هو هذا الشكل؟",
                "options": ["أوتار", "عضلة", "أربطة"],
                "answer": "أربطة"
            }
        ],

        "u1_dam_where": [
            {
                "question": "حدد موقع النسيج العظمي الكثيف:",
                "options": [
                    "في المشاشتين فقط",
                    "داخل غضاريف النمو",
                    "طبقة تحت السمحاق وتشكل جسم العظم"
                ],
                "answer": "طبقة تحت السمحاق وتشكل جسم العظم"
            }
        ],

        "u1_dam_level": [
            {
                "question": "استجابة العضلة:",
                "options": [
                    "تقلص ثم جهد",
                    "تنبيه ثم استرخاء",
                    "تنبيه → استجابة → عودة"
                ],
                "answer": "تنبيه → استجابة → عودة"
            }
        ],

        "u1_dam_result1": [
            {
                "question": "نتيجة المقوية العضلية:",
                "options": [
                    "انحناء الرقبة",
                    "ثبات الرأس",
                    "تعب"
                ],
                "answer": "ثبات الرأس"
            }
        ],

        "u1_dam_function": [
            {
                "question": "وظيفة الأربطة:",
                "options": [
                    "نقل الدم",
                    "ربط العظام",
                    "تحويل العظام"
                ],
                "answer": "ربط العظام"
            }
        ],

        # ================== العصبي ==================

        "u1_ns_taaleel": [
            {
                "question": "لماذا السحايا تحمي الدماغ؟",
                "options": [
                    "تمنع الأكسجين",
                    "تفصل عن العظام",
                    "هرمونات"
                ],
                "answer": "تفصل عن العظام"
            }
        ],

        "u1_ns_where": [
            {
                "question": "موقع شق سيلفيوس:",
                "options": [
                    "فصوص",
                    "جانبي",
                    "تقسيم"
                ],
                "answer": "جانبي"
            }
        ],

        "u1_ns_result1": [
            {
                "question": "نتيجة التكرار:",
                "options": [
                    "إجهاد",
                    "ذاكرة",
                    "توقف"
                ],
                "answer": "ذاكرة"
            }
        ],

        "u1_ns_compare": [
            {
                "question": "فرق الأعصاب:",
                "options": [
                    "نفس الاتجاه",
                    "عكس",
                    "حسي من الأعضاء"
                ],
                "answer": "حسي من الأعضاء"
            }
        ],

        "u1_ns_function": [
            {
                "question": "وظيفة العصبون البيني:",
                "options": [
                    "دم",
                    "ربط",
                    "حركة"
                ],
                "answer": "ربط"
            }
        ]
    }
}

# ================== بيانات المستخدم ==================
user_data = {}

# ================== START (ترحيب مزخرف) ==================
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
        "✨🌟 أهلاً وسهلاً بك في منصة بوابة العلامة الكاملة 🌟✨\n\n"
        "📚 اختبر نفسك وارتقِ بمستواك\n"
        "🧠 أسئلة متنوعة + صور + فيديوهات\n"
        "🚀 طريقك للنجاح يبدأ الآن\n\n"
        "👨‍🏫 إشراف: أحمد نور الدين\n"
        "💻 برمجة: سامي حبيب"
    )

    keyboard = [
        [InlineKeyboardButton("🧬 علم الأحياء", callback_data="bio")]
    ]

    await update.message.reply_text(
        "📚 اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== رفع الصور والفيديوهات (File ID) ==================
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.message.photo:
        file_id = update.message.photo[-1].file_id

        media_db.insert_one({
            "type": "photo",
            "file_id": file_id,
            "user_id": user_id
        })

        await update.message.reply_text(
            "📸 تم استلام الصورة\n\n"
            f"🆔 File ID:\n{file_id}"
        )
        return

    if update.message.video:
        file_id = update.message.video.file_id

        media_db.insert_one({
            "type": "video",
            "file_id": file_id,
            "user_id": user_id
        })

        await update.message.reply_text(
            "🎥 تم استلام الفيديو\n\n"
            f"🆔 File ID:\n{file_id}"
        )
        return

# ================== إرسال السؤال (يدعم الصور) ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_data:
        return

    info = user_data[user_id]

    subject = info["subject"]
    category = info["category"]
    index = info["q_index"]

    q_list = subjects[subject][category]

    if index >= len(q_list):
        await context.bot.send_message(chat_id=query.message.chat_id, text="🎉 انتهيت!")
        return

    q = q_list[index]

    if q.get("type") == "image":
        image_id = uploaded_images.get(q["image"])

        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=image_id,
            caption=q["question"]
        )
    else:
        text = q["question"] + "\n\n"
        for i, opt in enumerate(q["options"]):
            text += f"{chr(65+i)} - {opt}\n"

        await context.bot.send_message(chat_id=query.message.chat_id, text=text)

    keyboard = [[
        InlineKeyboardButton("A", callback_data="0"),
        InlineKeyboardButton("B", callback_data="1"),
        InlineKeyboardButton("C", callback_data="2"),
    ]]

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="اختر الإجابة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

app.run_polling()
