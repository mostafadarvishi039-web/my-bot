import os
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters, 
    ContextTypes
)

# توکن ربات رو از متغیر محیطی می‌خونه (یا می‌تونی مستقیم جاش بذاری)
TOKEN = os.environ.get("BOT_TOKEN", "توکن_ربات_اینجا")

SUBSCRIPTION_POOL = [
    "https://194.5.175.226:2096/sub/93ovrn26eymmn72o",
    "https://panel.vip.veraxideas.ir:2096/sub/3rn4vx5s8ekhhlu3"
]

ADMIN_CHAT_ID = 7357227534
WAITING_FOR_RECEIPT = set()

# منوی اصلی پایین صفحه (دقیقاً مشابه نمونه‌ای که فرستادی)
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🟢 خرید اشتراک 🔑"), KeyboardButton("♻️ تمدید سرویس")],
        [KeyboardButton("🔑 اکانت تست")],
        [KeyboardButton("🛍️ سرویس‌های من"), KeyboardButton("🏦 کیف پول + شارژ")],
        [KeyboardButton("☎️ پشتیبانی"), KeyboardButton("👥 زیر مجموعه گیری")],
        [KeyboardButton("👨‍💻 پنل مدیریت"), KeyboardButton("💻 درخواست نمایندگی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام به ربات رسمی **Verax VPN** خوش آمدید! ⚡️\n\n"
        "از دکمه‌های زیر برای مدیریت حساب و خرید سرویس استفاده کنید:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    user_id = user.id
    
    # بررسی ارسال رسید توسط کاربر
    if user_id in WAITING_FOR_RECEIPT and update.message.photo:
        photo_file = update.message.photo[-1].file_id
        
        caption = (
            f"🔔 **رسید جدید پرداخت برای بررسی!**\n\n"
            f"👤 نام: {user.full_name}\n"
            f"آیدی: `@{user.username}`\n"
            f"🆔 یوزر‌دی: `{user_id}`"
        )
        
        # دکمه‌های مدیریت زیر رسید برای خودت (ادمین)
        admin_keyboard = [
            [InlineKeyboardButton("✅ تایید پرداخت", callback_data=f"approve_{user_id}"),
             InlineKeyboardButton("❌ رد پرداخت", callback_data=f"reject_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(admin_keyboard)
        
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photo_file,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                "✅ **رسید شما با موفقیت ارسال شد!**\n\n"
                "به زودی پس از تایید ادمین، اشتراک شما فعال خواهد شد. 🙏",
                reply_markup=get_main_keyboard()
            )
        except Exception as e:
            print("Error:", e)
            await update.message.reply_text("❌ خطا در ارسال رسید. لطفاً مستقیم به ادمین پیام دهید.")
            
        WAITING_FOR_RECEIPT.remove(user_id)
        return

    # مدیریت دکمه‌های کیبورد اصلی
    if text == "🔑 اکانت تست":
        if len(SUBSCRIPTION_POOL) > 0:
            assigned_sub = random.choice(SUBSCRIPTION_POOL)
            await update.message.reply_text(
                f"✅ **اشتراک تست شما با موفقیت آماده شد!**\n\n"
                f"🔗 **لینک سابسکریپشن شما:**\n`{assigned_sub}`\n\n"
                f"📥 این لینک را کپی کرده و در برنامه (مثل V2rayNG) وارد کنید. 🚀",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ فعلاً لینک تستی در انبار موجود نیست!")
            
    elif text == "🟢 خرید اشتراک 🔑":
        # شبیه‌سازی پیش‌فاکتور و روش پرداخت مشابه عکس‌های فرستاده شده
        keyboard = [
            [InlineKeyboardButton("💳 کارت به کارت", callback_data="pay_card")],
            [InlineKeyboardButton("✨ Star Telegram", callback_data="pay_star")],
            [InlineKeyboardButton("❌ بستن لیست", callback_data="close_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        invoice_text = (
            "🖨️ **پیش فاکتور شما:**\n"
            f"👤 نام کاربری: `{user.username or user.first_name}`\n"
            "🔒 نام سرویس: ⚙️ سرویس دلخواه\n"
            "📅 مدت اعتبار: ۳۰ روز\n"
            "💶 قیمت: ۱۵۰,۰۰۰ تومان\n"
            "👥 حجم اکانت: ۳۰ گیگ\n"
            "💰 موجودی کیف پول شما: 0\n\n"
            "💰 **موجودی حساب شما کافی نمی باشد یک روش پرداخت از لیست پایین انتخاب نمایید** 📝"
        )
        await update.message.reply_text(invoice_text, reply_markup=reply_markup, parse_mode="Markdown")
        
    elif text == "🛍️ سرویس‌های من":
        await update.message.reply_text("👤 شما در حال حاضر یک اشتراک فعال ۳۰ روزه دارید.")
        
    elif text == "🏦 کیف پول + شارژ":
        await update.message.reply_text("💰 موجودی کیف پول شما: **0 تومان**\n\nبرای افزایش موجودی با ادمین در ارتباط باشید.")
        
    elif text == "☎️ پشتیبانی":
        await update.message.reply_text("💬 برای ارتباط با پشتیبانی و رفع مشکلات به آیدی زیر پیام دهید:\n@matinejlali_official")
        
    elif text == "👥 زیر مجموعه گیری":
        await update.message.reply_text("🔗 لینک زیرمجموعه‌گیری شما:\n`https://t.me/YourBot?start=ref_{}`\n\nبا دعوت دوستان خود هدیه بگیرید!".format(user_id), parse_mode="Markdown")
        
    elif text == "👨‍💻 پنل مدیریت":
        if user_id == ADMIN_CHAT_ID:
            await update.message.reply_text("👑 خوش آمدید ادمین عزیز. پنل مدیریت فعال است.")
        else:
            await update.message.reply_text("❌ شما دسترسی به پنل مدیریت ندارید!")
            
    elif text == "💻 درخواست نمایندگی":
        await update.message.reply_text("💼 برای دریافت پنل نمایندگی و شرایط همکاری، به ادمین پیام دهید.")
        
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید.", reply_markup=get_main_keyboard())

# مدیریت کلیک دکمه‌های شیشه‌ای (پرداخت، کارت به کارت و تایید ادمین)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "pay_card":
        WAITING_FOR_RECEIPT.add(user_id)
        card_info = (
            "برای افزایش موجودی، مبلغ **150,000 تومان** را به شماره‌ی حساب زیر واریز کنید 👇\n\n"
            "=====================\n"
            "<code>5047061673289241</code>\n"
            "مهدی حسینی صفا\n"
            "=====================\n\n"
            "❌ این تراکنش به مدت یک ساعت اعتبار دارد پس از آن امکان پرداخت این تراکنش امکان ندارد.\n"
            "‼️ مبلغ باید همان مبلغی که در بالا ذکر شده واریز نمایید.\n"
            "⬆️ بعد از پرداخت، دکمه پرداخت کردم را زده سپس تصویر رسید را ارسال نمایید."
        )
        await query.edit_message_text(card_info, parse_mode="HTML")
        
    elif data == "pay_star":
        await query.edit_message_text("⭐️ پرداخت با استارز تلگرام به زودی فعال خواهد شد.")
        
    elif data == "close_list":
        await query.edit_message_text("❌ منوی پرداخت بسته شد.")
        
    elif data.startswith("approve_"):
        target_user = data.split("_")[1]
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ **وضعیت: پرداخت تایید شد!**")
        await context.bot.send_message(chat_id=int(target_user), text="✅ پرداخت شما توسط ادمین تایید شد! اشتراک شما فعال گردید. مبارکتون باشه 🚀")
        
    elif data.startswith("reject_"):
        target_user = data.split("_")[1]
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ **وضعیت: پرداخت رد شد!**")
        await context.bot.send_message(chat_id=int(target_user), text="❌ متاسفانه رسید پرداخت شما توسط ادمین تایید نشد. در صورت وجود مشکل به پشتیبانی پیام دهید.")

if __name__ == '__main__':
    if TOKEN == "توکن_ربات_اینجا":
        print("لطفاً توکن ربات را در کد وارد کنید!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    
    print("BOT WITH FULL MENU IS RUNNING...")
    app.run_polling()
