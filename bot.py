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
    "الاربطة والاوتار": "AgACAgQAAxkBAAIDxGnj27EBbQ7NdocwG8BMMx-pXpz0AAJvDGsb4XYhU0SlG3BDNztZAQADAgADbQADOwQ",
}

# ================== بنك الأسئلة ==================
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
                "question": "ما هي الصورة؟",
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
                "question": "استجابة العضلة بالترتيب:",
                "options": [
                    "تقلص ثم جهد",
                    "تنبيه ثم استرخاء",
                    "تنبيه → استجابة → عودة للوضع الطبيعي"
                ],
                "answer": "تنبيه → استجابة → عودة للوضع الطبيعي"
            }
        ],

        "u1_dam_result1": [
            {
                "question": "ماذا ينتج عن المقوية العضلية؟",
                "options": [
                    "انحناء الرقبة",
                    "ثبات الرأس منتصباً",
                    "تعب عضلي"
                ],
                "answer": "ثبات الرأس منتصباً"
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

        # ================== الجهاز العصبي ==================

        "u1_ns_taaleel": [
            {
                "question": "لماذا السحايا تحمي الدماغ؟",
                "options": [
                    "تمنع الأكسجين",
                    "تفصل الدماغ عن العظام",
                    "تفرز هرمونات"
                ],
                "answer": "تفصل الدماغ عن العظام"
            }
        ],

        "u1_ns_where": [
            {
                "question": "موقع شق سيلفيوس:",
                "options": [
                    "بين الفصوص",
                    "شق جانبي",
                    "يقسم الدماغ"
                ],
                "answer": "شق جانبي"
            }
        ],

        "u1_ns_result1": [
            {
                "question": "ماذا ينتج عن التكرار؟",
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
                "question": "الفرق بين العصب الحسي والمحرك:",
                "options": [
                    "نفس الاتجاه",
                    "الحسي للمخ والمحرك للعكس",
                    "الحسي من الأعضاء للمراكز والمحرك بالعكس"
                ],
                "answer": "الحسي من الأعضاء للمراكز والمحرك بالعكس"
            }
        ],

        "u1_ns_function": [
            {
                "question": "وظيفة العصبون البيني:",
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

# ================== بيانات المستخدم ==================
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

# ================== إرسال السؤال ==================
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

# ================== الأزرار ==================
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
            [InlineKeyboardButton("الدعامي", callback_data="sec_u1_dam")],
            [InlineKeyboardButton("العصبي", callback_data="sec_u1_ns")]
        ]
        await query.message.reply_text("الوحدة 1:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ================== اختيار القسم ==================
    if data in ["sec_u1_dam", "sec_u1_ns"]:

        section = "dam" if "dam" in data else "ns"

        user_data[user_id] = {
            "subject": "bio",
            "unit": "u1",
            "section": section,
            "score": 0,
            "q_index": 0
        }

        keyboard = [
            [InlineKeyboardButton("تعليل", callback_data="taaleel")],
            [InlineKeyboardButton("صور", callback_data="images")],
            [InlineKeyboardButton("موقع", callback_data="where")],
            [InlineKeyboardButton("ترتيب", callback_data="level")],
            [InlineKeyboardButton("نتائج", callback_data="result1")],
            [InlineKeyboardButton("وظيفة", callback_data="function")],
            [InlineKeyboardButton("مقارنة", callback_data="compare")],
            [InlineKeyboardButton("ابدأ الاختبار", callback_data="start_quiz")]
        ]

        await query.message.reply_text("اختر نوع الأسئلة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ================== تحديد نوع السؤال ==================
    if data in ["taaleel", "images", "where", "level", "result1", "function", "compare"]:

        if user_id not in user_data:
            return

        unit = user_data[user_id]["unit"]
        section = user_data[user_id]["section"]

        category = f"{unit}_{section}_{data}"

        if category not in subjects["bio"]:
            await query.message.reply_text("❌ لا يوجد أسئلة")
            return

        user_data[user_id]["category"] = category
        user_data[user_id]["q_index"] = 0

        keyboard = [[InlineKeyboardButton("ابدأ الاختبار", callback_data="start_quiz")]]

        await query.message.reply_text("ابدأ:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # ================== بدء الاختبار ==================
    if data == "start_quiz":
        await send_question(update, context)
        return

    # ================== الإجابة ==================
    if data in ["0", "1", "2"]:

        if user_id not in user_data:
            return

        info = user_data[user_id]

        category = info["category"]
        q = subjects["bio"][category][info["q_index"]]

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
