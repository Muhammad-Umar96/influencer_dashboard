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
        return jsonify({"error": "Please provide a url parameter"}), 400

    if not any(platform in url for platform in ["facebook.com", "instagram.com", "youtube.com", "tiktok.com"]):
        return jsonify({"error": "Please provide a valid Facebook, Instagram, YouTube or TikTok URL"}), 400

    result = scrape(url)
    print(result)
    return render_template('result.html', data=result)

@app.route('/api/followers', methods=['GET'])
def api_followers():
    url = request.args.get('url')

    if not url:
        return jsonify({"error": "Please provide a url parameter"}), 400

    if "facebook.com" not in url and "instagram.com" not in url:
        return jsonify({"error": "Please provide a valid Facebook or Instagram URL"}), 400

    try:
        result = scrape(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "url": url,
            "page_name": None,
            "followers": None,
            "following": None,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)