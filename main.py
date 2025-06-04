import logging
import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

TOKEN = os.getenv("YOUR_BOT_TOKEN")
PROFILE_FILE = "profiles.json"

logging.basicConfig(level=logging.INFO)

# سؤالات مرحله‌ای
questions = [
    {
        "text": "سوال 1: ترجیح می‌دی تعطیلات رو چطور بگذرونی؟\nA) توی خونه، با کتاب یا فیلم\nB) با دوستان، بیرون و شلوغ",
        "trait": "introversion"
    },
    {
        "text": "سوال 2: موقع تصمیم‌گیری بیشتر به چی تکیه می‌کنی؟\nA) منطق و تحلیل\nB) احساسات",
        "trait": "logic"
    },
    {
        "text": "سوال 3: وقتی کار مهمی داری...\nA) براش برنامه‌ریزی می‌کنی\nB) بدون برنامه انجامش می‌دی",
        "trait": "planner"
    },
    {
        "text": "سوال 4: توی گروه...\nA) بیشتر شنونده‌ای\nB) بیشتر رهبر یا فعال هستی",
        "trait": "passive"
    }
]

user_states = {}

def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return {}
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_profiles(profiles):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من آینه شخصیت هستم.\nاز دستور /mirror برای شروع تست شخصیت استفاده کن.")

async def mirror(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_states[user_id] = {"step": 0, "answers": {}}
    await update.message.reply_text("🚀 تست شخصیت شروع شد!\n" + questions[0]["text"])

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    profiles = load_profiles()
    if user_id not in profiles:
        await update.message.reply_text("📭 هنوز تست شخصیت ندادی. از /mirror استفاده کن.")
        return

    profile = profiles[user_id]
    result = f"""🧠 پروفایل شخصیت تو:
- درون‌گرایی/برون‌گرایی: {profile['introversion']}
- منطقی/احساسی: {profile['logic']}
- برنامه‌ریز/ماجراجو: {profile['planner']}
- منفعل/فعال: {profile['passive']}"""
    await update.message.reply_text(result)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip().upper()

    if user_id not in user_states:
        return

    state = user_states[user_id]
    step = state["step"]

    if text not in ["A", "B"]:
        await update.message.reply_text("لطفاً فقط یکی از گزینه‌های A یا B رو انتخاب کن.")
        return

    trait = questions[step]["trait"]
    state["answers"][trait] = "A" if text == "A" else "B"
    state["step"] += 1

    if state["step"] < len(questions):
        next_q = questions[state["step"]]["text"]
        await update.message.reply_text(next_q)
    else:
        profile = {
            "introversion": "درون‌گرا" if state["answers"]["introversion"] == "A" else "برون‌گرا",
            "logic": "منطقی" if state["answers"]["logic"] == "A" else "احساسی",
            "planner": "برنامه‌ریز" if state["answers"]["planner"] == "A" else "ماجراجو",
            "passive": "منفعل" if state["answers"]["passive"] == "A" else "فعال"
        }
        profiles = load_profiles()
        profiles[user_id] = profile
        save_profiles(profiles)

        result = f"""✅ تست تموم شد! این تحلیل شخصیت توئه:
- {profile['introversion']}
- {profile['logic']}
- {profile['planner']}
- {profile['passive']}"""
        await update.message.reply_text(result)
        del user_states[user_id]

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("⛔️ خطا:", exc_info=context.error)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mirror", mirror))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    app.add_error_handler(error_handler)

    print("🤖 ربات در حال اجراست...")
    app.run_polling()
