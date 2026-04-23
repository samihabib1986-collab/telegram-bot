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
"question": "23. كثرة التلافيف في قشرة المخ:",
"options": ["لتقليل حجم الدماغ","لزيادة مساحة سطح القشرة المخية (المادة الرمادية)",""],
"answer": "لزيادة مساحة سطح القشرة المخية (المادة الرمادية)"
},


{
"question": "24. أهمية السائل الدماغي الشوكي:",
"options": ["يعمل كوسادة مائية تحمي المراكز العصبية من الصدمات والضغط","لتغذية العظام فقط",""],
"answer": "يعمل كوسادة مائية تحمي المراكز العصبية من الصدمات والضغط"
},


{
"question": "25. التصاق الأم الحنون بقوة بالمراكز العصبية:",
"options": ["لنقل الغذاء والأكسجين إليها عبر أوعيتها الغزيرة","لتكوين العظام",""],
"answer": "لنقل الغذاء والأكسجين إليها عبر أوعيتها الغزيرة"
},


{
"question": "26. تسمية الغدة النخامية بسيدة الغدد:",
"options": ["لأنها تتحكم في الهضم","لأن هرموناتها تنظم عمل معظم الغدد الصماء الأخرى",""],
"answer": "لأن هرموناتها تنظم عمل معظم الغدد الصماء الأخرى"
},


{
"question": "27. أهمية اليود في الغذاء:",
"options": ["لزيادة قوة العضلات","لتكوين كريات الدم الحمراء",""],
"answer": "ضروري جداً لتركيب هرمون التيروكسين في الغدة الدرقية"
},


{
"question": "28. إفراز الأدرينالين في حالات الخوف:",
"options": ["لتقليل ضربات القلب","لتخزين الطاقة فقط",""],
"answer": "لزيادة نشاط القلب وتحويل الدم للأعضاء المهمة لمواجهة الخطر"
},


{
"question": "29. سرعة استجابة السيالة العصبية مقارنة بالهرمونات:",
"options": ["لأن السيالة تنتقل بسرعة عبر الألياف العصبية بينما الهرمونات ببطء عبر الدم","لأن الدم لا ينقل الهرمونات","لأن الهرمونات أسرع من الأعصاب"],
"answer": "لأن السيالة تنتقل بسرعة عبر الألياف العصبية بينما الهرمونات ببطء عبر الدم"
},



        ],

        "u1_images": [
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
"question": "18. حدد موقع النخاع الشوكي:",
"options": ["في الجمجمة","في تجويف البطن","في القناة الفقرية الناتجة عن تتالي الثقوب الفقرية"],
"answer": "في القناة الفقرية الناتجة عن تتالي الثقوب الفقرية"
},




{
"question": "21. حدد موقع المخيخ:",
"options": ["خلف وأسفل المخ","داخل النخاع الشوكي","أمام المخ"],
"answer": "خلف وأسفل المخ"
},


{
"question": "22. حدد موقع البصلة السيسائية:",
"options": ["داخل القحف الأمامي فقط","فوق المخ","بين الحدبة الحلقية في الاعلى والنخاع الشوكي في الاسفل"],
"answer": "بين الحدبة الحلقية في الاعلى والنخاع الشوكي في الاسفل"
},


{
"question": "23. حدد موقع الجسم الثفني:",
"options": ["في النخاع الشوكي","في المخيخ","في قاع الشق الأمامي الخلفي بين نصفي كرة المخ"],
"answer": "في قاع الشق الأمامي الخلفي بين نصفي كرة المخ"
},


{
"question": "24. حدد موقع مثلث المخ:",
"options": ["في جذع الدماغ","صفيحة بيضاء تحت الجسم الثفني","في القشرة المخية"],
"answer": "صفيحة بيضاء تحت الجسم الثفني"
},


{
"question": "25. حدد موقع قناة السيساء:",
"options": ["في مركز المادة الرمادية للنخاع الشوكي","في المخيخ","في القناة الفقرية خارج النخاع وعلى امتداده"],
"answer": "في القناة الفقرية خارج النخاع وعلى امتداده"
},


