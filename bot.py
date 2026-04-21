import os
import logging
import asyncio
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ================== إعدادات ==================
MONGO_URL = os.environ.get("mongodb+srv://samihabib1986_db_user:a5c7t6@cluster0.bm9w0u0.mongodb.net/?appName=Cluster0")
TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN is missing")

client = MongoClient(MONGO_URL)
db = client["quiz_bot"]
users = db["users"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

ADMIN_ID = 8491023024

# ================== أدوات المستخدمين ==================

def create_user(user_id):
    users.update_one(
        {"_id": user_id},
        {
            "$setOnInsert": {
                "_id": user_id,
                "approved": False,
                "score": 0,
                "q_index": 0
            }
        },
        upsert=True
    )

def get_user(user_id):
    return users.find_one({"_id": user_id})

def is_approved(user_id):
    user = get_user(user_id)
    return user and user.get("approved", False)

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
        "u1_taaleel": [
            {
"question": "1. لماذا عظم الفك السفلي متحرك؟",
"options": [" لتسهيل التنفس"," لتسهيل المضغ والنطق "," لحماية الدماغ"],
"answer": " لتسهيل المضغ والنطق "
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

        ],

        "u1_images": [
{
"type": "image",
"image": "الهيكل العظمي",
"question": "1",
"options": ["الجمجمة (عظام الوجه + عظام القحف)","الهيكل المحوري","القص"],
"answer": "الهيكل المحوري"
},
{
"type": "image",
"image": "الهيكل العظمي",
"question": "3",
"options": ["الجمجمة (عظام الوجه + عظام القحف)","القص","هيكل الجذع"],
"answer": "الجمجمة (عظام الوجه + عظام القحف)"
},
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

{
"type": "image",
"image": "عظام الوجه",
"question": "2",
"options": [" الفك السفلي","عظام جوف الحجاج","الفك العلوي"],
"answer": "عظام جوف الحجاج"
},
{
"type": "image",
"image": "عظام الوجه",
"question": "1",
"options": ["عظام جوف الحجاج","عظام الانف"," الفك السفلي"],
"answer": "عظام الانف"
},

{
"type": "image",
"image": "مفصل العضد الكتفي",
"question": "1",
"options": ["عظم لوح الكتف","عظم العضد","عظم الترقوة"],
"answer": "عظم لوح الكتف"
},

{
"type": "image",
"image": "مفاصل العمود الفقري",
"question": "7",
"options": ["النخاع الشوكي","جسم الفقرة","القرص الغضروفي"],
"answer": "القرص الغضروفي"
},

{
"type": "image",
"image": "عظام الطرف العلوي",
"question": "16",
"options": ["عظم الزند","عظم العضد","عظم الكعبرة"],
"answer": "عظم الكعبرة"
},

{
"type": "image",
"image": "عظام الطرف العلوي",
"question": "19",
"options": ["اليد","الساعد","عظام السلاميات"],
"answer": "عظام السلاميات"
},




{
"type": "image",
"image": "عظام الطرف العلوي",
"question": "15",
"options": ["عظم العضد","عظم الزند","عظم الكعبرة"],
"answer": "عظم الزند"
},

{
"type": "image",
"image": "عظام الطرف السفلي",
"question": "4",
"options": ["عظم الرضفة","عظم الورك","عظم الفخد"],
"answer": "عظم الرضفة"
},

{
"type": "image",
"image": "عظام الطرف السفلي",
"question": "5",
"options": ["عظم الظنبوب","عظم الشظية","عظم الفخد"],
"answer": "عظم الظنبوب"
},

{
"type": "image",
"image": "عظام الطرف السفلي",
"question": "10",
"options": ["القدم","الساق","عظم الورك"],
"answer": "الساق"
},

{
"type": "image",
"image": "عظام الجمجمة",
"question": "3",
"options": ["العظم الصدغي","العظم الجداري","العظم القفوي"],
"answer": "العظم الصدغي"
},
{
"type": "image",
"image": "عظام الجمجمة",
"question": "4",
"options": ["العظم القفوي","العظم الجداري","العظم الصدغي"],
"answer": "العظم القفوي"
},

{
"type": "image",
"image": "بنية العظم الطويل",
"question": "3",
"options": ["المشاشة","نقي العظم","نسيج عظمي كثيف"],
"answer": "نقي العظم"
},

{
"type": "image",
"image": "القناة الفقرية",
"question": "5",
"options": ["النتوء الجانبي","قرص غضروفي","النتوء الشوكي"],
"answer": "النتوء الشوكي"
},

{
"type": "image",
"image": "القفص الصدري",
"question": "5",
"options": ["الاضلاع","الاضلاع السائبة","العمود الفقري"],
"answer": "الاضلاع السائبة"
},

{
"type": "image",
"image": "القفص الصدري",
"question": "2",
"options": ["عظم القص","الاضلاع","العمود الفقري"],
"answer": "عظم القص"
},

{
"type": "image",
"image": "الفقرة",
"question": "5",
"options": ["سطح مفصلي","نتوء جانبي","ثقب فقري"],
"answer": "نتوء جانبي"
},

{
"type": "image",
"image": "الفقرة",
"question": "3",
"options": ["ثقب فقري","نتوء شوكي","سطح مفصلي"],
"answer": "سطح مفصلي"
},

{
"type": "image",
"image": "العمود الفقري",
"question": "5",
"options": ["الفقرات العصعصية","الفقرات الظهرية","الفقرات القطنية"],
"answer": "الفقرات العصعصية"
},

{
"type": "image",
"image": "العمود الفقري",
"question": "4",
"options": ["الفقرات القطنية","الفقرات العجزية","الفقرات الظهرية"],
"answer": "الفقرات العجزية"
},

{
"type": "image",
"image": "الزنار الحوضي",
"question": "6",
"options": ["العصعص","العظم العاني","العجز"],
"answer": "العظم العاني"
},

{
"type": "image",
"image": "الاربطة والاوتار",
"question": "2",
"options": ["اوتار","عضلة","اربطة"],
"answer": "اربطة"
},


        ],
        "u1_where": [
{
"question": "1. أين يقع النتوء المرفقي؟",
"options": ["في عظم الفخذ","في نهاية عظم الزند العليا","في عظم العضد"],
"answer": "في نهاية عظم الزند العليا"
},



{
"question": "2. أين يوجد عظم الرضفة؟",
"options": ["في مفصل الكتف","في مفصل الركبة","في الكاحل"],
"answer": "في مفصل الركبة"
},



{
"question": "3. أين يوجد عظم الكعبرة وعظم الزند؟",
"options": ["في الساق","في الجمجمة","في الساعد ضمن الطرف العلوي"],
"answer": "في الساعد ضمن الطرف العلوي"
},



{
"question": "4. أين يوجد عظم الظنبوب وعظم الشظية؟",
"options": ["في الذراع","في الساق ضمن الطرف السفلي","في الصدر"],
"answer": "في الساق ضمن الطرف السفلي"
},



{
"question": "5. ما هي المشاشتان؟",
"options": ["عضلات","نهايتان منتفختان للعظم الطويل","أربطة"],
"answer": "نهايتان منتفختان للعظم الطويل"
},



{
"question": "6. أين يقع جسم العظم؟",
"options": ["في نهايات العظم","بين المشاشتين (القسم المتوسط)","خارج العظم"],
"answer": "بين المشاشتين (القسم المتوسط)"
},



{
"question": "7. أين توجد النتوءات؟",
"options": ["على سطح الجلد","داخل العضلات","على جسم العظم"],
"answer": "على جسم العظم"
},



{
"question": "8. أين توجد الثقوب في العظم؟",
"options": ["في الجلد","في القلب","على جسم العظم"],
"answer": "على جسم العظم"
},



{
"question": "9. أين يوجد السمحاق؟",
"options": ["داخل العظم","يغطي جسم العظم","داخل العضلات"],
"answer": "يغطي جسم العظم"
},



{
"question": "10. أين يوجد النسيج العظمي الكثيف؟",
"options": ["خارج العظم","في الجلد","يلي السمحاق في جسم العظم الطويل"],
"answer": "يلي السمحاق في جسم العظم الطويل"
},



{
"question": "11. أين توجد القناة المركزية؟",
"options": ["في الجلد","ضمن النسيج العظمي الكثيف","في العضلات"],
"answer": "ضمن النسيج العظمي الكثيف"
},



{
"question": "12. أين يوجد نقي العظم؟",
"options": ["في القلب","في الدم","داخل القناة المركزية والنسيج الإسفنجي"],
"answer": "داخل القناة المركزية والنسيج الإسفنجي"
},



{
"question": "13. أين يوجد النسيج العظمي الإسفنجي؟",
"options": ["في المشاشتين","في الجلد","في العضلات"],
"answer": "في المشاشتين"
},



{
"question": "14. أين يوجد النسيج الغضروفي؟",
"options": ["يستر المشاشتين","في الجلد","في القلب"],
"answer": "يستر المشاشتين"
},



{
"question": "15. أين توجد غضاريف النمو الطولي؟",
"options": ["بين جسم العظم والمشاشتين","في العضلات","في الجلد"],
"answer": "بين جسم العظم والمشاشتين"
},



{
"question": "16. أين توجد العضلات الملساء (الحشوية)؟",
"options": ["في جدران الأحشاء","في العظام","في الجلد"],
"answer": "في جدران الأحشاء"
},



{
"question": "17. أين توجد العضلات المخططة (الهيكلية)؟",
"options": ["في القلب","تستند على الهيكل العظمي","في المعدة"],
"answer": "تستند على الهيكل العظمي"
},

        ],
        "u1_level": [
       {
"question": "  1. رتب الطبقات المكونة لجسم العظم الطويل من الخارج إلى الداخل؟\n 1-السمحاق2- القناة المركزية 3- نقي العظم4- النسيج العظمي الكثيف",
"options": ["1➡️4➡️2➡️3","1➡️2➡️4➡️3","1➡️4➡️3➡️2"],
"answer": "1➡️4➡️2➡️3"
},     
        ],
        "u1_result": [
            {
"question": "1. ماذا ينتج عن تتالي الثقوب الفقرية؟",
"options": ["القفص الصدري","القناة الفقرية","الحوض"],
"answer": "القناة الفقرية"
},



{
"question": "2. ماذا ينتج عن ارتباط الأضلاع مع الفقرات الظهرية من الخلف وعظم القص من الأمام؟",
"options": ["العمود الفقري","الحوض","القفص الصدري"],
"answer": "القفص الصدري"
},



{
"question": "3. ماذا ينتج عن ارتباط عظام الزنار الحوضي مع عظم العجز؟",
"options": ["القفص الصدري","الحوض","العمود الفقري"],
"answer": "الحوض"
},



{
"question": "4. لماذا تكتسب العظام الصلابة والقساوة؟",
"options": ["بسبب الماء","بسبب العضلات","بسبب ارتباط أملاح الكالسيوم بمادة العظمين"],
"answer": "بسبب ارتباط أملاح الكالسيوم بمادة العظمين"
},



{
"question": "5. ما هو خلع المفصل؟",
"options": ["كسر العظم","خروج العظم من مكانه الطبيعي","تمزق العضلات"],
"answer": "خروج العظم من مكانه الطبيعي"
},



{
"question": "6. لماذا يتوقف النمو الطولي للعظم بعمر 18؟",
"options": ["بسبب نقص الغذاء","بسبب قلة الحركة","بسبب تعظم غضاريف النمو"],
"answer": "بسبب تعظم غضاريف النمو"
},
        ]
    }
}

