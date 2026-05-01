import time
import os
import logging
import asyncio
import random
import qrcode
from pymongo import MongoClient
from qrcode.image import pil
from telegram.ext import Defaults
from telegram.constants import ParseMode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ============ استيراد نظام الملاحة ============
from navigation import (
    navigation,
    ScreenType,
    ScreenState,
    ScreenBuilder,
    handle_back_button,
    get_user_navigation_info,
    print_user_navigation_debug
)

# ================== رسائل التشجيع ==================
positive = [
    "🎉 ممتاز! إجابة صحيحة",
    "💪 أحسنت! استمر",
    "🔥 رائع جداً!",
    "🌟 إجابة قوية!",
    "👏 أحسنت! أنت في الطريق الصحيح",
    "✅ إجابة صحيحة! استمر في التعلم",
]

negative = [
    "😅 لا بأس، حاول مرة أخرى",
    "💡 الإجابة الصحيحة تساعدك تتعلم",
    "📘 ركز أكثر في هذه النقطة",
    "🔍 الإجابة غير صحيحة، راجع المادة مرة أخرى",
    "❌ إجابة خاطئة، لا تيأس، التعلم يحتاج وقت",
]

async def delete_later(bot, chat_id, message_id, delay=30):
    """حذف الرسالة بعد تأخير معين"""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logger.warning(f"لم يتمكن من حذف الرسالة: {e}")

welcome_messages = [
    "🎉 رائع! اختر نوع الأسئلة التي تريد حلها:",
    "✨ ممتاز! حان وقت اختبار معلوماتك:",
    "🚀 ممتاز! اختر نوع الأسئلة لبدء التحدي:",
    "👋 أهلاً بك في بوت الأحياء الذكي!",
    "📘 هنا ستتعلم بطريقة ممتعة وسهلة",
    "🎯 حل الأسئلة واجمع النقاط",
    "🚀 واصِل التقدم لتصبح الأفضل!"
]

# ================== إعداد Logging ==================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== إعداد MongoDB ==================
MONGO_URL = os.environ.get("MONGO_URL")

if not MONGO_URL:
    raise ValueError("MONGO_URL is missing")

try:
    client = MongoClient(MONGO_URL)
    db = client["quiz_bot"]
    users = db["users"]
    media_db = db["media_files"]
    logger.info("✅ تم الاتصال بـ MongoDB بنجاح")
except Exception as e:
    logger.error(f"❌ خطأ في الاتصال بـ MongoDB: {e}")
    raise

# ================== التوكن ==================
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN is missing")

# ================== الأدمن ==================
ADMIN_ID = 8491023024

# ================== الفيديوهات ==================
UNIT_INTRO_VIDEOS = {
    "u1": "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ",
    "u2": "BAACAgQAAxkBAAIarWnuYDZ8o-UdC47sqMr0kxoHjzhUAAL-HAACoG9wU3XlGC00flPjOwQ"
}

SECTION_INTRO_VIDEOS = {
    # ===== الوحدة 1 =====
    "dam": "BAACAgQAAxkBAAIRvGnrQ2MKxeiZFuVJ3v16gEqefHA8AAKXHQAC74lYU-Qly3e3uLQTOwQ",
    "nervus": "BAACAgQAAxkBAAIROmnqiPKGP-YaRotjs-gcLld1YROxAAIPHgAD51BTVg5QB-v3elM7BA",
    "sum": "BAACAgQAAxkBAAISXWnrqRG-Ino_MV1BUS4PqeBeBgviAAIjHgAC74lYUxVywvZpsig4OwQ",
    "sens": "BAACAgQAAxkBAAIT2WnskRk5P6AlybxMghy56RqihQ6wAALvGgAC74lgU35l37gtm2KPOwQ",
    "heal": "BAACAgQAAxkBAAIVX2nswtCvfBXgSON9mnemgijzHOoPAAIXGwAC74lgU5GqlwUBoSZ5OwQ",
    # ===== الوحدة 2 =====
    "digest": "BAACAgQAAxkBAAIhcGnwjlUM5UgRTfU9NXNHZmH9lA38AALDHwACHteBU0eE5P_9WF48OwQ",
    "circulation": "BAACAgQAAxkBAAIhcmnwjqzCORR-yKu0ZCU9XIVxzoKEAALEHwACHteBU65OOMsDUH5qOwQ",
    "respiration": "BAACAgQAAxkBAAIhYWnwjE8KcZXHCVrqS-vGDapiwfZ1AAK8HwACHteBU24DZ_8EjIreOwQ",
    "excretion": "BAACAgQAAxkBAAIhX2nwivY6gErtv3fKd1aofjOYBkTgAAKnHwACHteBU4rYXIZHtO4pOwQ",
    "nutrition_health": "BAACAgQAAxkBAAIhZmnwjXwhy0WIPfE_bEndEzZdds5HAAK-HwACHteBU2sUu35aggUROwQ"
}

