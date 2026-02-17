# The Daily News Agent

A serverless Python agent that scrapes high-signal tech news, filters the noise using an LLM, and delivers a clean morning briefing directly to your phone. 

No paid servers. No subscriptions. Just pure signal.

## The Architecture (The GitHub Loophole)


Instead of paying for a cloud server (AWS/n8n) or keeping a laptop running 24/7, this project uses a loophole in **GitHub Actions**. By setting up a CRON job in a `.yml` file, GitHub's servers wake up automatically at 8:00 AM UTC, run the Python script, deliver the Telegram message, and go back to sleep. 

The running cost is $0.00.

## The Stack
* **The Brain:** Gemini 1.5 Flash (Fast, generous free tier)
* **The Eyes:** Firecrawl (Converts complex URLs to clean Markdown)
* **The Delivery:** Telegram Bot API
* **The Engine:** GitHub Actions (Ubuntu latest)

## Quick Start (Build Your Own)
1. **Fork this repository.** (Do not clone, fork it so you have your own copy).
2. **Get your API Keys:**
   - Telegram Bot Token (via @BotFather) & Chat ID (via @userinfobot)
   - Gemini API Key (Google AI Studio)
   - Firecrawl API Key
3. **Add Secrets:** Go to your repository settings -> `Secrets and variables` -> `Actions`. Add the keys as `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `GEMINI_API_KEY`, and `FIRECRAWL_KEY`.
4. **Deploy:** Go to the "Actions" tab and click "Run workflow" to test it manually. 

From then on, it runs automatically every morning. 

---
*Engineered by Sobika Sree Ramesh / so.bi.it*
