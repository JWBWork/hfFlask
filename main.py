from flask import Flask
from flask_cors import CORS
from src.api import api_blueprint
from src.database import db
from src.bcrypt import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
# flas-bcrypt for hashes on user-tokens
bcrypt.init_app(app)
# flask-sqlalchemy for database (duh)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'
db.init_app(app)
# Attaching api routes made with flask-restful
app.register_blueprint(api_blueprint)
# CORS! making it work as an API with a different domain from the requesting front-end
cors = CORS(app, resources={'*': {'origins': '*'}})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
