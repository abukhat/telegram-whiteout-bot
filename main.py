
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from keep_alive import keep_alive

# إعداد نظام التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# معرفات القنوات المطلوب الاشتراك فيها
REQUIRED_CHANNELS = [
    {"id": "@Survival_thefrost", "name": "قناة تلجرام", "link": "https://t.me/Survival_thefrost"},
    {"id": "@whiteoutsurvivel", "name": "قناة يوتيوب", "link": "https://www.youtube.com/@whiteoutsurvivel"}
]

# قاموس لحفظ اللغة المختارة لكل مستخدم
user_languages = {}

# النصوص متعددة اللغات
TEXTS = {
    "ar": {
        "language_selection": "🌍 **اختر لغتك المفضلة**\n\n🔤 يرجى اختيار اللغة التي تفضل استخدامها:",
        "arabic_button": "🇸🇦 العربية",
        "english_button": "🇺🇸 English",
        "subscription_required": "🚫 **اشتراك إجباري مطلوب!**\n\n🔒 **لا يمكن استخدام البوت بدون الاشتراك في القناتين**\n\n📺 **قناة يوتيوب:** شروحات ودروس حصرية للعبة\n💬 **قناة تلجرام:** التحديثات والأخبار الجديدة\n\n⚠️ **يجب الاشتراك في القناتين معاً:**\n1️⃣ اشترك في قناة يوتيوب أولاً\n2️⃣ اشترك في قناة تلجرام ثانياً\n3️⃣ اضغط 'تحقق من الاشتراك'\n\n👆 **اضغط على الأزرار أعلاه للاشتراك:**",
        "youtube_channel": "📺 قناة يوتيوب",
        "telegram_channel": "💬 قناة تلجرام", 
        "check_subscription": "✅ تحقق من الاشتراك",
        "subscription_verified": "✅ **مرحباً بك!**\n\n🎉 تم التحقق من اشتراكك بنجاح!\n🔓 يمكنك الآن استخدام جميع ميزات البوت\n\n📺 **تأكد من الاشتراك في قناة يوتيوب أيضاً**\n\n👇 اضغط الزر أدناه للبدء:",
        "start_now": "🚀 ابدأ الآن",
        "subscription_failed": "❌ **لم يتم الاشتراك بعد**\n\n🚫 **يجب الاشتراك في القناتين معاً:**\n📺 قناة يوتيوب للشروحات\n💬 قناة تلجرام للتحديثات\n\n⚠️ **تأكد من الاشتراك في كلا القناتين**\n\n🔄 استخدم /start للعودة للبداية",
        "try_again": "🔄 إعادة المحاولة",
        "welcome_message": "🎮 **مرحباً بك في بوت النجاة في الصقيع!**\n\n🔥 **الأوامر المتاحة:**\n⚔️ `/compare` - مقارنة القوات\n📚 `/help` - شرح مفصل للعبة\nℹ️ `/info` - معلومات البوت\n\n💡 **يمكنك أيضاً:**\n• إرسال أي سؤال وسأجد الفيديو المناسب\n• استخدام الأزرار أدناه للوصول السريع",
        "power_comparison": "⚔️ مقارنة القوات",
        "game_guide": "📚 شرح اللعبة", 
        "bot_info": "ℹ️ معلومات البوت",
        "back_to_menu": "🔙 العودة للقائمة",
        "change_language": "🌍 تغيير اللغة"
    },
    "en": {
        "language_selection": "🌍 **Choose Your Preferred Language**\n\n🔤 Please select the language you prefer to use:",
        "arabic_button": "🇸🇦 العربية",
        "english_button": "🇺🇸 English",
        "subscription_required": "🚫 **Mandatory Subscription Required!**\n\n🔒 **Bot cannot be used without subscribing to both channels**\n\n📺 **YouTube Channel:** Exclusive tutorials and lessons for the game\n💬 **Telegram Channel:** Updates and new announcements\n\n⚠️ **Must subscribe to both channels:**\n1️⃣ Subscribe to YouTube channel first\n2️⃣ Subscribe to Telegram channel second\n3️⃣ Click 'Check Subscription'\n\n👆 **Click the buttons above to subscribe:**",
        "youtube_channel": "📺 YouTube Channel",
        "telegram_channel": "💬 Telegram Channel",
        "check_subscription": "✅ Check Subscription", 
        "subscription_verified": "✅ **Welcome!**\n\n🎉 Subscription verified successfully!\n🔓 You can now use all bot features\n\n📺 **Make sure to subscribe to YouTube channel too**\n\n👇 Click button below to start:",
        "start_now": "🚀 Start Now",
        "subscription_failed": "❌ **Not subscribed yet**\n\n🚫 **Must subscribe to both channels:**\n📺 YouTube for tutorials\n💬 Telegram for updates\n\n⚠️ **Make sure to subscribe to both channels**\n\n🔄 Use /start to restart",
        "try_again": "🔄 Try Again",
        "welcome_message": "🎮 **Welcome to Whiteout Survival Bot!**\n\n🔥 **Available Commands:**\n⚔️ `/compare` - Power Comparison\n📚 `/help` - Detailed Game Guide\nℹ️ `/info` - Bot Information\n\n💡 **You can also:**\n• Send any question and I'll find the right video\n• Use buttons below for quick access",
        "power_comparison": "⚔️ Power Comparison",
        "game_guide": "📚 Game Guide",
        "bot_info": "ℹ️ Bot Info", 
        "back_to_menu": "🔙 Back to Menu",
        "change_language": "🌍 Change Language"
    }
}

