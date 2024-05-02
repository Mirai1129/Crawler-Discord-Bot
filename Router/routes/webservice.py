import os
import flask

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../web', 'templates')

webservice_blueprint = flask.Blueprint('web', __name__, template_folder=template_dir)


@webservice_blueprint.route('/')
def index():
    # 使用相对于模板文件所在目录的路径
    return flask.render_template('index.html')
