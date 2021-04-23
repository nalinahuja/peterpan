from .app import db

class Stock(db.model):
    __tablename__ = 'Stock'
    stock_id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String(10), nullable = False)
    price = db.Column(db.Float, nullable = False)
    balance = db.Column(db.Float, nullable = False)

class Stock_Update(db.model):
    __tablename__ = 'Stock_Update'
    update_id = db.Column(db.Integer, primary_key = True, nullable = False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.stock_id'), primary_key = True, nullable = False)
    price_change = db.Column(db.Float, nullable = False)

class User(db.model):
    __tablename__ = 'User'
    user_id = db.Column(db.String(30), primary_key = True, nullable = False)
    balance = db.Column(db.Float, nullable = False)
    password = db.Column(db.String(15), nullable = False)

class Watchlist(db.model):
    __tablename__ = 'Watchlist'
    user_id = db.Column(db.String(30), db.ForeignKey('User.stock_id'), primary_key = True, nullable = False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.stock_id'), primary_key = True, nullable = False)

class Group_Info(db.model):
    __tablename__ = 'Group_Info'
    group_id = db.Column(db.Integer, primary_key = True, nullable = False)
    balance = db.Column(db.Float, nullable = False)

class Group_Users(db.model):
    __tablename__ = 'Group_Users'
    group_id = db.Column(db.Integer, db.ForeignKey('Group.stock_id'), primary_key = True), nullable = False)
    user_id = db.Column(db.String(30), db.ForeignKey('User.stock_id'), primary_key = True, nullable = False)

class Group_Stock(db.model):
    __tablename__ = 'Group_Stock'
    group_id = db.Column(db.Integer, db.ForeignKey('Group.stock_id'), primary_key = True, nullable = False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.stock_id'), primary_key = True, nullable = False)

class Transaction(db.model):
    __tablename__ = 'Transaction'
    transaction_id = db.Column(db.Integer, primary_key = True, nullable = False)
    amount = db.Column(db.Float, nullable = False)
    date = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Float, nullable = False)

class User_Transaction(db.model):
    __tablename__ = 'User_Transaction'
    transaction_id = db.Column(db.Integer, db.ForeignKey('Transaction.stock_id'), primary_key = True, nullable = False)
    type = db.Column(db.Boolean, nullable = False)
    user_id = db.Column(db.String(30), db.ForeignKey('User.stock_id'), primary_key = True, nullable = False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.stock_id'), primary_key = True, nullable = False)

class Group_Transaction(db.model):
    __tablename__ = 'Group_Transaction'
    transaction_id = db.Column(db.Integer, db.ForeignKey('Transaction.stock_id'), primary_key = True, nullable = False)
    type = db.Column(db.Boolean, nullable = False)
    group_id = db.Column(db.Integer, db.ForeignKey('Group.stock_id'), primary_key = True, nullable = False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.stock_id'), primary_key = True, nullable = False)
