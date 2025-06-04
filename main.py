from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

# سوالات MBTI (16 سوال)
QUESTIONS = [
    {"q": "در یک مهمانی شلوغ، بیشتر انرژی می‌گیری یا خسته می‌شی؟", "A": ("I", "خسته می‌شم و ترجیح می‌دم زود برگردم"), "B": ("E", "انرژی می‌گیرم و لذت می‌برم")},
    {"q": "در زمان بیکاری ترجیح می‌دی تنها باشی یا با دیگران؟", "A": ("I", "تنهایی برای من شارژ کننده‌ست"), "B": ("E", "در کنار دیگران خوش می‌گذره")},
    {"q": "در حل مسئله بیشتر به چی توجه می‌کنی؟", "A": ("S", "واقعیت‌ها و جزئیات"), "B": ("N", "ایده‌ها و احتمالات")},
    {"q": "وقتی درباره چیزی فکر می‌کنی، تمرکزت روی چیه؟", "A": ("S", "حقایق موجود"), "B": ("N", "آنچه می‌تونه باشه")},
    {"q": "موقع تصمیم‌گیری بیشتر به چی تکیه می‌کنی؟", "A": ("T", "منطق و تحلیل"), "B": ("F", "احساسات و همدلی")},
    {"q": "اگه دوستت ازت مشورت بخواد...", "A": ("T", "واقع‌بینانه و منطقی نظر می‌دم"), "B": ("F", "اول احساسش رو درک می‌کنم")},
    {"q": "کدوم جمله بهت نزدیک‌تره؟", "A": ("J", "برنامه‌ریزی و نظم"), "B": ("P", "انعطاف و آزاد بودن")},
    {"q": "موقع کار یا درس...", "A": ("J", "برنامه دارم و طبق زمان‌بندی پیش می‌رم"), "B": ("P", "هر وقت حسش باشه انجام می‌دم")},
    {"q": "تعطیلات رو چطور می‌گذرونی؟", "A": ("I", "ترجیح می‌دم با خودم یا جمع کوچیک باشم"), "B": ("E", "با جمع‌های بزرگ تفریحی")},
    {"q": "موقع فکر کردن بیشتر دنبال...", "A": ("S", "واقعیت‌های ملموس"), "B": ("N", "معناها و احتمالات")},
    {"q": "وقتی یکی اشتباه می‌کنه...", "A": ("T", "راستشو می‌گم حتی اگه ناراحت بشه"), "B": ("F", "سعی می‌کنم احساسش رو در نظر بگیرم")},
    {"q": "برنامه‌هات رو چطور مدیریت می‌کنی؟", "A": ("J", "لیست و ساختارمند"), "B": ("P", "آزاد و بدون محدودیت")},
    {"q": "دوست داری چطور زندگی کنی؟", "A": ("J", "قابل پیش‌بینی و منظم"), "B": ("P", "هیجان‌انگیز و بدون چارچوب")},
    {"q": "در بحث و گفت‌وگو معمولاً...", "A": ("T", "تحلیلی و منطقی صحبت می‌کنم"), "B": ("F", "با همدلی و احساس پیش می‌رم")},
    {"q": "وقتی کسی ازت سؤال می‌پرسه...", "A": ("S", "به واقعیت پاسخ می‌دم"), "B": ("N", "نگاه آینده‌نگر دارم")},
    {"q": "وقتی وارد یه جمع جدید می‌شی...", "A": ("I", "کم‌کم گرم می‌گیرم"), "B": ("E", "سریع با همه ارتباط می‌گیرم")}
]

TYPES = {
    "INTJ": "معمار – متفکر استراتژیک، ساکت و تحلیلی",
    "ENTP": "مبتکر – پر از ایده، عاشق بحث و ماجراجویی",
    "INFP": "میانجی – ایده‌آل‌گرا، مهربون و درون‌گرا",
    "ENFP": "قهرمان – خلاق، احساسی و اجتماعی",
    "ISTJ": "بازرس – دقیق، مسئولیت‌پذیر و قابل اعتماد",
    "ISFJ": "حامی – وفادار، مهربون و عمل‌گرا",
    "ESTP": "کارآفرین – پرجنب‌وجوش، با انرژی و واقع‌گرا",
    "ESFJ": "کنسول – اجتماعی، مسئولیت‌پذیر و دلسوز",
    # بقیه تیپ‌ها رو هم می‌تونی اضافه کنی
}

user_states = {}

def get_mbti(answers):
    dim = {"I": 0, "E": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for d in answers:
        dim[d] += 1
    return ("I" if dim["I"] > dim["E"] else "E") + \
           ("S" if dim["S"] > dim["N"] else "N") + \
           ("T" if dim["T"] > dim["F"] else "F") + \
           ("J" if dim["J"] > dim["P"] else "P")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 🤖\nبه ربات آینه شخصیت خوش اومدی!\nبرای شروع تست MBTI، دستور /test رو بزن 🧠")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_states[user_id] = {"step": 0, "answers": []}
    await send_question(update, user_id)

async def send_question(update, user_id):
    step = user_states[user_id]["step"]
    q = QUESTIONS[step]
    markup = ReplyKeyboardMarkup([["A", "B"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(f"سؤال {step+1} از {len(QUESTIONS)}:\n{q['q']}\nA) {q['A'][1]}\nB) {q['B'][1]}", reply_markup=markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip().upper()

    if user_id not in user_states:
        await update.message.reply_text("برای شروع تست /test رو بزن.")
        return

    state = user_states[user_id]
    if text not in ["A", "B"]:
        await update.message.reply_text("❗️لطفاً فقط A یا B جواب بده.")
        return

    question = QUESTIONS[state["step"]]
    state["answers"].append(question[text][0])
    state["step"] += 1

    if state["step"] >= len(QUESTIONS):
        mbti = get_mbti(state["answers"])
        name = TYPES.get(mbti, "تیپ شخصیتی خاص و کمیاب")
        await update.message.reply_text(f"✅ نتیجه تست شخصیت:\n🎭 تیپ تو: {mbti}\n🔹 توضیح: {name}")
        del user_states[user_id]
        profiles = json.load(open("profiles.json", "r")) if os.path.exists("profiles.json") else {}
        profiles[str(user_id)] = mbti
        json.dump(profiles, open("profiles.json", "w"), indent=2)
    else:
        await send_question(update, user_id)

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if os.path.exists("profiles.json"):
        profiles = json.load(open("profiles.json", "r"))
        if user_id in profiles:
            mbti = profiles[user_id]
            name = TYPES.get(mbti, "تیپ شخصیتی خاص")
            await update.message.reply_text(f"📊 پروفایل تو:\n🧬 MBTI: {mbti}\n🔹 {name}")
            return
    await update.message.reply_text("❌ هنوز تست ندادی. با /test شروع کن.")

if __name__ == "__main__":
    TOKEN = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
