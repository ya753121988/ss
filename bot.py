import os
import requests
import telebot
from PIL import Image, ImageFont
from pilmoji import Pilmoji

# ==========================================
# ১. বটের বেসিক কনফিগারেশন
# ==========================================
# Render-এর Environment Variable থেকে টোকেন নেবে
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'এখানে_আপনার_বট_টোকেন_দিন')
bot = telebot.TeleBot(BOT_TOKEN)

# ফন্ট এবং ছবির নাম সেটআপ
FONT_URL = "https://raw.githubusercontent.com/whtsky/Kalpurush/master/kalpurush.ttf"
FONT_PATH = "kalpurush.ttf"
TEMPLATE_PATH = "template.png"

# ==========================================
# ২. অটোমেটিক বাংলা ফন্ট ডাউনলোড সিস্টেম
# ==========================================
def download_font():
    if not os.path.exists(FONT_PATH):
        print("বাংলা ফন্ট ডাউনলোড হচ্ছে...")
        response = requests.get(FONT_URL)
        with open(FONT_PATH, 'wb') as f:
            f.write(response.content)
        print("ফন্ট ডাউনলোড সফল!")

# কোড রান হওয়ার সাথে সাথেই ফন্ট নামিয়ে নেবে
download_font()

# ==========================================
# ৩. স্টার্ট ও ওয়েলকাম মেসেজ ডিজাইন
# ==========================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_msg = (
        "👋 স্বাগতম ডায়েরির শেষ পাতা বটে!\n\n"
        "আমি আপনার ফেসবুক স্ক্রিনশটে অটোমেটিক বাংলা টেক্সট ও ইমোজি বসিয়ে দেবো।\n\n"
        "🛠️ **কীভাবে ব্যবহার করবেন:**\n"
        "১. প্রথমে আপনার ওই **'ফাঁকা স্ক্রিনশট'** (Photo) আমাকে সেন্ড করুন।\n"
        "২. এরপর আপনি যে ক্যাপশনটি ছবির ওপর বসাতে চান, সেটা লিখে সেন্ড করুন (ইমোজিসহ)।\n"
        "৩. আমি ম্যাজিকের মতো আপনার লেখাটি ছবির ওপর বসিয়ে নতুন ছবি দিয়ে দেবো!"
    )
    bot.reply_to(message, welcome_msg)

# ==========================================
# ৪. ছবি রিসিভ এবং সেভ করার ফিউচার 
# ==========================================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        processing_msg = bot.reply_to(message, "আপনার টেমপ্লেট ছবি সেভ করা হচ্ছে... ⏳")
        
        # টেলিগ্রাম থেকে সবচেয়ে হাই-কোয়ালিটি ছবিটি ডাউনলোড করা
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # template.png নামে সেভ করা
        with open(TEMPLATE_PATH, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.delete_message(message.chat.id, processing_msg.message_id)
        bot.reply_to(message, "✅ আপনার স্ক্রিনশট সফলভাবে সেভ হয়েছে! \n\nএবার আপনার ছোট প্রশ্ন ও উত্তরগুলো (ইমোজিসহ) লিখে পাঠান।")
    
    except Exception as e:
        bot.reply_to(message, f"❌ ছবি সেভ করতে সমস্যা হয়েছে: {e}")

# ==========================================
# ৫. টেক্সট ও ইমোজি ছবির ওপর বসানোর মেইন কোড
# ==========================================
@bot.message_handler(func=lambda message: True, content_types=['text'])
def generate_post(message):
    text = message.text
    chat_id = message.chat.id
    
    # আগে চেক করবে ইউজার ছবি দিয়েছে কিনা
    if not os.path.exists(TEMPLATE_PATH):
        bot.send_message(chat_id, "❌ আগে আমাকে আপনার ফাঁকা স্ক্রিনশটটি (Photo) দিন! তারপর টেক্সট দিন।")
        return

    # প্রসেসিং মেসেজ
    processing_msg = bot.send_message(chat_id, "ডিজাইন তৈরি হচ্ছে, একটু অপেক্ষা করুন... 🎨⏳")

    try:
        # ছবি ওপেন করা
        img = Image.open(TEMPLATE_PATH).convert("RGBA")
        
        # ফন্ট সাইজ (৪৫ দেওয়া আছে, চাইলে বাড়াতে/কমাতে পারবেন)
        font = ImageFont.truetype(FONT_PATH, 45)

        # Pilmoji দিয়ে বাংলা + ইংরেজি + ইমোজি বসানো 
        # (40, 205) হলো লেখার পজিশন, fill=(0,0,0) মানে কালো রং, spacing=10 হলো দুই লাইনের গ্যাপ
        with Pilmoji(img) as pilmoji:
            pilmoji.text((40, 205), text, fill=(0, 0, 0), font=font, spacing=12)

        # নতুন তৈরি হওয়া ছবি সেভ করা
        output_path = f"final_post_{chat_id}.png"
        img.save(output_path)

        # ইউজারকে ফাইনাল ছবি পাঠানো
        with open(output_path, "rb") as photo:
            bot.send_photo(chat_id, photo)
            
        # কাজ শেষ হলে সার্ভার থেকে এক্সট্রা মেসেজ ও ছবি ক্লিয়ার করে দেওয়া
        bot.delete_message(chat_id, processing_msg.message_id)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(chat_id, f"❌ কোডে একটি সমস্যা হয়েছে: {e}")

# ==========================================
# ৬. সার্ভার যেন অফ না হয় তার সিস্টেম (Infinity Polling)
# ==========================================
print("✅ বট সফলভাবে চালু হয়েছে... টেলিগ্রামে মেসেজ দিন!")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
