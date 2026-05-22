from flask import Flask, request, jsonify, render_template
from scraper import scrape
import os
from urllib.parse import quote_plus
from models import db, InfluencerStat

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

password = quote_plus(os.getenv('DB_PASSWORD'))
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{password}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/followers', methods=['GET'])
def followers():
    url = request.args.get('url')

    if not url:
        return render_template('index.html', error="Please provide a URL.")

    if not any(p in url for p in ["facebook.com", "instagram.com", "youtube.com", "tiktok.com"]):
        return render_template('index.html', error="Please provide a valid Facebook, Instagram, YouTube or TikTok URL.")

    result = scrape(url)
    print(result)

    # save to database
    try:
        stat = InfluencerStat(
            platform=result.get('platform'),
            page_name=result.get('page_name') or result.get('channel_name'),
            url=result.get('url'),
            followers=result.get('followers'),
            following=result.get('following'),
            category=result.get('category'),
            image=result.get('image'),
            subscribers=result.get('subscribers'),
            channel_name=result.get('channel_name'),
        )
        db.session.add(stat)
        db.session.commit()
        print("Saved to database!")
    except Exception as e:
        print(f"DB ERROR: {str(e)}")

    return render_template('result.html', data=result)

@app.route('/api/followers', methods=['GET'])
def api_followers():
    url = request.args.get('url')

    if not url:
        return jsonify({"error": "Please provide a url parameter"}), 400

    if not any(p in url for p in ["facebook.com", "instagram.com", "youtube.com", "tiktok.com"]):
        return jsonify({"error": "Please provide a valid URL."}), 400

    try:
        result = scrape(url)

        stat = InfluencerStat(
            platform=result.get('platform'),
            page_name=result.get('page_name') or result.get('channel_name'),
            url=result.get('url'),
            followers=result.get('followers'),
            following=result.get('following'),
            category=result.get('category'),
            image=result.get('image'),
            subscribers=result.get('subscribers'),
            channel_name=result.get('channel_name'),
        )
        db.session.add(stat)
        db.session.commit()

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run( debug=True)