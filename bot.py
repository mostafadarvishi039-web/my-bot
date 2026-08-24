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

# توکن ربات رو اینجا بذار یا از متغیر محیطی بخون
TOKEN = os.environ.get("BOT_TOKEN", "توکن_ربات_اینجا")

ADMIN_CHAT_ID = 7357227534
WAITING_FOR_RECEIPT = set()

# پایگاه داده ساده فرضی برای موجودی کیف پول کاربران (به تومان)
# کلید: user_id، مقدار: موجودی
USER_WALLETS = {}

# اطلاعات کارت
CARD_NUMBER = "6219861956948888"
CARD_HOLDER = "محمد متین اجلالی"
PRICE_TOMAN = 248000
PRICE_RIAL = PRICE_TOMAN * 10  # تبدیل به ریال برای دکمه کپی

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
    
    # اطمینان از اینکه کاربر در دیکشنری کیف پول وجود دارد
    if user_id not in USER_WALLETS:
        USER_WALLETS[user_id] = 0  # پیش‌فرض موجودی صفر
        
    # بررسی ارسال رسید توسط کاربر
    if user_id in WAITING_FOR_RECEIPT and update.message.photo:
        photo_file = update.message.photo[-1].file_id
        
        caption = (
            f"🔔 **رسید جدید پرداخت برای بررسی!**\n\n"
            f"👤 نام: {user.full_name}\n"
            f"آیدی: `@{user.username}`\n"
            f"🆔 یوزر‌دی: `{user_id}`\n"
            f"💵 مبلغ فاکتور: {PRICE_TOMAN:,} تومان"
        )
        
        admin_keyboard = [
            [InlineKeyboardButton("✅ تایید پرداخت و شارژ کیف پول", callback_data=f"approve_{user_id}"),
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
                "به زودی پس از تایید ادمین، کیف پول شما شارژ و سفارش شما انجام خواهد شد. 🙏",
                reply_markup=get_main_keyboard()
            )
        except Exception as e:
            print("Error:", e)
            await update.message.reply_text("❌ خطا در ارسال رسید. لطفاً مستقیم به ادمین پیام دهید.")
            
        WAITING_FOR_RECEIPT.remove(user_id)
        return

    if text == "🟢 خرید اشتراک 🔑":
        # دکمه شیشه‌ای اشتراک یک ماهه نامحدود ۲۴۸ هزار تومانی
        keyboard = [
            [InlineKeyboardButton("اشتراک یک ماهه نامحدود ۲۴۸ هزار تومن 🏷️", callback_data="buy_unlimited_30d")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🛒 لطفاً نوع اشتراک خود را از زیر انتخاب کنید:",
            reply_markup=reply_markup
        )
        
    elif text == "🔑 اکانت تست":
        await update.message.reply_text("🔑 بخش اکانت تست موقتاً در این نسخه غیرفعال است.")
    elif text == "🛍️ سرویس‌های من":
        await update.message.reply_text("👤 شما در حال حاضر اشتراک فعالی ندارید.")
    elif text == "🏦 کیف پول + شارژ":
        wallet_balance = USER_WALLETS.get(user_id, 0)
        await update.message.reply_text(f"💰 موجودی کیف پول شما: **{wallet_balance:,} تومان**", parse_mode="Markdown")
    elif text == "☎️ پشتیبانی":
        await update.message.reply_text("💬 برای ارتباط با پشتیبانی به آیدی زیر پیام دهید:\n@matinejlali_official")
    elif text == "👥 زیر مجموعه گیری":
        await update.message.reply_text("🔗 لینک زیرمجموعه‌گیری شما فعال است.")
    elif text == "👨‍💻 پنل مدیریت":
        if user_id == ADMIN_CHAT_ID:
            await update.message.reply_text("👑 خوش آمدید ادمین عزیز.")
        else:
            await update.message.reply_text("❌ دسترسی ندارید.")
    elif text == "💻 درخواست نمایندگی":
        await update.message.reply_text("💼 برای دریافت پنل نمایندگی به ادمین پیام دهید.")
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید.", reply_markup=get_main_keyboard())

# مدیریت دکمه‌های شیشه‌ای
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    username = query.from_user.username or query.from_user.first_name
    
    if user_id not in USER_WALLETS:
        USER_WALLETS[user_id] = 0

    if data == "buy_unlimited_30d":
        wallet_balance = USER_WALLETS[user_id]
        
        # ساخت متن پیش‌فاکتور دقیقاً مطابق درخواست شما
        invoice_text = (
            "📇 **پیش فاکتور شما:**\n"
            f"👤 نام کاربری: `{username}`\n"
            "🔐 نام سرویس: سرویس نامحدود\n"
            "📆 مدت اعتبار: 30 روز\n"
            "💶 قیمت:  248,000 تومان\n"
            "👥 حجم اکانت: ♾️\n"
            "🗒 یادداشت محصول : \n"
            f"💵 موجودی کیف پول شما : {wallet_balance:,}\n\n"
            "💰 سفارش شما آماده پرداخت است"
        )
        
        # بررسی اینکه آیا موجودی کیف پول برای خرید کامل است یا خیر
        if wallet_balance >= PRICE_TOMAN:
            # موجودی کافی است -> دکمه برداشت از کیف پول
            keyboard = [
                [InlineKeyboardButton("💵 برداشت از کیف پول", callback_data="pay_from_wallet")],
                [InlineKeyboardButton("❌ انصراف", callback_data="cancel_order")]
            ]
        else:
            # موجودی کافی نیست -> پیام کسری موجودی و دکمه کارت به کارت
            invoice_text += "\n\n📝 موجودی حساب شما کافی نمی باشد یک روش پرداخت از لیست پایین انتخاب نمایید"
            keyboard = [
                [InlineKeyboardButton("💳 کارت به کارت", callback_data="pay_card")],
                [InlineKeyboardButton("❌ بستن لیست", callback_data="cancel_order")]
            ]
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(invoice_text, reply_markup=reply_markup, parse_mode="Markdown")
        
    elif data == "pay_from_wallet":
        wallet_balance = USER_WALLETS[user_id]
        if wallet_balance >= PRICE_TOMAN:
            USER_WALLETS[user_id] -= PRICE_TOMAN
            await query.edit_message_text(
                "✅ **پرداخت با موفقیت از کیف پول انجام شد!**\n\n"
                "سرویس نامحدود ۳۰ روزه شما فعال گردید. 🚀",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text("❌ موجودی کیف پول شما کافی نیست!")
            
    elif data == "pay_card":
        # متن کارت به کارت دقیقاً با جزئیات درخواستی شما
        card_info = (
            "برای افزایش موجودی، مبلغ 248,000 تومان را به شماره‌ی حساب زیر واریز کنید 👇🏻\n\n"
            "====================\n"
            f"<code>{CARD_NUMBER}</code>\n"
            f"{CARD_HOLDER}\n"
            "====================\n\n"
            "❌ این تراکنش به مدت یک ساعت اعتبار دارد پس از آن امکان پرداخت این تراکنش امکان ندارد.\n"
            "‼مبلغ باید همان مبلغی که در بالا ذکر شده واریز نمایید.\n"
            "‼️امکان برداشت وجه از کیف پول نیست.\n"
            "‼️مسئولیت واریز اشتباهی با شماست.\n"
            "🔝بعد از پرداخت دکمه پرداخت کردم را زده سپس تصویر رسید را ارسال نمایید"
        )
        # سه دکمه شیشه‌ای پایین کارت به کارت
        card_keyboard = [
            [InlineKeyboardButton("📋 کپی کردن شماره کارت", callback_data="copy_card"),
             InlineKeyboardButton("💵 کپی کردن مبلغ", callback_data="copy_price")],
            [InlineKeyboardButton("✅ پرداخت کردم | ارسال رسید", callback_data="send_receipt_prompt")]
        ]
        await query.edit_message_text(card_info, reply_markup=InlineKeyboardMarkup(card_keyboard), parse_mode="HTML")
        
    elif data == "copy_card":
        await query.answer(text=f"شماره کارت کپی شد: {CARD_NUMBER}", show_alert=True)
        
    elif data == "copy_price":
        # ارسال مبلغ به ریال به صورت هشدار یا متن
        await query.answer(text=f"مبلغ به ریال: {PRICE_RIAL:,} ریال", show_alert=True)
        
    elif data == "send_receipt_prompt":
        WAITING_FOR_RECEIPT.add(user_id)
        await query.edit_message_text(
            "🖼 تصویر رسید خود را ارسال نمایید...\n\n"
            "لطفاً اسکرین‌شات یا عکس فیش واریزی را همینجا در چت بفرستید تا برای ادمین ارسال شود."
        )
        
    elif data == "cancel_order":
        await query.edit_message_text("❌ عملیات لغو شد.")
        
    elif data.startswith("approve_"):
        target_user = int(data.split("_")[1])
        # شارژ کیف پول کاربر پس از تایید ادمین
        if target_user not in USER_WALLETS:
            USER_WALLETS[target_user] = 0
        USER_WALLETS[target_user] += PRICE_TOMAN
        
        await query.edit_message_caption(caption=query.message.caption + f"\n\n✅ **وضعیت: تایید شد و کیف پول کاربر به مبلغ {PRICE_TOMAN:,} تومان شارژ گردید!**")
        await context.bot.send_message(
            chat_id=target_user, 
            text=f"💵 پرداخت و رسید شما توسط ادمین تایید شد!\nکیف پول شما به مبلغ {PRICE_TOMAN:,} تومان شارژ شد و سفارش شما انجام گردید. مبارکتون باشه 🚀"
        )
        
    elif data.startswith("reject_"):
        target_user = int(data.split("_")[1])
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ **وضعیت: پرداخت رد شد!**")
        await context.bot.send_message(
            chat_id=target_user, 
            text="❌ متاسفانه رسید پرداخت شما توسط ادمین تایید نشد. در صورت وجود مشکل به پشتیبانی پیام دهید."
        )

if __name__ == '__main__':
    if TOKEN == "توکن_ربات_اینجا":
        print("لطفاً توکن ربات را در کد وارد کنید!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    
    print("BOT IS RUNNING PERFECTLY...")
    app.run_polling()