# قاعدة بيانات الفيديوهات والأسئلة الشائعة - محدثة بالكامل
YOUTUBE_VIDEOS = {
    "التمائم والحيوان": {
        "keywords": ["تمائم", "حيوان", "مهارة", "قوي", "اقوى", "مقارنة", "amulet", "animal", "skill", "strong", "strongest", "compare"],
        "video": "https://youtu.be/dC3SfhT6dd4?si=4Y_gT7Jdb5o9JqhA",
        "description_ar": "ماهو الأقوى في لعبة النجاة في الصقيع التمائم أو مهارة الحيوان",
        "description_en": "What is stronger in Whiteout Survival: Amulets or Animal Skills"
    },
    "عجلة الحظ": {
        "keywords": ["عجلة", "حظ", "تهكير", "حيل", "wheel", "luck", "hack", "tricks"],
        "video": "https://youtu.be/J5gJakTD94Y?si=bNqf6EUN0IuARjoo",
        "description_ar": "تهكير عجلة الحظ whiteout survival",
        "description_en": "Lucky wheel hack whiteout survival"
    },
    "مسبك الأسلحة": {
        "keywords": ["مسبك", "اسلحة", "أسلحة", "صناعة", "foundry", "weapons", "crafting"],
        "video": "https://youtu.be/9xGzuOhInj8?si=kRttVkOmZ0Rci1G4",
        "description_ar": "مسبك الأسلحة لعبة النجاة",
        "description_en": "Weapons foundry survival game"
    },
    "جمع الكريستال": {
        "keywords": ["كريستال", "جمع", "مجانا", "مجاني", "crystal", "collect", "free"],
        "video": "https://youtube.com/shorts/iK5n1fwuzKs?si=PZlrBYBA5PjkUrBO",
        "description_ar": "جمع الكريستال مجاناً",
        "description_en": "Collect crystals for free"
    },
    "صائد الكنوز": {
        "keywords": ["صائد", "كنوز", "خريطة", "treasure", "hunter", "map"],
        "video": "https://youtu.be/9Y7RAP4w0wU?si=leQL6QXlnRQYH9t-",
        "description_ar": "صائد الكنوز لعبة النجاة في الصقيع",
        "description_en": "Treasure hunter whiteout survival game"
    },
    "الأبطال القوية": {
        "keywords": ["أبطال", "قوية", "جيل", "اختيار", "انتبه", "heroes", "strong", "generation", "choose", "attention"],
        "video": "https://youtu.be/teywq6pO7fQ?si=a72pPpBrkukVyyIQ",
        "description_ar": "انتبه أبطال قوية لازم تاخدها من كل جيل",
        "description_en": "Strong heroes you must take from each generation"
    },
    "مقارنة القوة": {
        "keywords": ["قارن", "قوة", "خصم", "خطة", "فوز", "compare", "power", "enemy", "plan", "win"],
        "video": "https://youtube.com/shorts/lechAM-Walg?si=o2t1oel43HMoVfUJ",
        "description_ar": "قارن قوتك مع خصمك واختر خطة الفوز",
        "description_en": "Compare your power with your enemy and choose a winning plan"
    },
    "تطوير البداية": {
        "keywords": ["تطوير", "بداية", "ترقية", "احتراق", "حجرة", "develop", "beginning", "upgrade", "burning", "chamber"],
        "video": "https://youtube.com/watch?v=dZr1L6Y1lMA&feature=shared",
        "description_ar": "تطوير من البداية وترقية حجرة الاحتراق",
        "description_en": "Development from the beginning and upgrading the burning chamber"
    },
    "تعبئة التحالف": {
        "keywords": ["تعبئة", "تحالف", "نقاط", "alliance", "mobilization", "points"],
        "video": "https://youtu.be/YtjHkbf18WE?si=XVZV237cyPwnvrpK",
        "description_ar": "تعبئة التحالف",
        "description_en": "Alliance mobilization"
    },
    "تعبئة سريعة": {
        "keywords": ["5000", "نقطة", "5", "دقائق", "سريع", "points", "minutes", "quick"],
        "video": "https://youtu.be/AKWYbag0gjM",
        "description_ar": "تعبئة التحالف 5000 نقطة في 5 دقائق",
        "description_en": "Alliance mobilization 5000 points in 5 minutes"
    },
    "رفع القوة": {
        "keywords": ["رفع", "قوة", "15", "مليون", "دقائق", "رفعت", "raise", "power", "million", "minutes"],
        "video": "https://youtu.be/U42r_SfteG4",
        "description_ar": "رفعت قوة 15 مليون في دقائق",
        "description_en": "Raised 15 million power in minutes"
    },
    "رفع العتاد": {
        "keywords": ["رفع", "عتاد", "مجانا", "مجاني", "raise", "gear", "free"],
        "video": "https://youtu.be/8MN62xqnfTc?si=pZUa0lZnY186IcFb",
        "description_ar": "رفع العتاد مجاناً",
        "description_en": "Upgrade gear for free"
    },
    "كوخ الحظ": {
        "keywords": ["كوخ", "حظ", "ميا", "لميا", "hut", "luck"],
        "video": "https://youtu.be/DvaTHiEFP1A?si=PfRtj9duuQ-mPvrK",
        "description_ar": "كوخ الحظ لميا",
        "description_en": "Lemya's luck hut"
    },
    "ترقية أسبوعية": {
        "keywords": ["ارفع", "عتاد", "أسبوع", "اسبوعي", "كل", "upgrade", "gear", "week", "weekly"],
        "video": "https://youtu.be/Lo7LPRW5ync",
        "description_ar": "ارفع عتادك كل أسبوع",
        "description_en": "Upgrade your gear every week"
    },
    "المتاهة": {
        "keywords": ["متاهة", "لعبة", "maze", "game"],
        "video": "https://youtu.be/3PLBvj0voNg",
        "description_ar": "المتاهة",
        "description_en": "The maze"
    },
    "ثقرة البلية": {
        "keywords": ["ثقرة", "بلية", "ثقب", "hole", "marble"],
        "video": "https://youtu.be/3F3ZH6iHFDc",
        "description_ar": "ثقرة البلية - النجاة في الصقيع",
        "description_en": "Marble hole - Whiteout Survival"
    },
    "سرعة البناء": {
        "keywords": ["سرعة", "بناء", "70%", "70", "speed", "building"],
        "video": "https://youtu.be/9RKHMDharRs?si=3tjnl7xv55rXFrl5",
        "description_ar": "سرعة البناء 70%",
        "description_en": "Building speed 70%"
    },
    "مهارات الحيوان": {
        "keywords": ["تطوير", "مهارات", "حيوان", "develop", "skills", "animal"],
        "video": "https://youtu.be/yMdMuZE5YwI",
        "description_ar": "تطوير مهارات الحيوان",
        "description_en": "Developing animal skills"
    }
}

