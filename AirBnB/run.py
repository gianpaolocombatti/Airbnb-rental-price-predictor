from flask_login import login_user, logout_user, current_user, LoginManager
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import sqlite3
from sqlalchemy import Table, create_engine
import dash_bootstrap_components as dbc
from pages import index
from pages import predictions
import dash
import os
import warnings
import configparser
from .neighbors_model import bathroom_text_encoder, pipeline_model
import pandas as pd
from .data_loading import load_listing

def get_layout(center_lat, center_long):
    key = 'pk.eyJ1IjoiY2djb2xsaW5zOTEiLCJhIjoiY2txNDlzd2pwMTZlbjJ1bzR5M2xtbDM3cyJ9.JJ9ja2pcERkn2guyEVivg'
    map = dict(
        autosize=True,
        height=500,
        weidth=100,
        font=dict(color="#191A1A"),
        titlefont=dict(color="#191A1A", size='14'),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        ),
        hovermode="closest",
        plot_bgcolor='#fffcfc',
        paper_bgcolor='#fffcfc',
        legend=dict(font=dict(size=2), orientation='h'),
        mapbox=dict(
            accesstoken=key,
            style="open-street-map",
            center=dict(
                lon=center_long,
                lat=center_lat,
            ),
            zoom=10,
        )
    )
    return map
def create_figure(df, city):
    center_lat = sum(df.latitude) / len(df.latitude)
    center_long = sum(df.longitude) / len(df.longitude)
    layout_map = get_layout(center_lat, center_long)
    figure = {
        "data": [{
            "type": "scattermapbox",
            "lat": list(df.latitude),
            "lon": list(df.longitude),
            "hoverinfo": "text",
            "hovertext": [["Neighborhood: {} Price: {} Rating: {} Beds: {} Bath:{}".format(i, j, k, n, m)]
                          for i, j, k, n, m in zip(df['neighbourhood'], df['price'], df['review_scores_rating'],
                                                   df['bedrooms'], df['bathrooms_text'],
                                                   )],
            "mode": "markers",
            "name": city,
            "marker": {
                "size": df['size'],
                "opacity": 0.7,
                "color": df['color'],
                "color_discrete_map": {'yes': 'red', 'no': 'blue'},
                "color_discrete_sequence": ['blue', 'red']
            }
        }],
        "layout": layout_map
    }
    return figure

dir_value = 'united-states, tx, austin'
city_df, keys = load_listing(dir_value=dir_value, list_names=True)
for column in city_df.columns:
    city_df[column] = city_df[column].fillna("Missing")
lat = city_df['latitude']
long = city_df['longitude']
n = len(lat)
center_lat = sum(lat) / n
center_long = sum(long) / n
clicks = {'clicks': [0]}
count_btn_press = pd.DataFrame(data=clicks)
count_btn_press.to_pickle('clicks.pkl')
cities = [x for x in keys]
# server = flask.Flask(__name__)
# app = Dash(__name__, external_stylesheets=external_stylesheets, meta_tags=meta_tags, server=server)
# app.title = "Airbnb Rental Price Predictor"
# app.config.suppress_callback_exceptions = True
room_type = city_df['room_type'].unique()
bath_options = city_df['bathrooms_text'].unique()
bed_options = city_df['beds'].unique()
city_df['color'] = 'red'
city_df['size'] = 5


warnings.filterwarnings("ignore")
conn = sqlite3.connect('data.sqlite')
engine = create_engine('sqlite:///data.sqlite')
db = SQLAlchemy()
config = configparser.ConfigParser()

class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable = False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

Users_tbl = Table('users', Users.metadata)


external_stylesheets = [
    dbc.themes.UNITED, # Bootswatch theme
    'https://use.fontawesome.com/releases/v5.9.0/css/all.css', # for social media icons
]

meta_tags=[
    {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, meta_tags=meta_tags)
server = app.server
app.config.suppress_callback_exceptions = True # see https://dash.plot.ly/urls

server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI='sqlite:///data.sqlite',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
db.init_app(server)
app.title = 'Airbnb Price Predictor' # appears in browser title bar

navbar = dbc.NavbarSimple(
    brand='Airbnb Price Predictor',
    brand_href='/',
    children=[
        dbc.NavItem(dcc.Link('Predictions', href='/predictions', className='nav-link')),
    ],
    sticky='top',
    color='primary',
    light=False,
    dark=True
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Container(id='page-content', className='mt-4'),
    html.Hr(),
])

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

class Users(UserMixin, Users):
    pass

create = html.Div([html.H1('Create User Account')
        , dcc.Location(id='create_user', refresh=True)
        , dcc.Input(id="username"
            , type="text"
            , placeholder="user name"
            , maxLength =15)
        , dcc.Input(id="password"
            , type="password"
            , placeholder="password")
        , dcc.Input(id="email"
            , type="email"
            , placeholder="email"
            , maxLength = 50)
        , html.Button('Create User', id='submit-val', n_clicks=0)
        , html.Div(id='container-button-basic')
    ])


login =  html.Div([dcc.Location(id='url_login', refresh=True)
            , html.H2('''Please log in to continue:''', id='h1')
            , dcc.Input(placeholder='Enter your username',
                    type='text',
                    id='uname-box')
            , dcc.Input(placeholder='Enter your password',
                    type='password',
                    id='pwd-box')
            , html.Button(children='Login',
                    n_clicks=0,
                    type='submit',
                    id='login-button')
            , html.Div(children='', id='output-state')
        ])

