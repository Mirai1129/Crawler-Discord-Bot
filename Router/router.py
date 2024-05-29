import flask
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/database')
def database():
    return "This is database."


def main():
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
