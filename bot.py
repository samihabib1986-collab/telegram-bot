import os
import logging

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

# بنك الأسئلة
questions = [
{
"question": "1. لماذا عظم الفك السفلي متحرك؟",
"options": [" لتسهيل التنفس"," لتسهيل المضغ والنطق "," لحماية الدماغ"],
"answer": " لتسهيل المضغ والنطق ",
},



{
"question": "2. لماذا توجد فتحات عظمية في عظام القحف عند الرضيع؟",
"options": [" لتخفيف وزن الرأس"," لتسهيل التنفس","لتسمح لدماغ الرضيع بالنمو"],
"answer": "لتسمح لدماغ الرضيع بالنمو"
},



{
"question": "3. لماذا توجد أقراص غضروفية بين فقرات العمود الفقري؟",
"options": ["لمنع احتكاك الفقرات مع بعضها البعض"," لزيادة الطول"," لتقوية العضلات"],
"answer": "لمنع احتكاك الفقرات مع بعضها البعض"
},



{
"question": "4. لماذا يزداد طول رواد الفضاء؟",
"options": [" بسبب زيادة الكالسيوم"," بسبب غياب الجاذبية مما يقلل الضغط على الفقرات "," بسبب التمارين الرياضية"],
"answer": " بسبب غياب الجاذبية مما يقلل الضغط على الفقرات "
},



{
"question": "5. لماذا سميت الأضلاع السائبة بهذا الاسم؟",
"options": [" لأنها ضعيفة"," لأنها قصيرة"," لأنها لا تتصل مع عظم القص من الأمام "],
"answer": " لأنها لا تتصل مع عظم القص من الأمام "
},



{
"question": "6. لماذا لا يمكن ثني الساعد نحو الخلف؟",
"options": [" بسبب العضلات"," بسبب المفصل","لوجود نتوء مرفقي في نهاية الزند العليا"],
"answer": "لوجود نتوء مرفقي في نهاية الزند العليا"
},



{
"question": "7. لماذا لا يمكن ثني الساق نحو الأمام؟",
"options": [" بسبب الأربطة"," لوجود عظم الرضفة في مفصل الركبة "," بسبب العضلات"],
"answer": " لوجود عظم الرضفة في مفصل الركبة "
},



{
"question": "8. لماذا عدد العظام عند البالغ أقل من الطفل؟",
"options": [" لأن بعضها يتآكل"," لأن الجسم يفقد عظام"," لأن العديد منها يلتحم خلال النمو "],
"answer": " لأن العديد منها يلتحم خلال النمو "
},



{
"question": "9. لماذا توجد ثقوب في جسم العظم الطويل؟",
"options": [" لمرور الأوعية الدموية والأعصاب داخل العظم "," لتخفيف الوزن"," لتخزين الدهون"],
"answer": " لمرور الأوعية الدموية والأعصاب داخل العظم "
},



{
"question": "10. لماذا للهيكل العظمي دور في تكوين خلايا الدم؟",
"options": [" لأنه يخزن الدم"," لأنه يولد كريات الدم الحمراء والبيضاء والصفيحات "," لأنه ينقل الدم"],
"answer": " لأنه يولد كريات الدم الحمراء والبيضاء والصفيحات "
},
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


]

subjects = {"bio": questions}

user_data = {}
leaderboard = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_data[user_id] = {
        "score": 0,
        "q_index": 0,
        "subject": None
    }

    keyboard = [
        [InlineKeyboardButton("🦴 الجهاز العظمي", callback_data="bio")],
        [InlineKeyboardButton("🏆 أفضل الطلاب", callback_data="leaderboard")]
    ]

    await update.message.reply_text(
        "🎯 اختر:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= SEND QUESTION =================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    subject = user_data[user_id]["subject"]
    index = user_data[user_id]["q_index"]

    q_list = subjects[subject]

    if index >= len(q_list):
        score = user_data[user_id]["score"]
        leaderboard[user_id] = max(score, leaderboard.get(user_id, 0))

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

    await context.bot.send_message(
        chat_id=chat_id,
        text=q["question"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= BUTTON HANDLER =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # leaderboard
    if data == "leaderboard":
        if not leaderboard:
            await query.edit_message_text("لا يوجد نتائج بعد.")
            return

        text = "🏆 أفضل الطلاب:\n\n"
        sorted_board = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

        for i, (uid, score) in enumerate(sorted_board[:10], 1):
            text += f"{i}. 👤 {uid} - {score}\n"

        await query.edit_message_text(text)
        return

    # اختيار مادة
    if data in subjects:
        user_data[user_id] = {
            "score": 0,
            "q_index": 0,
            "subject": data
        }

        await query.edit_message_text("🚀 تم بدء الاختبار!")
        await send_question(update, context)
        return

    # إجابة
    subject = user_data[user_id]["subject"]
    index = user_data[user_id]["q_index"]

    q = subjects[subject][index]

    selected = q["options"][int(data)]

    if selected == q["answer"]:
        user_data[user_id]["score"] += 10
        text = "✅ صحيح!"
    else:
        text = f"❌ خطأ! الإجابة: {q['answer']}"

    user_data[user_id]["q_index"] += 1

    await query.edit_message_text(text)
    await send_question(update, context)

# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

if __name__ == "__main__":
    app.run_polling()
