import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# بارگذاری پروفایل تیپ‌ها از فایل json
with open("mbti_profiles.json", "r", encoding="utf-8") as f:
    mbti_data = json.load(f)

user_states = {}
user_answers = {}
user_results = {}

questions = [
    ("ترجیح می‌دی وقت آزادت رو چطور بگذرونی؟", {"E": "با دوستان و جمع", "I": "تنها یا در آرامش"}),
    ("وقتی با اطلاعات برخورد می‌کنی بیشتر به چی توجه می‌کنی؟", {"S": "جزئیات و واقعیت‌ها", "N": "ایده‌ها و مفاهیم"}),
    ("تصمیم‌گیری‌هات بر چه اساسی هست؟", {"T": "منطق و تحلیل", "F": "احساسات و ارزش‌ها"}),
    ("ترجیح می‌دی برنامه‌هات چطور باشن؟", {"J": "منظم و برنامه‌ریزی‌شده", "P": "آزاد و انعطاف‌پذیر"}),
    ("در مواجهه با مشکل، چه واکنشی نشون می‌دی؟", {"T": "تحلیل منطقی", "F": "همدلی و احساس"}),
    ("در یک جمع شلوغ، معمولاً...", {"E": "انرژی می‌گیرم", "I": "خسته می‌شم"}),
    ("در کارهات معمولاً...", {"J": "برنامه‌ریزی می‌کنم", "P": "یهو انجام می‌دم"}),
    ("بیشتر به چی علاقه‌داری؟", {"S": "چیزای واقعی", "N": "ایده‌های ذهنی"}),
    ("در روابط عاطفی، بیشتر...", {"F": "با احساساتم تصمیم می‌گیرم", "T": "با منطق تصمیم می‌گیرم"}),
    ("چطوری بهتر یاد می‌گیری؟", {"S": "با تجربه عملی", "N": "با درک مفاهیم"})
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای شروع تست شخصیت‌شناسی MBTI دستور /test رو بزن.")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_states[user_id] = 0
    user_answers[user_id] = []
    await update.message.reply_text(
        f"تست شخصیت MBTI شروع شد!\nبرای پاسخ به هر سؤال، روی پیام ریپلای بزن و گزینه مورد نظرت رو بنویس.",
    )
    await send_question(update, context, user_id)

async def send_question(update, context, user_id):
    q_index = user_states[user_id]
    question, options = questions[q_index]
    options_text = "\n".join([f"- {v}" for k, v in options.items()])
    await context.bot.send_message(
        chat_id=user_id,
        text=f"سؤال {q_index + 1}:\n{question}\n{options_text}"
    )

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # فقط به کاربری که تست را شروع کرده پاسخ بده
    if user_id not in user_states:
        return

    if not update.message.reply_to_message:
        return

    current_q = user_states[user_id]
    question, options = questions[current_q]

    response = update.message.text.strip()
    matched = False
    for key, val in options.items():
        if response == val:
            user_answers[user_id].append(key)
            matched = True
            break

    if not matched:
        await update.message.reply_text("❗️ لطفاً دقیقاً یکی از گزینه‌ها رو انتخاب کن.")
        return

    user_states[user_id] += 1
    if user_states[user_id] >= len(questions):
        await finish_test(update, context, user_id)
    else:
        await send_question(update, context, user_id)

def calculate_type(answers):
    result = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for a in answers:
        result[a] += 1
    mbti = ""
    mbti += "E" if result["E"] >= result["I"] else "I"
    mbti += "S" if result["S"] >= result["N"] else "N"
    mbti += "T" if result["T"] >= result["F"] else "F"
    mbti += "J" if result["J"] >= result["P"] else "P"
    return mbti

async def finish_test(update, context, user_id):
    mbti = calculate_type(user_answers[user_id])
    user_results[user_id] = mbti
    profile = mbti_data.get(mbti, {})
    description = profile.get("description", "اطلاعاتی موجود نیست.")
    strengths = "\n".join(profile.get("strengths", []))
    weaknesses = "\n".join(profile.get("weaknesses", []))
    partners = ", ".join(profile.get("ideal_partners", []))
    similar = ", ".join(profile.get("similar_types", []))

    text = (
        f"✅ تست MBTI شما کامل شد!\n\n"
        f"👤 تیپ شخصیتی شما: <b>{mbti}</b>\n\n"
        f"🧠 توضیح:\n{description}\n\n"
        f"✅ نقاط قوت:\n{strengths}\n\n"
        f"⚠️ نقاط ضعف:\n{weaknesses}\n\n"
        f"❤️ تیپ مناسب برای ازدواج: {partners}\n"
        f"👥 تیپ‌های مشابه: {similar}"
    )
    await context.bot.send_message(chat_id=user_id, text=text, parse_mode=ParseMode.HTML)
    del user_states[user_id]
    del user_answers[user_id]

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mbti = user_results.get(user_id)
    if not mbti:
        await update.message.reply_text("❌ هنوز تست رو انجام ندادی. با /test شروع کن.")
        return
    profile = mbti_data.get(mbti, {})
    await finish_test(update, context, user_id)

async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) != 1:
        await update.message.reply_text("دستور صحیح: /compare <user_id>")
        return
    target_id = int(context.args[0])
    mbti1 = user_results.get(user_id)
    mbti2 = user_results.get(target_id)
    if not mbti1 or not mbti2:
        await update.message.reply_text("هر دو کاربر باید تست رو کامل کرده باشن.")
        return
    text = f"👤 شما: {mbti1}\n👤 کاربر مقابل: {mbti2}\n"
    text += "📊 تفاوت شخصیتی: "
    diff = sum(1 for a, b in zip(mbti1, mbti2) if a != b)
    text += f"{diff} حرف متفاوت"
    await update.message.reply_text(text)

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await update.message.reply_text("❗️برای شروع تست شخصیت‌شناسی دستور /test رو بزن.")

def main():
    token = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("compare", compare))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply))
    app.add_handler(MessageHandler(filters.ALL, fallback))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
