from flask import Flask, render_template, current_app
import requests
import logging

app = Flask(__name__)
app.config['DEBUG'] = True

last_meme = None

def get_meme(attempts=5):
    dank_subreddits = ["dankmemes", "memes", "me_irl"]
    url = "https://meme-api.com/gimme"

    global last_meme
    
    for attempt in range(attempts):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            app.logger.info(f"API Response: {data}")

            subreddit = data.get("subreddit", "")
            if subreddit in dank_subreddits:
                meme_large = data.get("preview", [])[-2] if data.get("preview") else None
                if meme_large:
                    if last_meme != meme_large: 
                        last_meme = meme_large
                        return meme_large, subreddit

            app.logger.info(f"Non-dank subreddit: {subreddit}, retrying...")

        except requests.Timeout:
            app.logger.error("Request timed out")
        except requests.RequestException as e:
            app.logger.error(f"Request failed: {e}")
        except (KeyError, IndexError) as e:
            app.logger.error(f"Error processing response: {e}")

    app.logger.warning("Reached maximum attempts for getting a meme")
    return None, None

@app.route("/")
def index():
    app.logger.info(f"Template folder: {current_app.template_folder}")
    meme_pic, subreddit = get_meme()
    if meme_pic and subreddit:
        return render_template("index.html", meme_pic=meme_pic, subreddit=subreddit)
    else:
        return render_template("error.html"), 500
    
app.config['TEMPLATES_AUTO_RELOAD'] = True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5000)
