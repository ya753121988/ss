import os
import requests
import telebot
from PIL import Image, ImageFont
from pilmoji import Pilmoji

# টেলিগ্রাম বট টোকেন (Render-এ Environment Variable থেকে নেবে)
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'এখানে_আপনার_টেলিগ্রাম_বট_টোকেন_দিন')
bot = telebot.TeleBot(BOT_TOKEN)

# বাংলা ফন্ট অটোমেটিক ডাউনলোড করার সিস্টেম (যাতে আপনাকে কিছু করতে না হয়)
FONT_URL = "https://raw.githubusercontent.com/whtsky/Kalpurush/master/kalpurush.ttf"
FONT_PATH = "kalpurush.ttf"

def download_font():
    if not os.path.exists(FONT_PATH):
        print("বাংলা ফন্ট ডাউনলোড হচ্ছে...")
        response = requests.get(FONT_URL)
        with open(FONT_PATH, 'wb') as f:
            f.write(response.content)
        print("ফন্ট ডাউনলোড সফল!")

# বট চালু হওয়ার আগেই ফন্ট ডাউনলোড করে নেবে
download_font()

# বট স্টার্ট করলে এই মেসেজ দেবে
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "স্বাগতম! আমাকে আপনার ক্যাপশন লিখে দিন (ইমোজি সহ)। আমি অটোমেটিক আপনার ছবির ওপর বসিয়ে দেবো।"
    bot.reply_to(message, welcome_text)

# যেকোনো টেক্সট দিলে সে ছবি বানিয়ে দেবে
@bot.message_handler(func=lambda message: True)
def generate_post(message):
    text = message.text
    chat_id = message.chat.id
    
    # বটকে প্রসেসিং মেসেজ দেওয়া
    bot.send_message(chat_id, "ছবি তৈরি হচ্ছে, একটু অপেক্ষা করুন... ⏳")

    try:
        # আপনার ফাঁকা স্ক্রিনশটটি ওপেন করবে (ফাইলের নাম template.png হতে হবে)
        if os.path.exists("template.png"):
            img = Image.open("template.png").convert("RGBA")
        elif os.path.exists("template.jpg"):
            img = Image.open("template.jpg").convert("RGBA")
        else:
            bot.send_message(chat_id, "❌ 'template.png' নামের কোনো ছবি পাওয়া যায়নি! দয়া করে আপনার স্ক্রিনশটটি ফোল্ডারে রাখুন।")
            return

        # ফন্ট সাইজ (আপনার ছবির রেজুলেশন অনুযায়ী সাইজ 45 থেকে বাড়াতে/কমাতে পারেন)
        font = ImageFont.truetype(FONT_PATH, 45)

        # Pilmoji দিয়ে বাংলা, ইংরেজি এবং ইমোজি ছবির ওপর বসানো
        with Pilmoji(img) as pilmoji:
            # (40, 205) হলো লেখার পজিশন। আপনার ছবি অনুযায়ী একটু উপরে নিচে করতে হতে পারে।
            # (0, 0, 0) হলো কালো রঙের কোড।
            pilmoji.text((40, 205), text, (0, 0, 0), font=font)

        # তৈরি হওয়া ছবিটি সেভ করা
        output_path = f"final_post_{chat_id}.png"
        img.save(output_path)

        # ব্যবহারকারীকে ছবিটি পাঠানো
        with open(output_path, "rb") as photo:
            bot.send_photo(chat_id, photo)
            
        # পাঠানো শেষ হলে সার্ভার থেকে ডিলিট করে দেওয়া (জায়গা বাঁচানোর জন্য)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(chat_id, f"❌ একটি সমস্যা হয়েছে: {e}")

# বট কন্টিনিউয়াস চালানোর জন্য
print("বট সফলভাবে চালু হয়েছে...")
bot.polling(none_stop=True)
