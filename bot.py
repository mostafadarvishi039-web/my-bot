import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# خواندن توکن و آیدی ادمین از متغیرهای محیطی ریلی‌وی (Environment Variables)
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_ID", "7357227534"))

if not TOKEN:
    print("❌ خطا: متغیر محیطی BOT_TOKEN تنظیم نشده است!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

WAITING_FOR_CONFIG = {}
WAITING_FOR_RECEIPT = {}
ADMIN_TARGET_USER = {}

USER_WALLETS = {}
USER_CONFIG_NOTES = {}

CARD_NUMBER = "6219861956948888"
CARD_HOLDER = "محمد متین اجلالی"
PRICE_TOMAN = 248000
PRICE_RIAL = PRICE_TOMAN * 10

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("🟢 خرید اشتراک 🔑"), KeyboardButton("♻️ تمدید سرویس"))
    keyboard.row(KeyboardButton("🔑 اکانت تست"))
    keyboard.row(KeyboardButton("🛍️ سرویس‌های من"), KeyboardButton("🏦 کیف پول + شارژ"))
    keyboard.row(KeyboardButton("☎️ پشتیبانی"), KeyboardButton("👥 زیر مجموعه گیری"))
    keyboard.row(KeyboardButton("👨‍💻 پنل مدیریت"), KeyboardButton("💻 درخواست نمایندگی"))
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "سلام به ربات رسمی **Verax VPN** خوش آمدید! ⚡️\n\nاز دکمه‌های زیر برای مدیریت حساب و خرید سرویس استفاده کنید:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_all_messages(message):
    user_id = message.from_user.id
    
    if user_id not in USER_WALLETS:
        USER_WALLETS[user_id] = 0

    if user_id == ADMIN_CHAT_ID and ADMIN_CHAT_ID in ADMIN_TARGET_USER:
        target_user = ADMIN_TARGET_USER[ADMIN_CHAT_ID]
        sub_link = message.text.strip()
        
        try:
            bot.send_message(
                target_user,
                (
                    "🎉 **پرداخت و سفارش شما با موفقیت تایید شد!**\n\n"
                    "📦 **مشخصات اشتراک شما:**\n"
                    "🔐 نام سرویس: سرویس نامحدود\n"
                    "📆 مدت اعتبار: ۳۰ روز\n"
                    "👥 حجم: ♾️ نامحدود\n\n"
                    "🔗 **لینک سابسکریپشن اختصاصی شما:**\n"
                    f"`{sub_link}`\n\n"
                    "📥 این لینک را کپی کرده و در برنامه‌های اتصال (مثل V2rayNG) وارد کنید. از اتصال خود لذت ببرید! 🚀"
                ),
                parse_mode="Markdown"
            )
            bot.send_message(message.chat.id, "✅ لینک ساب با موفقیت برای کاربر ارسال شد!")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطا در ارسال لینک: {e}")
            
        del ADMIN_TARGET_USER[ADMIN_CHAT_ID]
        return

    if user_id in WAITING_FOR_RECEIPT and message.photo:
        photo_file = message.photo[-1].file_id
        config_note = USER_CONFIG_NOTES.get(user_id, "سرویس نامحدود")
        
        caption = (
            f"🔔 **رسید جدید پرداخت برای بررسی!**\n\n"
            f"👤 نام: {message.from_user.full_name}\n"
            f"آیدی: `@{message.from_user.username}`\n"
            f"🆔 یوزر‌دی: `{user_id}`\n"
            f"📌 نام کانفیگ / یادداشت: {config_note}\n"
            f"💵 مبلغ فاکتور: {PRICE_TOMAN:,} تومان"
        )
        
        admin_keyboard = InlineKeyboardMarkup()
        admin_keyboard.row(
            InlineKeyboardButton("✅ تایید پرداخت", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ رد پرداخت", callback_data=f"reject_{user_id}")
        )
        
        try:
            bot.send_photo(ADMIN_CHAT_ID, photo_file, caption=caption, reply_markup=admin_keyboard, parse_mode="Markdown")
            bot.send_message(message.chat.id, "✅ **رسید شما با موفقیت ارسال شد!**\n\nبه زودی پس از تایید ادمین، لینک اشتراک برای شما ارسال خواهد شد. 🙏", reply_markup=get_main_keyboard())
        except Exception as e:
            bot.send_message(message.chat.id, "❌ خطا در ارسال رسید. لطفاً مستقیم به ادمین پیام دهید.")
            
        del WAITING_FOR_RECEIPT[user_id]
        return

    if user_id in WAITING_FOR_CONFIG and message.text:
        config_note = message.text
        USER_CONFIG_NOTES[user_id] = config_note
        del WAITING_FOR_CONFIG[user_id]
        
        wallet_balance = USER_WALLETS[user_id]
        username = message.from_user.username or message.from_user.first_name
        
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
        
        keyboard = InlineKeyboardMarkup()
        if wallet_balance >= PRICE_TOMAN:
            keyboard.row(InlineKeyboardButton("💵 برداشت از کیف پول", callback_data="pay_from_wallet"))
            keyboard.row(InlineKeyboardButton("❌ انصراف", callback_data="cancel_order"))
        else:
            invoice_text += "\n\n📝 موجودی حساب شما کافی نمی باشد یک روش پرداخت از لیست پایین انتخاب نمایید"
            keyboard.row(InlineKeyboardButton("💳 کارت به کارت", callback_data="pay_card"))
            keyboard.row(InlineKeyboardButton("❌ بستن لیست", callback_data="cancel_order"))
            
        bot.send_message(message.chat.id, invoice_text, reply_markup=keyboard, parse_mode="Markdown")
        return

    text = message.text
    if text == "🟢 خرید اشتراک 🔑":
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("اشتراک یک ماهه نامحدود ۲۴۸ هزار تومن 🏷️", callback_data="select_unlimited_30d"))
        bot.send_message(message.chat.id, "🛒 لطفاً نوع اشتراک خود را انتخاب کنید:", reply_markup=keyboard)
        
    elif text == "🔑 اکانت تست":
        bot.send_message(message.chat.id, "🔑 بخش اکانت تست موقتا غیرفعال است.")
    elif text == "🛍️ سرویس‌های من":
        bot.send_message(message.chat.id, "👤 شما در حال حاضر سرویس فعالی ندارید.")
    elif text == "🏦 کیف پول + شارژ":
        wallet_balance = USER_WALLETS.get(user_id, 0)
        bot.send_message(message.chat.id, f"💰 موجودی کیف پول شما: **{wallet_balance:,} تومان**", parse_mode="Markdown")
    elif text == "☎️ پشتیبانی":
        bot.send_message(message.chat.id, "💬 پشتیبانی: @matinejlali_official")
    elif text == "👥 زیر مجموعه گیری":
        bot.send_message(message.chat.id, "🔗 لینک زیرمجموعه‌گیری شما فعال است.")
    elif text == "👨‍💻 پنل مدیریت":
        if user_id == ADMIN_CHAT_ID:
            bot.send_message(message.chat.id, "👑 پنل مدیریت فعال است.")
        else:
            bot.send_message(message.chat.id, "❌ دسترسی ندارید.")
    elif text == "💻 درخواست نمایندگی":
        bot.send_message(message.chat.id, "💼 برای دریافت نمایندگی به ادمین پیام دهید.")
    else:
        bot.send_message(message.chat.id, "لطفاً از دکمه‌های منو استفاده کنید.", reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    if user_id not in USER_WALLETS:
        USER_WALLETS[user_id] = 0

    if data == "select_unlimited_30d":
        WAITING_FOR_CONFIG[user_id] = True
        bot.send_message(
            call.message.chat.id,
            "📌 **یک یادداشت برای کانفیگ خود بنویسید.**\n⚠️ این نام برای جستجو سریع‌تر در مدیریت سرویس‌ها می باشد 📇\n(مثال: علی ، احمد ، عمو ، مشتری شهرستان و...)",
            parse_mode="Markdown"
        )
        
    elif data == "pay_from_wallet":
        wallet_balance = USER_WALLETS[user_id]
        if wallet_balance >= PRICE_TOMAN:
            USER_WALLETS[user_id] -= PRICE_TOMAN
            bot.edit_message_text(
                "✅ **پرداخت با موفقیت از کیف پول انجام شد!**\n\nسرویس نامحدود ۳۰ روزه شما خریداری شد. ادمین به زودی لینک ساب را برای شما ارسال می‌کند. 🚀",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )
            bot.send_message(
                ADMIN_CHAT_ID,
                f"🔔 خرید جدید از کیف پول!\nکاربر `{user_id}` مبلغ {PRICE_TOMAN:,} تومان از کیف پول پرداخت کرد.\nلطفاً لینک ساب را بفرستید:",
                parse_mode="Markdown"
            )
            ADMIN_TARGET_USER[ADMIN_CHAT_ID] = user_id
        else:
            bot.answer_callback_query(call.id, "❌ موجودی کیف پول شما کافی نیست!", show_alert=True)
            
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
        card_keyboard = InlineKeyboardMarkup()
        card_keyboard.row(
            InlineKeyboardButton("📋 کپی کردن شماره کارت", callback_data="copy_card"),
            InlineKeyboardButton("💵 کپی کردن مبلغ", callback_data="copy_price")
        )
        card_keyboard.row(InlineKeyboardButton("✅ پرداخت کردم | ارسال رسید", callback_data="send_receipt_prompt"))
        
        bot.edit_message_text(card_info, call.message.chat.id, call.message.message_id, reply_markup=card_keyboard, parse_mode="HTML")
        
    elif data == "copy_card":
        bot.answer_callback_query(call.id, f"شماره کارت کپی شد: {CARD_NUMBER}", show_alert=True)
        
    elif data == "copy_price":
        bot.answer_callback_query(call.id, f"مبلغ به ریال: {PRICE_RIAL:,} ریال", show_alert=True)
        
    elif data == "send_receipt_prompt":
        WAITING_FOR_RECEIPT[user_id] = True
        bot.edit_message_text(
            "🖼 **تصویر رسید خود را ارسال نمایید...**\n\nلطفاً اسکرین‌شات رسید پرداخت را همینجا در چت بفرستید.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        
    elif data == "cancel_order":
        bot.edit_message_text("❌ عملیات لغو شد.", call.message.chat.id, call.message.message_id)
        
    elif data.startswith("approve_"):
        target_user = int(data.split("_")[1])
        ADMIN_TARGET_USER[ADMIN_CHAT_ID] = target_user
        
        bot.edit_message_caption(
            caption=call.message.caption + "\n\n✅ **وضعیت: رسید تایید شد.**\nحالا لینک ساب را در همین چت بفرستید.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        bot.send_message(ADMIN_CHAT_ID, f"👇 لطفاً لینک سابسکریپشن مربوط به کاربر `{target_user}` را ارسال کنید:", parse_mode="Markdown")
        
    elif data.startswith("reject_"):
        target_user = int(data.split("_")[1])
        bot.edit_message_caption(
            caption=call.message.caption + "\n\n❌ **وضعیت: پرداخت رد شد!**",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        bot.send_message(target_user, "❌ متاسفانه رسید پرداخت شما توسط ادمین تایید نشد. در صورت وجود مشکل به پشتیبانی پیام دهید.")

if __name__ == '__main__':
    print("BOT IS RUNNING ON RAILWAY...")
    bot.infinity_polling()
