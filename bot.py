import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# لیست لینک‌های سابسکریپشن شما
SUBSCRIPTION_POOL = [
    "https://194.5.175.226:2096/sub/93ovrn26eymmn72o",
    "https://panel.vip.veraxideas.ir:2096/sub/3rn4vx5s8ekhhlu3"
]

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
        if len(SUBSCRIPTION_POOL) > 0:
            # انتخاب یک لینک سابسکریپشن از لیست
            assigned_sub = random.choice(SUBSCRIPTION_POOL)
            
            await query.edit_message_text(
                f"✅ **اشتراک تست شما با موفقیت آماده شد!**\n\n"
                f"🔗 **لینک سابسکریپشن شما:**\n`{assigned_sub}`\n\n"
                f"📥 این لینک را کپی کرده و در برنامه (مثل V2rayNG یا NekoBox) در بخش **Subscription** وارد کنید تا تمام کانفیگ‌ها برایتان آپدیت شوند. 🚀",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text("❌ فعلاً لینک تستی در انبار موجود نیست!")
            
    elif query.data == "buy_sub":
        await query.edit_message_text(
            "🛒 **راهنمای خرید اشتراک:**\n\n"
            "برای خرید اشتراک پرسرعت و اختصاصی، به ادمین پیام دهید:\n"
            "💬 @matinejlali_official",
            parse_mode="Markdown"
        )
    elif query.data == "my_account":
        await query.edit_message_text("👤 شما در حال حاضر یک اشتراک فعال دارید.")

if __name__ == '__main__':
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        exit(1)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
