from flask_sqlalchemy import SQLAlchemy

app = Flask (__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'

db = SQLAlchemy(app)

class Stock(db.model):
    __tablename__ = 'Stock'
    stock_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(10))
    price = db.Column(db.Float)
    balance = db.Column(db.Float)

class Stock_Update(db.model):
    __tablename__ = 'Stock_Update'
    update_id = db.Column(db.Integer, primary_key = True)
    stock_id = db.Column(db.Integer, primary_key = True)
    price_change = db.Column(db.Float)

class User(db.model):
    __tablename__ = 'User'
    user_id = db.Column(db.String(30), primary_key = True)
    balance = db.Column(db.Float)
    password = db.Column(db.String(15))

class Watchlist(db.model):
    __tablename__ = 'Watchlist'
    user_id = db.Column(db.String(30), primary_key = True)
    stock_id = db.Column(db.Integer, primary_key = True)

class Group_Info(db.model):
    __tablename__ = 'Group_Info'
    group_id = db.Column(db.Integer, primary_key = True)
    balance = db.Column(db.Float)

class Group_Users(db.model):
    __tablename__ = 'Group_Users'
    group_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String(30), primary_key = True)

class Group_Stock(db.model):
    __tablename__ = 'Group_Stock'
    group_id = db.Column(db.Integer, primary_key = True)
    stock_id = db.Column(db.Integer, primary_key = True)

class Transaction(db.model):
    __tablename__ = 'Transaction'
    transaction_id = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.Float)
    date = db.Column(db.Integer)
    price = db.Column(db.Float)

class User_Transaction(db.model):
    __tablename__ = 'User_Transaction'
    transaction_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String(30), primary_key = True)
    stock_id = db.Column(db.Integer, primary_key = True)

class Group_Transaction(db.model):
    __tablename__ = 'Group_Transaction'
    transaction_id = db.Column(db.Integer, primary_key = True)
    group_id = db.Column(db.Integer, primary_key = True)
    stock_id = db.Column(db.Integer, primary_key = True)
