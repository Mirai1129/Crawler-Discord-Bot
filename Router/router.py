import logging

import flask
from flask import Flask, request

from Features.Api import OpenAIEmotionalAnalyzer
from Mongo import MongoAdapter

# Configure global logging
logging.basicConfig(level=logging.INFO, format='[FLASK] %(message)s')

app = Flask(__name__)
ai = OpenAIEmotionalAnalyzer()
database = MongoAdapter()

# Configure Flask app logger
flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.INFO)


@app.route('/')
def index():
    emotions_data = database.get_all_emotions_amount()

    if not emotions_data:
        emotions_data = {'emotions_summary': {}}

    # 将数据传递给模板
    return flask.render_template('index.html', emotions_data=emotions_data)


@app.route('/myurl', methods=['POST'])
def myurl():
    if request.method == 'POST':
        # 获取通过 POST 方法发送的文本数据
        url = request.host_url.rstrip("/")
        return url
    else:
        return 'Only POST requests are allowed'


@app.route('/results', methods=['GET', 'POST'])
def result():
    # TODO 新增結果回傳邏輯
    return ""


@app.route('/results/<result_id>', methods=["GET", "POST"])
def result_by_id(result_id):
    # 获取情感数据
    emotions_data = database.get_emotions_amount(result_id)

    if not emotions_data:
        emotions_data = {'emotions_summary': {}}

    # 将数据传递给模板
    return flask.render_template('index.html', emotions_data=emotions_data)


def main():
    file_name = __file__.split("\\")[-1].split(".")[0]
    logging.info(f"{file_name} has been loaded")
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
