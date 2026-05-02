"""
نظام الملاحة (Navigation) المحسّن
يدير تنقل المستخدمين بين الشاشات بطريقة منظمة وآمنة
"""

from typing import Callable, Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============ تحديد أنواع الشاشات ============
class ScreenType(Enum):
    """أنواع الشاشات في البوت"""
    MAIN_MENU = "main_menu"
    UNIT_MENU = "unit_menu"
    SECTION_MENU = "section_menu"
    TYPES_MENU = "types_menu"
    QUIZ = "quiz"
    PAYMENT = "payment"
    ADMIN_PANEL = "admin_panel"
    RESULTS = "results"


# ============ تمثيل حالة الشاشة ============
@dataclass
class ScreenState:
    """
    تمثيل حالة الشاشة
    تحتفظ بنوع الشاشة والبيانات المتعلقة بها
    """
    screen_type: ScreenType
    context_data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        """تهيئة التاريخ الافتراضي"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def __repr__(self) -> str:
        return f"Screen({self.screen_type.value}, {self.context_data})"


# ============ فئة إدارة التاريخ ============
class NavigationHistory:
    """
    إدارة سجل التنقل بين الشاشات
    مثل زر الرجوع في المتصفح
    
    الاستخدام:
        nav = NavigationHistory()
        screen = ScreenState(ScreenType.MAIN_MENU, {})
        nav.add_screen(user_id=123, screen=screen)
        previous = nav.go_back(user_id=123)
    """
    
    def __init__(self, max_history: int = 20):
        """
        التهيئة
        
        Args:
            max_history: أقصى عدد خطوات يمكن الرجوع إليها
                        (بعد تجاوزه، يتم حذف الأقدم)
        """
        self.max_history = max_history
        # self.history[user_id] = [ScreenState1, ScreenState2, ...]
        self.history: Dict[int, List[ScreenState]] = {}
        logger.info(f"تم تهيئة NavigationHistory بـ max_history={max_history}")
    
    def add_screen(self, user_id: int, screen: ScreenState) -> None:
        """
        إضافة شاشة جديدة للتاريخ
        
        Args:
            user_id: معرف المستخدم
            screen: كائن ScreenState يمثل الشاشة الجديدة
        """
        # إنشاء قائمة جديدة للمستخدم إذا لم تكن موجودة
        if user_id not in self.history:
            self.history[user_id] = []
            logger.info(f"📝 إنشاء سجل جديد للمستخدم {user_id}")
        
        # إذا وصلنا للحد الأقصى، احذف الأقدم (من البداية)
        if len(self.history[user_id]) >= self.max_history:
            removed = self.history[user_id].pop(0)
            logger.debug(f"⏭️ تم حذف الشاشة القديمة: {removed.screen_type.value}")
        
        # إضافة الشاشة الجديدة
        self.history[user_id].append(screen)
        logger.info(
            f"✅ أضيفت شاشة للمستخدم {user_id}: "
            f"{screen.screen_type.value} مع البيانات {screen.context_data}"
        )
    
    def go_back(self, user_id: int) -> Optional[ScreenState]:
        """
        الرجوع للشاشة السابقة
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            ScreenState: الشاشة السابقة أو None إذا لم تكن موجودة
        
        المنطق:
            1. حذف الشاشة الحالية من القائمة
            2. الرجوع للشاشة قبل الأخيرة
        """
        # التحقق من وجود المستخدم والتاريخ
        if user_id not in self.history:
            logger.warning(f"⚠️ المستخدم {user_id} لا يملك تاريخ")
            return None
        
        history_list = self.history[user_id]
        
        # التحقق من أن هناك شاشات في التاريخ
        if len(history_list) == 0:
            logger.warning(f"⚠️ تاريخ المستخدم {user_id} فارغ")
            return None
        
        # حذف الشاشة الحالية (الأخيرة)
        current_screen = history_list.pop()
        logger.info(f"🗑️ تم حذف الشاشة الحالية: {current_screen.screen_type.value}")
        
        # التحقق من وجود شاشة سابقة
        if len(history_list) == 0:
            logger.info(f"🔙 لا توجد شاشة سابقة للمستخدم {user_id}")
            return None
        
        # الحصول على الشاشة السابقة (الأخيرة الآن)
        previous_screen = history_list[-1]
        logger.info(f"🔙 رجعنا إلى: {previous_screen.screen_type.value}")
        
        return previous_screen
    
    def get_current_screen(self, user_id: int) -> Optional[ScreenState]:
        """
        الحصول على الشاشة الحالية
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            ScreenState: الشاشة الحالية أو None
        """
        if user_id not in self.history or len(self.history[user_id]) == 0:
            return None
        
        return self.history[user_id][-1]
    
    def get_history_path(self, user_id: int) -> str:
        """
        الحصول على مسار التنقل كاملاً
        مفيد للتصحيح والتحليل
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            str: مسار التنقل مثل "main_menu → unit_menu → section_menu"
        """
        if user_id not in self.history or len(self.history[user_id]) == 0:
            return "لا يوجد"
        
        path_list = [
            screen.screen_type.value 
            for screen in self.history[user_id]
        ]
        
        path = " → ".join(path_list)
        return path
    
    def get_history_details(self, user_id: int) -> str:
        """
        الحصول على تفاصيل التاريخ كاملة
        يتضمن البيانات والأوقات
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            str: تفاصيل التاريخ المفصل
        """
        if user_id not in self.history or len(self.history[user_id]) == 0:
            return "لا يوجد تاريخ"
        
        details = "📜 التاريخ المفصل:\n"
        
        for idx, screen in enumerate(self.history[user_id], 1):
            timestamp = screen.timestamp.strftime("%H:%M:%S")
            details += f"\n{idx}. {screen.screen_type.value}\n"
            details += f"   ⏰ {timestamp}\n"
            
            if screen.context_data:
                details += f"   📊 البيانات: {screen.context_data}\n"
        
        return details
    
    def clear_history(self, user_id: int) -> None:
        """
        مسح تاريخ المستخدم بالكامل
        
        Args:
            user_id: معرف المستخدم
        """
        if user_id in self.history:
            count = len(self.history[user_id])
            self.history[user_id] = []
            logger.info(f"🗑️ تم مسح تاريخ المستخدم {user_id} ({count} شاشات)")
        else:
            logger.debug(f"ℹ️ لا يوجد تاريخ للمستخدم {user_id}")
    
    def remove_user_completely(self, user_id: int) -> None:
        """
        حذف المستخدم بالكامل من النظام
        
        Args:
            user_id: معرف المستخدم
        """
        if user_id in self.history:
            del self.history[user_id]
            logger.info(f"🗑️ تم حذف المستخدم {user_id} من النظام")
    
    def get_all_active_users(self) -> List[int]:
        """
        الحصول على قائمة بجميع المستخدمين النشطين
        
        Returns:
            List[int]: قائمة معرفات المستخدمين
        """
        return list(self.history.keys())
    
    def get_users_count(self) -> int:
        """
        الحصول على عدد المستخدمين النشطين
        
        Returns:
            int: عدد المستخدمين
        """
        return len(self.history)
    
    def get_user_history_length(self, user_id: int) -> int:
        """
        الحصول على عدد الشاشات في تاريخ المستخدم
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            int: عدد الشاشات
        """
        if user_id not in self.history:
            return 0
        
        return len(self.history[user_id])


# ============ إنشاء instance واحد لاستخدامه في البوت ============
navigation = NavigationHistory(max_history=20)


# ============ فئة بناء الشاشات ============
class ScreenBuilder:
    """
    بناء محتوى الشاشات (نصوص وأزرار)
    بطريقة منظمة وموحدة
    
    كل شاشة لها دالة مخصصة تبني محتواها
    """
# أضف دالة بناء SECTION_MENU
@staticmethod
async def build_section_menu(
    context,
    query,
    user_id: int,
    unit: str,
    section: str
) -> None:
    """بناء شاشة القسم"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
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
    
    text = """
📝 اختر نوع الأسئلة:

سيتم عرض أسئلة من هذا النوع فقط
    """
    
    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    
    logger.info(f"✅ عرضت شاشة القسم ({unit}/{section}) للمستخدم {user_id}")
    
    
    
        
    @staticmethod
    async def build_main_menu(
        context,
        query,
        user_id: int
    ) -> None:
        """
        بناء شاشة القائمة الرئيسية
        
        Args:
            context: context من Telegram
            query: callback_query
            user_id: معرف المستخدم
        """
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("🧬🌍 علم الأحياء والأرض🌍🧬", callback_data="bio")],
        ]
        
        text = """
📚 اختر المادة:

يمكنك اختيار المادة التي تريد حل الأسئلة فيها
        """
        
        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        
        logger.info(f"✅ عرضت شاشة القائمة الرئيسية للمستخدم {user_id}")
    
    @staticmethod
    async def build_unit_menu(
        context,
        query,
        user_id: int,
        unit: str
    ) -> None:
        """
        بناء شاشة قائمة الوحدات
        
        Args:
            context: context من Telegram
            query: callback_query
            user_id: معرف المستخدم
            unit: رقم الوحدة (u1 أو u2 او u3)
        """
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        if unit == "u1":
            keyboard = [
                [
                    InlineKeyboardButton("🦴 القسم الدعامي 🦴", callback_data="sec_u1_dam"),

                    InlineKeyboardButton("🧠 الجهاز العصبي 🧠", callback_data="sec_u1_nervus"),
                ],
                [
                    InlineKeyboardButton("🧬 الغدد الصم 🧬", callback_data="sec_u1_sum"),

                    InlineKeyboardButton("👅 أعضاء الحس 👅", callback_data="sec_u1_sens"),
                ],
                [
                    InlineKeyboardButton("🧑‍⚕️ صحة الدعامة والتنسيق 🧑‍⚕️", callback_data="sec_u1_heal"),
                ],
                [
                    InlineKeyboardButton("🔙 رجوع", callback_data="back"),
                ],
            ]
            
            text = """
📚 الوحدة 1: الدعامة والتنسيق

اختر القسم الذي تريد حل الأسئلة فيه
            """
        
        elif unit == "u2":
            keyboard = [
                [
                    InlineKeyboardButton("🥗 الهضم لدى الإنسان 🥗", callback_data="sec_u2_digest"),
                    InlineKeyboardButton("🫀 الدوران لدى الإنسان 🫀", callback_data="sec_u2_circulation"),
                ],
                [
                    InlineKeyboardButton("🫁 التنفس لدى الإنسان 🫁", callback_data="sec_u2_respiration"),
                    InlineKeyboardButton("🚽 الإطراح عند الإنسان 🚽", callback_data="sec_u2_excretion"),
                ],
                [
                    InlineKeyboardButton("🍎 صحة وظائف التغذية 🍎", callback_data="sec_u2_nutrition_health"),
                ],
                [
                    InlineKeyboardButton("🔙 رجوع", callback_data="back"),
                ],
            ] 
            text = """
📚 الوحدة2: وظائف التغذية

اختر القسم الذي تريد حل الأسئلة فيه
            """
        elif unit == "u3": 
            keyboard = [
                [
                    InlineKeyboardButton("🧬 الوراثة🧬", callback_data="sec_u3_genetics"),
                    InlineKeyboardButton("👶 أجهزة التكاثر👶", callback_data="sec_u3_reproduction"),
                ],
                [
                    InlineKeyboardButton("🔙 رجوع", callback_data="back"),
                ],                
            ]
            text = """
📚 الوحدة 3: علم الوراثة والتكاثر

اختر القسم الذي تريد حل الأسئلة فيه
            """
        elif unit == "u4": 
            keyboard = [
                [
                    InlineKeyboardButton("🌱 التكاثر لدى النباتات البذرية🌱", callback_data="sec_u4_reproduction"),
                     InlineKeyboardButton("🌍 التلوث🌍", callback_data="sec_u4_pollution"),
                ],
                [
                    InlineKeyboardButton("🔙 رجوع", callback_data="back"),
                ],                
            ]
            text = """
📚 الوحدة 3: علم الوراثة والتكاثر

اختر القسم الذي تريد حل الأسئلة فيه
            """
        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        
        logger.info(f"✅ عرضت شاشة الوحدات (الوحدة {unit}) للمستخدم {user_id}")
    
    @staticmethod
    async def build_types_menu(
        context,
        query,
        user_id: int
    ) -> None:
        """
        بناء شاشة أنواع الأسئلة
        
        Args:
            context: context من Telegram
            query: callback_query
            user_id: معرف المستخدم
        """
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("📘 تعليل", callback_data="taaleel"),
                InlineKeyboardButton("🖼 صور", callback_data="image"),
            ],
            [
                InlineKeyboardButton("📍 موقع", callback_data="where"),
                InlineKeyboardButton("📊 ترتيب", callback_data="level"),
            ],
            [
                InlineKeyboardButton("🧠 نتائج", callback_data="result"),
                InlineKeyboardButton("⚙️ وظيفة", callback_data="function"),
                InlineKeyboardButton("⚡ مقارنة", callback_data="compare"),
            ],
            [
                InlineKeyboardButton("🔙 رجوع", callback_data="back"),
            ],
        ]
        
        text = """
📝 اختر نوع الأسئلة:

سيتم عرض أسئلة من هذا النوع فقط
        """
        
        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        
        logger.info(f"✅ عرضت شاشة أنواع الأسئلة للمستخدم {user_id}")
    
    @staticmethod
    async def build_quiz_menu(
        context,
        query,
        user_id: int
    ) -> None:
        """
        بناء شاشة الاختبار (الشاشة قبل البدء)
        
        Args:
            context: context من Telegram
            query: callback_query
            user_id: معرف المستخدم
        """
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        import random
        
        welcome_messages = [
            "🎉 رائع! اختر نوع الأسئلة التي تريد حلها:",
            "✨ ممتاز! حان وقت اختبار معلوماتك:",
            "🚀 ممتاز! اختر نوع الأسئلة لبدء التحدي:",
            "👋 أهلاً بك في بوت الأحياء الذكي!",
            "📘 هنا ستتعلم بطريقة ممتعة وسهلة",
            "🎯 حل الأسئلة واجمع النقاط",
            "🚀 واصِل التقدم لتصبح الأفضل!",
        ]
        
        keyboard = [
            [
                InlineKeyboardButton("▶️ بدء الاختبار", callback_data="start_quiz"),
            ],
            [
                InlineKeyboardButton("🔙 رجوع", callback_data="back"),
            ],
        ]
        
        text = random.choice(welcome_messages)
        
        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        
        logger.info(f"✅ عرضت شاشة بدء الاختبار للمستخدم {user_id}")
    
    @staticmethod
    async def build_payment_menu(
        context,
        query,
        user_id: int
    ) -> None:
        """
        بناء شاشة الدفع
        
        Args:
            context: context من Telegram
            query: callback_query
            user_id: معرف المستخدم
        """
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [
                InlineKeyboardButton("💳 شام كاش", callback_data="pay_shamcash"),
            ],
            [
                InlineKeyboardButton("🧾 دفع يدوي", callback_data="paid"),
            ],
            [
                InlineKeyboardButton("🔙 رجوع", callback_data="back"),
            ],
        ]
        
        text = """
💰 هذا القسم مدفوع

اختر طريقة الدفع:
• شام كاش: دفع فوري عبر محفظة شام كاش
• دفع يدوي: تحويل بنكي (موافقة يدوية من الأدمن)
        """
        
        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
        
        logger.info(f"✅ عرضت شاشة الدفع للمستخدم {user_id}")


