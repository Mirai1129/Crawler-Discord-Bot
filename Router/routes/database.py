from flask import Blueprint

database_blueprint = Blueprint('database', __name__)


@database_blueprint.route('/data')
def data():
    return 'This is the data page of the database blueprint.'
