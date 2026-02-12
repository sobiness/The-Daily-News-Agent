import os
import time
import telebot
from google import genai
from firecrawl import Firecrawl  # UPDATED IMPORT
from dotenv import load_dotenv
from datetime import datetime

# --- DEBUG PRINT: AM I ALIVE? ---
print("✅ SCRIPT IS LOADED. Starting imports...")

load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FIRECRAWL_KEY = os.environ.get("FIRECRAWL_KEY")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- DEBUG PRINT: CHECK KEYS (Safe version) ---
if TELEGRAM_TOKEN: print("   > Telegram Token found.")
else: print("   > ❌ Telegram Token MISSING.")

if CHAT_ID: print(f"   > Chat ID found: {CHAT_ID}")
else: print("   > ❌ Chat ID MISSING.")

SOURCES = [
    "https://github.com/trending/python?since=daily",
    "https://news.ycombinator.com/news",
    "https://huggingface.co/papers",
    "https://www.producthunt.com/topics/artificial-intelligence",
    "https://simonwillison.net/",
    "https://techcrunch.com/category/artificial-intelligence/"
]

def get_smart_news():
    print("🔥 Warming up Firecrawl...")
    if not FIRECRAWL_KEY:
        print("❌ Error: Missing FIRECRAWL_KEY")
        return ""
    
    # --- FIX 1: Use the new Class Name ---
    app = Firecrawl(api_key=FIRECRAWL_KEY)
    
    combined_content = f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"

    for url in SOURCES:
        try:
            print(f"   --> Scraping: {url}")
            
            # --- FIX 2: Use correct arguments per docs ---
            # The new SDK uses 'formats' list
            data = app.scrape(url, formats=['markdown'])
            
            # --- FIX 3: Access attribute directly (Object, not Dict) ---
            # The docs say: print(doc.markdown)
            if hasattr(data, 'markdown'):
                raw_text = data.markdown[:3000]
            else:
                # Fallback just in case structure varies slightly
                raw_text = str(data)[:3000]
            
            if raw_text:
                combined_content += f"\n\n=== SOURCE: {url} ===\n{raw_text}"
            else:
                print(f"   ⚠️ No markdown content found for {url}")
            
            time.sleep(1) 
        except Exception as e:
            print(f"   ⚠️ Failed to scrape {url}: {e}")
            continue
            
    return combined_content

def summarize_with_ai(raw_news):
    print("🧠 Wake up Gemini...")
    if not GEMINI_API_KEY:
        return "Error: No API Key found."

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    You are a cynical software engineer's assistant. Filter signal from noise.

    Raw News:
    {raw_news}

    TASK: Write a 'Morning Intel' briefing.
    RULES:
    1. Sections: 🚨 Breaking, 🛠️ New Tools, 🔬 Research, ⚠️ Security.
    2. No fluff. Bullet points. Under 400 words.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return "Error generating summary."

def send_telegram(message):
    print("🚀 Sending to Telegram...")
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Error: Missing Telegram Creds")
        return

    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    try:
        bot.send_message(CHAT_ID, message, parse_mode=None)
        print("✅ Message sent successfully!")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def main():
    print("--- 🏁 ENTERING MAIN FUNCTION ---")
    raw_data = get_smart_news()
    if not raw_data or len(raw_data) < 100:
        print("❌ Error: Not enough data scraped.")
        return

    newsletter = summarize_with_ai(raw_data)
    send_telegram(newsletter)
    print("--- 😴 SCRIPT FINISHED ---")

if __name__ == "__main__":
    main()