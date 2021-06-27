from wtforms import StringField, PasswordField, IntegerField, validators
from wtforms.validators import ValidationError
from flask_wtf import FlaskForm
from data_model import User


def validate_user(field):
    if User.query.filter_by(username = field.data).count > 0:
        raise ValidationError('Username %s already exists!' % field.data)

class Registration(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(max=64)])
    password = PasswordField('Password', [validators.Length(6, 16)])

    def validate_username(self, field):
        if not self.get_user():
            raise ValidationError('Invalid username!')

    def validate_password(self, field):
        if not self.get_user():
            return
        if not self.get_user().check_password(field.data):
            raise ValidationError('Incorrect password!')

    def get_user(self):
        return User.query.filter_by(username=self.username.data).first()