from flask import Flask
from app.interfaces.api.routes import register_routes
import os

template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_path)
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
