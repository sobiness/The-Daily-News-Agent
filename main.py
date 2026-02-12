import os
import time
import telebot
from google import genai
from firecrawl import FirecrawlApp
from datetime import datetime

# --- CONFIGURATION (Load from GitHub Secrets) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FIRECRAWL_KEY = os.environ.get("FIRECRAWL_KEY")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") # Optional: Hardcode your ID if you want

# --- THE HIGH-SIGNAL SOURCE LIST ---
# We cover: Code, Research, New Tools, Security, and Industry News.
SOURCES = [
    # 1. WHAT ENGINEERS ARE CODING (Trends)
    "https://github.com/trending/python?since=daily",
    
    # 2. THE DISCOURSE (Hacker News is the filter for BS)
    "https://news.ycombinator.com/news",
    
    # 3. LATEST AI RESEARCH (The "Brain" stuff)
    "https://huggingface.co/papers", 
    
    # 4. NEW AI TOOLS (Product Launches)
    "https://www.producthunt.com/topics/artificial-intelligence",
    
    # 5. SECURITY & LLM ENGINEERING (Vulnerabilities & Deep Dives)
    "https://simonwillison.net/", 
    
    # 6. INDUSTRY MOVES (Business & funding)
    "https://techcrunch.com/category/artificial-intelligence/"
]

def get_smart_news():
    """
    Scrapes the sources using Firecrawl to get clean Markdown.
    """
    print("🔥 Warming up Firecrawl...")
    app = FirecrawlApp(api_key=FIRECRAWL_KEY)
    combined_content = f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"

    for url in SOURCES:
        try:
            print(f"   --> Scraping: {url}")
            # Scrape into markdown
            data = app.scrape_url(url, params={'formats': ['markdown']})
            
            # Extract content. We limit to 3000 chars per source to fit context window safely.
            # Firecrawl returns a dictionary, we want the 'markdown' key.
            raw_text = data.get('markdown', '')[:3000]
            
            combined_content += f"\n\n=== SOURCE: {url} ===\n{raw_text}"
            
            # Polite delay to not get rate-limited
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Failed to scrape {url}: {e}")
            continue
            
    return combined_content

def summarize_with_ai(raw_news):
    print("🧠 Wake up Gemini...")
    
    # NEW CLIENT SETUP
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

    # NEW GENERATION CALL
    response = client.models.generate_content(
        model='gemini-2.0-flash', 
        contents=prompt
    )
    return response.text

def send_telegram(message):
    """
    Delivers the goods to your phone.
    """
    print("🚀 Sending to Telegram...")
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    
    # If CHAT_ID isn't in env vars, you might need to message the bot first to get it.
    # For now, we assume you put it in GitHub Secrets or hardcoded it.
    # To find your Chat ID: Message @userinfobot on Telegram.
    
    bot.send_message(CHAT_ID, message, parse_mode=None) # parse_mode=None is safer for AI text
    print("✅ Message sent!")

def main():
    print("--- 🏁 STARTING DAILY AGENT ---")
    
    # 1. Scrape
    raw_data = get_smart_news()
    if len(raw_data) < 500:
        print("❌ Error: Not enough data scraped.")
        return

    # 2. Analyze
    newsletter = summarize_with_ai(raw_data)
    
    # 3. Deliver
    send_telegram(newsletter)
    
    print("--- 😴 AGENT GOING TO SLEEP ---")

if __name__ == "__main__":
    main()