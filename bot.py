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

# ================== بنك الأسئلة ==================
subjects = {
    "bio": {

        "u1_dam_taaleel": [
            {
                "question": "10. لماذا توفر مفاصل القحف أقصى درجات الحماية للدماغ؟",
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
                "question": "2",
                "options": ["اوتار","عضلة","اربطة"],
                "answer": "اربطة"
            }
        ],

        "u1_dam_where": [
            {
                "question": "10. حدد موقع النسيج العظمي الكثيف في العظم الطويل:",
                "options": [
                    "يوجد في المشاشتين فقط",
                    "يوجد داخل غضاريف النمو",
                    "طبقة تلي السمحاق وتشكل البنية الأساسية لجسم العظم"
                ],
                "answer": "طبقة تلي السمحاق وتشكل البنية الأساسية لجسم العظم"
            }
        ],

        "u1_dam_level": [
            {
                "question": "10. استجابة العضلة للتنبيه بالترتيب:",
                "options": [
                    "تقلص ⬅️ بذل جهد",
                    "بذل جهد ⬅️ استرخاء",
                    "تنبيه ⬅️ استجابة ⬅️ عودة لوضعها الطبيعي"
                ],
                "answer": "تنبيه ⬅️ استجابة ⬅️ عودة لوضعها الطبيعي"
            }
        ],

        "u1_dam_result1": [
            {
                "question": "10. ماذا ينتج عن خاصية المقوية العضلية؟",
                "options": [
                    "انحناء الرقبة",
                    "بقاء الرأس منتصباً",
                    "تعب عضلي"
                ],
                "answer": "بقاء الرأس منتصباً"
            }
        ],

        "u1_dam_function": [
            {
                "question": "10. ما هي وظيفة الأربطة؟",
                "options": [
                    "نقل الدم",
                    "تحويل الغضاريف",
                    "ربط العظام وتثبيت المفصل"
                ],
                "answer": "ربط العظام وتثبيت المفصل"
            }
        ],

        # ================== الجهاز العصبي ==================

        "u1_ns_taaleel": [
            {
                "question": "10. لماذا توفر السحايا حماية إضافية؟",
                "options": [
                    "تمنع الأكسجين",
                    "تفصل عن العظام",
                    "تفرز هرمونات"
                ],
                "answer": "تفصل عن العظام"
            }
        ],

        "u1_ns_where": [
            {
                "question": "10. موقع شق سيلفيوس:",
                "options": [
                    "يفصل الجبهي والجداري",
                    "شق جانبي",
                    "يقسم المخ"
                ],
                "answer": "شق جانبي"
            }
        ],

        "u1_ns_result1": [
            {
                "question": "10. ماذا ينتج عن تكرار المعلومات؟",
                "options": [
                    "إجهاد",
                    "تنشيط الذاكرة",
                    "توقف السيالات"
                ],
                "answer": "تنشيط الذاكرة"
            }
        ],

        "u1_ns_compare": [
            {
                "question": "10. الفرق بين العصب الحسي والمحرك:",
                "options": [
                    "كلاهما نفس الاتجاه",
                    "الحسي للمخ والمحرك للعكس",
                    "الحسي من الأعضاء للمراكز والمحرك بالعكس"
                ],
                "answer": "الحسي من الأعضاء للمراكز والمحرك بالعكس"
            }
        ],

        "u1_ns_function": [
            {
                "question": "10. وظيفة العصبون البيني:",
                "options": [
                    "نقل الدم",
                    "ربط الحسي بالمحرك",
                    "تنفيذ الحركة"
                ],
                "answer": "ربط الحسي بالمحرك"
            }
        ]
    }
}

# ================== user data ==================
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

    await update.message.reply_text("✨ أهلاً بك ✨")

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

    info = user_data[user_id]

    subject = info["subject"]
    category = info["category"]
    index = info["q_index"]

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
        text += f"{chr(65+i)} - {opt}\n"

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

# ================== BUTTON ==================
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

    if data == "bio_u1":
        keyboard = [
            [InlineKeyboardButton("🎬 فيديو", callback_data="unit_video")],
            [InlineKeyboardButton("الدعامي", callback_data="sec_u1_dam")],
            [InlineKeyboardButton("العصبي", callback_data="sec_u1_ns")]
        ]
        await query.message.reply_text("الوحدة 1:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "unit_video":
        await context.bot.send_video(chat_id=query.message.chat_id, video=UNIT_VIDEOS["u1"])
        return

    # ================== القسم الدعامي ==================
    if data == "sec_u1_dam":
        user_data[user_id] = {
            "subject": "bio",
            "unit": "u1",
            "section": "dam",
            "score": 0,
            "q_index": 0
        }

        keyboard = [
            [InlineKeyboardButton("🎥 فيديو القسم", callback_data="section_video_dam")],
            [InlineKeyboardButton("ابدأ الاختبار", callback_data="start_quiz")]
        ]

        await query.message.reply_text("الدعامي", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "section_video_dam":
        await context.bot.send_video(chat_id=query.message.chat_id, video=SECTION_VIDEOS["dam"])
        return

    # ================== القسم العصبي ==================
    if data == "sec_u1_ns":
        user_data[user_id] = {
            "subject": "bio",
            "unit": "u1",
            "section": "ns",
            "score": 0,
            "q_index": 0
        }

        keyboard = [
            [InlineKeyboardButton("🎥 فيديو القسم", callback_data="section_video_ns")],
            [InlineKeyboardButton("ابدأ الاختبار", callback_data="start_quiz")]
        ]

        await query.message.reply_text("العصبي", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "section_video_ns":
        await context.bot.send_video(chat_id=query.message.chat_id, video=SECTION_VIDEOS["ns"])
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
        section = info["section"]

        # تحديد أول كاتيجوري متاح (بدون حذف أسئلتك)
        category = f"{subject}_u1_{section}_taaleel"

        if category not in subjects[subject]:
            return

        q = subjects[subject][category][info["q_index"]]

        selected = q["options"][int(data)]

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
