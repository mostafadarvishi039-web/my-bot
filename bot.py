import os
import requests
import random
import string
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# اطلاعات پنل شما
PANEL_URL = "https://panel.vip.veraxideas.ir:2053/PanelMrMatinVpn"
USERNAME = "Mr.Matin.Panel"
PASSWORD = "@2041390Mm"
INBOUND_ID = 1  # شناسه اینباند (معمولاً 1 است)

# غیرفعال کردنشدن خطاهای مربوط به SSL (برای گواهی‌های خودامضا)
requests.packages.urllib3.disable_warnings()

# تابع برای لاگین و گرفتن کوکی از پنل
def get_panel_session():
    session = requests.Session()
    login_url = f"{PANEL_URL}/login"
    payload = {"username": USERNAME, "password": PASSWORD}
    try:
        response = session.post(login_url, data=payload, verify=False, timeout=10)
        if response.json().get("success"):
            return session
    except Exception as e:
        print("Login Error:", e)
    return None

# تابع ساخت کاربر جدید در پنل 3X-UI
def create_client_in_panel(client_email, total_gb=1, expire_days=1):
    session = get_panel_session()
    if not session:
        return None
    
    # تبدیل حجم به بایت
    total_bytes = int(total_gb * 1024 * 1024 * 1024)
    # محاسبه تاریخ انقضا (به میلی‌ثانیه)
    expiry_time = int(time.time() * 1000) + (expire_days * 24 * 60 * 60 * 1000)
    
    # ساخت UUID رندم برای کلاینت
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
    
    try:
        response = session.post(add_url, data=data, verify=False, timeout=10)
        res_json = response.json()
        if res_json.get("success"):
            return client_id
    except Exception as e:
        print("Add Client Error:", e)
    return None

# منوی اصلی ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎁 دریافت تست رایگان", callback_data="get_test")],
        [InlineKeyboardButton("🛒 خرید اشتراک", callback_data="buy_sub")],
        [InlineKeyboardButton("⚙️ اکانت‌های من", callback_data="my_account")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "سلام به ربات رسمی **Verax VPN** خوش آمدید! ⚡️\n\n"
        "از دکمه‌های زیر می‌توانید برای دریافت تست رایگان یا خرید اشتراک استفاده کنید:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# مدیریت دکمه‌های شیشه‌ای
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "get_test":
        await query.edit_message_text("⏳ در حال ساخت کانفیگ تست رایگان روی سرور...")
        
        user_telegram_id = query.from_user.id
        client_email = f"test_{user_telegram_id}"
        
        # ایجاد اکانت تست (۱ گیگابایت، ۱ روزه)
        client_uuid = create_client_in_panel(client_email, total_gb=1, expire_days=1)
        
        if client_uuid:
            await query.edit_message_text(
                f"✅ **اشتراک تست شما با موفقیت ساخته شد!**\n\n"
                f"👤 نام کاربری: `{client_email}`\n"
                f"🔑 شناسه (UUID): `{client_uuid}`\n\n"
                f"حالا برو تو پنلت چک کن ببین کاربر `{client_email}` اضافه شده یا نه! 🚀",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text("❌ خطا در ارتباط با پنل یا ساخت اکانت. لطفاً دوباره تلاش کنید.")
            
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
