import telebot
from telebot import types
import subprocess

BOT_TOKEN = "7660898301:AAFZKk0exENW0MkYVTGas0NupeeJnSQhDjE"
ADMIN_ID = 8182023588
DEFAULT_CHANNELS = ["@Chanel_BuLlEt"]

bot = telebot.TeleBot(BOT_TOKEN)
buttons = {}

def get_required_channels():
    channels_text = os.environ.get("CHANNELS")
    if channels_text:
        return [ch.strip() for ch in channels_text.split(",") if ch.strip()]
    return DEFAULT_CHANNELS

def is_member(user_id):
    for ch in get_required_channels():
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["member", "creator", "administrator"]:
                continue
            return False
        except:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    if not is_member(user_id):
        markup = types.InlineKeyboardMarkup()
        for ch in get_required_channels():
            markup.add(types.InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{ch.replace('@','')}"))
        bot.send_message(user_id, "برای استفاده از ربات باید عضو کانال شوید:", reply_markup=markup)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for label in buttons:
        markup.add(label)
    if user_id == ADMIN_ID:
        markup.add("پنل مدیریت", "اجرای اسکریپت Python", "اجرای دستور Shell")
    bot.send_message(user_id, "سلام! به ربات خوش اومدی.", reply_markup=markup)

# اجرای اسکریپت Python
def execute_python_script():
    try:
        # اسکریپت Python خود را در اینجا اجرا کن
        result = "اسکریپت Python با موفقیت اجرا شد."
        return result
    except Exception as e:
        return f"خطا در اجرای اسکریپت Python: {str(e)}"

# اجرای دستور Shell
def execute_shell_command(command):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return f"خطا در اجرای دستور: {str(e)}"

# دکمه‌های "اجرای اسکریپت Python" و "اجرای دستور Shell"
@bot.message_handler(func=lambda m: m.text == "اجرای اسکریپت Python")
def run_python_script(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    result = execute_python_script()
    bot.send_message(msg.chat.id, f"نتیجه اسکریپت Python: {result}")

@bot.message_handler(func=lambda m: m.text == "اجرای دستور Shell")
def run_shell_command(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    # اینجا دستور Shell رو مشخص کن
    command = "ls"  # می‌تونی دستور دلخواه خود رو وارد کنی
    result = execute_shell_command(command)
    bot.send_message(msg.chat.id, f"نتیجه دستور Shell: {result}")

# پنل مدیریت
@bot.message_handler(func=lambda m: m.text == "پنل مدیریت")
def admin_panel(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ افزودن دکمه", "➖ حذف دکمه")
    markup.add("📢 تنظیم کانال", "💳 افزودن دکمه پولی")
    bot.send_message(msg.chat.id, "پنل مدیریت فعال است:", reply_markup=markup)

# بقیه کدهای قبلی برای افزودن و حذف دکمه‌ها
@bot.message_handler(func=lambda m: m.text == "➕ افزودن دکمه")
def add_button(msg):
    if msg.from_user.id != ADMIN_ID:
        bot.send_message(msg.chat.id, "دسترسی نداری.")
        return
    sent = bot.send_message(msg.chat.id, "نام دکمه را ارسال کنید:")
    bot.register_next_step_handler(sent, get_button_label)

def get_button_label(msg):
    label = msg.text
    sent = bot.send_message(msg.chat.id, f"محتوای دکمه '{label}' را بفرست:")
    bot.register_next_step_handler(sent, lambda m: save_button(label, m))

def save_button(label, msg):
    buttons[label] = msg.text
    bot.send_message(msg.chat.id, f"دکمه '{label}' افزوده شد.")

@bot.message_handler(func=lambda m: m.text == "➖ حذف دکمه")
def remove_button(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    sent = bot.send_message(msg.chat.id, "نام دکمه‌ای که میخوای حذف کنی رو بفرست:")
    bot.register_next_step_handler(sent, confirm_remove)

def confirm_remove(msg):
    label = msg.text
    if label in buttons:
        del buttons[label]
        bot.send_message(msg.chat.id, f"دکمه '{label}' حذف شد.")
    else:
        bot.send_message(msg.chat.id, "چنین دکمه‌ای پیدا نشد.")

@bot.message_handler(func=lambda m: m.text == "📢 تنظیم کانال")
def set_channel(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    sent = bot.send_message(msg.chat.id, "آیدی کانال‌ها را با کاما جدا بنویس (مثلاً: @channel1,@channel2):")
    bot.register_next_step_handler(sent, save_channels)

def save_channels(msg):
    os.environ["CHANNELS"] = msg.text
    bot.send_message(msg.chat.id, "کانال‌ها بروزرسانی شدند.")

@bot.message_handler(func=lambda m: m.text == "💳 افزودن دکمه پولی")
def add_payment_button(msg):
    if msg.from_user.id != ADMIN_ID:
        sent = bot.send_message(msg.chat.id, "نام دکمه پولی رو بفرست:")
        bot.register_next_step_handler(sent, lambda m: register_paid_button(m, msg.from_user.id))

def register_paid_button(msg, uid):
    label = msg.text
    pending_payments[uid] = label
    bot.send_message(uid, f"دکمه پولی '{label}' ثبت شد. حالا از کاربر می‌خوایم رسید پرداخت رو بفرسته.")

@bot.message_handler(content_types=['photo'])
def handle_photo(msg):
    uid = msg.from_user.id
    if uid in pending_payments:
        label = pending_payments[uid]
        bot.send_photo(ADMIN_ID, msg.photo[-1].file_id, caption=f"رسید پرداخت برای: {label}\nاز طرف: @{msg.from_user.username or 'ندارد'}")
        bot.send_message(uid, "رسید ارسال شد. بعد از بررسی محتوا برات فعال میشه.")
        del pending_payments[uid]

@bot.message_handler(func=lambda m: m.text in buttons)
def handle_button(msg):
    bot.send_message(msg.chat.id, buttons[msg.text])

bot.infinity_polling()