def get_user_language(user_id):
    """الحصول على لغة المستخدم أو الافتراضي العربية"""
    return user_languages.get(user_id, "ar")

def get_text(user_id, key):
    """الحصول على النص بلغة المستخدم"""
    lang = get_user_language(user_id)
    return TEXTS[lang].get(key, TEXTS["ar"].get(key, ""))

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق من الاشتراك في القنوات المطلوبة"""
    user_id = update.effective_user.id

    try:
        # التحقق من قناة التلجرام فقط (قناة يوتيوب لا يمكن التحقق منها برمجياً)
        member = await context.bot.get_chat_member(chat_id="@Survival_thefrost", user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception as e:
        logger.warning(f"خطأ في التحقق من الاشتراك: {e}")
        # في حالة الخطأ، نعتبر المستخدم غير مشترك
        return False

def find_youtube_video(message_text):
    """البحث عن فيديو يوتيوب مناسب بناءً على النص"""
    message_lower = message_text.lower()

    for topic, data in YOUTUBE_VIDEOS.items():
        for keyword in data["keywords"]:
            if keyword in message_lower:
                return data
    return None

async def send_language_selection(update: Update):
    """إرسال رسالة اختيار اللغة"""
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    language_text = "🌍 **Choose Your Language | اختر لغتك**\n\n🔤 Please select your preferred language:\n🔤 يرجى اختيار لغتك المفضلة:"

    await update.message.reply_text(
        language_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def send_subscription_message(update: Update, user_id):
    """إرسال رسالة طلب الاشتراك الإجباري"""
    keyboard = []

    # إضافة أزرار الاشتراك
    for channel in REQUIRED_CHANNELS:
        keyboard.append([InlineKeyboardButton(
            f"🔗 {get_text(user_id, 'youtube_channel') if 'youtube' in channel['link'] else get_text(user_id, 'telegram_channel')}", 
            url=channel['link']
        )])

    # زر التحقق من الاشتراك
    keyboard.append([InlineKeyboardButton(get_text(user_id, "check_subscription"), callback_data="check_sub")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        get_text(user_id, "subscription_required"), 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار التفاعلية"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "lang_ar":
        user_languages[user_id] = "ar"
        # التحقق من الاشتراك بعد اختيار اللغة
        is_subscribed = await check_subscription(update, context)
        if not is_subscribed:
            await send_subscription_message_callback(query, user_id)
        else:
            await show_main_menu(query, user_id)
            
    elif query.data == "lang_en":
        user_languages[user_id] = "en"
        # التحقق من الاشتراك بعد اختيار اللغة
        is_subscribed = await check_subscription(update, context)
        if not is_subscribed:
            await send_subscription_message_callback(query, user_id)
        else:
            await show_main_menu(query, user_id)

    elif query.data == "check_sub":
        is_subscribed = await check_subscription(update, context)

        if is_subscribed:
            # أزرار البداية بعد التحقق من الاشتراك
            keyboard = [
                [InlineKeyboardButton(get_text(user_id, "start_now"), callback_data="start_bot")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                get_text(user_id, "subscription_verified"),
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton(get_text(user_id, "youtube_channel"), url="https://youtube.com/@whiteoutsurvivel?si=uYvtRgnm1UAZgnyk")],
                [InlineKeyboardButton(get_text(user_id, "telegram_channel"), url="https://t.me/Survival_thefrost")],
                [InlineKeyboardButton(get_text(user_id, "try_again"), callback_data="check_sub")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                get_text(user_id, "subscription_failed"),
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

    elif query.data == "start_bot":
        await show_main_menu(query, user_id)

    elif query.data == "compare":
        await show_power_comparison(query, user_id)

    elif query.data == "help":
        await show_game_guide(query, user_id)

    elif query.data == "info":
        await show_bot_info(query, user_id)

    elif query.data == "change_lang":
        await show_language_selection(query)

async def send_subscription_message_callback(query, user_id):
    """إرسال رسالة الاشتراك عبر callback"""
    keyboard = []

    # إضافة أزرار الاشتراك
    for channel in REQUIRED_CHANNELS:
        keyboard.append([InlineKeyboardButton(
            f"🔗 {get_text(user_id, 'youtube_channel') if 'youtube' in channel['link'] else get_text(user_id, 'telegram_channel')}", 
            url=channel['link']
        )])

    # زر التحقق من الاشتراك
    keyboard.append([InlineKeyboardButton(get_text(user_id, "check_subscription"), callback_data="check_sub")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        get_text(user_id, "subscription_required"), 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_language_selection(query):
    """عرض اختيار اللغة"""
    keyboard = [
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🌍 **Choose Your Language | اختر لغتك**\n\n🔤 Please select your preferred language:\n🔤 يرجى اختيار لغتك المفضلة:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_main_menu(query, user_id):
    """عرض القائمة الرئيسية"""
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "power_comparison"), callback_data="compare")],
        [InlineKeyboardButton(get_text(user_id, "game_guide"), callback_data="help")],
        [InlineKeyboardButton(get_text(user_id, "bot_info"), callback_data="info")],
        [InlineKeyboardButton(get_text(user_id, "change_language"), callback_data="change_lang")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        get_text(user_id, "welcome_message"),
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_power_comparison(query, user_id):
    """عرض صفحة مقارنة القوات"""
    lang = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🌐 " + ("موقع المقارنة" if lang == "ar" else "Comparison Site"), url="https://abukhat.github.io/whiteout/")],
        [InlineKeyboardButton("🎥 " + ("فيديو المقارنة" if lang == "ar" else "Comparison Video"), url="https://youtube.com/shorts/lechAM-Walg?si=o2t1oel43HMoVfUJ")],
        [InlineKeyboardButton("📺 " + ("قناة يوتيوب" if lang == "ar" else "YouTube Channel"), url="https://www.youtube.com/@whiteoutsurvivel")],
        [InlineKeyboardButton("💬 " + ("قناة تلجرام" if lang == "ar" else "Telegram Channel"), url="https://t.me/Survival_thefrost")],
        [InlineKeyboardButton(get_text(user_id, "back_to_menu"), callback_data="start_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if lang == "ar":
        response = (
            "⚔️ **مقارنة القوات - النجاة في الصقيع**\n\n"
            "🎯 **موقع المقارنة التفصيلية:**\n"
            "🔗 https://abukhat.github.io/whiteout/\n\n"
            "📊 **مقارنة شاملة تشمل:**\n"
            "• 🏹 قوة الأبطال والمهارات\n"
            "• 🛡️ العتاد والتمائم\n"
            "• 🏰 المباني والدفاعات\n"
            "• 🐺 مهارات الحيوانات\n\n"
            "💡 **نصيحة:** استخدم الموقع لمقارنة قوتك\n"
            "🎬 **شاهد فيديو المقارنة**"
        )
    else:
        response = (
            "⚔️ **Power Comparison - Whiteout Survival**\n\n"
            "🎯 **Detailed Comparison Site:**\n"
            "🔗 https://abukhat.github.io/whiteout/\n\n"
            "📊 **Complete comparison includes:**\n"
            "• 🏹 Heroes power & skills\n"
            "• 🛡️ Gear & amulets\n"
            "• 🏰 Buildings & defenses\n"
            "• 🐺 Animal skills\n\n"
            "💡 **Tip:** Use the site to compare your power\n"
            "🎬 **Watch comparison video**"
        )
        
    await query.edit_message_text(
        response, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_game_guide(query, user_id):
    """عرض دليل اللعبة"""
    lang = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🏠 " + ("تطوير من البداية" if lang == "ar" else "Development Guide"), url="https://youtube.com/watch?v=dZr1L6Y1lMA&feature=shared"),
         InlineKeyboardButton("⚔️ " + ("الأبطال القوية" if lang == "ar" else "Strong Heroes"), url="https://youtu.be/teywq6pO7fQ?si=a72pPpBrkukVyyIQ")],
        [InlineKeyboardButton("💎 " + ("جمع الكريستال" if lang == "ar" else "Crystal Collection"), url="https://youtube.com/shorts/iK5n1fwuzKs?si=PZlrBYBA5PjkUrBO"),
         InlineKeyboardButton("🛡️ " + ("رفع العتاد" if lang == "ar" else "Gear Upgrade"), url="https://youtu.be/8MN62xqnfTc?si=pZUa0lZnY186IcFb")],
        [InlineKeyboardButton("🎰 " + ("عجلة الحظ" if lang == "ar" else "Lucky Wheel"), url="https://youtu.be/J5gJakTD94Y?si=bNqf6EUN0IuARjoo"),
         InlineKeyboardButton("⚒️ " + ("مسبك الأسلحة" if lang == "ar" else "Weapons Foundry"), url="https://youtu.be/9xGzuOhInj8?si=kRttVkOmZ0Rci1G4")],
        [InlineKeyboardButton("🗺️ " + ("صائد الكنوز" if lang == "ar" else "Treasure Hunter"), url="https://youtu.be/9Y7RAP4w0wU?si=leQL6QXlnRQYH9t-"),
         InlineKeyboardButton("🐺 " + ("التمائم والحيوان" if lang == "ar" else "Amulets & Animals"), url="https://youtu.be/dC3SfhT6dd4?si=4Y_gT7Jdb5o9JqhA")],
        [InlineKeyboardButton("📺 " + ("القناة كاملة" if lang == "ar" else "Full Channel"), url="https://www.youtube.com/@whiteoutsurvivel")],
        [InlineKeyboardButton(get_text(user_id, "back_to_menu"), callback_data="start_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if lang == "ar":
        help_text = (
            "📚 **الدليل الشامل - النجاة في الصقيع**\n\n"
            "🔥 **أساسيات اللعبة:**\n"
            "• 🏠 البناء وتطوير القاعدة\n"
            "• ⚔️ تدريب الأبطال والجيوش\n"
            "• 🛡️ الدفاع ضد الأعداء\n"
            "• 🤝 الانضمام للتحالفات\n\n"
            "💡 **نصائح متقدمة:**\n"
            "• 💎 جمع الكريستال مجاناً\n"
            "• 🔧 ترقية العتاد بذكاء\n"
            "• 🎯 اختيار الأبطال الأقوى\n"
            "• 🏹 استراتيجيات القتال المتقدمة\n\n"
            "🎬 **جميع الشروحات متاحة (18 فيديو):**\n"
            "استخدم الأزرار أدناه للوصول لكل شرح بالتفصيل\n\n"
            "❓ **اسأل عن أي موضوع**"
        )
    else:
        help_text = (
            "📚 **Complete Guide - Whiteout Survival**\n\n"
            "🔥 **Game Basics:**\n"
            "• 🏠 Base Building & Development\n"
            "• ⚔️ Heroes & Army Training\n"
            "• 🛡️ Defense Against Enemies\n"
            "• 🤝 Alliance Systems\n\n"
            "💡 **Advanced Tips:**\n"
            "• 💎 Free Crystal Collection\n"
            "• 🔧 Smart Gear Upgrades\n"
            "• 🎯 Selecting Best Heroes\n"
            "• 🏹 Advanced Battle Strategies\n\n"
            "🎬 **All Tutorials Available (18 Videos):**\n"
            "Use buttons below to access each detailed tutorial\n\n"
            "❓ **Ask about anything**"
        )
        
    await query.edit_message_text(
        help_text, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_bot_info(query, user_id):
    """عرض معلومات البوت"""
    lang = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🌐 " + ("الموقع الرسمي" if lang == "ar" else "Official Site"), url="https://abukhat.github.io/whiteout/")],
        [InlineKeyboardButton("📺 " + ("قناة يوتيوب" if lang == "ar" else "YouTube Channel"), url="https://www.youtube.com/@whiteoutsurvivel")],
        [InlineKeyboardButton("💬 " + ("قناة تلجرام" if lang == "ar" else "Telegram Channel"), url="https://t.me/Survival_thefrost")],
        [InlineKeyboardButton(get_text(user_id, "back_to_menu"), callback_data="start_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    user_name = query.from_user.first_name

    if lang == "ar":
        info_text = (
            "ℹ️ **معلومات البوت**\n\n"
            "🤖 **الاسم:** بوت النجاة في الصقيع الشامل\n"
            "📅 **الإصدار:** 4.0 المطور\n"
            "🔧 **المطور:** @fulldesigne\n"
            "🌍 **اللغات:** العربية + English\n\n"
            "⚡ **الميزات:**\n"
            "• 🔒 اشتراك إجباري محمي\n"
            "• 🎥 قاعدة فيديوهات ضخمة (18 فيديو)\n"
            "• 🤖 ردود ذكية تلقائية\n"
            "• ⚔️ مقارنة القوات المتقدمة\n"
            "• 📚 شروحات شاملة\n"
            "• 🌐 دعم متعدد اللغات\n\n"
            f"📊 **إحصائياتك:**\n"
            f"• 🆔 معرف المستخدم: `{user_id}`\n"
            f"• 👤 الاسم: {user_name}\n"
            f"• ✅ حالة الاشتراك: مؤكد\n\n"
            "🔄 **البوت يعمل 24/7**"
        )
    else:
        info_text = (
            "ℹ️ **Bot Information**\n\n"
            "🤖 **Name:** Complete Whiteout Survival Bot\n"
            "📅 **Version:** 4.0 Advanced\n"
            "🔧 **Developer:** @fulldesigne\n"
            "🌍 **Languages:** العربية + English\n\n"
            "⚡ **Features:**\n"
            "• 🔒 Protected Subscription System\n"
            "• 🎥 Huge Video Database (18 Videos)\n"
            "• 🤖 Smart Auto Responses\n"
            "• ⚔️ Advanced Power Comparison\n"
            "• 📚 Complete Tutorials\n"
            "• 🌐 Multi-language Support\n\n"
            f"📊 **Your Stats:**\n"
            f"• 🆔 User ID: `{user_id}`\n"
            f"• 👤 Name: {user_name}\n"
            f"• ✅ Subscription: Confirmed\n\n"
            "🔄 **Bot works 24/7**"
        )
        
    await query.edit_message_text(
        info_text, 
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start - يبدأ باختيار اللغة"""
    try:
        user_id = update.effective_user.id
        
        # إذا لم يتم اختيار اللغة من قبل، عرض خيارات اللغة
        if user_id not in user_languages:
            await send_language_selection(update)
            return

        # إذا تم اختيار اللغة، التحقق من الاشتراك
        is_subscribed = await check_subscription(update, context)

        if not is_subscribed:
            await send_subscription_message(update, user_id)
            return

        # إذا كان مشترك، عرض القائمة الرئيسية
        keyboard = [
            [InlineKeyboardButton(get_text(user_id, "power_comparison"), callback_data="compare")],
            [InlineKeyboardButton(get_text(user_id, "game_guide"), callback_data="help")],
            [InlineKeyboardButton(get_text(user_id, "bot_info"), callback_data="info")],
            [InlineKeyboardButton(get_text(user_id, "change_language"), callback_data="change_lang")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            get_text(user_id, "welcome_message"),
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        logger.info(f"المستخدم {update.effective_user.first_name} بدأ المحادثة")
    except Exception as e:
        logger.error(f"خطأ في أمر start: {e}")

async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /compare - مقارنة القوات"""
    try:
        user_id = update.effective_user.id
        
        # التحقق من اختيار اللغة
        if user_id not in user_languages:
            await send_language_selection(update)
            return
            
        # التحقق من الاشتراك
        is_subscribed = await check_subscription(update, context)

        if not is_subscribed:
            await send_subscription_message(update, user_id)
            return

        lang = get_user_language(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🌐 " + ("موقع المقارنة" if lang == "ar" else "Comparison Site"), url="https://abukhat.github.io/whiteout/")],
            [InlineKeyboardButton("🎥 " + ("فيديو المقارنة" if lang == "ar" else "Comparison Video"), url="https://youtube.com/shorts/lechAM-Walg?si=o2t1oel43HMoVfUJ")],
            [InlineKeyboardButton("📺 " + ("قناة يوتيوب" if lang == "ar" else "YouTube Channel"), url="https://www.youtube.com/@whiteoutsurvivel")],
            [InlineKeyboardButton("💬 " + ("قناة تلجرام" if lang == "ar" else "Telegram Channel"), url="https://t.me/Survival_thefrost")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if lang == "ar":
            response = (
                "⚔️ **مقارنة القوات - النجاة في الصقيع**\n\n"
                "🎯 **موقع المقارنة التفصيلية:**\n"
                "🔗 https://abukhat.github.io/whiteout/\n\n"
                "📊 **مقارنة شاملة تشمل:**\n"
                "• 🏹 قوة الأبطال والمهارات\n"
                "• 🛡️ العتاد والتمائم\n"
                "• 🏰 المباني والدفاعات\n"
                "• 🐺 مهارات الحيوانات\n\n"
                "💡 **نصيحة:** استخدم الموقع لمقارنة قوتك\n"
                "🎬 **شاهد فيديو المقارنة**\n\n"
                "📞 **للمساعدة:** /help"
            )
        else:
            response = (
                "⚔️ **Power Comparison - Whiteout Survival**\n\n"
                "🎯 **Detailed Comparison Site:**\n"
                "🔗 https://abukhat.github.io/whiteout/\n\n"
                "📊 **Complete comparison includes:**\n"
                "• 🏹 Heroes power & skills\n"
                "• 🛡️ Gear & amulets\n"
                "• 🏰 Buildings & defenses\n"
                "• 🐺 Animal skills\n\n"
                "💡 **Tip:** Use the site to compare your power\n"
                "🎬 **Watch comparison video**\n\n"
                "📞 **For Help:** /help"
            )
            
        await update.message.reply_text(
            response, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        logger.info(f"المستخدم {update.effective_user.first_name} طلب المقارنة")
    except Exception as e:
        logger.error(f"خطأ في أمر compare: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /help - شرح شامل للعبة"""
    try:
        user_id = update.effective_user.id
        
        # التحقق من اختيار اللغة
        if user_id not in user_languages:
            await send_language_selection(update)
            return
            
        # التحقق من الاشتراك
        is_subscribed = await check_subscription(update, context)

        if not is_subscribed:
            await send_subscription_message(update, user_id)
            return

        lang = get_user_language(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🏠 " + ("تطوير من البداية" if lang == "ar" else "Development Guide"), url="https://youtube.com/watch?v=dZr1L6Y1lMA&feature=shared")],
            [InlineKeyboardButton("⚔️ " + ("الأبطال القوية" if lang == "ar" else "Strong Heroes"), url="https://youtu.be/teywq6pO7fQ?si=a72pPpBrkukVyyIQ")],
            [InlineKeyboardButton("💎 " + ("جمع الكريستال" if lang == "ar" else "Crystal Collection"), url="https://youtube.com/shorts/iK5n1fwuzKs?si=PZlrBYBA5PjkUrBO")],
            [InlineKeyboardButton("🛡️ " + ("رفع العتاد" if lang == "ar" else "Gear Upgrade"), url="https://youtu.be/8MN62xqnfTc?si=pZUa0lZnY186IcFb")],
            [InlineKeyboardButton("📺 " + ("قناة يوتيوب" if lang == "ar" else "YouTube Channel"), url="https://www.youtube.com/@whiteoutsurvivel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if lang == "ar":
            help_text = (
                "📚 **الدليل الشامل - النجاة في الصقيع**\n\n"
                "🔥 **أساسيات اللعبة:**\n"
                "• 🏠 البناء وتطوير القاعدة\n"
                "• ⚔️ تدريب الأبطال والجيوش\n"
                "• 🛡️ الدفاع ضد الأعداء\n"
                "• 🤝 الانضمام للتحالفات\n\n"
                "💡 **نصائح متقدمة:**\n"
                "• 💎 جمع الكريستال مجاناً\n"
                "• 🔧 ترقية العتاد بذكاء\n"
                "• 🎯 اختيار الأبطال الأقوى\n"
                "• 🏹 استراتيجيات القتال\n\n"
                "🎬 **فيديوهات مفيدة:**\n"
                "استخدم الأزرار أدناه للوصول للشروحات\n\n"
                "❓ **اسأل عن أي موضوع:** أرسل رسالة وسأجد الفيديو المناسب!"
            )
        else:
            help_text = (
                "📚 **Complete Guide - Whiteout Survival**\n\n"
                "🔥 **Game Basics:**\n"
                "• 🏠 Base Building & Development\n"
                "• ⚔️ Heroes & Army Training\n"
                "• 🛡️ Defense Against Enemies\n"
                "• 🤝 Alliance Systems\n\n"
                "💡 **Advanced Tips:**\n"
                "• 💎 Free Crystal Collection\n"
                "• 🔧 Smart Gear Upgrade\n"
                "• 🎯 Selecting Best Heroes\n"
                "• 🏹 Battle Strategies\n\n"
                "🎬 **Useful Videos:**\n"
                "Use buttons below to access tutorials\n\n"
                "❓ **Ask anything:** Send a message and I'll find the right video!"
            )
            
        await update.message.reply_text(
            help_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"خطأ في أمر help: {e}")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /info - معلومات البوت"""
    try:
        user_id = update.effective_user.id
        
        # التحقق من اختيار اللغة
        if user_id not in user_languages:
            await send_language_selection(update)
            return
            
        # التحقق من الاشتراك
        is_subscribed = await check_subscription(update, context)

        if not is_subscribed:
            await send_subscription_message(update, user_id)
            return

        lang = get_user_language(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🌐 " + ("الموقع الرسمي" if lang == "ar" else "Official Site"), url="https://abukhat.github.io/whiteout/")],
            [InlineKeyboardButton("📺 " + ("قناة يوتيوب" if lang == "ar" else "YouTube Channel"), url="https://www.youtube.com/@whiteoutsurvivel")],
            [InlineKeyboardButton("💬 " + ("قناة تلجرام" if lang == "ar" else "Telegram Channel"), url="https://t.me/Survival_thefrost")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if lang == "ar":
            info_text = (
                "ℹ️ **معلومات البوت**\n\n"
                "🤖 **الاسم:** بوت النجاة في الصقيع الشامل\n"
                "📅 **الإصدار:** 4.0 المطور\n"
                "🔧 **المطور:** @fulldesigne\n"
                "🌍 **اللغات:** العربية + English\n\n"
                "⚡ **الميزات:**\n"
                "• 🔒 اشتراك إجباري محمي\n"
                "• 🎥 قاعدة فيديوهات ضخمة\n"
                "• 🤖 ردود ذكية تلقائية\n"
                "• ⚔️ مقارنة القوات المتقدمة\n"
                "• 📚 شروحات شاملة\n"
                "• 🌐 دعم متعدد اللغات\n\n"
                f"📊 **إحصائياتك:**\n"
                f"• 🆔 معرف المستخدم: `{user_id}`\n"
                f"• 👤 الاسم: {update.effective_user.first_name}\n"
                f"• ✅ حالة الاشتراك: مؤكد\n\n"
                "🔄 **البوت يعمل 24/7**"
            )
        else:
            info_text = (
                "ℹ️ **Bot Information**\n\n"
                "🤖 **Name:** Complete Whiteout Survival Bot\n"
                "📅 **Version:** 4.0 Advanced\n"
                "🔧 **Developer:** @fulldesigne\n"
                "🌍 **Languages:** العربية + English\n\n"
                "⚡ **Features:**\n"
                "• 🔒 Protected Subscription System\n"
                "• 🎥 Huge Video Database\n"
                "• 🤖 Smart Auto Responses\n"
                "• ⚔️ Advanced Power Comparison\n"
                "• 📚 Complete Tutorials\n"
                "• 🌐 Multi-language Support\n\n"
                f"📊 **Your Stats:**\n"
                f"• 🆔 User ID: `{user_id}`\n"
                f"• 👤 Name: {update.effective_user.first_name}\n"
                f"• ✅ Subscription: Confirmed\n\n"
                "🔄 **Bot works 24/7**"
            )
            
        await update.message.reply_text(
            info_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"خطأ في أمر info: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل العادية مع دعم اللغتين"""
    try:
        user_id = update.effective_user.id
        
        # التحقق من اختيار اللغة
        if user_id not in user_languages:
            await send_language_selection(update)
            return
            
        # التحقق من الاشتراك
        is_subscribed = await check_subscription(update, context)

        if not is_subscribed:
            await send_subscription_message(update, user_id)
            return

        user_message = update.message.text.lower()
        lang = get_user_language(user_id)

        # البحث عن فيديو يوتيوب مناسب
        youtube_result = find_youtube_video(user_message)

        if youtube_result:
            keyboard = [
                [InlineKeyboardButton("🎥 " + ("شاهد الفيديو" if lang == "ar" else "Watch Video"), url=youtube_result["video"])],
                [InlineKeyboardButton("📺 " + ("القناة كاملة" if lang == "ar" else "Full Channel"), url="https://www.youtube.com/@whiteoutsurvivel")],
                [InlineKeyboardButton("💬 " + ("قناة تلجرام" if lang == "ar" else "Telegram Channel"), url="https://t.me/Survival_thefrost")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            description = youtube_result.get(f"description_{lang}", youtube_result.get("description_ar", ""))
            
            if lang == "ar":
                response = (
                    f"🎯 **وجدت الإجابة!**\n\n"
                    f"📹 **{description}**\n\n"
                    f"🎬 شاهد الشرح المفصل في الفيديو المرفق\n"
                    f"👆 اضغط على 'شاهد الفيديو' أعلاه\n\n"
                    f"💡 **نصيحة:** اشترك في القناة ولا تنس الإعجاب!"
                )
            else:
                response = (
                    f"🎯 **Found the answer!**\n\n"
                    f"📹 **{description}**\n\n"
                    f"🎬 Watch the detailed explanation in attached video\n"
                    f"👆 Click 'Watch Video' above\n\n"
                    f"💡 **Tip:** Subscribe to the channel and like!"
                )
                
            await update.message.reply_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.info(f"تم إرسال فيديو يوتيوب للمستخدم {update.effective_user.first_name}")
            return

        # ردود ذكية حسب اللغة
        greetings_ar = ['مرحبا', 'السلام', 'هلا', 'أهلا', 'هاي']
        greetings_en = ['hello', 'hi', 'hey', 'greetings']
        thanks_ar = ['شكرا', 'شكراً', 'ممتاز', 'رائع']
        thanks_en = ['thanks', 'thank', 'excellent', 'amazing', 'great']

        if any(word in user_message for word in greetings_ar + greetings_en):
            if lang == "ar":
                response = "🌟 أهلاً وسهلاً بك في عالم النجاة في الصقيع! 🧊❄️\nاسأل عن أي شيء في اللعبة وسأساعدك!"
            else:
                response = "🌟 Welcome to the world of Whiteout Survival! 🧊❄️\nAsk me anything about the game and I'll help you!"
                
        elif any(word in user_message for word in thanks_ar + thanks_en):
            if lang == "ar":
                response = "😊 العفو! سعيد جداً لمساعدتك في رحلة النجاة! 🎮❄️"
            else:
                response = "😊 You're welcome! Glad to help you in your survival journey! 🎮❄️"
                
        elif any(word in user_message for word in ['مقارنة', 'قارن', 'قوة', 'compare', 'power']):
            if lang == "ar":
                response = "⚔️ للحصول على مقارنة القوات الشاملة، استخدم /compare"
            else:
                response = "⚔️ For a comprehensive power comparison, use /compare"
                
        elif any(word in user_message for word in ['مساعدة', 'ساعدني', 'شرح', 'help', 'guide']):
            if lang == "ar":
                response = "📚 للحصول على الشرح الكامل، استخدم /help"
            else:
                response = "📚 For a complete guide, use /help"
                
        elif any(word in user_message for word in ['معلومات', 'تفاصيل', 'بوت', 'info', 'details', 'bot']):
            if lang == "ar":
                response = "ℹ️ لمعرفة تفاصيل البوت، استخدم /info"
            else:
                response = "ℹ️ For bot details, use /info"
                
        else:
            keyboard = [
                [InlineKeyboardButton(get_text(user_id, "power_comparison"), callback_data="compare")],
                [InlineKeyboardButton(get_text(user_id, "game_guide"), callback_data="help")],
                [InlineKeyboardButton("🎥 " + ("فيديوهات يوتيوب" if lang == "ar" else "YouTube Videos"), url="https://www.youtube.com/@whiteoutsurvivel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if lang == "ar":
                response = (
                    "💬 شكراً لرسالتك! ❄️\n\n"
                    "🔍 **جرب أن تسأل عن:**\n"
                    "• التمائم والحيوانات 🐺\n"
                    "• عجلة الحظ وتهكيرها 🎰\n"
                    "• مسبك الأسلحة ⚔️\n"
                    "• جمع الكريستال 💎\n"
                    "• رفع العتاد 🛡️\n"
                    "• تعبئة التحالف 🤝\n"
                    "• سرعة البناء 🏗️\n\n"
                    "👇 **أو استخدم الأزرار:**"
                )
            else:
                response = (
                    "💬 Thanks for your message! ❄️\n\n"
                    "🔍 **Try asking about:**\n"
                    "• Amulets & Animals 🐺\n"
                    "• Lucky Wheel & Hacks 🎰\n"
                    "• Weapons Foundry ⚔️\n"
                    "• Crystal Collection 💎\n"
                    "• Gear Upgrade 🛡️\n"
                    "• Alliance Filling 🤝\n"
                    "• Building Speed 🏗️\n\n"
                    "👇 **Or use the buttons:**"
                )
                
            await update.message.reply_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return

        await update.message.reply_text(response)
        logger.info(f"رد على رسالة من {update.effective_user.first_name}")

    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة ترحيب للأعضاء الجدد"""
    try:
        for new_member in update.message.new_chat_members:
            user_id = new_member.id
            
            # إذا لم يتم اختيار اللغة، استخدم الافتراضي
            if user_id not in user_languages:
                lang = "ar"  # افتراضي
            else:
                lang = get_user_language(user_id)

            keyboard = [
                [InlineKeyboardButton("🚀 " + ("ابدأ مع البوت" if lang == "ar" else "Start with Bot"), callback_data="start_bot")],
                [InlineKeyboardButton("📺 " + ("قناة يوتيوب" if lang == "ar" else "YouTube Channel"), url="https://www.youtube.com/@whiteoutsurvivel")],
                [InlineKeyboardButton("🌐 " + ("الموقع الرسمي" if lang == "ar" else "Official Site"), url="https://abukhat.github.io/whiteout/")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if lang == "ar":
                welcome_text = (
                    f"🎉 **مرحباً {new_member.first_name}!**\n\n"
                    f"❄️ أهلاً بك في **قناة النجاة في الصقيع**\n\n"
                    f"📋 **قواعد القناة:**\n"
                    f"• احترم جميع الأعضاء 🤝\n"
                    f"• لا تنشر روابط مشبوهة 🚫\n"
                    f"• استخدم البوت للحصول على المساعدة 🤖\n"
                    f"• شارك خبراتك مع الآخرين 📢\n\n"
                    f"🎮 **أرسل أي سؤال للبوت:**\n"
                    f"💡 مثال: التمائم, العتاد, الكريستال\n\n"
                    f"📺 **لا تنس الاشتراك في يوتيوب للشروحات الحصرية!**"
                )
            else:
                welcome_text = (
                    f"🎉 **Welcome {new_member.first_name}!**\n\n"
                    f"❄️ Welcome to **Whiteout Survival Channel**\n\n"
                    f"📋 **Channel Rules:**\n"
                    f"• Respect all members 🤝\n"
                    f"• No suspicious links 🚫\n"
                    f"• Use the bot for help 🤖\n"
                    f"• Share your experience 📢\n\n"
                    f"🎮 **Ask bot any question:**\n"
                    f"💡 Example: Amulets, Gear, Crystals\n\n"
                    f"📺 **Don't forget to subscribe to YouTube for exclusive tutorials!**"
                )

            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.info(f"رحب بالعضو الجديد: {new_member.first_name}")
    except Exception as e:
        logger.error(f"خطأ في رسالة الترحيب: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام"""
    error_msg = str(context.error)

    # تجاهل أخطاء التضارب المؤقتة
    if "Conflict" in error_msg and "getUpdates" in error_msg:
        logger.warning("تضارب مؤقت في getUpdates - سيتم المتابعة تلقائياً")
        return

    logger.error(f"حدث خطأ: {context.error}")

    if update and update.effective_message:
        try:
            user_id = update.effective_user.id
            lang = get_user_language(user_id)
            
            if lang == "ar":
                error_text = (
                    "⚠️ حدث خطأ مؤقت. يرجى المحاولة مرة أخرى.\n"
                    "🔄 إذا استمر الخطأ، استخدم /start للإعادة التشغيل."
                )
            else:
                error_text = (
                    "⚠️ A temporary error occurred. Please try again.\n"
                    "🔄 If the error persists, use /start to restart."
                )
                
            await update.effective_message.reply_text(error_text)
        except:
            pass

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    # الحصول على التوكن من متغيرات البيئة
    TOKEN = "7780237024:AAFDPz7eqZO2GqgNsBxEwCJt82JGIZQWFXU"

    if not TOKEN:
        logger.error("لم يتم العثور على TOKEN في متغيرات البيئة!")
        print("❌ خطأ: يرجى إضافة TOKEN في Secrets")
        print("💡 اذهب إلى Tools > Secrets وأضف:")
        print("   Key: TOKEN")
        print("   Value: توكن البوت الخاص بك")
        return

    try:
        # تفعيل خادم Flask للحفاظ على البوت نشطاً 24/7
        keep_alive()
        
        # إنشاء التطبيق
        application = Application.builder().token(TOKEN).build()

        # إضافة معالجات الأوامر
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("compare", compare))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("info", info_command))

        # معالج الأعضاء الجدد
        from telegram.ext import MessageHandler
        application.add_handler(MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS, 
            welcome_new_member
        ))

        # إضافة معالج الأزرار التفاعلية
        from telegram.ext import CallbackQueryHandler
        application.add_handler(CallbackQueryHandler(handle_callback))

        # إضافة معالج الرسائل العادية
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # إضافة معالج الأخطاء
        application.add_error_handler(error_handler)

        logger.info("🚀 تم بدء تشغيل البوت بنجاح...")
        logger.info("🚀 Bot started successfully...")
        print("✅ البوت المحدث مع دعم اللغتين يعمل الآن!")
        print("✅ Updated bot with dual language support is now running!")
        print("🌍 نظام اختيار اللغة مفعل")
        print("🌍 Language selection system activated")
        print("🔒 الاشتراك الإجباري مفعل كأولوية")
        print("🔒 Mandatory subscription is active as a priority")
        print("📺 قاعدة فيديوهات يوتيوب محدثة بالكامل")
        print("📺 YouTube videos database fully updated")
        print("⚔️ أوامر محسنة: /start /compare /help /info")
        print("⚔️ Improved commands: /start /compare /help /info")
        print("🎯 ردود ذكية متطورة بدعم اللغتين")
        print("🎯 Advanced smart responses with dual language support")
        print("🔄 البوت جاهز لاستقبال المستخدمين 24/7")
        print("🔄 Bot is ready to receive users 24/7")

        # تشغيل البوت مع معالجة التضارب
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            close_loop=False
        )

    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == "__main__":
    main()
    
