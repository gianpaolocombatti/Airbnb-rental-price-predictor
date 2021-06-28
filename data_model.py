from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

DB = SQLAlchemy()


class User(DB.Model, UserMixin):

    id = DB.Column(DB.Unicode(1000), primary_key=True)
    username = DB.Column(DB.String, nullable=False)
    email = DB.Column(DB.String, nullable=False)
    password = DB.Column(DB.String, nullable=False)

    def check_password(self, password):
        if not password == self.password:
            return False
        else:
            return True