# ============ خريطة ربط أنواع الشاشات بدوال البناء ============
SCREEN_BUILDERS = {
    ScreenType.MAIN_MENU: ScreenBuilder.build_main_menu,
    ScreenType.UNIT_MENU: ScreenBuilder.build_unit_menu,
    ScreenType.SECTION_MENU: ScreenBuilder.build_section_menu,  # ✅ أضفنا هنا
    ScreenType.TYPES_MENU: ScreenBuilder.build_types_menu,
    ScreenType.QUIZ: ScreenBuilder.build_quiz_menu,
    ScreenType.PAYMENT: ScreenBuilder.build_payment_menu,
}



# ============ دالة الرجوع الموحدة ============
async def handle_back_button(
    update,
    context
) -> None:
    """
    معالج موحد لزر الرجوع
    لا حاجة لتكرار الكود!
    
    هذه الدالة تقوم بـ:
    1. الرجوع للشاشة السابقة
    2. بناء الشاشة السابقة
    3. عرضها للمستخدم
    
    Args:
        update: update من Telegram
        context: context من Telegram
    """
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    query = update.callback_query
    user_id = query.from_user.id
    
    logger.info(f"👤 المستخدم {user_id} ضغط زر الرجوع")
    
    try:
        # ============ الرجوع للشاشة السابقة ============
        previous_screen = navigation.go_back(user_id)
        
        if previous_screen is None:
            # لا توجد شاشة سابقة
            await query.answer(
                "❌ لا يمكن الرجوع أكثر",
                show_alert=True
            )
            logger.warning(f"⚠️ المستخدم {user_id} حاول الرجوع لكن لا توجد شاشة سابقة")
            return
        
        # ============ الحصول على معلومات الشاشة السابقة ============
        screen_type = previous_screen.screen_type
        context_data = previous_screen.context_data
        
        logger.info(
            f"🔙 المستخدم {user_id} رجع إلى: {screen_type.value}"
        )
        
        # ============ الإجابة على الزر ============
        await query.answer()
        
        # ============ الحصول على دالة البناء ============
        builder = SCREEN_BUILDERS.get(screen_type)
        
        if builder is None:
            # نوع الشاشة غير معروف
            await query.answer(
                "❌ خطأ: نوع الشاشة غير معروف",
                show_alert=True
            )
            logger.error(f"❌ نوع الشاشة {screen_type.value} غير موجود في SCREEN_BUILDERS")
            return
        
        # ============ بناء وعرض الشاشة السابقة ============
        try:
            # إذا كانت الشاشة تحتاج parameters إضافية
            if context_data:
                # تمرير البيانات كـ keyword arguments
                await builder(context, query, user_id, **context_data)
            else:
                # بدون parameters إضافية
                await builder(context, query, user_id)
            
            logger.info(f"✅ تم عرض الشاشة السابقة للمستخدم {user_id}")
        
        except TypeError as e:
            logger.error(f"❌ خطأ في تمرير البيانات: {e}")
            
            # محاولة بدون بيانات
            try:
                await builder(context, query, user_id)
            except Exception as e2:
                logger.error(f"❌ خطأ في عرض الشاشة: {e2}")
                await query.answer("❌ حدث خطأ في عرض الشاشة", show_alert=True)
    
    except Exception as e:
        logger.error(f"❌ خطأ في معالج الرجوع: {e}")
        await query.answer("❌ حدث خطأ غير متوقع", show_alert=True)


