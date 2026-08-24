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

TOKEN = os.environ.get("BOT_TOKEN", "توکن_ربات_اینجا")
ADMIN_CHAT_ID = 7357227534

WAITING_FOR_RECEIPT = set()
WAITING_FOR_CONFIG_NOTE = set()  # برای گرفتن اسم/یادداشت کانفیگ از کاربر

USER_WALLETS = {}
USER_CONFIG_NOTES = {}  # ذخیره یادداشت کانفیگ هر کاربر

CARD_NUMBER = "6219861956948888"
CARD_HOLDER = "محمد متین اجلالی"
PRICE_TOMAN = 248000
PRICE_RIAL = PRICE_TOMAN * 10

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
    
    if user_id not in USER_WALLETS:
        USER_WALLETS[user_id] = 0
        
    # ۱. اگر کاربر منتظر ارسال رسید بود
    if user_id in WAITING_FOR_RECEIPT and update.message.photo:
        photo_file = update.message.photo[-1].file_id
        config_note = USER_CONFIG_NOTES.get(user_id, "سرویس نامحدود")
        
        caption = (
            f"🔔 **رسید جدید پرداخت برای بررسی!**\n\n"
            f"👤 نام: {user.full_name}\n"
            f"آیدی: `@{user.username}`\n"
            f"🆔 یوزر‌دی: `{user_id}`\n"
            f"📌 نام کانفیگ / یادداشت: {config_note}\n"
            f"💵 مبلغ فاکتور: {PRICE_TOMAN:,} تومان"
        )
        
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
                "به زودی پس از تایید ادمین، کیف پول شما شارژ و سفارش شما انجام خواهد شد. 🙏",
                reply_markup=get_main_keyboard()
            )
        except Exception as e:
            print("Error:", e)
            await update.message.reply_text("❌ خطا در ارسال رسید. لطفاً مستقیم به ادمین پیام دهید.")
            
        WAITING_FOR_RECEIPT.remove(user_id)
        return

    # ۲. اگر کاربر داشت نام/یادداشت کانفیگ رو می‌نوشت (دقیقا مطابق عکس مربوط به نام کانفیگ)
    if user_id in WAITING_FOR_CONFIG_NOTE:
        config_note = text
        USER_CONFIG_NOTES[user_id] = config_note
        WAITING_FOR_CONFIG_NOTE.remove(user_id)
        
        wallet_balance = USER_WALLETS[user_id]
        username = user.username or user.first_name
        
        # نمایش پیش‌فاکتور نهایی
        invoice_text = (
            "📇 **پیش فاکتور شما:**\n"
            f"👤 نام کاربری: `{username}`\n"
            "🔐 نام سرویس: سرویس نامحدود\n"
            "📆 مدت اعتبار: 30 روز\n"
            f"💶 قیمت: {PRICE_TOMAN:,} تومان\n"
            "👥 حجم اکانت: ♾️\n"
            f"🗒 یادداشت محصول : {config_note}\n"
            f"💵 موجودی کیف پول شما : {wallet_balance:,}\n\n"
            "💰 سفارش شما آماده پرداخت است"
        )
        
        if wallet_balance >= PRICE_TOMAN:
            keyboard = [
                [InlineKeyboardButton("💵 برداشت از کیف پول", callback_data="pay_from_wallet")],
                [InlineKeyboardButton("❌ انصراف", callback_data="cancel_order")]
            ]
        else:
            invoice_text += "\n\n📝 موجودی حساب شما کافی نمی باشد یک روش پرداخت از لیست پایین انتخاب نمایید"
            keyboard = [
                [InlineKeyboardButton("💳 کارت به کارت", callback_data="pay_card")],
                [InlineKeyboardButton("❌ بستن لیست", callback_data="cancel_order")]
            ]
            
        await update.message.reply_text(invoice_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # مدیریت دکمه‌های منوی اصلی
    if text == "🟢 خرید اشتراک 🔑":
        # ابتدا دکمه انتخاب اشتراک یک ماهه نامحدود رو میدیم
        keyboard = [
            [InlineKeyboardButton("اشتراک یک ماهه نامحدود ۲۴۸ هزار تومن 🏷️", callback_data="select_unlimited_30d")]
        ]
        await update.message.reply_text("🛒 لطفاً نوع اشتراک خود را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif text == "🔑 اکانت تست":
        await update.message.reply_text("🔑 بخش اکانت تست.")
    elif text == "🛍️ سرویس‌های من":
        await update.message.reply_text("👤 شما در حال حاضر سرویس فعالی ندارید.")
    elif text == "🏦 کیف پول + شارژ":
        wallet_balance = USER_WALLETS.get(user_id, 0)
        await update.message.reply_text(f"💰 موجودی کیف پول شما: **{wallet_balance:,} تومان**", parse_mode="Markdown")
    elif text == "☎️ پشتیبانی":
        await update.message.reply_text("💬 پشتیبانی: @matinejlali_official")
    elif text == "👥 زیر مجموعه گیری":
        await update.message.reply_text("🔗 لینک زیرمجموعه‌گیری شما فعال است.")
    elif text == "👨‍💻 پنل مدیریت":
        if user_id == ADMIN_CHAT_ID:
            await update.message.reply_text("👑 پنل مدیریت فعال است.")
        else:
            await update.message.reply_text("❌ دسترسی ندارید.")
    elif text == "💻 درخواست نمایندگی":
        await update.message.reply_text("💼 برای دریافت نمایندگی به ادمین پیام دهید.")
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید.", reply_markup=get_main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if user_id not in USER_WALLETS:
        USER_WALLETS[user_id] = 0

    # وقتی روی دکمه شیشه‌ای اشتراک می‌زنه، ربات ازش یادداشت/نام کانفیگ رو می‌خواد (دقیقاً مشابه عکس شما)
    if data == "select_unlimited_30d":
        WAITING_FOR_CONFIG_NOTE.add(user_id)
        await query.message.reply_text(
            "📌 **یک یادداشت برای کانفیگ خود بنویسید.**\n"
            "⚠️ این نام برای جستجو سریع‌تر در مدیریت سرویس‌ها می باشد 📇\n"
            "(مثال: علی ، احمد ، عمو ، مشتری شهرستان و...)",
            parse_mode="Markdown"
        )
        
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
        card_info = (
            f"برای افزایش موجودی، مبلغ {PRICE_TOMAN:,} تومان را به شماره‌ی حساب زیر واریز کنید 👇🏻\n\n"
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
        # سه دکمه شیشه‌ای پایین کارت به کارت دقیقاً مطابق خواسته شما
        card_keyboard = [
            [InlineKeyboardButton("📋 کپی کردن شماره کارت", callback_data="copy_card"),
             InlineKeyboardButton("💵 کپی کردن مبلغ", callback_data="copy_price")],
            [InlineKeyboardButton("✅ پرداخت کردم | ارسال رسید", callback_data="send_receipt_prompt")]
        ]
        await query.edit_message_text(card_info, reply_markup=InlineKeyboardMarkup(card_keyboard), parse_mode="HTML")
        
    elif data == "copy_card":
        await query.answer(text=f"شماره کارت کپی شد: {CARD_NUMBER}", show_alert=True)
        
    elif data == "copy_price":
        await query.answer(text=f"مبلغ به ریال: {PRICE_RIAL:,} ریال", show_alert=True)
        
    elif data == "send_receipt_prompt":
        WAITING_FOR_RECEIPT.add(user_id)
        await query.edit_message_text(
            "🖼 **تصویر رسید خود را ارسال نمایید...**\n\n"
            "لطفاً اسکرین‌شات رسید پرداخت را همینجا در چت بفرستید.",
            parse_mode="Markdown"
        )
        
    elif data == "cancel_order":
        await query.edit_message_text("❌ عملیات لغو شد.")
        
    elif data.startswith("approve_"):
        target_user = int(data.split("_")[1])
        if target_user not in USER_WALLETS:
            USER_WALLETS[target_user] = 0
        USER_WALLETS[target_user] += PRICE_TOMAN
        
        await query.edit_message_caption(caption=query.message.caption + f"\n\n✅ **وضعیت: تایید شد و کیف پول به مبلغ {PRICE_TOMAN:,} تومان شارژ گردید!**")
        await context.bot.send_message(
            chat_id=target_user, 
            text=f"💵 پرداخت شما تایید شد!\nکیف پول شما به مبلغ {PRICE_TOMAN:,} تومان شارژ شد و سفارش شما انجام گردید. مبارکتون باشه 🚀"
        )
        
    elif data.startswith("reject_"):
        target_user = int(data.split("_")[1])
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ **وضعیت: پرداخت رد شد!**")
        await context.bot.send_message(
            chat_id=target_user, 
            text="❌ متاسفانه رسید پرداخت شما توسط ادمین تایید نشد."
        )

if __name__ == '__main__':
    if TOKEN == "توکن_ربات_اینجا":
        print("لطفاً توکن ربات را در کد وارد کنید!")
        exit(1)
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    
    print("BOT IS RUNNING WITH EXACT CONFIG NOTE & CARDS...")
    app.run_polling()
