import os
import glob

from flask import Flask, Blueprint


def search_blueprint(app: Flask):
    app_dict = {}
    # 取得目標路徑下所有的 Python 檔案
    blueprint_files = glob.glob(os.path.join(os.path.dirname(__file__), 'routes', '*.py'))
    for file in blueprint_files:
        if not file.endswith('__init__.py'):
            module_name = os.path.splitext(os.path.basename(file))[0]
            module = __import__('routes.' + module_name, fromlist=['*'])
            module_attrs = dir(module)
            for name in module_attrs:
                var_obj = getattr(module, name)
                if isinstance(var_obj, Blueprint):
                    if app_dict.get(name) is None:
                        app_dict[name] = var_obj
                        app.register_blueprint(var_obj)
                        print("Successfully Registered {} {}".format((Blueprint.__name__, name), var_obj),
                              var_obj.__str__())


def main():
    app = Flask(__name__)
    search_blueprint(app)
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()

