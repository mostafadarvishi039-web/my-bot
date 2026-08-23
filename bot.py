import os
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)

print("BOT IS STARTING UP...")

# 📌 لینک‌های تست رایگان
SUBSCRIPTION_POOL = [
    "https://194.5.175.226:2096/sub/93ovrn26eymmn72o",
    "https://panel.vip.veraxideas.ir:2096/sub/3rn4vx5s8ekhhlu3"
]

# ⚠️ شناسه تلگرام خودت برای دریافت رسیدها
ADMIN_CHAT_ID = 7357227534

WAITING_FOR_RECEIPT = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🎁 دریافت تست رایگان"), KeyboardButton("🛒 خرید اشتراک")],
        [KeyboardButton("⚙️ اکانت‌های من")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "سلام به ربات رسمی **Verax VPN** خوش آمدید! ⚡️\n\n"
        "از دکمه‌های زیر برای دریافت تست رایگان یا خرید اشتراک استفاده کنید:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    user_id = user.id
    
    if user_id in WAITING_FOR_RECEIPT and update.message.photo:
        photo_file = update.message.photo[-1].file_id
        
        caption = (
            f"🔔 **رسید جدید از طرف خریدار!**\n\n"
            f"👤 نام: {user.full_name}\n"
            f"آیدی: `@{user.username}`\n"
            f"🆔 یوزر‌دی: `{user_id}`"
        )
        
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photo_file,
                caption=caption,
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                "✅ **رسید شما با موفقیت به ادمین ارسال شد!**\n\n"
                "به زودی پس از بررسی، اشتراک اختصاصی برایتان ارسال خواهد شد. 🙏"
            )
        except Exception as e:
            print("Error:", e)
            await update.message.reply_text("❌ خطا در ارسال رسید. لطفاً مستقیم به ادمین پیام دهید: @matinejlali_official")
            
        WAITING_FOR_RECEIPT.remove(user_id)
        return

    if text == "🎁 دریافت تست رایگان":
        if len(SUBSCRIPTION_POOL) > 0:
            assigned_sub = random.choice(SUBSCRIPTION_POOL)
            await update.message.reply_text(
                f"✅ **اشتراک تست شما با موفقیت آماده شد!**\n\n"
                f"🔗 **لینک سابسکریپشن شما:**\n`{assigned_sub}`\n\n"
                f"📥 این لینک را کپی کرده و در برنامه (مثل V2rayNG) وارد کنید. 🚀",
                parse_Mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ فعلاً لینک تستی در انبار موجود نیست!")
            
    elif text == "🛒 خرید اشتراک":
        WAITING_FOR_RECEIPT.add(user_id)
        await update.message.reply_text(
            "🛒 **خرید اشتراک پرسرعت:**\n\n"
            "لطفاً مبلغ مورد نظر را واریز کرده و **اسکرین‌شات رسید پرداخت** را همینجا برای ربات ارسال کنید. 💳"
        )
        
    elif text == "⚙️ اکانت‌های من":
        await update.message.reply_text("👤 شما در حال حاضر یک اشتراک تست فعال دارید.")
    
    else:
        await update.message.reply_text("لطفاً از دکمه‌های کیبورد استفاده کنید یا دستور /start را بفرستید.")

if __name__ == '__main__':
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("ERROR: BOT_TOKEN is missing!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    
    print("BOT IS RUNNING AND POLLING...")
    app.run_polling()