# ================== بيانات المستخدم داخل التشغيل ==================
user_data = {}

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    create_user(user_id)

    if not is_approved(user_id):
        await update.message.reply_text("💰 البوت مدفوع\nاكتب /paid لطلب الاشتراك")
        return

    await update.message.reply_text("✨ نرحب بكم في منصة بوابة العلامة الكاملة ✨")

    keyboard = [
        [InlineKeyboardButton("🧬 علم الأحياء", callback_data="bio")]
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
        text=f"💳 طلب اشتراك جديد:\n/approve {user_id}"
    )

    await update.message.reply_text("⏳ تم إرسال طلبك للأدمن")

# ================== الموافقة ==================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])

    users.update_one(
        {"_id": user_id},
        {"$set": {"approved": True}}
    )

    await update.message.reply_text("✅ تم تفعيل المستخدم")

    await context.bot.send_message(
        chat_id=user_id,
        text="🎉 تم قبول اشتراكك في البوت"
    )

# ================== إرسال السؤال ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    data = user_data.get(user_id)
    if not data:
        return

    subject = data["subject"]
    category = data["category"]
    index = data["q_index"]

    q_list = subjects[subject][category]

    if index >= len(q_list):
        score = data["score"]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"🎉 انتهيت!\n📊 نتيجتك: {score} من {len(q_list)*10}"
        )
        return

    q = q_list[index]

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=str(i))]
        for i, opt in enumerate(q["options"])
    ]

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=q["question"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== الأزرار ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if not is_approved(user_id):
        await query.message.reply_text("❌ غير مشترك")
        return

    # ================== اختيار المادة ==================
    if data == "bio":
        keyboard = [
            [InlineKeyboardButton("الوحدة 1", callback_data="bio_u1")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر الوحدة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================== اختيار الوحدة ==================
    if data == "bio_u1":
        user_data[user_id] = {
            "subject": "bio",
            "category": "u1_taaleel",
            "score": 0,
            "q_index": 0
        }

        keyboard = [
            [InlineKeyboardButton("▶️ بدء الاختبار", callback_data="start")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="تم اختيار الوحدة",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================== بدء ==================
    if data == "start":
        await send_question(update, context)
        return

    # ================== الإجابة ==================
    if user_id not in user_data:
        return

    q_data = user_data[user_id]

    q_list = subjects[q_data["subject"]][q_data["category"]]
    q = q_list[q_data["q_index"]]

    selected = q["options"][int(data)]

    if selected == q["answer"]:
        q_data["score"] += 10
        result = "✅ صحيح"
    else:
        result = f"❌ خطأ\nالإجابة الصحيحة: {q['answer']}"

    q_data["q_index"] += 1

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
