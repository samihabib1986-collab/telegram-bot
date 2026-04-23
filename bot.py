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
print("BOT IS RUNNING")
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
    "dam": "BAACAgQAAxkBAAIG_GnmTG0PIxI5oVt3I9oK1G3n2XtBAAI7GwACj3k4U_ihISwgbvOoOwQ"
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
"question": "1. لماذا توجد يافوخات (فتحات عظمية) في جمجمة الرضيع؟",
"options": ["لتسهيل عملية التنفس لدى الرضيع", "للسماح لعظام القحف بالنمو تماشياً مع نمو الدماغ", "لحماية الدماغ من الصدمات الخارجية"],
"answer": "للسماح لعظام القحف بالنمو تماشياً مع نمو الدماغ"
},
{
"question": "2. لماذا تعمل الأقراص الغضروفية بين الفقرات كوسادة مرنة؟",
"options": ["لأنها تمنع احتكاك عظام الفقرات ببعضها وتتحمل الضغط", "لتسهيل مرور الأعصاب الشوكية", "لزيادة طول العمود الفقري"],
"answer": "لأنها تمنع احتكاك عظام الفقرات ببعضها وتتحمل الضغط"
},
{
"question": "3. لماذا يزداد طول رواد الفضاء في الفضاء الخارجي؟",
"options": ["بسبب تمدد العضلات الطولية", "بسبب زيادة نشاط نقي العظم", "بسبب غياب الجاذبية مما يقلل الضغط على فقرات العمود الفقري"],
"answer": "بسبب غياب الجاذبية مما يقلل الضغط على فقرات العمود الفقري"
},
{
"question": "4. لماذا يمتاز العظم بالصلابة والقساوة والمتانة؟",
"options": ["بسبب الروابط الوثيقة بين الأملاح المعدنية والمواد العضو", "بسبب كثرة الأوعية الدموية فيه", "بسبب وجود السمحاق الذي يغطيه"],
"answer": "بسبب الروابط الوثيقة بين الأملاح المعدنية والمواد العضوي"
},
{
"question": "5. لماذا تتوقف قامة الإنسان عن النمو الطولي عند سن الثامنة عشرة تقريباً؟",
"options": ["بسبب نقص أملاح الكالسيوم", "بسبب توقف انقسام خلايا السمحاق", "بسبب تعظم غضاريف النمو (الاتصال)"],
"answer": "بسبب تعظم غضاريف النمو (الاتصال)"
},
{
"question": "6. لماذا تسمى العضلات المخططة بالعضلات الهيكلية؟",
"options": ["لأن معظمها يرتبط بعظام الهيكل العظمي", "لأنها توجد في جدران الأحشاء", "لأن حركتها تكون لاإرادية"],
"answer": "لأن معظمها يرتبط بعظام الهيكل العظمي"
},
{
"question": "7. لماذا يبقى الرأس منتصباً في أثناء اليقظة دون بذل جهد كبير؟",
"options": ["بسبب قوة مفاصل الرقبة", "بسبب خاصية المقوية العضلية", "بسبب وجود الأربطة المفصلية"],
"answer": "بسبب خاصية المقوية العضلية"
},
{
"question": "8. لماذا تسمى عضلات القلب والأحشاء بالعضلات اللاإرادية؟",
"options": ["لأن حركتها لا تخضع لإرادة الإنسان", "لأنها لا ترتبط بالعظام", "لأن حركتها بطيئة جداً"],
"answer": "لأن حركتها لا تخضع لإرادة الإنسان"
},
{
"question": "9. لماذا تعتبر العظام مخزناً احتياطياً مهماً للجسم؟",
"options": ["لأنها تحمي الأحشاء الداخلية", "لأنها تختزن أملاح الكالسيوم الضرورية للجسم", "لأنها تنتج كريات الدم الحمراء"],
"answer": "لأنها تختزن أملاح الكالسيوم الضرورية للجسم"
},
{
"question": "10. لماذا توفر مفاصل القحف أقصى درجات الحماية للدماغ؟",
"options": ["لأنها مفاصل واسعة الحركة", "لأنها محاطة بأوتار قوية", "لأنها مفاصل ثابتة تلتحم بواسطة مسننات عظمية"],
"answer": "لأنها مفاصل ثابتة تلتحم بواسطة مسننات عظمية"
}
        ],

        "u1_dam_images": [
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

        "u1_dam_where": [
            {
"question": "1. حدد موقع غضاريف النمو (الاتصال) في العظم الطويل:",
"options": ["تقع بين جسم العظم والمشاشتين", "تغطي جسم العظم من الخارج", "توجد داخل القناة المركزية"],
"answer": "تقع بين جسم العظم والمشاشتين"
},
{
"question": "2. حدد موقع النخاع الشوكي بالنسبة للهيكل العظمي:",
"options": ["بين أضلاع القفص الصدري", "يسكن القناة الفقرية الناتجة عن تتالي الثقوب الفقرية", "داخل تجويف الجمجمة"],
"answer": "يسكن القناة الفقرية الناتجة عن تتالي الثقوب الفقرية"
},
{
"question": "3. حدد موقع السمحاق في العظم الطويل:",
"options": ["طبقة رقيقة ليفية تغطي جسم العظم", "يملأ فراغات المشاشتين", "يوجد داخل نقي العظم"],
"answer": "طبقة رقيقة ليفية تغطي جسم العظم"
},
{
"question": "4. حدد موقع النسيج العظمي الإسفنجي في العظم الطويل:",
"options": ["يبطن القناة المركزية", "يوجد في السطح الخارجي للجسم", "يوجد في المشاشتين (النهايتين المنتفختين)"],
"answer": "يوجد في المشاشتين (النهايتين المنتفختين)"
},
{
"question": "5. حدد موقع عظم الرضفة في جسم الإنسان:",
"options": ["في مفصل الركبة لمنع انثناء الساق للأمام", "في مفصل المرفق", "في مفصل العضد"],
"answer": "في مفصل الركبة لمنع انثناء الساق للأمام"
},
{
"question": "6. حدد موقع نقي العظم الأحمر:",
"options": ["يوجد في الأقراص الغضروفية", "يملأ فراغات النسيج العظمي الإسفنجي", "في السطح الخارجي للسمحاق"],
"answer": "يملأ فراغات النسيج العظمي الإسفنجي"
},
{
"question": "7. حدد موقع العضلة الماصغة في جسم الإنسان:",
"options": ["في الناحية الخلفية للعضد", "توجد في جدار المعدة", "تقع على جانبي الوجه وتغلق الفكين"],
"answer": "تقع على جانبي الوجه وتغلق الفكين"
},
{
"question": "8. حدد موقع الزنار الكتفي في الهيكل الطرفي:",
"options": ["يربط الطرفين العلويين بالجذع (ترقوة ولوح كتف)", "يربط الطرفين السفليين بالجذع", "يوجد في عظام الرسغ"],
"answer": "يربط الطرفين العلويين بالجذع (ترقوة ولوح كتف)"
},
{
"question": "9. حدد موقع عظمة القص في الهيكل المحوري:",
"options": ["في الناحية الأمامية للقفص الصدري", "في الناحية الخلفية للجذع", "فوق عظم الفخذ مباشرة"],
"answer": "في الناحية الأمامية للقفص الصدري"
},
{
"question": "10. حدد موقع النسيج العظمي الكثيف في العظم الطويل:",
"options": ["يوجد في المشاشتين فقط", "يوجد داخل غضاريف النمو", "طبقة تلي السمحاق وتشكل البنية الأساسية لجسم العظم"],
"answer": "طبقة تلي السمحاق وتشكل البنية الأساسية لجسم العظم"
}

        ],
        "u1_dam_level": [{
"question": "1. بنية العظم من الخارج للداخل:",
"options": ["نسيج كثيف⬅️ السمحاق⬅️ قناة مركزية","السمحاق⬅️ نسيج عظمي كثيف⬅️ قناة مركزية","قناة مركزية⬅️ نسيج كثيف⬅️ السمحاق"],
"answer": "السمحاق⬅️ نسيج عظمي كثيف⬅️ قناة مركزية"
},


{
"question": "2. أغشية السحايا من الخارج للداخل:",
"options": ["العنكبوتي⬅️ الجافية⬅️ الحنون","الجافية⬅️ العنكبوتي⬅️ الحنون","الأم الحنون⬅️ العنكبوتي⬅️ الجافية"],
"answer": "الجافية⬅️ العنكبوتي⬅️ الحنون"
},


{
"question": "3. انتقال السيالة في العصبون:",
"options": ["استطالات⬅️ جسم الخلية⬅️ المحور⬅️ الأزرار","المحور⬅️ جسم الخلية⬅️ استطالات⬅️ الأزرار","جسم الخلية⬅️ استطالات⬅️ المحور⬅️ الأزرار"],
"answer": "استطالات⬅️ جسم الخلية⬅️ المحور⬅️ الأزرار"
},


{
"question": "4. عناصر القوس الانعكاسية:",
"options": ["عصب محرك⬅️ مستقبل⬅️ مركز⬅️ عضو","مستقبل⬅️ عصب حسي⬅️ مركز⬅️ عصب محرك⬅️ عضو منفذ","مركز⬅️ مستقبل⬅️ عصب⬅️ عضو"],
"answer": "مستقبل⬅️ عصب حسي⬅️ مركز⬅️ عصب محرك⬅️ عضو منفذ"
},


{
"question": "5. فقرات العمود الفقري من الأعلى:",
"options": ["قطني⬅️ رقبي⬅️ ظهري⬅️ عجزي⬅️ عصعصي","عصعصي⬅️ عجزي⬅️ قطني⬅️ ظهري⬅️ رقبي","رقبي⬅️ ظهري⬅️ قطني⬅️ عجزي⬅️ عصعصي"],
"answer": "رقبي⬅️ ظهري⬅️ قطني⬅️ عجزي⬅️ عصعصي"
},


{
"question": "6. بنية العصب من الخارج للداخل:",
"options": ["غمد العصب⬅️ غلاف الحزمة⬅️ ليف عصبي","غلاف⬅️ ليف⬅️ غمد","ليف⬅️ غمد⬅️ غلاف"],
"answer": "غمد العصب⬅️ غلاف الحزمة⬅️ ليف عصبي"
},


{
"question": "7. ترتيب شقوق المخ حسب العمق:",
"options": ["الأمامي الخلفي⬅️ رولاندو وسيلفيوس","سيلفيوس⬅️ الأمامي","رولاندو⬅️ الأمامي الخلفي"],
"answer": "الأمامي الخلفي⬅️ رولاندو وسيلفيوس"
},


{
"question": "8. نمو العظام طولياً:",
"options": ["تعظم⬅️ انقسام","انقسام خلايا الغضروف⬅️ تعظمها","تعظم فقط"],
"answer": "انقسام خلايا الغضروف⬅️ تعظمها"
},


{
"question": "9. عمل الهرمون:",
"options": ["إفراز⬅️ انتقال⬅️ تأثير","تأثير⬅️ إفراز⬅️ انتقال","انتقال⬅️ إفراز⬅️ تأثير"],
"answer": "إفراز⬅️ انتقال⬅️ تأثير"
},


{
"question": "10. ترتيب عظام الطرف العلوي:",
"options": ["يد⬅️ ساعد⬅️ عضد","عضد⬅️ ساعد⬅️ يد","ساعد⬅️ عضد⬅️ يد"],
"answer": "عضد⬅️ ساعد⬅️ يد"
},


{
"question": "11. أقسام الدماغ من الأعلى للأسفل:",
"options": ["مخ⬅️ مخيخ⬅️ بصلة سيسائية","بصلة⬅️ب مخ⬅️ مخيخ","مخيخ⬅️مخ⬅️ بصلة سيسائية"],
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
],
        "u1_dam_result1": [
            {
"question": "1. ماذا ينتج عن انقسام خلايا السمحاق في العظم؟",
"options": ["النمو العرضي للعظم", "النمو الطولي للعظم", "توقف نمو العظم نهائياً"],
"answer": "النمو العرضي للعظم"
},
{
"question": "2. ماذا ينتج عن انقسام خلايا غضاريف النمو (الاتصال)؟",
"options": ["زيادة ثخانة العظم", "النمو الطولي للعظم", "تحول العظم إلى نسيج غضروفي"],
"answer": "النمو الطولي للعظم"
},
{
"question": "3. ماذا ينتج عن تعظم غضاريف النمو عند سن الثامنة عشرة؟",
"options": ["توقف النمو الطولي للإنسان", "زيادة طول القامة", "تآكل رؤوس العظام"],
"answer": "توقف النمو الطولي للإنسان"
},
{
"question": "4. ماذا ينتج عن تقلص العضلة من حيث القطر والصلابة؟",
"options": ["ينقص قطرها وتقل صلابتها", "يزداد قطرها وتزداد صلابتها", "يبقى قطرها ثابتاً وتسترخي"],
"answer": "يزداد قطرها وتزداد صلابتها"
},
{
"question": "5. ماذا ينتج عن نشاط نقي العظم الأحمر في الجسم؟",
"options": ["تكوين خلايا الدم (حمراء وبيضاء وصفيحات)", "ترسيب أملاح الكالسيوم", "التحام عظام القحف"],
"answer": "تكوين خلايا الدم (حمراء وبيضاء وصفيحات)"
},
{
"question": "6. ماذا ينتج عن تنبيه ليفة عضلية بمنبه ما؟",
"options": ["استرخاء العضلة", "تحولها إلى نسيج ليفي", "تقلص العضلة واستجابتها للمنبه"],
"answer": "تقلص العضلة واستجابتها للمنبه"
},
{
"question": "7. ماذا ينتج عن خاصية المرونة في العضلات؟",
"options": ["عودة العضلة إلى وضعها الطبيعي بعد زوال التأثير عنها", "بقاء العضلة متقلصة دائماً", "تعب العضلة السريع"],
"answer": "عودة العضلة إلى وضعها الطبيعي بعد زوال التأثير عنها"
},
{
"question": "8. ماذا ينتج عن وجود النتوء المرفقي في نهاية عظم الزند؟",
"options": ["تسهيل حركة الساعد في جميع الاتجاهات", "منع انثناء الساعد نحو الخلف", "زيادة قوة القبضة"],
"answer": "منع انثناء الساعد نحو الخلف"
},
{
"question": "9. ماذا ينتج عن غياب الروابط بين الأملاح المعدنية والمواد العضوية في العظم؟",
"options": ["زيادة قوة العظم", "نمو العظم بشكل أسرع", "فقدان العظم لصلابته ومتانته"],
"answer": "فقدان العظم لصلابته ومتانته"
},
{
"question": "10. ماذا ينتج عن خاصية المقوية العضلية في عضلات الرقبة؟",
"options": ["انحناء الرقبة نحو الأمام", "بقاء الرأس منتصباً في أثناء اليقظة", "التعب العضلي الشديد"],
"answer": "بقاء الرأس منتصباً في أثناء اليقظة"
}

],
        "u1_dam_function": [
{
"question": "1. ما هي وظيفة نقي العظم الأحمر؟",
"options": ["تخزين أملاح الكالسيوم فقط", "تكوين خلايا الدم (حمراء وبيضاء وصفيحات)", "إعطاء العظم اللون الأبيض"],
"answer": "تكوين خلايا الدم (حمراء وبيضاء وصفيحات)"
},
{
"question": "2. ما هي وظيفة السمحاق في العظم الطويل؟",
"options": ["حماية نقي العظم الأحمر", "المسؤول عن النمو الطولي للعظم", "المسؤول عن النمو العرضي للعظم (زيادة الثخانة)"],
"answer": "المسؤول عن النمو العرضي للعظم (زيادة الثخانة)"
},
{
"question": "3. ما هي وظيفة الأوتار في الجهاز الحركي؟",
"options": ["ربط العضلات بالعظام والمساهمة في تحريك العظام", "ربط العظام ببعضها وتثبيتها", "تكوين المادة العظمية"],
"answer": "ربط العضلات بالعظام والمساهمة في تحريك العظام"
},
{
"question": "4. ما هي وظيفة القفص الصدري؟",
"options": ["حماية القلب والرئتين", "حماية الدماغ والنخاع الشوكي", "تسهيل حركة الأطراف العلوية"],
"answer": "حماية القلب والرئتين"
},
{
"question": "5. ما هي وظيفة عظام القحف في الجمجمة؟",
"options": ["تسهيل عملية النطق", "تثبيت الأسنان في الفكين", "توفير الحماية للدماغ"],
"answer": "توفير الحماية للدماغ"
},
{
"question": "6. ما هي وظيفة العمود الفقري؟",
"options": ["يشكل دعامة للجسم ويحمي النخاع الشوكي", "حماية القلب والرئتين", "تخزين المواد الغذائية"],
"answer": "يشكل دعامة للجسم ويحمي النخاع الشوكي"
},
{
"question": "7. ما هي وظيفة غضاريف النمو (الاتصال)؟",
"options": ["المسؤولة عن نمو العظم عرضياً", "المسؤولة عن النمو الطولي للعظام", "ربط الفقرات ببعضها"],
"answer": "المسؤولة عن النمو الطولي للعظام"
},
{
"question": "8. ما هي وظيفة المفاصل في جسم الإنسان؟",
"options": ["إنتاج السيالة العصبية المحركة", "تؤدي عملاً ميكانيكياً يساعد على تنفيذ الحركات المطلوبة", "تخزين الأملاح المعدنية"],
"answer": "تؤدي عملاً ميكانيكياً يساعد على تنفيذ الحركات المطلوبة"
},
{
"question": "9. ما هي وظيفة العضلة الماصغة؟",
"options": ["توجد على جانبي الوجه ووظيفتها إغلاق الفكين", "تحريك الرأس يميناً ويساراً", "تسهيل عملية التنفس"],
"answer": "توجد على جانبي الوجه ووظيفتها إغلاق الفكين"
},
{
"question": "10. ما هي وظيفة الأربطة في المفاصل؟",
"options": ["نقل الدم إلى العظام", "تحويل الغضاريف إلى عظام", "تربط العظام ببعضها وتساعد على اتزان المفاصل وحركتها"],
"answer": "تربط العظام ببعضها وتساعد على اتزان المفاصل وحركتها"
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

    await update.message.reply_text(
        "✨ نرحب بكم في منصة بوابة العلامة الكاملة ✨\n"
        "✨إشراف الاستاذ :احمد نور الدين  939138720✨\n"
        "✨ برمجة وتصميم المهندس :سامي حبيب  943512782✨"
    )

    keyboard = [
        [InlineKeyboardButton("🧬 علم الأحياء و الأرض", callback_data="bio")]
    ]

    await update.message.reply_text(
        "📚 اختر المادة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================== إرسال السؤال ==================
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

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
        text += f"{chr(65+i)}- {opt}\n"

    keyboard = [[
        InlineKeyboardButton("A", callback_data="0"),
        InlineKeyboardButton("B", callback_data="1"),
        InlineKeyboardButton("C", callback_data="2"),
    ]]

    # ✅ حل مشكلة الصور
    if "image" in q:
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=uploaded_images[q["image"]],
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
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
        keyboard = [
            [InlineKeyboardButton("الوحدة 1", callback_data="bio_u1")]
        ]
        await query.message.reply_text("اختر الوحدة:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # الوحدة
    if data == "bio_u1":
        keyboard = [
            [InlineKeyboardButton("🎬 فيديو الوحدة", callback_data="unit_video")],
            [InlineKeyboardButton("القسم الأول: الدعامي الحركي", callback_data="sec_u1_dam")]
        ]
        await query.message.reply_text("📘 الوحدة 1:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # فيديو الوحدة
    if data == "unit_video":
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=UNIT_VIDEOS["u1"]
        )
        return

    # القسم
    if data == "sec_u1_dam":

        user_data[user_id] = {
            "subject": "bio",
            "unit": "u1",
            "section": "dam",
            "score": 0,
            "q_index": 0
        }

        keyboard = [
            [InlineKeyboardButton("🎥 فيديو القسم", callback_data="section_video")],
            [InlineKeyboardButton("📘 تعليل", callback_data="taaleel")],
            [InlineKeyboardButton("🖼️ صور", callback_data="images")],
            [InlineKeyboardButton("📍 موقع", callback_data="where")],
            [InlineKeyboardButton("📊 ترتيب", callback_data="level")],
            [InlineKeyboardButton("🧠 نتائج", callback_data="result1")],
            [InlineKeyboardButton("⚙️ وظيفة", callback_data="function")]
        ]

        await query.message.reply_text("📚 اختر:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # فيديو القسم
    if data == "section_video":
        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=SECTION_VIDEOS["dam"]
        )
        return

    # نوع الأسئلة
    if data in ["taaleel", "images", "where", "level", "result1", "function"]:

        if user_id not in user_data:
            return

        unit = user_data[user_id]["unit"]
        section = user_data[user_id]["section"]

        category = f"{unit}_{section}_{data}"

        if category not in subjects["bio"]:
            await query.message.reply_text("❌ لا يوجد أسئلة لهذا القسم")
            return

        user_data[user_id]["category"] = category

        keyboard = [[
            InlineKeyboardButton("▶️ بدء الاختبار", callback_data="start_quiz")
        ]]

        await query.message.reply_text("ابدأ 👇", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # بدء الاختبار
    if data == "start_quiz":
        await send_question(update, context)
        return

    # الإجابة
    if user_id not in user_data:
        return

    subject = user_data[user_id]["subject"]
    category = user_data[user_id]["category"]
    index = user_data[user_id]["q_index"]

    q = subjects[subject][category][index]
    selected = q["options"][int(data)]

    if selected == q["answer"]:
        user_data[user_id]["score"] += 10
        result = "✔️ صحيح"
    else:
        result = f"❌ خطأ\nالإجابة: {q['answer']}"

    user_data[user_id]["q_index"] += 1

    await query.message.reply_text(result)
    await asyncio.sleep(1)
    await send_question(update, context)

# ================== تشغيل ==================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
