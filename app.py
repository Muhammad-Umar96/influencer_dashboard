from flask import Flask, request, jsonify, render_template
from scraper import scrape

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/followers', methods=['GET'])
def followers():
    url = request.args.get('url')

    if not url:
        return render_template('index.html', error="Please provide a URL.")

    if not any(word in url for word in ["facebook.com", "instagram.com", "youtube.com", "tiktok.com"]):
        return render_template('index.html', error="Please provide a valid Facebook, Instagram, YouTube or TikTok URL.")

    result = scrape(url)
    print(result)
    return render_template('result.html', data=result)

@app.route('/api/followers', methods=['GET'])
def api_followers():
    url = request.args.get('url')

    if not url:
        return jsonify({"error": "Please provide a url parameter"}), 400

    if not any(word in url for word in ["facebook.com", "instagram.com", "youtube.com", "tiktok.com"]):
        return jsonify({"error": "Please provide a valid Facebook, Instagram, YouTube or TikTok URL."}), 400

    try:
        result = scrape(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)