import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode

# بارگذاری دیتای MBTI
with open("mbti_profiles.json", "r", encoding="utf-8") as f:
    mbti_data = json.load(f)

# وضعیت کاربران
user_states = {}       # مرحله سؤال فعلی
user_answers = {}      # جواب‌ها
user_results = {}      # نتیجه تست
active_users = set()   # فقط کاربرانی که /test زده‌اند

# سوالات (قابل افزایش)
questions = [
    ("وقتی با اطلاعات برخورد می‌کنی بیشتر به چی توجه می‌کنی؟", {"S": "جزئیات و واقعیت‌ها", "N": "ایده‌ها و مفاهیم"}),
    ("تصمیم‌گیری‌هات بر چه اساسی هست؟", {"T": "منطق و تحلیل", "F": "احساسات و ارزش‌ها"}),
    ("ترجیح می‌دی وقت آزادت رو چطور بگذرونی؟", {"E": "با دوستان و جمع", "I": "تنها یا در آرامش"}),
    ("در مواجهه با مشکل، چه واکنشی نشون می‌دی؟", {"T": "تحلیل منطقی", "F": "همدلی و احساس"}),
    ("در کارهات معمولاً...", {"J": "برنامه‌ریزی می‌کنم", "P": "یهو انجام می‌دم"}),
    ("بیشتر به چی علاقه‌داری؟", {"S": "چیزای واقعی", "N": "ایده‌های ذهنی"}),
    ("چطوری بهتر یاد می‌گیری؟", {"S": "با تجربه عملی", "N": "با درک مفاهیم"}),
    ("در یک جمع شلوغ، معمولاً...", {"E": "انرژی می‌گیرم", "I": "خسته می‌شم"}),
    ("در روابط عاطفی، بیشتر...", {"F": "با احساساتم تصمیم می‌گیرم", "T": "با منطق تصمیم می‌گیرم"}),
    ("ترجیح می‌دی برنامه‌هات چطور باشن؟", {"J": "منظم و برنامه‌ریزی‌شده", "P": "آزاد و انعطاف‌پذیر"}),
]

# شروع اولیه
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! برای شروع تست شخصیت‌شناسی MBTI دستور /test رو بزن.")

# شروع تست
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    active_users.add(user_id)
    user_states[user_id] = 0
    user_answers[user_id] = []
    await update.message.reply_text(
        "تست شخصیت MBTI شروع شد!\nبرای پاسخ، روی پیام سؤال ریپلای بزن و گزینه موردنظرت رو دقیقاً بنویس (مثلاً: جزئیات و واقعیت‌ها)"
    )
    await send_question(update, context, user_id)

# ارسال سؤال
async def send_question(update, context, user_id):
    index = user_states[user_id]
    q_text, options = questions[index]
    options_text = "\n".join([f"- {v} = {k}" for k, v in options.items()])
    await context.bot.send_message(
        chat_id=user_id,
        text=f"سؤال {index+1}:\n{q_text}\n\n{options_text}"
    )

# پردازش پاسخ
async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_states:
        return
    if not update.message.reply_to_message:
        return

    current_q = user_states[user_id]
    _, options = questions[current_q]
    text = update.message.text.strip()

    matched = False
    for key, val in options.items():
        if text == val:
            user_answers[user_id].append(key)
            matched = True
            break

    if not matched:
        await update.message.reply_text("❗ لطفاً دقیقاً یکی از گزینه‌ها رو بنویس.")
        return

    user_states[user_id] += 1
    if user_states[user_id] >= len(questions):
        await finish_test(update, context, user_id)
    else:
        await send_question(update, context, user_id)

# محاسبه تیپ
def calculate_type(answers):
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for a in answers:
        scores[a] += 1
    return "".join([
        "E" if scores["E"] >= scores["I"] else "I",
        "S" if scores["S"] >= scores["N"] else "N",
        "T" if scores["T"] >= scores["F"] else "F",
        "J" if scores["J"] >= scores["P"] else "P"
    ])

# پایان تست و نمایش نتیجه
async def finish_test(update, context, user_id):
    mbti = calculate_type(user_answers[user_id])
    user_results[user_id] = mbti
    profile = mbti_data.get(mbti, {})
    description = profile.get("description", "توضیحی موجود نیست.")
    strengths = "\n".join(profile.get("strengths", []))
    weaknesses = "\n".join(profile.get("weaknesses", []))
    partners = ", ".join(profile.get("ideal_partners", []))
    similar = ", ".join(profile.get("similar_types", []))

    msg = (
        f"✅ تست MBTI شما کامل شد!\n\n"
        f"👤 تیپ شخصیتی: <b>{mbti}</b>\n\n"
        f"🧠 توضیح:\n{description}\n\n"
        f"✅ نقاط قوت:\n{strengths}\n\n"
        f"⚠️ نقاط ضعف:\n{weaknesses}\n\n"
        f"❤️ مناسب برای ازدواج: {partners}\n"
        f"👥 تیپ‌های مشابه: {similar}"
    )
    await context.bot.send_message(chat_id=user_id, text=msg, parse_mode=ParseMode.HTML)
    # پاک‌سازی وضعیت
    user_states.pop(user_id)
    user_answers.pop(user_id)

# نمایش دوباره پروفایل
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_results:
        await update.message.reply_text("❌ هنوز تست ندادی. با /test شروع کن.")
        return
    await finish_test(update, context, user_id)

# مقایسه تیپ‌ها
async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) != 1:
        await update.message.reply_text("مثال: /compare 123456789")
        return
    try:
        target_id = int(context.args[0])
    except:
        await update.message.reply_text("شناسه عددی معتبر نیست.")
        return

    mbti1 = user_results.get(user_id)
    mbti2 = user_results.get(target_id)
    if not mbti1 or not mbti2:
        await update.message.reply_text("هر دو کاربر باید تست رو داده باشن.")
        return
    diff = sum(1 for a, b in zip(mbti1, mbti2) if a != b)
    await update.message.reply_text(f"👤 شما: {mbti1}\n👤 کاربر مقابل: {mbti2}\n📊 تفاوت شخصیتی: {diff} مورد")

# فیلتر سایر پیام‌ها
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in active_users:
        return

# اجرای اصلی
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
