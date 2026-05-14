from flask import Flask, request, jsonify, render_template
from scraper import get_follower_count

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/followers', methods=['GET'])
def followers():
    url = request.args.get('url')

    if not url:
        return jsonify({"error": "Please provide a url parameter"}), 400

    if "facebook.com" not in url:
        return jsonify({"error": "Please provide a valid Facebook page URL"}), 400

    result = get_follower_count(url)
    return render_template('result.html', data=result)

if __name__ == '__main__':
    app.run(debug=True)