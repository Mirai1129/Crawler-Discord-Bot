import logging

import flask
from flask import Flask, jsonify, request

from Features import PttCrawler, CozeApi
from Mongo import MongoAdapter

# Configure global logging
logging.basicConfig(level=logging.INFO, format='[FLASK] %(message)s')

app = Flask(__name__)
crawler = PttCrawler()
ai = CozeApi()
database = MongoAdapter()

# Configure Flask app logger
flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/database')
def database():
    return "This is database."


@app.route('/crawler')
def crawler():
    crawler.get_article_data()


@app.route('/emotions', methods=['GET', 'POST'])
def emotions():
    content = request.json.get('content')
    if not content:
        return jsonify({"error": "No content provided"}), 400

    emotion = ai.get_article_emoji(content)
    return jsonify({"emotion": emotion}), 200


def main():
    file_name = __file__.split("\\")[-1].split(".")[0]
    logging.info(f"{file_name} has been loaded")
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