# ================== الصور ==================
uploaded_images = {
    "الهيكل العظمي": "AgACAgQAAxkBAAIC7mnjrd4qryTOyoW_z_xsNkEvFM7iAAIwDGsb4XYhU1NT2bwGdzhNAQADAgADbQADOwQ",
    "عظام الوجه": "AgACAgQAAxkBAAIDgmnjuaxzSVnHSg-Ht5sh8MLSRxgDAAJEDGsb4XYhUyf_4zNepyt6AQADAgADbQADOwQ",
}

# ================== بنك الأسئلة ==================
subjects = {
    "bio": {
        "u1_dam_taaleel": [
            {
                "question": "1. لماذا توجد يافوخات (فتحات عظمية) في جمجمة الرضيع؟",
                "options": [
                    "لتسهيل عملية التنفس لدى الرضيع",
                    "للسماح لعظام القحف بالنمو تماشياً مع نمو الدماغ",
                    "لحماية الدماغ من الصدمات الخارجية"
                ],
                "answer": "للسماح لعظام القحف بالنمو تماشياً مع نمو الدماغ"
            },
        ],
    }
}

# ================== بيانات المستخدم ==================
user_data = {}
approved_users = set()
pending_users = set()

FREE_SECTIONS = ["dam"]

def back_button():
    """إنشاء زر الرجوع"""
    return [InlineKeyboardButton("🔙 رجوع", callback_data="back")]

def generate_code():
    """توليد كود دفع عشوائي"""
    return str(random.randint(100000, 999999))

def is_payment_user(update):
    """التحقق من أن المستخدم في وضع الدفع"""
    user = users.find_one({"_id": update.effective_user.id})
    return (
        user 
        and user.get("payment_mode") == "shamcash"
        and user.get("pending")
    )

# ================== الدفع (شام كاش) ==================
async def shamcash_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الدفع عبر شام كاش"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    code = generate_code()
    
    def generate_qr(data, filename):
        """توليد كود QR"""
        qr = qrcode.make(data)
        qr.save(filename)
    
    wallet_number = "5e5b1d5ed4a8b86a85fd3beb63f0b1fa"
    qr_data = f"ShamCash:{wallet_number}|Amount:5|Code:{code}"

    file_name = f"qr_{user.id}.png"
    generate_qr(qr_data, file_name)

    # تحديث قاعدة البيانات
    users.update_one(
        {"_id": user.id},
        {"$set": {
            "payment_code": code,
            "approved": False,
            "payment_mode": "shamcash",
            "pending": True,
        }},
        upsert=True
    )

    try:
        await query.message.reply_photo(
            photo=open(file_name, "rb"),
            caption=(
                "💳 الدفع عبر شام كاش\n\n"
                f"📌 رقم المحفظة: {wallet_number}\n"
                "💰 المبلغ: 5$ او 60000 ل.س\n"
                f"🧾 كود العملية: {code}\n\n"
                "📸 أرسل صورة التحويل بعد الدفع"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="go_start")]
            ])
        )
        logger.info(f"✅ تم إرسال كود QR للدفع للمستخدم {user.id}")
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الدفع: {e}")
    finally:
        try:
            os.remove(file_name)
        except:
            pass