{
"question": "26. حدد موقع الغشاء العنكبوتي:",
"options": ["بين الام الجافية والأم الحنون (يحتوي السائل الخارجي)","داخل العظام","بين العظم والجلد"],
"answer": "بين الام الجافية والأم الحنون (يحتوي السائل الخارجي)"
},


{
"question": "27. حدد موقع الباحة المحركة:",
"options": ["في الفص الصدغي","في الفص القفوي","في الفص الجبهي أمام شق رولاندو"],
"answer": "في الفص الجبهي أمام شق رولاندو"
},


{
"question": "28. حدد موقع الباحة البصرية:",
"options": ["في المخيخ","في الفص الجبهي","في الفص القفوي"],
"answer": "في الفص القفوي"
},


{
"question": "29. حدد موقع الباحة السمعية:",
"options": ["في الفص الجبهي","في النخاع الشوكي","في الفص الصدغي"],
"answer": "في الفص الصدغي"
},


{
"question": "30. حدد موقع العقدة الشوكية:",
"options": ["على الجذر الأمامي الحركي","داخل الدماغ","على الجذر الخلفي الحسي للعصب الشوكي"],
"answer": "على الجذر الخلفي الحسي للعصب الشوكي"
},


{
"question": "31. حدد موقع الغدة النخامية:",
"options": ["في الرقبة","في الصدر","على الوجه السفلي للدماغ"],
"answer": "على الوجه السفلي للدماغ"
},


{
"question": "32. حدد موقع الغدة الدرقية:",
"options": ["تحيط بالحنجرة وأعلى الرغامي","في الدماغ","في البطن"],
"answer": "تحيط بالحنجرة وأعلى الرغامي"
},


{
"question": "33. حدد موقع الغدد جارات الدرق:",
"options": ["أربع غدد تلتصق بالسطح الخلفي للغدة الدرقية","في القلب","داخل الكبد"],
"answer": "أربع غدد تلتصق بالسطح الخلفي للغدة الدرقية"
},


{
"question": "34. حدد موقع جزر لانغرهانس:",
"options": ["في الكبد","في الدماغ","في مؤخرة المعثكلة (البنكرياس)"],
"answer": "في مؤخرة المعثكلة (البنكرياس)"
},


{
"question": "35. حدد موقع الغدتين الكظريتين:",
"options": ["داخل المثانة","في الرقبة","فوق الكليتين مباشرة"],
"answer": "فوق الكليتين مباشرة"
},


