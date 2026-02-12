import os
import time
import telebot
from google import genai
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from datetime import datetime

# Load local environment variables
load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FIRECRAWL_KEY = os.environ.get("FIRECRAWL_KEY")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- HIGH-SIGNAL SOURCES ---
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
        
    app = FirecrawlApp(api_key=FIRECRAWL_KEY)
    combined_content = f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"

    for url in SOURCES:
        try:
            print(f"   --> Scraping: {url}")
            
            # --- FIX IS HERE (Updated for v1.0 SDK) ---
            # Old: app.scrape_url(url, params={...})
            # New: app.scrape(url, params={...})
            data = app.scrape(url, params={'formats': ['markdown']})
            
            # Extract content (Firecrawl v1 returns a dict)
            raw_text = data.get('markdown', '')[:3000] 
            
            if raw_text:
                combined_content += f"\n\n=== SOURCE: {url} ===\n{raw_text}"
            else:
                print(f"   ⚠️ No markdown returned for {url}")

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
        print("✅ Message sent!")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def main():
    print("--- 🏁 STARTING DAILY AGENT ---")
    raw