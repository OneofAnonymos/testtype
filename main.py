import os import json from telegram import Update, ReplyKeyboardMarkup from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

بارگذاری توکن از متغیر محیطی رندر

BOT_TOKEN = os.environ.get("BOT_TOKEN")

وضعیت کاربران

user_states = {} user_answers = {} user_results = {}

سوالات تست MBTI (نمونه‌ای با تعداد زیادتر)

survey_questions = [ ("در مهمانی‌ها ترجیح می‌دهید؟", ["با همه صحبت کنم (E)", "فقط با چند نفر خاص باشم (I)"]), ("بیشتر به واقعیت‌ها توجه دارید یا مفاهیم؟", ["واقعیت‌ها (S)", "مفاهیم (N)"]), ("تصمیماتتان بیشتر بر اساس؟", ["منطق (T)", "احساس (F)"]), ("ترجیح می‌دهید برنامه‌ریزی داشته باشید یا خودجوش باشید؟", ["برنامه‌ریزی (J)", "خودجوش (P)"]), ("ترجیح می‌دهم روزم را چگونه بگذرانم؟", ["با دیگران در تعامل باشم (E)", "تنهایی کار کنم (I)"]), ("در حل مشکلات بیشتر تمرکز دارید روی؟", ["تجربیات گذشته (S)", "ایده‌های نو (N)"]), ("در موقعیت‌های احساسی؟", ["سعی می‌کنم منطقی باشم (T)", "به احساساتم گوش می‌دهم (F)"]), ("در کارها؟", ["همه چیز طبق برنامه پیش برود (J)", "بر اساس موقعیت تصمیم می‌گیرم (P)"]), # سوالات بیشتری می‌توان اضافه کرد ]

mbti_profiles = { "INTJ": { "strengths": "تحلیلی، آینده‌نگر، مستقل", "weaknesses": "لجباز، بیش‌ازحد درونگرا، انتقادی", "matches": "ENFP, ENTP", "similar": "INFJ, INTP", "anime": "L (Death Note)" }, "INFP": { "strengths": "خلاق، با احساس، آرمان‌گرا", "weaknesses": "بیش از حد احساساتی، حساس", "matches": "ENFJ, ENTJ", "similar": "ISFP, INFJ", "anime": "Shinji Ikari (Evangelion)" }, "INFJ": {"strengths": "درون‌گرا، بینش‌مند، عمیق", "weaknesses": "کمال‌گرا، گاهی منزوی", "matches": "ENFP, ENTP", "similar": "INTJ, INFP", "anime": "Itachi Uchiha (Naruto)"}, "INTP": {"strengths": "تحلیل‌گر، مبتکر، کنجکاو", "weaknesses": "دور از احساس، گاهی تنبل", "matches": "ENTP, INFP", "similar": "INTJ, ENTP", "anime": "Lain Iwakura (Serial Experiments Lain)"}, "ENFP": {"strengths": "شورمند، الهام‌بخش، خلاق", "weaknesses": "بی‌نظم، بیش‌فعال", "matches": "INFJ, INTJ", "similar": "ENFJ, INFP", "anime": "Naruto Uzumaki (Naruto)"}, "ENFJ": {"strengths": "رهبری، دلسوز، هدف‌مند", "weaknesses": "وابسته به تأیید، عجول", "matches": "INFP, ISFP", "similar": "ENFP, INFJ", "anime": "Tanjiro Kamado (Demon Slayer)"}, "ENTP": {"strengths": "پر انرژی، خلاق، زیرک", "weaknesses": "کم‌حوصله، اهل بحث", "matches": "INFJ, INFP", "similar": "ENTJ, ENFP", "anime": "Okabe Rintarou (Steins;Gate)"}, "ENTJ": {"strengths": "رهبری، تصمیم‌گیرنده، منطقی", "weaknesses": "سلطه‌گر، سخت‌گیر", "matches": "INFP, ISFP", "similar": "INTJ, ESTJ", "anime": "Light Yagami (Death Note)"}, "ISFJ": {"strengths": "وفادار، محتاط، فداکار", "weaknesses": "کناره‌گیر، از خودگذشته زیاد", "matches": "ESFP, ESTP", "similar": "ISTJ, INFJ", "anime": "Hinata Hyuga (Naruto)"}, "ISFP": {"strengths": "احساسی، آرام، انعطاف‌پذیر", "weaknesses": "پنهان‌کار، زود رنج", "matches": "ESFJ, ENFJ", "similar": "INFP, ISFJ", "anime": "Yuki Sohma (Fruits Basket)"}, "ISTJ": {"strengths": "وظیفه‌شناس، منظم، واقع‌گرا", "weaknesses": "لجباز، سرد", "matches": "ESFP, ESTP", "similar": "ISFJ, INTJ", "anime": "Levi Ackerman (Attack on Titan)"}, "ISTP": {"strengths": "تحلیل‌گر، مستقل، اهل عمل", "weaknesses": "بی‌احساس، منزوی", "matches": "ESFP, ESTP", "similar": "INTP, ESTP", "anime": "Spike Spiegel (Cowboy Bebop)"}, "ESFJ": {"strengths": "اجتماعی، مهربان، وفادار", "weaknesses": "بیش‌ازحد نگران نظر دیگران", "matches": "ISFP, INFP", "similar": "ENFJ, ISFJ", "anime": "Tohru Honda (Fruits Basket)"}, "ESFP": {"strengths": "ماجراجو، خونگرم، سرگرم‌کننده", "weaknesses": "بی‌برنامه، سطحی", "matches": "ISFJ, ISTJ", "similar": "ENFP, ESFJ", "anime": "Narumi Momose (Wotakoi)"}, "ESTJ": {"strengths": "سازمان‌دهنده، قاطع، کارآمد", "weaknesses": "خشک، کنترل‌گر", "matches": "ISTP, ISFP", "similar": "ENTJ, ESTP", "anime": "Asuka Langley (Evangelion)"}, "ESTP": {"strengths": "اهل عمل، ریسک‌پذیر، واقع‌گرا", "weaknesses": "بی‌فکر، کم‌حوصله", "matches": "ISFP, INFP", "similar": "ISTP, ESTJ", "anime": "Bakugo (My Hero Academia)"}, }

محاسبه تیپ MBTI

def calculate_mbti(answers): counts = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0} for a in answers: code = a.split("(")[-1].strip(")") if code in counts: counts[code] += 1 return ("E" if counts["E"] >= counts["I"] else "I") + 
("S" if counts["S"] >= counts["N"] else "N") + 
("T" if counts["T"] >= counts["F"] else "F") + 
("J" if counts["J"] >= counts["P"] else "P")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("سلام! برای شروع تست شخصیت MBTI دستور /test رو بزنید.")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.effective_user.id user_states[user_id] = 0 user_answers[user_id] = [] await update.message.reply_text("تست شروع شد. به هر سوال با ریپلای پاسخ دهید:") q, options = survey_questions[0] markup = ReplyKeyboardMarkup([options], one_time_keyboard=True, resize_keyboard=True) await update.message.reply_text(f"1. {q}", reply_markup=markup)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): if not update.message.reply_to_message: return