{
"question": "36. حدد موقع الغدة الصنوبرية:",
"options": ["في المعدة","تقع داخل الدماغ","في النخاع الشوكي"],
"answer": "تقع داخل الدماغ"
},
        ],
        "u1_level": [



{
"question": "11. أقسام الدماغ من الأعلى للأسفل:",
"options": ["","بصلة⬅️ مخ⬅️ مخيخ","مخيخ⬅️ مخ⬅️ بصلة"],
"answer": "مخ⬅️ مخيخ⬅️ بصلة سيسائية"
},


{
"question": "12. توزع الأضلاع:",
"options": ["كاذبة⬅️ حقيقية⬅️ سائبة","حقيقية⬅️ كاذبة⬅️ سائبة","سائبة⬅️ كاذبة⬅️ حقيقية"],
"answer": "حقيقية⬅️ كاذبة⬅️ سائبة"
},


{
"question": "13. نشوء الفعل المنعكس:",
"options": ["مستقبل⬅️ سيالة حسية⬅️ مركز⬅️ سيالة محركة⬅️ استجابة","استجابة⬅️ مركز⬅️ مستقبل","مركز⬅️ مستقبل⬅️ استجابة"],
"answer": "مستقبل⬅️ سيالة حسية⬅️ مركز⬅️ سيالة محركة⬅️ استجابة"
},


{
"question": "14. أقسام الهيكل العظمي:",
"options": ["محوري⬅️ طرفي","عضلي⬅️ عظمي","طرفي⬅️ محوري"],
"answer": "محوري⬅️ طرفي"
},


{
"question": "15. بنية السطح العلوي للمخ:",
"options": ["شقوق⬅️ نصفين⬅️ تلافيف","نصفي كرة⬅️ شق⬅️ تلافيف وشقوق","تلافيف⬅️ شق⬅️ نصفين"],
"answer": "نصفي كرة⬅️ شق⬅️ تلافيف وشقوق"
},


{
"question": "16. ترتيب عظام القحف:",
"options": ["صدغي⬅️ جبهي⬅️ قفوي","جبهي⬅️ جداري⬅️ قفوي⬅️ صدغي","قفوي⬅️ جبهي⬅️ جداري"],
"answer": "جبهي⬅️ جداري⬅️ قفوي⬅️ صدغي"
},


{
"question": "17. انقسام خلايا السمحاق:",
"options": ["انقسام⬅️ تكوين طبقات عظمية عرضياً","تعظم فقط","تكوين⬅️ انقسام"],
"answer": "انقسام⬅️ تكوين طبقات عظمية عرضياً"
},


{
"question": "18. ترتيب الأزرار النهائية:",
"options": ["تفرعات المحور⬅️ أزرار نهائية","محور⬅️ جسم","أزرار⬅️ تفرعات"],
"answer": "تفرعات المحور⬅️ أزرار نهائية"
},


{
"question": "19. بنية النسيج العصبي:",
"options": ["خلايا دبقية⬅️ عصبونات","عصبونات⬅️ خلايا دبقية","عضلات⬅️ أعصاب"],
"answer": "عصبونات⬅️ خلايا دبقية"
},


{
"question": "20. استجابة البنكرياس لارتفاع السكر:",
"options": ["إفراز⬅️ تنبيه⬅️ تخزين","تخزين⬅️ إفراز⬅️ تنبيه","تنبيه الجزر⬅️ إفراز أنسولين⬅️ تخزين غليكوجين"],
"answer": "تنبيه الجزر⬅️ إفراز أنسولين⬅️ تخزين غليكوجين"
},
        ],
        "u1_result1": [




{
"question": "27. ماذا ينتج عن تأثير الجملة الودية وقرب الودية على حدقة العين؟",
"options": [" الودية تضيقها وقرب الودية توسعها"," الودية توسعها وقرب الودية تضيقها"," كلاهما يوسعها"],
"answer": " الودية توسعها وقرب الودية تضيقها"
},



{
"question": "28. ماذا ينتج عن اختلاف الأعصاب الدماغية والشوكية؟",
"options": [" الدماغية 31 والشوكية 12"," الدماغية 12 شفعاً والشوكية 31 شفعاً"," كلاهما 12"],
"answer": " الدماغية 12 شفعاً والشوكية 31 شفعاً"
},



{
"question": "29. ماذا ينتج عن تأثير الأنسولين والغلوكاغون على السكر؟",
"options": [" الأنسولين يرفعه والغلوكاغون يخفضه"," الأنسولين يخفضه والغلوكاغون يرفعه"," كلاهما يرفعه"],
"answer": " الأنسولين يخفضه والغلوكاغون يرفعه"
},



{
"question": "30. ماذا ينتج عن اختلاف الغدد الصماء والمفتوحة؟",
"options": [" الصماء عبر قنوات والمفتوحة في الدم"," الصماء في الدم مباشرة والمفتوحة عبر قنوات"," كلاهما عبر قنوات"],
"answer": " الصماء في الدم مباشرة والمفتوحة عبر قنوات"
},
        ],
        "u1_function": [




{
"question": "5. ما هي وظيفة المخ؟",
"options": [" مركز الإحساس الشعوري والأفعال الإرادية والذكاء"," تنظيم التنفس فقط"," تخزين الكالسيوم"],
"answer": " مركز الإحساس الشعوري والأفعال الإرادية والذكاء"
},



{
"question": "6. ما هي وظيفة المخيخ؟",
"options": [" إفراز الهرمونات"," تنسيق التقلصات العضلية وضمان توازن الجسم"," التحكم في الهضم"],
"answer": " تنسيق التقلصات العضلية وضمان توازن الجسم"
},



{
"question": "7. ما هي وظيفة البصلة السيسائية؟",
"options": [" مركز للأفعال الانعكاسية الحيوية (تنفس، قلب."," تخزين المعلومات"," تنظيم الإحساس"],
"answer": " مركز للأفعال الانعكاسية الحيوية (تنفس، قلب."
},



{
"question": "8. ما هي وظيفة النخاع الشوكي؟",
"options": [" إنتاج الطاقة"," مركز للأفعال الانعكاسية الشوكية وطريق لنقل السيالة"," تحليل الغذاء"],
"answer": " مركز للأفعال الانعكاسية الشوكية وطريق لنقل السيالة"
},



{
"question": "9. ما هي وظيفة الأم الحنون؟",
"options": [" تغذية المراكز العصبية"," نقل الدم"," حماية العظام"],
"answer": " تغذية المراكز العصبية"
},



{
"question": "10. ما هي وظيفة السائل الدماغي الشوكي؟",
"options": [" إنتاج العصبونات"," حماية المراكز العصبية من الصدمات"," تنظيم الهرمونات"],
"answer": " حماية المراكز العصبية من الصدمات"
},



{
"question": "11. ما هي وظيفة الخلايا الدبقية؟",
"options": [" دعم وحماية وتغذية العصبونات"," إنتاج العضلات"," نقل السيالة العصبية"],
"answer": " دعم وحماية وتغذية العصبونات"
},



{
"question": "12. ما هي وظيفة غمد النخاعين؟",
"options": [" إنتاج الدم"," عزل الألياف العصبية كهربائياً"," زيادة التقلص العضلي"],
"answer": " عزل الألياف العصبية كهربائياً"
},



{
"question": "13. ما هي وظيفة هرمون النمو (GH.؟",
"options": [" تنظيم السكر"," ضبط نمو العظام والعضلات"," تنظيم النوم"],
"answer": " ضبط نمو العظام والعضلات"
},



{
"question": "14. ما هي وظيفة التيروكسين؟",
"options": [" زيادة الكالسيوم"," تنظيم درجة حرارة الجسم وإنتاج الطاقة"," خفض ضغط الدم"],
"answer": " تنظيم درجة حرارة الجسم وإنتاج الطاقة"
},



{
"question": "15. ما هي وظيفة الكالسيتونين؟",
"options": [" سحب الكالسيوم من العظام"," زيادة ترسيب الكالسيوم في العظام"," رفع سكر الدم"],
"answer": " زيادة ترسيب الكالسيوم في العظام"
},



{
"question": "16. ما هي وظيفة الباراثورمون؟",
"options": [" زيادة الطاقة"," تنظيم نسبة الكالسيوم في الدم"," خفض الكالسيوم في الدم"],
"answer": " تنظيم نسبة الكالسيوم في الدم"
},



{
"question": "17. ما هي وظيفة الأنسولين؟",
"options": [" خفض نسبة سكر العنب في الدم"," زيادة ضغط الدم"," رفع سكر الدم"],
"answer": " خفض نسبة سكر العنب في الدم"
},



{
"question": "18. ما هي وظيفة الأدرينالين؟",
"options": [" تنظيم النوم"," تحذير الجسم في حالات الخوف والخطر"," تهدئة الجسم"],
"answer": " تحذير الجسم في حالات الخوف والخطر"
},



{
"question": "19. ما هي وظيفة الميلاتونين؟",
"options": [" زيادة الهضم"," تنظيم الساعة البيولوجية (النوم واليقظة."," زيادة النشاط"],
"answer": " تنظيم الساعة البيولوجية (النوم واليقظة."
},



{
"question": "20. ما هي وظيفة الجهاز العصبي المحيطي؟",
"options": [" تخزين الكالسيوم"," إنتاج الهرمونات"," صلة الوصل بين المركزي ومختلف أعضاء الجسم"],
"answer": " صلة الوصل بين المركزي ومختلف أعضاء الجسم"
},


        ]
    }
}

