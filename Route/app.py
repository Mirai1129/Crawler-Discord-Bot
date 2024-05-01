import os
import flask

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../web', 'templates')

app = flask.Flask(__name__, template_folder=template_dir)


@app.route('/')
def index():
    # 使用相对于模板文件所在目录的路径
    return flask.render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
