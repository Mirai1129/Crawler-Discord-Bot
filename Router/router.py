import logging

import flask
import requests
from flask import Flask, request, jsonify

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
    emotions_data = database.get_emotions_summary(result_id="init")
    if "error" in emotions_data:
        emotions_data = {'emotions_summary': {}}

    title_and_link_data = database.get_titles_and_links_by_result_id(result_id="init")
    if "error" in title_and_link_data:
        title_and_link_data = []

    return flask.render_template(
        template_name_or_list='index.html',
        emotions_data=emotions_data,
        title_and_link_data=title_and_link_data
    )


@app.route('/about-us', methods=['GET'])
def about_us():
    return flask.render_template("aboutus.html")


@app.route('/contact-us', methods=['GET'])
def contact_us():
    return flask.render_template("contact.html")


@app.route('/myurl', methods=['POST'])
def myurl():
    if request.method == 'POST':
        url = request.host_url.rstrip("/")
        return url
    else:
        return 'Only POST requests are allowed'


@app.route('/results', methods=['GET', 'POST'])
def result():
    emotions_data = database.get_emotions_summary(result_id="init")
    if "error" in emotions_data:
        emotions_data = {'emotions_summary': {}}

    title_and_link_data = database.get_titles_and_links_by_result_id(result_id="init")
    if "error" in title_and_link_data:
        title_and_link_data = []

    return flask.render_template(
        template_name_or_list='index.html',
        emotions_data=emotions_data,
        title_and_link_data=title_and_link_data
    )


@app.route('/results/<result_id>', methods=["GET", "POST"])
def result_by_id(result_id):
    emotions_data = database.get_emotions_summary(result_id=result_id)
    if "error" in emotions_data:
        emotions_data = {'emotions_summary': {}}

    title_and_link_data = database.get_titles_and_links_by_result_id(result_id=result_id)
    if "error" in title_and_link_data:
        title_and_link_data = []

    return flask.render_template(
        template_name_or_list='index.html',
        emotions_data=emotions_data,
        title_and_link_data=title_and_link_data
    )


def main():
    file_name = __file__.split("\\")[-1].split(".")[0]
    logging.info(f"{file_name} has been loaded")
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
