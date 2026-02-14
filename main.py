import os
import time
import requests
import telebot
from firecrawl import Firecrawl
from dotenv import load_dotenv
from datetime import datetime

# --- DEBUG PRINT ---
print("✅ SCRIPT STARTED. USING RAW REST API.")

load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FIRECRAWL_KEY = os.environ.get("FIRECRAWL_KEY")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- SOURCES ---
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
        
    app = Firecrawl(api_key=FIRECRAWL_KEY)
    combined_content = f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"

    for url in SOURCES:
        try:
            print(f"   --> Scraping: {url}")
            data = app.scrape(url, formats=['markdown'])
            
            if hasattr(data, 'markdown'):
                raw_text = data.markdown[:3000]
            else:
                raw_text = str(data)[:3000]
            
            if raw_text:
                combined_content += f"\n\n=== SOURCE: {url} ===\n{raw_text}"
            else:
                print(f"   ⚠️ No markdown content for {url}")
            
            time.sleep(1) 
        except Exception as e:
            print(f"   ⚠️ Failed to scrape {url}: {e}")
            continue
            
    return combined_content

def summarize_with_ai(raw_news):
    print("🧠 Wake up Gemini (REST API)...")
    if not GEMINI_API_KEY:
        return "Error: No API Key found."

    # --- FIX: We are now explicitly using the stable 1.5-flash model ---
    # This model has generous free-tier limits and does not require a billing account.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""
    You are a cynical software engineer's assistant. Filter signal from noise.
    
    Raw News:
    {raw_news}

    TASK: Write a 'Morning Intel' briefing.
    RULES:
    1. Sections: 🚨 Breaking, 🛠️ New Tools, 🔬 Research, ⚠️ Security.
    2. No fluff. Bullet points. Under 400 words.
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"❌ Gemini REST Error: {response.status_code} - {response.text}")
            return f"Error: AI generation failed ({response.status_code})"
            
    except Exception as e:
        print(f"❌ Request Failed: {e}")
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