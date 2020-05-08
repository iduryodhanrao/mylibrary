from src.mymodel import db
from flask import Flask
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.app_context().push()

#create database if running first time
#db.session.remove()
#db.drop_all()
db.create_all()
