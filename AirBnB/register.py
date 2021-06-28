# from wtforms import StringField, PasswordField, IntegerField, validators
# from wtforms.validators import ValidationError
# from flask_wtf import FlaskForm
# from data_model import User
# from flask_login import login_user, logout_user, current_user, LoginManager, UserMixin
# import dash_core_components as dcc
# import dash_html_components as html
# import dash
# from dash.dependencies import Input, Output, State
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin
# import sqlite3
# from sqlalchemy import Table, create_engine
#
# from app import app
#
# conn = sqlite3.connect('data.sqlite')
# engine = create_engine('sqlite:///data.sqlite')
# DB = SQLAlchemy()
#
#
# class User(DB.Model):
#
#     id = DB.Column(DB.Unicode(1000), primary_key=True)
#     username = DB.Column(DB.String, unique=True, nullable=False)
#     email = DB.Column(DB.String, unique=True, nullable=False)
#     password = DB.Column(DB.String, nullable=False)
#
# Users_tbl = Table('users', User.metadata)
#
# def create_users_table():
#     User.metadata.create_all(engine)
#
#
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = '/login'
#
# class Users(UserMixin, User):
#     pass
#
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
# create = html.Div([html.H1('Create User Account')
#         , dcc.Location(id='create_user', refresh=True)
#         , dcc.Input(id="username"
#             , type="text"
#             , placeholder="user name"
#             , maxLength =15)
#         , dcc.Input(id="password"
#             , type="password"
#             , placeholder="password")
#         , dcc.Input(id="email"
#             , type="email"
#             , placeholder="email"
#             , maxLength = 50)
#         , html.Button('Create User', id='submit-val', n_clicks=0)
#         , html.Div(id='container-button-basic')
#     ])
#
#
# @app.callback(
#    [Output('container-button-basic', "children")]
#     , [Input('submit-val', 'n_clicks')]
#     , [State('username', 'value'), State('password', 'value'), State('email', 'value')])
# def insert_users(n_clicks, un, pw, em):
#     hashed_password = generate_password_hash(pw, method='sha256')
#     if un is not None and pw is not None and em is not None:
#         ins = Users_tbl.insert().values(username=un,  password=hashed_password, email=em,)
#         con = engine.connect()
#         con.execute(ins)
#         con.close()
#         return [login]
#     else:
#         return [html.Div([html.H2('Already have a user account?'), dcc.Link('Click here to Log In', href='/login')])]
#
# login =  html.Div([dcc.Location(id='url_login', refresh=True)
#             , html.H2('''Please log in to continue:''', id='h1')
#             , dcc.Input(placeholder='Enter your username',
#                     type='text',
#                     id='uname-box')
#             , dcc.Input(placeholder='Enter your password',
#                     type='password',
#                     id='pwd-box')
#             , html.Button(children='Login',
#                     n_clicks=0,
#                     type='submit',
#                     id='login-button')
#             , html.Div(children='', id='output-state')
#         ])
#
# @app.callback(
#     Output('url_login', 'pathname')
#     , [Input('login-button', 'n_clicks')]
#     , [State('uname-box', 'value'), State('pwd-box', 'value')])
# def successful(n_clicks, input1, input2):
#     user = Users.query.filter_by(username=input1).first()
#     if user:
#         if check_password_hash(user.password, input2):
#             login_user(user)
#             return '/success'
#         else:
#             pass
#     else:
#         pass
# @app.callback(
#     Output('output-state', 'children')
#     , [Input('login-button', 'n_clicks')]
#     , [State('uname-box', 'value'), State('pwd-box', 'value')])
# def update_output(n_clicks, input1, input2):
#     if n_clicks > 0:
#         user = Users.query.filter_by(username=input1).first()
#         if user:
#             if check_password_hash(user.password, input2):
#                 return ''
#             else:
#                 return 'Incorrect username or password'
#         else:
#             return 'Incorrect username or password'
#     else:
#         return ''
#
# success = html.Div([dcc.Location(id='url_login_success', refresh=True)
#             , html.Div([html.H2('Login successful.')
#                     , html.Br()
#                     , html.P('Select a Dataset')
#                     , dcc.Link('Data', href = '/data')
#                 ]) #end div
#             , html.Div([html.Br()
#                     , html.Button(id='back-button', children='Go back', n_clicks=0)
#                 ]) #end div
#         ]) #end div
#
# failed = html.Div([ dcc.Location(id='url_login_df', refresh=True)
#             , html.Div([html.H2('Log in Failed. Please try again.')
#                     , html.Br()
#                     , html.Div([login])
#                     , html.Br()
#                     , html.Button(id='back-button', children='Go back', n_clicks=0)
#                 ]) #end div
#         ]) #end div
#
# logout = html.Div([dcc.Location(id='logout', refresh=True)
#         , html.Br()
#         , html.Div(html.H2('You have been logged out - Please login'))
#         , html.Br()
#         , html.Div([login])
#         , html.Button(id='back-button', children='Go back', n_clicks=0)
#     ])#end div