# ================== حذف مستخدم ==================
async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف مستخدم (للأدمن فقط)"""
    if update.effective_user.id != ADMIN_ID:
        logger.warning(f"⚠️ محاولة حذف من {update.effective_user.id} بدون صلاحيات")
        return

    if not context.args:
        await update.message.reply_text("استخدم: /delete user_id")
        return

    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ ID غير صحيح")
        return

    result = users.delete_one({"_id": user_id})
    navigation.remove_user_completely(user_id)

    if result.deleted_count:
        await update.message.reply_text("🗑 تم حذف المستخدم")
        logger.info(f"✅ تم حذف المستخدم {user_id}")
    else:
        await update.message.reply_text("⚠️ المستخدم غير موجود")

# ================== استقبال صورة التحويل ==================
async def receive_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استقبال إثبات الدفع من المستخدم"""
    user_id = update.effective_user.id
    user = users.find_one({"_id": user_id})

    # إذا ليس في وضع الدفع
    if not user or user.get("payment_mode") != "shamcash" or not user.get("pending"):
        return

    try:
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 إثبات دفع\n👤 {user.get('name','')}\n🆔 {user_id}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ قبول", callback_data=f"approve_{user_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")],
            ])
        )

        await update.message.reply_text("⏳ تم إرسال الإثبات للمراجعة")
        logger.info(f"✅ تم استقبال إثبات دفع من {user_id}")
    except Exception as e:
        logger.error(f"❌ خطأ في استقبال إثبات الدفع: {e}")

# ================== الدفع اليدوي ==================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الدفع اليدوي"""
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user = query.from_user
        send_func = query.message.reply_text
    else:
        user = update.effective_user
        send_func = update.message.reply_text

    first_name = user.first_name or ""
    last_name = user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    user_id = user.id

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ قبول", callback_data=f"approve_{user_id}")]
    ])

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💳 طلب اشتراك:\n\n"
                 f"👤 الاسم: {full_name}\n"
                 f"🆔 ID: {user_id}",
            reply_markup=keyboard
        )

        await send_func(
            "⏳ تم إرسال طلب الاشتراك\n\nاضغط الرجوع للمتابعة 👇",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="go_start")]
            ])
        )
        logger.info(f"✅ تم إرسال طلب اشتراك من {user_id}")
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الدفع اليدوي: {e}")

# ================== قبول الطلب ==================
async def handle_admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار الأدمن"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        logger.warning(f"⚠️ محاولة وصول من {query.from_user.id} بدون صلاحيات")
        return

    data = query.data
    user_id = int(data.split("_")[1])
    
    if data.startswith("approve_"):
        users.update_one(
            {"_id": user_id},
            {"$set": {
                "approved": True,
                "pending": False,
                "method": "manual"
            }},
            upsert=True
        )

        await query.edit_message_text("✅ تم قبول المستخدم")

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 تم قبول اشتراكك\n\nاضغط لبدء استخدام البوت 👇",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 بدء", callback_data="bio")]
                ])
            )
            logger.info(f"✅ تم قبول المستخدم {user_id}")
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال رسالة القبول: {e}")
    
    elif data.startswith("reject_"):
        await query.edit_message_text("❌ تم رفض الطلب")

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ تم رفض عملية الدفع"
            )
            logger.info(f"❌ تم رفض المستخدم {user_id}")
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال رسالة الرفض: {e}")

