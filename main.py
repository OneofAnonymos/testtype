import logging
import json
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

# تنظیم توکن از محیط
TOKEN = os.getenv("YOUR_BOT_TOKEN")

# اگر در Render تنظیم نکردی، این‌جوری مستقیم توکنت رو بذار:
# TOKEN = "7808766886:AAEV7zDt9KhCMGD0WP23gOJWYdjdcOLVgn0"

# تنظیم لاگ
logging.basicConfig(level=logging.INFO)

# فایل ذخیره اطلاعات
PROFILE_FILE = "profiles.json"

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من آینه شخصیت هستم. از /mirror برای تحلیل شخصیت استفاده کن.")

# دستور آینه
async def mirror(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("یه متن درباره خودت بنویس. مثلاً بگو چه اخلاقی داری، از چی خوشت میاد، و ...")

    # انتظار برای پیام بعدی کاربر
    msg = await context.bot.wait_for_message(chat_id=update.effective_chat.id, timeout=60)
    
    if msg:
        analysis = analyze_personality(msg.text)
        user_id = str(update.effective_user.id)
        profiles = load_profiles()
        profiles[user_id] = analysis
        save_profiles(profiles)

        await update.message.reply_text(f"🔍 تحلیل شخصیتت:\n{analysis}")
    else:
        await update.message.reply_text("⏱ زمانت تموم شد! دوباره /mirror رو بزن.")

# تابع تحلیل ساده شخصیت
def analyze_personality(text: str):
    text = text.lower()
    traits = []

    if "تنها" in text or "ساکت" in text:
        traits.append("درون‌گرا")
    if "شلوغ" in text or "دوست دارم با همه حرف بزنم" in text:
        traits.append("برون‌گرا")
    if "منظم" in text or "برنامه‌ریزی" in text:
        traits.append("برنامه‌ریز")
    if "عاشق هیجان" in text or "بی‌برنامه" in text:
        traits.append("ماجراجو")

    if not traits:
        return "شخصیتت خیلی خاصه! هنوز نتونستم چیزی تشخیص بدم 😅"

    return "، ".join(traits)

# ذخیره و بارگذاری فایل شخصیت‌ها
def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return {}
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_profiles(profiles):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

# اجرای ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mirror", mirror))

    print("✅ ربات راه افتاد.")
    app.run_polling()
