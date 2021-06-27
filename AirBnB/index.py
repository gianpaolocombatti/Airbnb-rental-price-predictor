import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

from app import app

column1 = dbc.Col(
    [
        dcc.Markdown(
            """

            ## This app will enable Airbnb Hosts decide what is the ideal price of their listings dependant on location,type of home, rooms and number of bathrooms. 
            
            
            """
        ),
        dcc.Link(dbc.Button('Predict Price', color='primary'), href='/predictions')
    ],
    md=4,
)

column2 = dbc.Col(
    [
        html.Img(src='assets/airbnb-host.jpeg',className='img-fluid', style = {'height': '350px'})
    ]
)

layout = dbc.Row([column1, column2])