success = html.Div([dcc.Location(id='url_login_success', refresh=True)
            , html.Div([html.H2('Login successful.')
                    , html.Br()
                    , html.P('Go to Predictor')
                    , dcc.Link(dbc.Button('Predict', color='primary'), href='/predictions')
                ]) #end div
            , html.Div([html.Br()
                    , html.Button(id='back-button', children='Go back', n_clicks=0)
                ]) #end div
        ]) #end div

failed = html.Div([dcc.Location(id='url_login_df', refresh=True)
            , html.Div([html.H2('Log in Failed. Please try again.')
                    , html.Br()
                    , html.Div([login])
                    , html.Br()
                    , html.Button(id='back-button', children='Go back', n_clicks=0)
                ]) #end div
        ]) #end div

logout = html.Div([dcc.Location(id='logout', refresh=True)
        , html.Br()
        , html.Div(html.H2('You have been logged out - Please login'))
        , html.Br()
        , html.Div([login])
        , html.Button(id='back-button', children='Go back', n_clicks=0)
    ])#end div

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return index.layout
    elif pathname == '/create':
        return create
    elif pathname == '/login':
        return login
    elif pathname == '/success':
        if current_user.is_authenticated:
            return success
        else:
            return failed
    elif pathname == '/predictions':
        return predictions.layout
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout
        else:
            return logout
    else:
        return '404'

@app.callback(
   [Output('container-button-basic', "children")]
    , [Input('submit-val', 'n_clicks')]
    , [State('username', 'value'), State('password', 'value'), State('email', 'value')])
def insert_users(n_clicks, un, pw, em):
    hashed_password = generate_password_hash(pw, method='sha256')
    if un is not None and pw is not None and em is not None:
        ins = Users_tbl.insert().values(username=un,  password=hashed_password, email=em,)
        conn = engine.connect()
        conn.execute(ins)
        conn.close()
        return [login]
    else:
        return [html.Div([html.H2('Already have a user account?'), dcc.Link('Click here to Log In', href='/login')])]

@app.callback(
    Output('url_login', 'pathname')
    , [Input('login-button', 'n_clicks')]
    , [State('uname-box', 'value'), State('pwd-box', 'value')])
def successful(n_clicks, input1, input2):
    user = Users.query.filter_by(username=input1).first()
    if user:
        if check_password_hash(user.password, input2):
            login_user(user)
            return '/success'
        else:
            pass
    else:
        pass
@app.callback(
    Output('output-state', 'children')
    , [Input('login-button', 'n_clicks')]
    , [State('uname-box', 'value'), State('pwd-box', 'value')])
def update_output(n_clicks, input1, input2):
    if n_clicks > 0:
        user = Users.query.filter_by(username=input1).first()
        if user:
            if check_password_hash(user.password, input2):
                return ''
            else:
                return 'Incorrect username or password'
        else:
            return 'Incorrect username or password'
    else:
        return ''

@app.callback(
    Output('prediction-output', 'value'),
    Output('MapPlot', 'figure'),
    [Input('city_dd', 'value'),
     Input('num_bedrooms_dd', 'value'),
     Input('num_bathrooms_dd', 'value'),
     Input('listing_dd', 'value'),
     Input('lat_dd', 'value'),
     Input('long_dd', 'value'),
     ]
)
def predict_price(city_dd, num_bedrooms_dd, num_bathrooms_dd, listing_dd, lat_dd, long_dd):
    df_predict = pd.DataFrame(
        columns=['bedrooms', 'bathrooms_text', 'room_type', 'latitude', 'longitude'],
        data=[[num_bedrooms_dd, num_bathrooms_dd, listing_dd, lat_dd, long_dd]])
    new = load_listing(dir_value=city_dd)
    new['color'] = 'red'
    new['size'] = 5
    new1 = new[['bedrooms', 'bathrooms_text', 'room_type', 'price', 'latitude', 'longitude']]
    shared, private = bathroom_text_encoder(df_predict)
    df_predict['shared_bathrooms'] = shared
    df_predict['private_bathrooms'] = private
    df_predict.drop(columns=['bathrooms_text'], inplace=True)
    new1 = new1.replace("Missing", None)
    pipe, oh, stand, simp, kneigh = pipeline_model(new1,
                                                   cols_to_keep=['bathrooms_text', 'bedrooms', 'room_type',
                                                                 'price', 'latitude', 'longitude'])
    one = oh.transform(df_predict)
    two = stand.transform(one)
    three = simp.transform(two)
    four = kneigh.kneighbors(three, n_neighbors=20)
    y_pred = pipe.predict(df_predict)[0]
    near_neighbors = four[1]
    value = f'${y_pred} is the optimal rental price for the property'
    filter_df = new.copy()
    filter_df['bedrooms'] = filter_df['bedrooms'].astype('float')
    filter_df = filter_df.loc[filter_df['bathrooms_text'] == num_bathrooms_dd]
    filter_df = filter_df.loc[filter_df['bedrooms'] >= float(num_bedrooms_dd)]
    filter_df = filter_df.loc[filter_df['room_type'] == listing_dd]
    for x in near_neighbors:
        beta = new.loc[x]
        beta['color'] = 'blue'
        beta['size'] = 20
        final_df = pd.concat([filter_df, beta])
    figure = create_figure(final_df, city_dd)
    return value, figure

if __name__ == '__main__':
    app.run_server()