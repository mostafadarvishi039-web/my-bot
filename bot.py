import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)

# 📌 لینک‌های تست رایگان
SUBSCRIPTION_POOL = [
    "https://194.5.175.226:2096/sub/93ovrn26eymmn72o",
    "https://panel.vip.veraxideas.ir:2096/sub/3rn4vx5s8ekhhlu3"
]

# ⚠️ شناسه تلگرام خودت برای دریافت رسیدها
ADMIN_CHAT_ID = 7357227534

# دیکشنری موقت برای بررسی اینکه کدام کاربر در حال ارسال رسید است
WAITING_FOR_RECEIPT = set()

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
    
    user_id = query.from_user.id
    
    if query.data == "get_test":
        if len(SUBSCRIPTION_POOL) > 0:
            assigned_sub = random.choice(SUBSCRIPTION_POOL)
            
            await query.edit_message_text(
                f"✅ **اشتراک تست شما با موفقیت آماده شد!**\n\n"
                f"🔗 **لینک سابسکریپشن شما:**\n`{assigned_sub}`\n\n"
                f"📥 این لینک را کپی کرده و در برنامه (مثل V2rayNG) وارد کنید. 🚀",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text("❌ فعلاً لینک تستی در انبار موجود نیست!")
            
    elif query.data == "buy_sub":
        WAITING_FOR_RECEIPT.add(user_id)
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back_to_home")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🛒 **خرید اشتراک پرسرعت:**\n\n"
            "لطفاً مبلغ مورد نظر را واریز کرده و **اسکرین‌شات رسید پرداخت** را همینجا برای ربات ارسال کنید تا پس از بررسی، اشتراک اختصاصی برایتان ارسال شود. 💳",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    elif query.data == "my_account":
        await query.edit_message_text("👤 شما در حال حاضر یک اشتراک تست فعال دارید.")
        
    elif query.data == "back_to_home":
        if user_id in WAITING_FOR_RECEIPT:
            WAITING_FOR_RECEIPT.remove(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🎁 دریافت تست رایگان", callback_data="get_test")],
            [InlineKeyboardButton("🛒 خرید اشتراک", callback_data="buy_sub")],
            [InlineKeyboardButton("⚙️ اکانت‌های من", callback_data="my_account")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "سلام مجدد! از دکمه‌های زیر استفاده کنید:",
            reply_markup=reply_markup
        )

# دریافت رسید و ارسال آن به ادمین
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            print("Error sending to admin:", e)
            await update.message.reply_text("❌ خطا در ارسال رسید به ادمین. لطفاً مستقیماً به ادمین پیام دهید: @matinejlali_official")
            
        WAITING_FOR_RECEIPT.remove(user_id)
    else:
        await update.message.reply_text("برای شروع از دستور /start استفاده کنید.")

if __name__ == '__main__':
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_message))
    
    app.run_polling()
