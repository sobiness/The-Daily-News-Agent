import os
import time
import telebot
from google import genai
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from datetime import datetime

# Load local environment variables (for testing on your laptop)
load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FIRECRAWL_KEY = os.environ.get("FIRECRAWL_KEY")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- VERIFIED HIGH-SIGNAL SOURCES ---
SOURCES = [
    "https://github.com/trending/python?since=daily",
    "https://news.ycombinator.com/news",
    "https://huggingface.co/papers",
    "https://www.producthunt.com/topics/artificial-intelligence",
    "https://simonwillison.net/",
    "https://techcrunch.com/category/artificial-intelligence/"
]

def get_smart_news():
    """
    Scrapes the sources using Firecrawl (v1 SDK pattern).
    """
    print("🔥 Warming up Firecrawl...")
    if not FIRECRAWL_KEY:
        print("❌ Error: Missing FIRECRAWL_KEY")
        return ""
        
    app = FirecrawlApp(api_key=FIRECRAWL_KEY)
    combined_content = f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"

    for url in SOURCES:
        try:
            print(f"   --> Scraping: {url}")
            # Scrape into markdown
            data = app.scrape_url(url, params={'formats': ['markdown']})
            
            # Firecrawl returns a dict with 'markdown' key
            raw_text = data.get('markdown', '')[:3000] # Limit chars to save tokens
            
            combined_content += f"\n\n=== SOURCE: {url} ===\n{raw_text}"
            time.sleep(1) # Polite delay
            
        except Exception as e:
            print(f"   ⚠️ Failed to scrape {url}: {e}")
            continue
            
    return combined_content

def summarize_with_ai(raw_news):
    """
    Uses the NEW Google GenAI SDK (google-genai)
    """
    print("🧠 Wake up Gemini...")
    if not GEMINI_API_KEY:
        print("❌ Error: Missing GEMINI_API_KEY")
        return "Error: No API Key found."

    # NEW SDK CLIENT SETUP
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    You are a cynical, high-level software engineer's personal assistant. 
    Your goal is to filter signal from noise.

    Here is the raw text scraped from the top tech sites today:
    {raw_news}

    TASK:
    Write a 'Morning Intel' briefing for me. 
    
    RULES:
    1. **Format:** Use clear emojis and bold headers.
    2. **Sections:**
       - 🚨 **Breaking / Viral** (The #1 thing everyone is talking about)
       - 🛠️ **New Tools & Repos** (GitHub trending or Product Hunt tools worth clicking)
       - 🔬 **Research & Papers** (Cool new ML concepts)
       - ⚠️ **Vulnerabilities/Drama** (Security issues or industry fights)
    3. **Tone:** Professional but conversational. No corporate fluff. 
    4. **Length:** Keep it under 400 words total. Bullet points are best.

    GO.
    """

    # NEW GENERATE CONTENT CALL
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
    
    # 1. Scrape
    raw_data = get_smart_news()
    if not raw_data or len(raw_data) < 100:
        print("❌ Error: Not enough data scraped.")
        return

    # 2. Analyze
    newsletter = summarize_with_ai(raw_data)
    
    # 3. Deliver
    send_telegram(newsletter)
    
    print("--- 😴 AGENT GOING TO SLEEP ---")

if __name__ == "__main__":
    main()