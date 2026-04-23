import os
import asyncio
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ================== إعداد ==================
TOKEN = os.environ.get("TOKEN")
MONGO_URL = os.environ.get("MONGO_URL")
ADMIN_ID = 8491023024

client = MongoClient(MONGO_URL)
db = client["quiz_bot"]
users = db["users"]

# ================== فيديوهات ==================
UNIT_VIDEO = "VIDEO_UNIT"
SECTION_VIDEO = "VIDEO_SECTION"

# ================== الأسئلة ==================

taaleel = [
    {"question": "لماذا العظام صلبة؟", "options": ["كالسيوم","ماء","هواء"], "answer": "كالسيوم"},
]

images = []
where = []
level = []
result1 = []
function = []

# ================== الهيكل ==================
subjects = {
    "science": {
        "units": {
            "u1": {
                "title": "📘 الدعامة والتنسيق",
                "video": UNIT_VIDEO,

                "sections": {
                    "support": {
                        "title": "📂 الجهاز الدعامي الحركي",
                        "video": SECTION_VIDEO,

                        "types": {
                            "taaleel": taaleel,
                            "images": images,
                            "where": where,
                            "level": level,
                            "result1": result1,
                            "function": function
                        }
                    }
                }
            }
        }
    }
}

user_data = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📚 كتاب العلوم", callback_data="science")]]
    await update.message.reply_text("اختر:", reply_markup=InlineKeyboardMarkup(keyboard))

# ================== إرسال سؤال ==================
async def send_question(update, context):
    query = update.callback_query
    user = user_data[query.from_user.id]

    q_list = subjects["science"]["units"][user["unit"]]["sections"][user["section"]]["types"][user["type"]]

    if user["q"] >= len(q_list):
        await context.bot.send_message(chat_id=query.message.chat_id, text="انتهى الاختبار")
        return

    q = q_list[user["q"]]

    text = q["question"] + "\n"
    for i, opt in enumerate(q["options"]):
        text += f"{chr(65+i)}- {opt}\n"

    keyboard = [[
        InlineKeyboardButton("A", callback_data="0"),
        InlineKeyboardButton("B", callback_data="1"),
        InlineKeyboardButton("C", callback_data="2"),
    ]]

    await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))

# ================== الأزرار ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data

    # كتاب
    if data == "science":
        keyboard = [[InlineKeyboardButton("📘 الوحدة 1", callback_data="u1")]]
        await context.bot.send_message(chat_id=query.message.chat_id, text="اختر الوحدة", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # وحدة
    if data.startswith("u"):
        user_data[uid] = {"unit": data}
        unit = subjects["science"]["units"][data]

        keyboard = [[InlineKeyboardButton("🎬 فيديو الوحدة", callback_data="unit_video")]]

        for k, s in unit["sections"].items():
            keyboard.append([InlineKeyboardButton(s["title"], callback_data=f"sec_{k}")])

        await context.bot.send_message(chat_id=query.message.chat_id, text=unit["title"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # فيديو وحدة
    if data == "unit_video":
        vid = subjects["science"]["units"][user_data[uid]["unit"]]["video"]
        await context.bot.send_video(chat_id=query.message.chat_id, video=vid)
        return

    # قسم
    if data.startswith("sec_"):
        sec = data.split("_")[1]
        user_data[uid]["section"] = sec

        keyboard = [
            [InlineKeyboardButton("🎬 فيديو القسم", callback_data="sec_video")],
            [InlineKeyboardButton("🧪 اختبار القسم", callback_data="test_menu")]
        ]

        await context.bot.send_message(chat_id=query.message.chat_id, text="اختر:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # فيديو قسم
    if data == "sec_video":
        u = user_data[uid]["unit"]
        s = user_data[uid]["section"]
        vid = subjects["science"]["units"][u]["sections"][s]["video"]
        await context.bot.send_video(chat_id=query.message.chat_id, video=vid)
        return

    # قائمة أنواع الأسئلة
    if data == "test_menu":
        keyboard = [
            [InlineKeyboardButton("📘 تعاليل", callback_data="type_taaleel")],
            [InlineKeyboardButton("🖼️ صور", callback_data="type_images")],
            [InlineKeyboardButton("📍 حدد موقع", callback_data="type_where")],
            [InlineKeyboardButton("📊 رتب", callback_data="type_level")],
            [InlineKeyboardButton("🧠 ماذا ينتج", callback_data="type_result1")],
            [InlineKeyboardButton("👍 وظائف", callback_data="type_function")]
        ]

        await context.bot.send_message(chat_id=query.message.chat_id, text="اختر نوع الأسئلة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # اختيار نوع
    if data.startswith("type_"):
        t = data.split("_")[1]
        user_data[uid]["type"] = t
        user_data[uid]["q"] = 0
        await send_question(update, context)
        return

    # الإجابة
    user = user_data[uid]
    q_list = subjects["science"]["units"][user["unit"]]["sections"][user["section"]]["types"][user["type"]]
    q = q_list[user["q"]]

    if q["options"][int(data)] == q["answer"]:
        await context.bot.send_message(chat_id=query.message.chat_id, text="✅ صحيح")
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"❌ خطأ\n{q['answer']}")

    user_data[uid]["q"] += 1
    await asyncio.sleep(1)
    await send_question(update, context)

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
