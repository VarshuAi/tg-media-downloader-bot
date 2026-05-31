import os
import re
import time
import glob
import logging
from dotenv import load_dotenv
import telebot
import yt_dlp

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in the environment or .env file!")

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Bot
bot = telebot.TeleBot(BOT_TOKEN)

# Set global timeouts for pyTelegramBotAPI to handle large uploads smoothly on slow connections
telebot.apihelper.CONNECT_TIMEOUT = 90
telebot.apihelper.READ_TIMEOUT = 300

# Ensure downloads folder exists
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Regex to detect links
URL_PATTERN = re.compile(r'(https?://[^\s]+)')

def clean_ansi(text):
    """Strip ANSI escape sequences from strings."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def to_bold_sans(text):
    """Convert standard alphanumeric characters to mathematical bold sans-serif."""
    result = []
    for char in text:
        o = ord(char)
        if 0x41 <= o <= 0x5A:  # A-Z
            result.append(chr(o - 0x41 + 0x1D5D4))
        elif 0x61 <= o <= 0x7A:  # a-z
            result.append(chr(o - 0x61 + 0x1D5EE))
        elif 0x30 <= o <= 0x39:  # 0-9
            result.append(chr(o - 0x30 + 0x1D7EC))
        else:
            result.append(char)
    return "".join(result)

def to_italic_sans(text):
    """Convert standard letters to mathematical italic sans-serif."""
    result = []
    for char in text:
        o = ord(char)
        if 0x41 <= o <= 0x5A:  # A-Z
            result.append(chr(o - 0x41 + 0x1D608))
        elif 0x61 <= o <= 0x7A:  # a-z
            result.append(chr(o - 0x61 + 0x1D622))
        else:
            result.append(char)
    return "".join(result)

def to_bold_italic_sans(text):
    """Convert standard letters to mathematical bold italic sans-serif."""
    result = []
    for char in text:
        o = ord(char)
        if 0x41 <= o <= 0x5A:  # A-Z
            result.append(chr(o - 0x41 + 0x1D63C))
        elif 0x61 <= o <= 0x7A:  # a-z
            result.append(chr(o - 0x61 + 0x1D656))
        else:
            result.append(char)
    return "".join(result)

def make_progress_hook(chat_id, message_id, title):
    """Generate a throttled progress hook for yt-dlp."""
    last_update = [0.0]  # Mutable storage inside closure
    
    def hook(d):
        if d['status'] == 'downloading':
            now = time.time()
            # Throttled to update at most once every 3.5 seconds to avoid Telegram rate limits
            if now - last_update[0] > 3.5:
                # Clean up yt-dlp values
                percent = clean_ansi(d.get('_percent_str', '0%')).strip()
                speed = clean_ansi(d.get('_speed_str', 'N/A')).strip()
                eta = clean_ansi(d.get('_eta_str', 'N/A')).strip()
                
                status_text = (
                    f"⚡ *{to_bold_sans('FETCHING THE MEDIA... RUNNIN` UP!')}* 🔥\n\n"
                    f"🎬 *{to_bold_sans('TRACK:')}* `{title[:40]}...`\n"
                    f"📈 *{to_bold_sans('PROGRESS:')}* `{percent}` (no cap 🧢)\n"
                    f"⚡ *{to_bold_sans('SPEED:')}* `{speed}`\n"
                    f"⏳ *{to_bold_sans('ETA:')}* `{eta}`\n\n"
                    f"⚡ ━━━━━━━━━━━━━━━━━━━━ ⚡\n"
                    f"_{to_italic_sans('Almost there, bestie! we cookin\' fr fr')}_ 💅"
                )
                try:
                    bot.edit_message_caption(
                        chat_id=chat_id,
                        message_id=message_id,
                        caption=status_text,
                        parse_mode="Markdown"
                    )
                    last_update[0] = now
                except Exception as e:
                    logger.debug(f"Progress update skipped: {e}")
                    
    return hook

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_photo = "assets/welcome.png"
    welcome_text = (
        f"✨ ━━━━━━━━━━━━━━━━━━━━ ✨\n"
        f"👋 *{to_bold_sans('YO! WELCOME TO THE ULTIMATE DOWNLOADER')}* 🔥\n\n"
        f"{to_italic_sans('We don\'t do slow downloads here, fr fr. Send me any link and watch me cook!')} 💅🚀\n\n"
        f"⚡ *{to_bold_sans('HOW TO SUMMON MY POWER:')}*\n"
        f"Just copy-paste and *drop any link* from:\n"
        f"• *YouTube* (videos or shorts)\n"
        f"• *Instagram* (reels and posts)\n"
        f"• *TikTok* (pure brain rot 💀)\n"
        f"• *Twitter / X* (memes and hot takes)\n"
        f"• *Pinterest* (aesthetic inspo)\n\n"
        f"🚀 *{to_bold_sans('WHY THIS BOT IS BUILT DIFFERENT:')}*\n"
        f"• Live download progress updates (real-time speed!)\n"
        f"• Smart compression to bypass 50MB limits (no cap 🧢)\n"
        f"• Absolute zero local disk footprint\n\n"
        f"✨ ━━━━━━━━━━━━━━━━━━━━ ✨\n"
        f"_Drop a link below and let\'s get cookin\'!_"
    )
    if os.path.exists(welcome_photo):
        with open(welcome_photo, 'rb') as photo:
            bot.send_photo(
                chat_id=message.chat.id,
                photo=photo,
                caption=welcome_text,
                parse_mode="Markdown"
            )
    else:
        bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Search for links in the message
    match = URL_PATTERN.search(message.text)
    if not match:
        return
        
    url = match.group(1)
    chat_id = message.chat.id
    unique_id = int(time.time())
    
    # Send initial status message using neon cooking graphic
    cooking_photo = "assets/cooking.png"
    initial_text = f"🔍 *{to_bold_sans('ANALYZING YOUR LINK...')}* {to_italic_sans('It\'s giving premium quality, let me cook.')} 💅"
    
    if os.path.exists(cooking_photo):
        with open(cooking_photo, 'rb') as photo:
            status_msg = bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=initial_text,
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )
    else:
        status_msg = bot.reply_to(message, initial_text, parse_mode="Markdown")
    
    try:
        # Step 1: Extract media metadata first
        ydl_opts_meta = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts_meta) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')
            duration = info.get('duration', 0)
            
        prep_text = f"⏳ *{to_bold_sans('WE COOKIN\' NOW:')}* {to_italic_sans('Preparing to download')} `{title[:40]}...` {to_italic_sans('fr fr!')} 🍳"
        
        if os.path.exists(cooking_photo):
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                caption=prep_text,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text=prep_text,
                parse_mode="Markdown"
            )
        
        # Step 2: Set up download options with smart 50MB file sizing
        output_template = os.path.join(DOWNLOADS_DIR, f"{unique_id}_%(title).50s.%(ext)s")
        
        ydl_opts = {
            'format': 'bestvideo[filesize<45M][ext=mp4]+bestaudio[filesize<5M][ext=m4a]/best[filesize<50M]/worst',
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
            'progress_hooks': [make_progress_hook(chat_id, status_msg.message_id, title)],
            'quiet': True,
            'no_warnings': True,
        }
        
        # Run download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # Step 3: Locate the downloaded file
        search_pattern = os.path.join(DOWNLOADS_DIR, f"{unique_id}_*")
        found_files = glob.glob(search_pattern)
        
        if not found_files:
            raise FileNotFoundError("Could not find the downloaded media file on disk.")
            
        file_path = found_files[0]
        file_size = os.path.getsize(file_path)
        
        # Step 4: Uploading status
        uploading_text = (
            f"📤 *{to_bold_sans('UPLOADING TO TELEGRAM RIGHT NOW!')}* 🚀\n\n"
            f"📁 *{to_bold_sans('FILE SIZE:')}* `{file_size / (1024*1024):.2f} MB` *(certified valid weight)* 💥\n\n"
            f"⚡ ━━━━━━━━━━━━━━━━━━━━ ⚡\n"
            f"_{to_italic_sans('Hold tight, sending the files to your chat...')}_"
        )
        
        if os.path.exists(cooking_photo):
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                caption=uploading_text,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text=uploading_text,
                parse_mode="Markdown"
            )
        
        # Step 5: Send the success banner with details
        duration_minutes = f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"
        caption = (
            f"✨ *{to_bold_sans('HERE IS YOUR DOWNLOAD! SLAY!')}* 💅🔥\n\n"
            f"🎬 *{to_bold_sans('TITLE:')}* `{title}`\n"
            f"⏱️ *{to_bold_sans('DURATION:')}* `{duration_minutes}`\n"
            f"🔗 *{to_bold_sans('ORIGINAL LINK:')}* [Tap here]({url})\n\n"
            f"✨ ━━━━━━━━━━━━━━━━━━━━ ✨\n"
            f"_{to_italic_sans('Enjoy, bestie! we delivered fr fr')}_ 💀🤝"
        )
        
        success_photo = "assets/success.png"
        if os.path.exists(success_photo):
            with open(success_photo, 'rb') as photo:
                success_msg = bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    parse_mode="Markdown"
                )
            reply_target = success_msg.message_id
        else:
            success_msg = bot.send_message(chat_id, caption, parse_mode="Markdown")
            reply_target = success_msg.message_id
        
        # Send the video file replying to the success banner
        with open(file_path, 'rb') as video_file:
            bot.send_video(
                chat_id=chat_id,
                video=video_file,
                reply_to_message_id=reply_target,
                supports_streaming=True,
                timeout=300  # 5 minutes upload timeout
            )
            
        # Delete the temporary cooking status message & clean up the temporary file
        bot.delete_message(chat_id, status_msg.message_id)
        os.remove(file_path)
        logger.info(f"Successfully processed and deleted: {file_path}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to process URL: {url} - Error: {error_msg}")
        
        # Clean up any leftover files in case of failure
        for f in glob.glob(os.path.join(DOWNLOADS_DIR, f"{unique_id}_*")):
            try:
                os.remove(f)
            except Exception:
                pass
                
        # Send user-friendly error message
        error_text = (
            f"❌ *{to_bold_sans('BRUH, THE DOWNLOAD FAILED... MAJOR L!')}* 💀\n\n"
            f"⚠️ *{to_bold_sans('REASON:')}* `{error_msg[:150]}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"_{to_italic_sans('Make sure the link is public, valid, and not age-restricted, fr fr.')}_"
        )
        
        try:
            if os.path.exists(cooking_photo):
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=status_msg.message_id,
                    caption=error_text,
                    parse_mode="Markdown"
                )
            else:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=status_msg.message_id,
                    text=error_text,
                    parse_mode="Markdown"
                )
        except Exception:
            bot.send_message(chat_id, error_text, parse_mode="Markdown")

if __name__ == "__main__":
    logger.info("Starting Telegram Media Downloader Bot...")
    bot.infinity_polling()
