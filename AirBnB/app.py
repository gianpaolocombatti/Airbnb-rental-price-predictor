from dash.exceptions import PreventUpdate
from neighbors_model import bathroom_text_encoder, pipeline_model
from read_listings import load_data
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


def create_app():
    load_data()
    path = os.getcwd()
    pickle_path = os.path.abspath(os.path.join(path, './AirBnB.pkl'))
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    df = pd.read_pickle(pickle_path)
    city = 'Austin, TX'
    city_df = df.loc[df['City'] == city]
    lat = city_df['latitude']  # *100
    long = city_df['longitude']  # *100
    n = len(lat)
    center_lat = sum(lat) / n
    center_long = sum(long) / n
    clicks = {'clicks': [0]}
    count_btn_press = pd.DataFrame(data=clicks)
    count_btn_press.to_pickle('clicks.pkl')

    cities = ['Asheville, NC', 'Austin, TX', 'Broward, FL', 'Cambridge, MA', 'Chicago, IL', 'Columbus, OH']
    server = flask.Flask(__name__)
    app = Dash(__name__, external_stylesheets=external_stylesheets, server=server)
    room_type = city_df['room_type'].unique()
    bath_options = city_df['bathrooms_text'].unique()
    bed_options = city_df['beds'].unique()

    app.layout = html.Div(children=[
            html.Div(
                html.H4(children="Select City:")
            ),
            html.Div(children=[
                dcc.Dropdown(id='city_dd',
                             options=[{'label': i, 'value': i} for i in cities],
                             value='Austin, TX', placeholder='Austin, TX',
                             style={'color': "black"}),
                dcc.Store(id='current_city', storage_type='session', data='Austin, TX'),
            ]),
            html.Div(className='row',
                     children=[
                         html.Div(
                                 dcc.Textarea(id='Static_listing_type_text',
                                              value='Select Listing Type:',
                                              className="six columns",
                                              style={'height': 50, 'width': 100},
                                              disabled=True)
                        ),
                         html.Div(
                             dcc.Dropdown(id='listing_dd',
                                          options=[{'label': i, 'value': i} for i in room_type],
                                          value=room_type[0], placeholder=room_type[0],
                                          className="six columns",
                                          style={'height': 50, 'width': 150, 'color': 'black'},
                                          )
                                ),
                         html.Div(
                             dcc.Textarea(id='Static_num_bathrooms_text',
                                          value='Select # of bathrooms:',
                                          className="six columns",
                                          style={'height': 50, 'width': 150},
                                          disabled=True)
                                 ),
                         html.Div(
                             dcc.Dropdown(id='num_bathrooms_dd',
                                          options=[{'label': i, 'value': i} for i in bath_options],
                                          value='1 bath', placeholder='1 bath',
                                          className="six columns",
                                          style={'height': 50, 'width': 150, 'color': 'black'},
                                          )
                         ),
                         html.Div(
                             dcc.Textarea(id='Static_num_bedrooms_text',
                                          value='Select # of Beds:',
                                          className="six columns",
                                          style={'height': 50, 'width': 150},
                                          disabled=True)
                         ),
                         html.Div(
                             dcc.Dropdown(id='num_bedrooms_dd',
                                          options=[{'label': i, 'value': i} for i in bed_options],
                                          value='1', placeholder='1',
                                          className="six columns",
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
                             style={'height': 50, 'width': 150},
                             disabled=True))
            ])
        ]
    )

    @app.callback(
        Output('MapPlot', 'figure'),
        [Input('city_dd', 'value')],
        state=[State('num_bedrooms_dd', 'value'),
               State('num_bathrooms_dd', 'value'),
               State('listing_dd', 'value'),
               State('current_city', 'data'),
               ]
    )
    def update_city_data(city_dd, num_bedrooms_dd, num_bathrooms_dd,
                         listing_dd,  current_city):

        df = pd.read_pickle(pickle_path) # This will be replaced with pull dataframe from SQL
        city_df = df.loc[df['City'] == city_dd]
        filter_df = city_df.loc[city_df['bedrooms'] != 'Missing'].copy()
        filter_df['bedrooms'] = filter_df['bedrooms'].astype('float')
        filter_df = filter_df.loc[filter_df['bathrooms_text'] == num_bathrooms_dd]
        filter_df = filter_df.loc[filter_df['bedrooms'] >= float(num_bedrooms_dd)]
        filter_df = filter_df.loc[filter_df['room_type'] == listing_dd]
        figure = create_figure(filter_df, city_dd)
        if len(filter_df) == 0:
            city_df = df.loc[df['City'] == city_dd]
            figure = create_figure(city_df, city_dd)
        else:
            figure = create_figure(filter_df, city_dd)

        if current_city != city_dd:
            city_df = df.loc[df['City'] == city_dd]
            filter_df = df.loc[df['City'] == city_dd].copy()
            filter_df = filter_df.loc[filter_df['bedrooms'] != 'Missing'].copy()
            filter_df['bedrooms'] = filter_df['bedrooms'].astype('float')
            filter_df = filter_df.loc[filter_df['bathrooms_text'] == num_bathrooms_dd]
            filter_df = filter_df.loc[filter_df['bedrooms'] >= float(num_bedrooms_dd)]
            filter_df = filter_df.loc[filter_df['room_type'] == listing_dd]
            figure = create_figure(city_df, city_dd)

            if len(filter_df) == 0:
                city_df = df.loc[df['City'] == city_dd]
                figure = create_figure(city_df, city_dd)
            else:
                figure = create_figure(filter_df, city_dd)

        return figure

    @app.callback(
        Output('prediction-output','value'),
        [Input('city_dd', 'value'),
        Input('num_bedrooms_dd', 'value'),
        Input('num_bathrooms_dd', 'value'),
        Input('listing_dd', 'value'),
             ]
    )

    def predict_price(city_dd, num_bedrooms_dd, num_bathrooms_dd,listing_dd):

        df_predict = pd.DataFrame(
            columns = ['City','bedrooms','bathrooms_text','room_type'],
            data = [[city_dd, num_bedrooms_dd, num_bathrooms_dd, listing_dd]])
        new = df.loc[df['City']==city_dd]
        shared, private = bathroom_text_encoder(df_predict)
        df_predict['shared_bathrooms'] = shared
        df_predict['private_bathrooms'] = private
        df_predict.drop(columns=['bathrooms_text', 'City'], inplace=True)
        pipe, oh, stand, simp, kneigh = pipeline_model(new, cols_to_keep=['bathrooms_text', 'bedrooms', 'room_type',
                                                                         'price'])
        one = oh.transform(df_predict)
        two = stand.transform(one)
        three = simp.transform(two)
        four = kneigh.kneighbors(three, n_neighbors=20)
        y_pred = pipe.predict(df_predict)[0]
        near_neighbors = four[1]
        return f'{y_pred} is the optimal rental price for the property'

    return app


if __name__ == "__main__":
    app = create_app()
    app.run_server(debug=True, port=8040)