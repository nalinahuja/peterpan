from globl import SQL_ALCHEMY_DB as db

class Stock(db.Model):
    __tablename__ = 'Stock'
    stock_id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String(10), nullable = False)
    price = db.Column(db.Float, nullable = False)
    balance = db.Column(db.Float, nullable = False)

class Stock_Update(db.Model):
    __tablename__ = 'Stock_Update'
    update_id = db.Column(db.Integer, primary_key = True, nullable = False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.stock_id'), primary_key = True, nullable = False)
    price_change = db.Column(db.Float, nullable = False)

class User(db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.String(30), primary_key = True, nullable = False)
    balance = db.Column(db.Float, nullable = False)
    password = db.Column(db.String(15), nullable = False)

class Watchlist(db.Model):
    __tablename__ = 'Watchlist'
    user_id = db.Column(db.String(30), db.ForeignKey('User.stock_id'), primary_key = True, nullable = False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.stock_id'), primary_key = True, nullable = False)

class Group_Info(db.Model):
    __tablename__ = 'Group_Info'
    group_id = db.Column(db.Integer, primary_key = True, nullable = False)
    balance = db.Column(db.Float, nullable = False)

class Group_Users(db.Model):
    __tablename__ = 'Group_Users'
    group_id = db.Column(db.Integer, db.ForeignKey('Group.stock_id'), primary_key = True, nullable = False)
    user_id = db.Column(db.String(30), db.ForeignKey('User.stock_id'), primary_key = True, nullable = False)

class Group_Stock(db.Model):
    __tablename__ = 'Group_Stock'
    group_id = db.Column(db.Integer, db.ForeignKey('Group.stock_id'), primary_key = True, nullable = False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.stock_id'), primary_key = True, nullable = False)

    def __init__(self, group_id, stock_id):
        self.group_id = group_id
        self.stock_id = stock_id

class Transaction(db.Model):
    __tablename__ = 'Transaction'
    transaction_id = db.Column(db.Integer, primary_key = True, nullable = False)
    amount = db.Column(db.Float, nullable = False)
    date = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Float, nullable = False)

    def __init__(self, transaction_id, amount, date, price):
        self.transaction_id = transaction_id
        self.amount = amount
        self.date = date
        self.price = price

class User_Transaction(db.Model):
    __tablename__ = 'User_Transaction'
    transaction_id = db.Column(db.Integer, db.ForeignKey('Transaction.stock_id'), primary_key = True, nullable = False)
    type = db.Column(db.Boolean, nullable = False)
    user_id = db.Column(db.String(30), db.ForeignKey('User.stock_id'), primary_key = True, nullable = False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.stock_id'), primary_key = True, nullable = False)

    def __init__(self, transaction_id, type, user_id, stock_id):
        self.transaction_id = transaction_id
        self.type = type
        self.user_id = user_id
        self.stock_id = stock_id

class Group_Transaction(db.Model):
    __tablename__ = 'Group_Transaction'
    transaction_id = db.Column(db.Integer, db.ForeignKey('Transaction.stock_id'), primary_key = True, nullable = False)
    type = db.Column(db.Boolean, nullable = False)
    group_id = db.Column(db.Integer, db.ForeignKey('Group.stock_id'), primary_key = True, nullable = False)
    stock_id = db.Column(db.Integer, db.ForeignKey('Stock.stock_id'), primary_key = True, nullable = False)

    def __init__(self, transaction_id, type, group_id, stock_id):
        self.transaction_id = transaction_id
        self.type = type
        self.group_id = group_id
        self.stock_id  = stock_id

# Create All Databases
db.create_all()
