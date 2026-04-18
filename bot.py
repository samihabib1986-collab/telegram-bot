import os
import logging
import asyncio

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

approved_users = set()
pending_users = set()

# ================== 🔥 الصور (ثابتة داخل الكود) ==================
uploaded_images = {
    "الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ"
}

# ================== بنك الأسئلة ==================
subjects = {
    "bio": {
        "taaleel": [
            {
"question": "11. لماذا تتصف العظام بالصلابة والقساوة؟",
"options": [" لوجود الروابط الوثيقة بين أملاح الكالسيوم ومادة العظم "," بسبب العضلات"," لاحتوائها على ماء"],
"answer": " لوجود الروابط الوثيقة بين أملاح الكالسيوم ومادة العظم "
},



{
"question": "12. لماذا عظام القحف غير متحركة؟",
"options": [" لأنها صغيرة"," لأن المفاصل بينها ثابتة "," لأنها خفيفة"],
"answer": " لأن المفاصل بينها ثابتة "
},



{
"question": "13. لماذا فقرات العمود الفقري محدودة الحركة؟",
"options": [" لأنها ضعيفة"," لأن المفاصل بينها نصف متحركة "," لأنها كثيرة"],
"answer": " لأن المفاصل بينها نصف متحركة "
},



{
"question": "14. لماذا حركة المفصل العضدي الكتفي واسعة؟",
"options": [" لأنه ثابت"," لأنه مفصل متحرك "," لأنه صغير"],
"answer": " لأنه مفصل متحرك "
},



{
"question": "15. لماذا يحدث خلع المفصل؟",
"options": [" بسبب كسر العظم"," بسبب خروج العظم من مكانه الطبيعي "," بسبب ضعف العضلات"],
"answer": " بسبب خروج العظم من مكانه الطبيعي "
},



{
"question": "16. لماذا للسمحاق دور في جبر الكسور؟",
"options": [" لأنه يفرز مادة تساعد على وصل العظم المكسور "," لأنه صلب"," لأنه يحمي العظم"],
"answer": " لأنه يفرز مادة تساعد على وصل العظم المكسور "
},



{
"question": "17. لماذا يتوقف النمو الطولي عند عمر 18 سنة؟",
"options": [" بسبب نقص الغذاء"," بسبب تعظم غضاريف النمو "," بسبب قلة الحركة"],
"answer": " بسبب تعظم غضاريف النمو "
},



{
"question": "18. لماذا تسمى العضلات الملساء عضلات حشوية؟",
"options": [" لأنها قوية"," لوجودها في جدران الأحشاء (المعدة والأمعاء) "," لأنها سريعة"],
"answer": " لوجودها في جدران الأحشاء (المعدة والأمعاء) "
},



{
"question": "19. لماذا تسمى العضلات المخططة عضلات هيكلية؟",
"options": [" لأنها كبيرة"," لأنها بطيئة"," لأنها مرتبطة بالعظام في الهيكل العظمي "],
"answer": " لأنها مرتبطة بالعظام في الهيكل العظمي "
},



{
"question": "20. لماذا تعود العضلة إلى وضعها الطبيعي بعد الشد؟",
"options": [" لأنها تتمتع بخاصية المرونة "," بسبب الأعصاب"," بسبب الدم"],
"answer": " لأنها تتمتع بخاصية المرونة "
},



{
"question": "21. لماذا عضلات الرقبة والفك السفلي لا تتعب بسهولة؟",
"options": ["لأنها تتمتع بخاصية المقوية العضلية (تحافظ على تقلصها)","لأنها صغيرة","لأنها سريعة"],
"answer": "لأنها تتمتع بخاصية المقوية العضلية (تحافظ على تقلصها)"
},



{
"question": "22. لماذا تبقى الرأس منتصبة أثناء اليقظة؟",
"options": ["بسبب العظام","بسبب الأعصاب","لأن عضلات الرقبة تتمتع بخاصية المقوية العضلية"],
"answer": "لأن عضلات الرقبة تتمتع بخاصية المقوية العضلية"
},

        ],

        "images": [

{
"type": "image",
"image": "الهيكل العظمي",
"question": "5",
"options": ["هيكل الجذع","القص","الزنار الكتفي"],
"answer": "القص"
},
{
"type": "image",
"image": "الهيكل العظمي",
"question": "8",
"options": ["الزنار الكتفي","الطرف العلوي","هيكل الجذع"],
"answer": "هيكل الجذع"
},
{
"type": "image",
"image": "الهيكل العظمي",
"question": "4",
"options": ["الزنار الكتفي","الطرف العلوي","هيكل الجذع"],
"answer": "الزنار الكتفي"
},
{
"type": "image",
"image": "الهيكل العظمي",
"question": "9",
"options": ["الزنار الكتفي","الهيكل الطرفي","الطرف العلوي"],
"answer": "الطرف العلوي"
},
{
"type": "image",
"image": "الهيكل العظمي",
"question": "10",
"options": ["الطرف السفلي","الزنار الحوضي","الهيكل الطرفي"],
"answer": "الزنار الحوضي"
},
{
"type": "image",
"image": "الهيكل العظمي",
"question": "11",
"options": ["الهيكل الطرفي","الطرف السفلي","الزنار الحوضي"],
"answer": "الطرف السفلي"
},
{
"type": "image",
"image": "الهيكل العظمي",
"question": "2",
"options": ["الزنار الحوضي","الطرف السفلي","الهيكل الطرفي"],
"answer": "الهيكل الطرفي"
},
{
"type": "image",
"image": "الهيكل العظمي",
"question": "6",
"options": ["العمود الفقري","الاضلاع","الهيكل الطرفي"],
"answer": "الاضلاع"
},
{
"type": "image",
"image": "الهيكل العظمي",
"question": "7",
"options": ["العمود الفقري","الهيكل الطرفي","الاضلاع"],
"answer": "العمود الفقري"
},

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

    # نهاية الاختبار
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

# ================== تشغيل البوت ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("approve", approve))

app.add_handler(CallbackQueryHandler(button))

if __name__ == "__main__":
    app.run_polling()
