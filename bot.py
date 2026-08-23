import os
import requests
import random
import string
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

PANEL_URL = "https://panel.vip.veraxideas.ir:2053"
USERNAME = "Mr.Matin.Panel"
PASSWORD = "@2041390Mm"
INBOUND_ID = 1

requests.packages.urllib3.disable_warnings()

# هدرهای مرورگر برای جلوگیری از مسدود شدن توسط فایروال یا کلادفلر
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def create_client_in_panel(client_email, total_gb=1, expire_days=1):
    session = requests.Session()
    session.headers.update(HEADERS)
    
    login_url = f"{PANEL_URL}/login"
    payload = {"username": USERNAME, "password": PASSWORD}
    
    try:
        login_res = session.post(login_url, data=payload, verify=False, timeout=10)
        
        try:
            res_json = login_res.json()
        except:
            return f"Error: Blocked (Status: {login_res.status_code})"
            
        if not res_json.get("success"):
            return "Login Failed: Wrong Username or Password"
            
        total_bytes = int(total_gb * 1024 * 1024 * 1024)
        expiry_time = int(time.time() * 1000) + (expire_days * 24 * 60 * 60 * 1000)
        client_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + '-' + \
                    ''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) + '-' + \
                    '4' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=3)) + '-' + \
                    '8' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=3)) + '-' + \
                    ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        
        add_url = f"{PANEL_URL}/panel/api/inbounds/addClient"
        data = {
            "id": INBOUND_ID,
            "settings": f"""{{
                "clients": [{{
                    "id": "{client_id}",
                    "alterId": 0,
                    "email": "{client_email}",
                    "limitIp": 2,
                    "totalGB": {total_bytes},
                    "expiryTime": {expiry_time},
                    "enable": true,
                    "flow": "xtls-rprx-vision"
                }}]
            }}"""
        }
        
        add_res = session.post(add_url, data=data, verify=False, timeout=10)
        add_json = add_res.json()
        
        if add_json.get("success"):
            return client_id
        else:
            return f"API Error: {add_json.get('msg', 'Unknown')}"
            
    except Exception as e:
        return f"Exception: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎁 دریافت تست رایگان", callback_data="get_test")],
        [InlineKeyboardButton("🛒 خرید اشتراک", callback_data="buy_sub")],
        [InlineKeyboardButton("⚙️ اکانت‌های من", callback_data="my_account")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام به ربات رسمی **Verax VPN** خوش آمدید! ⚡️",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "get_test":
        await query.edit_message_text("⏳ در حال ارتباط با پنل و ساخت تست...")
        user_telegram_id = query.from_user.id
        client_email = f"test_{user_telegram_id}"
        
        result = create_client_in_panel(client_email)
        
        if len(result) > 30:  # یعنی UUID ساخته شده
            await query.edit_message_text(
                f"✅ **اکانت تست با موفقیت ساخته شد!**\n\n"
                f"👤 ایمیل: `{client_email}`\n"
                f"🔑 UUID: `{result}`\n\n"
                f"الان برو تو پنلت چک کن ببین کاربر اومده یا نه! 🚀",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(f"❌ خطا:\n`{result}`", parse_mode="Markdown")
            
    elif query.data == "buy_sub":
        await query.edit_message_text("🛒 بخش خرید اشتراک به زودی فعال خواهد شد...")

if __name__ == '__main__':
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        exit(1)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
