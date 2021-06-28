from dash.exceptions import PreventUpdate
from ..neighbors_model import bathroom_text_encoder, pipeline_model
import pandas as pd
import numpy as np
import json
import os
import flask
from dash import Dash
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from ..data_loading import load_listing
import dash_bootstrap_components as dbc


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
    center_lat = sum(df.latitude)/len(df.latitude)
    center_long = sum(df.longitude)/len(df.longitude)
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
                "size": 5,
                "opacity": 0.7,
                "color": '#F70F0F'
            }
        }],
        "layout": layout_map
    }
    return figure




# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
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

layout = html.Div(children=[
    html.Div(
        html.H4(children="Select City:")
    ),
    html.Div(children=[
        dcc.Dropdown(id='city_dd',
                     options=[{'label': i, 'value': i} for i in cities],
                     value='united-states, tx, austin', placeholder='united-states, tx, austin',
                     style={'height': 50, 'width': 500, }),
        dcc.Store(id='current_city', storage_type='session', data='Austin, TX'),
    ]),
    html.Div(className='row',
             children=[
                 html.Div(
                     dcc.Textarea(id='Static_listing_type_text',
                                  value='Select Listing Type:',
                                  className="three columns",
                                  style={'height': 50, 'width': 200, "margin-left": "15px"},
                                  disabled=True)
                 ),
                 html.Div(
                     dcc.Dropdown(id='listing_dd',
                                  options=[{'label': i, 'value': i} for i in room_type],
                                  value=room_type[0], placeholder=room_type[0],
                                  className="three columns",
                                  style={'height': 50, 'width': 200, 'color': 'black'},
                                  )
                 ),
                 html.Div(
                     dcc.Textarea(id='Static_num_bathrooms_text',
                                  value='Select # of bathrooms:',
                                  className="twelve columns",
                                  style={'height': 50, 'width': 175, "margin-left": "15px"},
                                  disabled=True)
                 ),
                 html.Div(
                     dcc.Dropdown(id='num_bathrooms_dd',
                                  options=[{'label': i, 'value': i} for i in bath_options],
                                  value='1 bath', placeholder='1 bath',
                                  className="three columns",
                                  style={'height': 50, 'width': 150, 'color': 'black'},
                                  )
                 ),
                 html.Div(
                     dcc.Textarea(id='Static_num_bedrooms_text',
                                  value='Select # of Beds:',
                                  className="three columns",
                                  style={'height': 50, 'width': 175, "margin-left": "15px"},
                                  disabled=True)
                 ),
                 html.Div(
                     dcc.Dropdown(id='num_bedrooms_dd',
                                  options=[{'label': i, 'value': i} for i in bed_options],
                                  value='1', placeholder='1',
                                  className="three columns",
                                  style={'height': 50, 'width': 150, 'color': 'black'},
                                  )
                 ),
             ]
             ),
    html.Div(className='row', children=[
        html.Div(children=[
            html.Button('Filter Listings for Selected Options', id='filter_button', n_clicks=0),
            dcc.Store(id='session', storage_type='session', data=clicks),
        ])]
             ),
    html.Div(className='row',
                 children=[
                html.Div(
                    html.H6(children="Latitude:")
                    ),
                 dcc.Input(id="lat_dd", placeholder=center_lat, type="number"),
                 html.Br(),
                 html.P(id="output")
                ]),
    html.Div(className='row',
                     children=[
                    html.Div(
                        html.H6(children="Longitude:")
                        ),
                     dcc.Input(id="long_dd", placeholder=center_long, type="number"),
                     html.Br(),
                     html.P(id="output")
                    ]),
    html.Div(className='row', children=[
        html.Div(children=[
            dcc.Graph(
                id='MapPlot', figure=create_figure(city_df, 'Austin, TX')
            )
        ]
        ),
        html.Div(
            dcc.Textarea(id='prediction-output',
                         value='Output',
                         className="two columns",
                         style={'height': 100, 'width': 300, "margin-left": "15px"},
                         disabled=True))
    ])
]
)