# ================== بيانات المستخدم المؤقتة ==================
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

    await update.message.reply_text(" ✨ نرحب بكم في منصة بوابة العلامة الكاملة ✨\n✨إشراف الاستاذ :احمد نور الدين  939138720✨\n✨ برمجة وتصميم المهندس :سامي حبيب  943512782✨/")

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

    if not context.args:
        await update.message.reply_text("❌ أرسل ID")
        return

    user_id = int(context.args[0])

    approve_user(user_id)

    await update.message.reply_text(" تم التفعيل")
    await context.bot.send_message(chat_id=user_id, text="اضغط  /start 🎉 تم قبولك")

# ================== إرسال السؤال ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if user_id not in user_data:
        return

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q_list = subjects[subject][category]

    # ================== نهاية الأسئلة ==================
    if index >= len(q_list):
        score = user_data[user_id]["score"]

        users.update_one(
            {"_id": user_id},
            {"$set": {"score": score}}
        )

        keyboard = [
            [InlineKeyboardButton("🔁 إعادة الاختبار", callback_data="start_quiz")]
        ]

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎉 انتهيت!\n📊 نتيجتك: {score} من {len(q_list)*10}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================== السؤال الحالي ==================
    q = q_list[index]

    # 🧠 بناء النص (هنا كان الخطأ عندك)
    text = q["question"] + "\n\n"

    for i, opt in enumerate(q["options"]):
        text += f"{chr(65+i)}- {opt}\n"

    # 🎯 أزرار مختصرة (تحل مشكلة طول النص)
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data="0"),
            InlineKeyboardButton("B", callback_data="1"),
            InlineKeyboardButton("C", callback_data="2"),
        ]
    ]

    # ================== إرسال ==================
    if q.get("type") == "image":
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=uploaded_images[q["image"]],
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ================== الأزرار ==================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # ================== اختيار المادة ==================
    if data == "bio":
        keyboard = [
            [InlineKeyboardButton("الوحدة 1", callback_data="bio_u1")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🧬 اختر الوحدة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================== اختيار الوحدة ==================
    if data.startswith("bio_u"):
        unit = data.split("_")[1]

        user_data[user_id] = {
            "score": 0,
            "q_index": 0,
            "subject": "bio",
            "unit": unit
        }

        keyboard = [
            [InlineKeyboardButton("📘 تعليل", callback_data="taaleel")],
            [InlineKeyboardButton("🖼️ صور", callback_data="images")],
            [InlineKeyboardButton("📍 حدد موقع", callback_data="where")],
            [InlineKeyboardButton("📊 رتب مراحل", callback_data="level")],
            [InlineKeyboardButton("🧠 ماذا ينتج عن", callback_data="result1")],
            [InlineKeyboardButton("👍 ماهي وظيفة ", callback_data="function")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="اختر نوع الأسئلة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================== اختيار نوع الأسئلة ==================
    if data in ["taaleel", "images", "where", "level", "result1","function"]:

        if user_id not in user_data:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ ابدأ من البداية /start"
            )
            return

        unit = user_data[user_id].get("unit")

        if not unit:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ لم يتم تحديد الوحدة"
            )
            return

        category = f"{unit}_{data}"

        if category not in subjects["bio"]:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ لا يوجد قسم: {category}"
            )
            return

        user_data[user_id]["category"] = category

        keyboard = [
            [InlineKeyboardButton("🎬 مشاهدة الفيديو التعليمي", callback_data="watch_video")],
            [InlineKeyboardButton("▶️ ابدأ الاختبار", callback_data="start_quiz")]
        ]

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="📚 يمكنك الآن:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ================== الفيديو ==================
    if data == "watch_video":
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=INTRO_VIDEO
        )
        return

    if data == "start_quiz":
        await send_question(update, context)
        return 
# ================== الإجابة ==================
    if user_id not in user_data:
        return

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q = subjects[subject][category][index]
    selected = q["options"][int(data)]

    if selected == q["answer"]:
        user_data[user_id]["score"] += 10
        result = " صحيح"
    else:
        result = f"❌ خطأ\nالإجابة: {q['answer']}"

    user_data[user_id]["q_index"] += 1

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=result
    )

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
