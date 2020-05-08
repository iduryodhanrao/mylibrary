from flask_sqlalchemy import SQLAlchemy
'''
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY']='Je123'
'''
db=SQLAlchemy()

class Books(db.Model):
    __tablename__ ='books'
    id              =db.Column(db.Integer, primary_key=True)
    name            =db.Column(db.String(50))
    author          =db.Column(db.String(50))
    available       =db.Column(db.String(1))
    def __init__(self,name,author):
        self.name=name
        self.author=author
        self.available='Y'

class Bookloans(db.Model):
    __tablename__ ='bookloans'
    id              =db.Column(db.Integer, primary_key=True)
    name            =db.Column(db.String(50))
    email           =db.Column(db.String(50))
    issuedt         =db.Column(db.Date)

    def __init__(self,name,email,issuedt):
        self.name=name
        self.email=email
        self.issuedt=issuedt

class Members(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    username    =db.Column(db.String(50))
    password    =db.Column(db.String(50))
    email       =db.Column(db.String(50), unique=True)

    def __init__(self,username,password, email):
        self.username=username
        self.password=password
        self.email=email
