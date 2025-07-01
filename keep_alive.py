
from flask import Flask
from threading import Thread
import logging

# إعداد تسجيل Flask
logging.getLogger('werkzeug').setLevel(logging.WARNING)

app = Flask('')

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Telegram Bot - Whiteout Survival</title>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 50px;">
            <h1>🤖 بوت النجاة في الصقيع نشط</h1>
            <h2>🤖 Whiteout Survival Bot is Active</h2>
            <p>✅ البوت يعمل على مدار 24/7</p>
            <p>✅ Bot is running 24/7</p>
            <p>🔄 آخر تحديث: نشط الآن</p>
            <p>🔄 Last update: Active now</p>
            <br>
            <p>📱 للوصول للبوت على تلجرام ابحث عن اسم البوت</p>
            <p>📱 To access the bot on Telegram, search for the bot name</p>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'bot': 'running', 'message': 'Bot is active 24/7'}

@app.route('/status')
def status():
    return '''
    {
        "status": "online",
        "bot_name": "Whiteout Survival Bot",
        "uptime": "24/7",
        "last_check": "active"
    }
    '''

def run():
    """تشغيل خادم Flask"""
    try:
        print("🌐 بدء تشغيل خادم Flask...")
        print("🌐 Starting Flask server...")
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ خطأ في تشغيل Flask: {e}")

def keep_alive():
    """بدء خادم Flask في خيط منفصل"""
    print("🚀 تفعيل نظام البقاء نشطاً...")
    print("🚀 Activating keep-alive system...")
    
    t = Thread(target=run)
    t.daemon = True
    t.start()
    
    print("✅ خادم Flask جاهز على المنفذ 8080")
    print("✅ Flask server ready on port 8080")
    print("🔗 سيكون الرابط متاحاً قريباً للاستخدام مع Uptime Robot")
    print("🔗 URL will be available soon for use with Uptime Robot")
