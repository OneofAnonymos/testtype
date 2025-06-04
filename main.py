import logging from telegram import Update, ReplyKeyboardRemove from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes import asyncio

راه‌اندازی لاگر

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

دیتابیس ساده داخل حافظه برای کاربران

user_data = {}

سوالات تست MBTI

questions = [ ("در یک مهمانی شلوغ، بیشتر احساس انرژی می‌کنی یا خسته می‌شی؟", ("انرژی می‌گیرم", "خسته می‌شم"), "E", "I"), ("بیشتر دوست داری کارهات برنامه‌ریزی‌شده باشه یا انعطاف‌پذیر؟", ("برنامه‌ریزی‌شده", "انعطاف‌پذیر"), "J", "P"), ("در تصمیم‌گیری، احساسات مهم‌ترن یا منطق؟", ("احساسات", "منطق"), "F", "T"), ("بیشتر روی جزئیات تمرکز می‌کنی یا تصویر کلی؟", ("جزئیات", "تصویر کلی"), "S", "N"), # سوالات اضافه‌تر برای دقت بیشتر ("وقتی با کسی آشنا می‌شی، سریع صمیمی می‌شی یا زمان می‌بره؟", ("سریع صمیمی می‌شم", "زمان می‌بره"), "E", "I"), ("برای حل مشکلات بیشتر به شهود تکیه می‌کنی یا تجربه؟", ("شهود", "تجربه"), "N", "S"), ("دوست داری یک روز برنامه‌ریزی‌شده داشته باشی یا آزاد باشه؟", ("برنامه‌ریزی‌شده", "آزاد"), "J", "P"), ("در بحث‌ها بیشتر دنبال حقایقی یا احساسات افراد؟", ("حقایق", "احساسات"), "T", "F") ]

mbti_profiles = { "INTJ": { "title": "معمار (INTJ)", "strengths": ["استراتژیک", "مستقل", "تحلیلی"], "weaknesses": ["کمال‌گرا", "کم‌حوصله"], "compatible": ["ENFP", "ENTP"], "similar": ["INFJ", "INTP"], "anime": "L (Death Note)" }, "ENFP": { "title": "فعال (ENFP)", "strengths": ["خلاق", "پرانرژی", "احساساتی"], "weaknesses": ["بی‌نظم", "احساساتی زیاد"], "compatible": ["INFJ", "INTJ"], "similar": ["INFP", "ENFJ"], "anime": "Naruto Uzumaki" }, # بقیه تیپ‌ها رو هم می‌تونم اضافه کنم }

def calculate_mbti(answers): letters = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0} for i, ans in enumerate(answers): q = questions[i] letters[q[2 if ans == 0 else 3]] += 1 return ("E" if letters["E"] >= letters["I"] else "I") + 
("S" if letters["S"] >= letters["N"] else "N") + 
("T" if letters["T"] >= letters["F"] else "F") + 
("J" if letters["J"] >= letters["P"] else "P")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("سلام! برای شروع تست شخصیت‌شناسی MBTI دستور /test رو بزن.")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.message.from_user.id user_data[user_id] = {"answers": [], "current": 0, "active": True, "chat_id": update.effective_chat.id} await send_question(update, context, user_id)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id): current = user_data[user_id]["current"] if current < len(questions): q, opts, *_ = questions[current] await context.bot.send_message(chat_id=user_data[user_id]["chat_id"], text=f"❓ {q}\n1️⃣ {opts[0]}\n2️⃣ {opts[1]}") else: mbti = calculate_mbti(user_data[user_id]["answers"]) user_data[user_id]["active"] = False profile = mbti_profiles.get(mbti, None) if profile: await update.message.reply_text(f"✅ تست تموم شد!\n\nتیپ شخصیتی تو: {mbti}\n{profile['title']}", parse_mode="Markdown") await update.message.reply_text(f"✨ نقاط قوت: {', '.join(profile['strengths'])}\n⚠️ نقاط ضعف: {', '.join(profile['weaknesses'])}\n💞 مناسب ازدواج: {', '.join(profile['compatible'])}\n👯‍♂️ تیپ‌های نزدیک: {', '.join(profile['similar'])}\n🎌 شخصیت انیمه‌ای مشابه: {profile['anime']}") else: await update.message.reply_text(f"تیپ شخصیتی تو: {mbti}")

async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.message.from_user.id if user_id not in user_data or not user_data[user_id].get("active"): return if not update.message.reply_to_message: return text = update.message.text.strip() if text == "1" or text == "۱": user_data[user_id]["answers"].append(0) elif text == "2" or text == "۲": user_data[user_id]["answers"].append(1) else: await update.message.reply_text("فقط عدد 1 یا 2 رو وارد کن با ریپلای به سؤال.") return user_data[user_id]["current"] += 1 await send_question(update, context, user_id)

def main(): app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build() app.add_handler(CommandHandler("start", start)) app.add_handler(CommandHandler("test", test)) app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, answer_handler))

# پیامی که کاربر عادی می‌ده و تست رو شروع نکرده
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برای شروع تست، دستور /test رو بزن ✅")

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
app.run_polling()

if name == 'main': main()