user_id = update.effective_user.id
if user_id not in user_states:
    return

index = user_states[user_id]
user_answers[user_id].append(update.message.text)
user_states[user_id] += 1

if user_states[user_id] >= len(survey_questions):
    mbti = calculate_mbti(user_answers[user_id])
    user_results[user_id] = mbti
    profile = mbti_profiles.get(mbti, {})
    text = f"تیپ شخصیت شما: {mbti}\n\n"
    text += f"نقاط قوت: {profile.get('strengths', 'ندارد')}\n"
    text += f"نقاط ضعف: {profile.get('weaknesses', 'ندارد')}\n"
    text += f"تیپ‌های مشابه: {profile.get('similar', 'ندارد')}\n"
    text += f"مناسب ازدواج: {profile.get('matches', 'نامشخص')}\n"
    text += f"شخصیت انیمه مشابه: {profile.get('anime', 'نامشخص')}"
    await update.message.reply_text(text)
    del user_states[user_id]
    del user_answers[user_id]
else:
    q, options = survey_questions[user_states[user_id]]
    markup = ReplyKeyboardMarkup([options], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(f"{user_states[user_id]+1}. {q}", reply_markup=markup)

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = update.effective_user.id mbti = user_results.get(user_id) if not mbti: await update.message.reply_text("شما هنوز تست شخصیت رو کامل نکردید. اول /test رو بزنید.") return profile = mbti_profiles.get(mbti, {}) text = f"📘 پروفایل شخصیت شما ({mbti}):\n" text += f"- نقاط قوت: {profile.get('strengths')}\n" text += f"- نقاط ضعف: {profile.get('weaknesses')}\n" text += f"- مشابه‌ترین تیپ‌ها: {profile.get('similar')}\n" text += f"- مناسب‌ترین برای ازدواج: {profile.get('matches')}\n" text += f"- شخصیت انیمه‌ای مشابه: {profile.get('anime')}" await update.message.reply_text(text)

async def compare_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): if not context.args or not context.args[0].isdigit(): await update.message.reply_text("لطفاً آیدی عددی کاربر رو وارد کن: /compare 12345678") return user_id = update.effective_user.id other_id = int(context.args[0]) mbti1 = user_results.get(user_id) mbti2 = user_results.get(other_id) if not mbti1 or not mbti2: await update.message.reply_text("هر دو کاربر باید تست رو کامل کرده باشند.") return result = "✅ تشابه زیاد" if mbti1[:2] == mbti2[:2] else "⚠️ تفاوت زیاد" await update.message.reply_text(f"مقایسه بین شما ({mbti1}) و کاربر {other_id} ({mbti2}):\n{result}")

if name == "main": app = ApplicationBuilder().token(BOT_TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(CommandHandler("test", test)) app.add_handler(CommandHandler("profile", profile_handler)) app.add_handler(CommandHandler("compare", compare_handler)) app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, message_handler)) app.run_polling()