# ================== START (ترحيب مزخرف) ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دالة البداية - الترحيب بالمستخدم"""
    user_id = update.effective_user.id
    user = users.find_one({"_id": user_id})

    username = update.effective_user.username or update.effective_user.full_name or "المستخدم"
    adminname = "sami habib"
    teachname = "أحمد نور الدين"
    mentionadmin = f"<a href='tg://user?id={ADMIN_ID}'>{adminname}</a>"
    mentionteach = f"<a href='tg://user?id={6177458463}'>{teachname}</a>"
    mention = f"<a href='tg://user?id={user_id}'>{username}</a>"

    try:
        await update.message.reply_text(
            f"""✨🌟 أهلاً وسهلاً بك في منصة بوابة العلامة الكاملة 🌟✨\n
    🌟✨{mention} 🌟✨

    📚 اختبر نفسك وارتقِ بمستواك
    🧠 أسئلة متنوعة + صور + فيديوهات
    🚀 طريقك للنجاح يبدأ الآن

    👨‍🏫 إشراف المدرس: أحمد نور الدين
    💻 برمجة المهندس: سامي حبيب
    🎁 قسم مجاني: الدعامي الحركي
    💰 باقي الأقسام مدفوعة

    📞 للتواصل مع الدعم: {mentionadmin} هاتف +واتس:0943 512 782
    📞 للتواصل مع المدرس: {mentionteach} هاتف +واتس:0939 138 720
    """,
            parse_mode="HTML"
        )

        keyboard = [
            [InlineKeyboardButton(f"🧬🌍 علم الأحياء والأرض🌍🧬", callback_data="bio")]
        ]

        await update.message.reply_text(
            "📚 اختر المادة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        # إضافة الشاشة الرئيسية للتاريخ
        screen = ScreenState(
            screen_type=ScreenType.MAIN_MENU,
            context_data={}
        )
        navigation.add_screen(user_id, screen)
        
        logger.info(f"✅ بداية جديدة للمستخدم {user_id}")
    except Exception as e:
        logger.error(f"❌ خطأ في دالة START: {e}")

# ================== رفع الوسائط ==================
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج رفع الصور والفيديوهات"""
    user_id = update.effective_user.id
    user = users.find_one({"_id": user_id})

    # حالة الدفع
    if user and user.get("payment_mode") == "shamcash" and user.get("pending"):
        try:
            await context.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📩 إثبات دفع\n👤 {update.effective_user.first_name}\n🆔 {user_id}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ قبول", callback_data=f"approve_{user_id}")],
                    [InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")],
                ])
            )

            await update.message.reply_text("⏳ تم إرسال الإثبات للمراجعة")
            logger.info(f"✅ تم استقبال إثبات دفع من {user_id}")
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة إثبات الدفع: {e}")
        return

    # الحالة العادية
    try:
        if update.message.photo:
            file_id = update.message.photo[-1].file_id

            media_db.insert_one({
                "type": "photo",
                "file_id": file_id,
                "user_id": user_id
            })

            await update.message.reply_text(
                f"📸 تم استلام الصورة\n\n🆔 File ID:\n{file_id}"
            )
            logger.info(f"✅ تم استلام صورة من {user_id}")
            return

        if update.message.video:
            file_id = update.message.video.file_id

            media_db.insert_one({
                "type": "video",
                "file_id": file_id,
                "user_id": user_id
            })

            await update.message.reply_text(
                f"🎥 تم استلام الفيديو\n\n🆔 File ID:\n{file_id}"
            )
            logger.info(f"✅ تم استلام فيديو من {user_id}")
            return
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الوسائط: {e}")

# ================== إرسال السؤال ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال السؤال التالي"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in user_data:
        await query.answer("❌ حدث خطأ، حاول مرة أخرى", show_alert=True)
        return

    info = user_data[user_id]

    info.setdefault("q_index", 0)
    info.setdefault("score", 0)

    subject = info["subject"]
    category = info["category"]
    index = info["q_index"]

    q_list = subjects[subject][category]

    if index >= len(q_list):
        text = f"👤 ID: {user_id}\n\n" + f"🎉 انتهيت!\n\n🏆 نتيجتك: {info['score']} من {len(q_list)*10}"

        keyboard = [
            [InlineKeyboardButton("🔄 إعادة الاختبار", callback_data="restart_quiz")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back")],
        ]

        try:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                protect_content=True
            )
            logger.info(f"✅ انتهى الاختبار للمستخدم {user_id} برصيد {info['score']}")
        except Exception as e:
            logger.error(f"❌ خطأ في عرض النتائج: {e}")
        return

    q = q_list[index]

    text = None

    if "image" in q:
        image_id = uploaded_images.get(q["image"])

        if not image_id:
            try:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ لا يوجد اسئلة لهذا القسم حالياً"
                )
            except Exception as e:
                logger.error(f"❌ خطأ في عرض الرسالة: {e}")
            return

        caption = q.get("question", "❓ اختر الإجابة الصحيحة:") + "\n\n"
        for i, opt in enumerate(q["options"]):
            caption += f"{chr(65+i)} - {opt}\n"

        keyboard = [[
            InlineKeyboardButton("A", callback_data="0"),
            InlineKeyboardButton("B", callback_data="1"),
            InlineKeyboardButton("C", callback_data="2"),
        ]]

        try:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=image_id,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard),
                protect_content=True
            )
            logger.info(f"✅ تم إرسال صورة للسؤال {index+1} للمستخدم {user_id}")
        except Exception as e:
            logger.error(f"❌ خطأ في عرض الصورة: {e}")
        return
    else:
        text = f"👤 ID: {user_id}\n\n{q['question']}\n\n"
        for i, opt in enumerate(q["options"]):
            text += f"{chr(65+i)} - {opt}\n"

    try:
        msg = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=text,
            protect_content=True
        )
        
        keyboard = [[
            InlineKeyboardButton("A", callback_data="0"),
            InlineKeyboardButton("B", callback_data="1"),
            InlineKeyboardButton("C", callback_data="2"),
        ]]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر الإجابة:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            protect_content=True
        )
        logger.info(f"✅ تم إرسال السؤال {index+1} للمستخدم {user_id}")
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال السؤال: {e}")

# ================== معالج الأزرار ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج جميع أزرار الـ callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data

    try:
        # ============ اختيار المادة ============
        if data == "bio":
            if user_id not in user_data:
                user_data[user_id] = {
                    "subject": "bio",
                    "unit": "",
                    "section": "",
                    "score": 0,
                    "q_index": 0,
                    "history": []
                }

            if "history" not in user_data[user_id]:
                user_data[user_id]["history"] = []
            
            user_data[user_id]["history"].append({"type": "main_menu"})
            
            # إضافة للملاحة
            screen = ScreenState(
                screen_type=ScreenType.UNIT_MENU,
                context_data={}
            )
            navigation.add_screen(user_id, screen)
            
            teacher_image_id = "AgACAgQAAxkBAAIat2nuYkI0Vyu42G9VYtE--7R0Ms2MAAKZDGsboG9wU0hGmo9s3vMvAQADAgADeQADOwQ"

            caption = (
                "👨‍🏫 الأستاذ: أحمد نور الدين\n\n"
                "📘 مدرس مادة علم الأحياء\n"
                "🎯 يهدف إلى تبسيط المفاهيم العلمية\n"
                "🚀 ويساعد الطلاب على تحقيق أعلى الدرجات\n\n"
                "✨ أهلاً بك في رحلتك التعليمية!"
            )
            
            try:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=teacher_image_id,
                    caption=f"👤 {user_id}\n\n" + caption,
                    protect_content=True
                )
            except Exception as e:
                logger.error(f"❌ خطأ في إرسال صورة المدرس: {e}")
            
            keyboard = [
                [InlineKeyboardButton("الوحدة 1: (الدعامة والتنسيق)", callback_data="bio_u1")],
                [InlineKeyboardButton("الوحدة 2: (وظائف التغذية)", callback_data="bio_u2")]
            ]
            
            try:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="📚 اختر الوحدة:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    protect_content=True
                )
                logger.info(f"✅ عرضت قائمة الوحدات للمستخدم {user_id}")
            except Exception as e:
                logger.error(f"❌ خطأ في عرض قائمة الوحدات: {e}")
            return

        # ============ الوحدة 1 ============
        if data == "bio_u1":
            user_data[user_id]["history"].append({"type": "unit_menu"})
            
            # إضافة للملاحة
            screen = ScreenState(
                screen_type=ScreenType.SECTION_MENU,
                context_data={"unit": "u1"}
            )
            navigation.add_screen(user_id, screen)
            
            unit_video = UNIT_INTRO_VIDEOS.get("u1")

            if unit_video:
                try:
                    await context.bot.send_video(
                        chat_id=query.message.chat_id,
                        video=unit_video,
                        caption="🎬 مقدمة الوحدة 1"
                    )
                except Exception as e:
                    logger.error(f"❌ خطأ في إرسال فيديو الوحدة: {e}")

            keyboard = [
                [InlineKeyboardButton("🦴 القسم الدعامي 🦴", callback_data="sec_u1_dam"),
                 InlineKeyboardButton("🧠 الجهاز العصبي 🧠", callback_data="sec_u1_nervus")],
                [InlineKeyboardButton("🧬 الغدد الصم 🧬", callback_data="sec_u1_sum"),
                 InlineKeyboardButton("👅 أعضاء الحس 👅", callback_data="sec_u1_sens")],
                [InlineKeyboardButton("🧑‍⚕️ صحة الدعامة والتنسيق 🧑‍⚕️", callback_data="sec_u1_heal")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ]

            try:
                await query.message.reply_text(
                    "📚 اختر القسم:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                logger.info(f"✅ عرضت أقسام الوحدة 1 للمستخدم {user_id}")
            except Exception as e:
                logger.error(f"❌ خطأ في عرض الأقسام: {e}")
            return

        # ============ الوحدة 2 ============
        if data == "bio_u2":
            user_data[user_id]["history"].append({"type": "unit_menu"})
            
            # إضافة للملاحة
            screen = ScreenState(
                screen_type=ScreenType.SECTION_MENU,
                context_data={"unit": "u2"}
            )
            navigation.add_screen(user_id, screen)
            
            unit_video = UNIT_INTRO_VIDEOS.get("u2")

            if unit_video:
                try:
                    await context.bot.send_video(
                        chat_id=query.message.chat_id,
                        video=unit_video,
                        caption="🎬 مقدمة الوحدة 2"
                    )
                except Exception as e:
                    logger.error(f"❌ خطأ في إرسال فيديو الوحدة: {e}")

            keyboard = [
                [InlineKeyboardButton("🥗 الهضم لدى الإنسان 🥗", callback_data="sec_u2_digest"),
                 InlineKeyboardButton("🫀 الدوران لدى الإنسان 🫀", callback_data="sec_u2_circulation")],
                [InlineKeyboardButton("🫁 التنفس لدى الإنسان 🫁", callback_data="sec_u2_respiration"),
                 InlineKeyboardButton("🚽 الإطراح عند الإنسان 🚽", callback_data="sec_u2_excretion")],
                [InlineKeyboardButton("🍎 صحة وظائف التغذية 🍎", callback_data="sec_u2_nutrition_health")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ]

            try:
                await query.message.reply_text(
                    "📚 اختر القسم:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                logger.info(f"✅ عرضت أقسام الوحدة 2 للمستخدم {user_id}")
            except Exception as e:
                logger.error(f"❌ خطأ في عرض الأقسام: {e}")
            return

        # ============ الأقسام ============
        if data.startswith("sec_"):

            section_map = {
                "sec_u1_dam": ("u1", "dam"),
                "sec_u1_nervus": ("u1", "nervus"),
                "sec_u1_sum": ("u1", "sum"),
                "sec_u1_sens": ("u1", "sens"),
                "sec_u1_heal": ("u1", "heal"),
                "sec_u2_digest": ("u2", "digest"),
                "sec_u2_circulation": ("u2", "circulation"),
                "sec_u2_respiration": ("u2", "respiration"),
                "sec_u2_excretion": ("u2", "excretion"),
                "sec_u2_nutrition_health": ("u2", "nutrition_health"),
            }

            mapped = section_map.get(data)
            if not mapped:
                logger.error(f"❌ قسم غير معروف: {data}")
                return

            unit, section = mapped

            user_data[user_id]["unit"] = unit
            user_data[user_id]["section"] = section

            user = users.find_one({"_id": user_id})

            # التحقق من الدفع
            if section not in FREE_SECTIONS:
                if not user or not user.get("approved", False):
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("💳 شام كاش", callback_data="pay_shamcash")],
                        [InlineKeyboardButton("🧾 دفع يدوي", callback_data="paid")]
                    ])
                    try:
                        await query.answer()
                        await query.message.reply_text(
                            "💰 هذا القسم مدفوع\n\n📩 اختر طريقة الدفع:",
                            reply_markup=keyboard
                        )
                        logger.info(f"⚠️ المستخدم {user_id} يحتاج دفع للقسم {section}")
                    except Exception as e:
                        logger.error(f"❌ خطأ في عرض شاشة الدفع: {e}")
                    return

            # السماح بالدخول
            await query.answer("✅ تم الدخول للقسم")
            
            # إضافة للملاحة
            screen = ScreenState(
                screen_type=ScreenType.TYPES_MENU,
                context_data={"unit": unit, "section": section}
            )
            navigation.add_screen(user_id, screen)
            
            if user_id not in user_data:
                user_data[user_id] = {
                    "subject": "bio",
                    "unit": "",
                    "section": "",
                    "score": 0,
                    "q_index": 0,
                    "history": []
                }

            user_data[user_id]["unit"] = unit
            user_data[user_id]["section"] = section
            
            section_video = SECTION_INTRO_VIDEOS.get(section)

            if section_video:
                try:
                    await context.bot.send_video(
                        chat_id=query.message.chat_id,
                        video=section_video,
                        caption="🎬 مقدمة القسم",
                        protect_content=True
                    )
                except Exception as e:
                    logger.error(f"❌ خطأ في إرسال فيديو القسم: {e}")
            
            keyboard = [
                [InlineKeyboardButton("📘 تعليل", callback_data="taaleel"),
                 InlineKeyboardButton("🖼 صور", callback_data="image")],
                [InlineKeyboardButton("📍 موقع", callback_data="where"),
                 InlineKeyboardButton("📊 ترتيب", callback_data="level")],
                [InlineKeyboardButton("🧠 نتائج", callback_data="result"),
                 InlineKeyboardButton("⚙️ وظيفة", callback_data="function"),
                 InlineKeyboardButton("⚡ مقارنة", callback_data="compare")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ]

            try:
                await query.message.reply_text(
                    "اختر نوع الأسئلة:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                logger.info(f"✅ عرضت أنواع الأسئلة للمستخدم {user_id}")
            except Exception as e:
                logger.error(f"❌ خطأ في عرض أنواع الأسئلة: {e}")

        # ============ اختيار نوع السؤال ============
        if data in ["taaleel", "image", "where", "level", "result", "function", "compare"]:

            if user_id not in user_data:
                await query.answer("❌ حدث خطأ", show_alert=True)
                return
            
            if "history" not in user_data[user_id]:
                user_data[user_id]["history"] = []
            
            user_data[user_id]["history"].append({
                "type": "types_menu",
                "unit": user_data[user_id]["unit"],
                "section": user_data[user_id]["section"]
            })
            
            unit = user_data[user_id]["unit"]
            section = user_data[user_id]["section"]

            category = f"{unit}_{section}_{data}"

            bio_subjects = subjects.get("bio", {})

            if category not in bio_subjects:
                try:
                    await query.message.reply_text("❌ لا يوجد أسئلة لهذا النوع في هذا القسم")
                except Exception as e:
                    logger.error(f"❌ خطأ في الرسالة: {e}")
                return

            user_data[user_id]["category"] = category
            user_data[user_id]["q_index"] = 0

            # إضافة للملاحة
            screen = ScreenState(
                screen_type=ScreenType.QUIZ,
                context_data={"type": data}
            )
            navigation.add_screen(user_id, screen)

            keyboard = [[InlineKeyboardButton("▶️ بدء", callback_data="start_quiz")],
                        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]]

            try:
                await query.message.reply_text(
                    random.choice(welcome_messages),
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                logger.info(f"✅ جاهز لبدء الاختبار مع المستخدم {user_id}")
            except Exception as e:
                logger.error(f"❌ خطأ في عرض شاشة البداية: {e}")
            return

        # ============ بدء الاختبار ============
        if data == "start_quiz":
            import time
            user_data[user_id]["session"] = time.time()
            user_data[user_id]["q_index"] = 0
            user_data[user_id]["score"] = 0
            await send_question(update, context)
            logger.info(f"✅ بدء الاختبار للمستخدم {user_id}")
            return

        if data == "go_start":
            keyboard = [
                [InlineKeyboardButton("🧬 علم الأحياء", callback_data="bio")],
                [InlineKeyboardButton("💳 الدفع", callback_data="payment_menu")]
            ]

            try:
                await query.message.reply_text(
                    "📚 اختر من القائمة:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception as e:
                logger.error(f"❌ خطأ في عرض القائمة: {e}")
            return

        if data == "payment_menu":
            keyboard = [
                [InlineKeyboardButton("💳 شام كاش", callback_data="pay_shamcash")],
                [InlineKeyboardButton("🧾 دفع يدوي", callback_data="paid")]
            ]

            try:
                await query.message.reply_text(
                    "💰 اختر طريقة الدفع:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception as e:
                logger.error(f"❌ خطأ في عرض طرق الدفع: {e}")
            return

        # ============ الرجوع ============
        if data == "back":
            await handle_back_button(update, context)
            return

        # ============ إعادة الاختبار ============
        if data == "restart_quiz":

            if user_id not in user_data:
                await query.answer("❌ حدث خطأ", show_alert=True)
                return

            user_data[user_id]["q_index"] = 0
            user_data[user_id]["score"] = 0

            await send_question(update, context)
            logger.info(f"✅ إعادة اختبار من قبل {user_id}")
            return

        # ============ الإجابات ============
        if data in ["0", "1", "2"]:

            if user_id not in user_data:
                await query.answer("❌ حدث خطأ", show_alert=True)
                return

            info = user_data[user_id]

            if "session" not in info:
                await query.answer("❌ انتهت الجلسة", show_alert=True)
                return

            current_session = info["session"]

            if info.get("session") != current_session:
                await query.answer("❌ تغيرت الجلسة", show_alert=True)
                return

            category = info["category"]

            q_list = subjects["bio"].get(category)
            if not q_list or info["q_index"] >= len(q_list):
                await query.answer("❌ لا توجد أسئلة", show_alert=True)
                return

            q = q_list[info["q_index"]]

            selected_index = int(data)
            correct_index = q["options"].index(q["answer"])

            buttons = []
            row = []

            for i, option in enumerate(q["options"]):
                if i == correct_index:
                    text = f"{chr(65+i)} ✅"
                elif i == selected_index:
                    text = f"{chr(65+i)} ❌"
                else:
                    text = f"{chr(65+i)}"
                if "history" not in user_data[user_id]:
                    user_data[user_id]["history"] = []
                row.append(InlineKeyboardButton(text, callback_data="locked"))

            buttons.append(row)

            try:
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except Exception as e:
                logger.error(f"❌ خطأ في تحديث الأزرار: {e}")

            # التقييم

            if selected_index == correct_index:
                info["score"] += 10

                text = random.choice(positive)

                try:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=text + " 🎉",
                        message_effect_id="5104841245755180586",
                        protect_content=True
                    )
                except:
                    try:
                        await context.bot.send_message(
                            chat_id=query.message.chat_id,
                            text=text,
                            protect_content=True
                        )
                    except Exception as e:
                        logger.error(f"❌ خطأ في إرسال الرسالة: {e}")

            else:
                try:
                    await query.message.reply_text(
                        random.choice(negative) + f"\n\n📌 الإجابة الصحيحة: {q['answer']}"
                    )
                except Exception as e:
                    logger.error(f"❌ خطأ في عرض الإجابة: {e}")

            info["q_index"] += 1

            await asyncio.sleep(1)

            await send_question(update, context)
            return
    
    except Exception as e:
        logger.error(f"❌ خطأ عام في معالج الأزرار: {e}")
        await query.answer("❌ حدث خطأ غير متوقع", show_alert=True)

# ================== تشغيل البوت ==================
app = (
    ApplicationBuilder()
    .token(TOKEN)
    .defaults(Defaults(parse_mode=ParseMode.HTML))
    .build()
)

# أوامر
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("delete", delete_user))
app.add_handler(CommandHandler("paid", paid))

# الأدمن
app.add_handler(CallbackQueryHandler(handle_admin_buttons, pattern="^(approve_|reject_).*"))

# الدفع
app.add_handler(CallbackQueryHandler(shamcash_payment, pattern="^pay_shamcash$"))
app.add_handler(CallbackQueryHandler(paid, pattern="^paid$"))

# الوسائط
app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

# باقي الأزرار
app.add_handler(CallbackQueryHandler(button))

# ================== تشغيل ==================
if __name__ == "__main__":
    logger.info("✅ بدء تشغيل البوت...")
    try:
        app.run_polling()
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
