import os, requests, random, time, schedule
from flask import Flask
import threading

# Environment variable (Discord Webhook URL)
WEBHOOK_URL = os.getenv("MEME_WEBHOOK")

# Meme subreddits
REDDIT_SUBS = [
    "memes", "dankmemes", "ProgrammerHumor",
    "wholesomememes", "me_irl", "funny", "techhumor"
]

# Imgflip fallback captions
CAPTIONS = [
    ("Freelancer life", "Client: can you do it for free?"),
    ("Design Brief:", "Just make it pop 💥"),
    ("Before deadline", "After feedback round 7"),
    ("Editor at 3AM", "Just one more render..."),
    ("This meeting could’ve been", "An email."),
    ("When Premiere crashes", "And you didn’t save")
]

# Post to Discord
def post_to_discord(title, image_url, source_label):
    payload = {
        "embeds": [{
            "title": title,
            "image": {"url": image_url},
            "footer": {"text": source_label}
        }]
    }
    try:
        res = requests.post(WEBHOOK_URL, json=payload)
        if res.status_code == 204:
            print(f"✅ Posted from {source_label}")
        else:
            print(f"❌ Discord webhook error: {res.status_code}")
    except Exception as e:
        print(f"❌ Failed to post: {e}")

# Reddit meme fetch
def get_reddit_meme():
    subreddit = random.choice(REDDIT_SUBS)
    try:
        r = requests.get(f"https://meme-api.com/gimme/{subreddit}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            post_to_discord(data["title"], data["url"], f"Reddit: r/{data['subreddit']}")
        else:
            print(f"❌ Meme API error: {r.status_code}")
    except Exception as e:
        print(f"❌ Reddit fetch failed: {e}")

# Imgflip meme fallback
def get_imgflip_meme():
    try:
        templates = requests.get("https://api.imgflip.com/get_memes").json()["data"]["memes"]
        template = random.choice(templates[:20])
        top, bottom = random.choice(CAPTIONS)
        meme_url = f"https://api.memegen.link/images/custom/{top}/{bottom}.png?background={template['url']}"
        post_to_discord(f"{top} / {bottom}", meme_url, "Generated via Imgflip")
    except Exception as e:
        print(f"❌ Imgflip fallback failed: {e}")

# Combined poster
def hybrid_meme_poster():
    source = random.choices(["reddit", "imgflip"], weights=[70, 30])[0]
    if source == "reddit":
        get_reddit_meme()
    else:
        get_imgflip_meme()

# Flask server to keep instance awake
app = Flask('')

@app.route('/')
def home():
    return "✅ Meme Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# Run initial meme + schedule next
hybrid_meme_poster()
schedule.every(4).hours.do(hybrid_meme_poster)

# Start web server thread
threading.Thread(target=run_web).start()

# Main loop
while True:
    schedule.run_pending()
    time.sleep(30)
