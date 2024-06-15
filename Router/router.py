import logging

import flask
from flask import Flask, jsonify, request

from Features import PttCrawler, CozeApi
from Mongo import MongoAdapter
from .methods import get_ptt_articles_data

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


@app.route('/results', methods=['GET', 'POST'])
def result():
    # TODO 新增結果回傳邏輯
    return ""


@app.route('/results/<result_id>', methods=["GET", "POST"])
def result(result_id):
    # TODO 新增特定結果回傳邏輯
    return ""


def main():
    file_name = __file__.split("\\")[-1].split(".")[0]
    logging.info(f"{file_name} has been loaded")
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