# ============ دوال مساعدة إضافية ============

def get_user_navigation_info(user_id: int) -> Dict[str, Any]:
    """
    الحصول على معلومات الملاحة الكاملة للمستخدم
    
    Args:
        user_id: معرف المستخدم
    
    Returns:
        Dict: معلومات شاملة عن ملاحة المستخدم
    """
    current_screen = navigation.get_current_screen(user_id)
    history_path = navigation.get_history_path(user_id)
    history_length = navigation.get_user_history_length(user_id)
    
    return {
        "user_id": user_id,
        "current_screen": current_screen.screen_type.value if current_screen else None,
        "current_context": current_screen.context_data if current_screen else None,
        "history_path": history_path,
        "history_length": history_length,
        "max_history": navigation.max_history,
    }


def print_user_navigation_debug(user_id: int) -> None:
    """
    طباعة معلومات الملاحة للتصحيح
    
    Args:
        user_id: معرف المستخدم
    """
    info = get_user_navigation_info(user_id)
    
    print("\n" + "="*50)
    print("🔍 معلومات الملاحة للمستخدم")
    print("="*50)
    print(f"👤 معرف المستخدم: {info['user_id']}")
    print(f"📍 الشاشة الحالية: {info['current_screen']}")
    print(f"📊 بيانات الشاشة: {info['current_context']}")
    print(f"🛤️ مسار التنقل: {info['history_path']}")
    print(f"📈 عدد الخطوات: {info['history_length']}/{info['max_history']}")
    print("="*50 + "\n")


def get_all_users_navigation_summary() -> Dict[int, Dict[str, Any]]:
    """
    الحصول على ملخص الملاحة لجميع المستخدمين
    
    Returns:
        Dict: معلومات الملاحة لجميع المستخدمين
    """
    summary = {}
    
    for user_id in navigation.get_all_active_users():
        summary[user_id] = get_user_navigation_info(user_id)
    
    return summary
