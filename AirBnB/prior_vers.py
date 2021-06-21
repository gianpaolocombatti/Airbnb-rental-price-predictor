# NOT USED CURRENTLY

# Run this app with `python prior_vers.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import gmplot
import pandas as pd
from dash.dependencies import Input, Output
from read_listings import load_data
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import arrow_function

def create_app():
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    load_data()
    cities = ['Asheville, NC', 'Austin, TX', 'Broward, FL', 'Cambridge, MA', 'Chicago, IL', 'Columbus, OH']

    col_names = df.columns
    city_df = df

    app.layout = html.Div([
        html.Div([
            html.Div([
            dcc.Dropdown(
                id='city',
                options=[{'label': i, 'value': i} for i in cities],
                value=cities[0]
            ),
        ],
            style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                dcc.Dropdown(
                    id='xaxis-column',
                    options=[{'label': i, 'value': i} for i in col_names],
                    value=col_names[0]
                ),
            ],
                style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                dcc.Dropdown(
                    id='yaxis-column',
                    options=[{'label': i, 'value': i} for i in col_names],
                    value=col_names[1]
                ),

            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),



        dcc.Graph(id='city-map'),
    ])

    @app.callback(
        Output('indicator-graphic', 'figure'),
        Input('xaxis-column', 'value'),
        Input('yaxis-column', 'value'),
        Input('city', 'value'))
    def update_graph(xaxis_column_name, yaxis_column_name,
                     city_value):
        dff = df[df['City'] == city_value]

        fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
                         y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
                         hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

        fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

        fig.update_xaxes(title=xaxis_column_name)

        fig.update_yaxes(title=yaxis_column_name,
                         type='linear' if yaxis_type == 'Linear' else 'log')

        return fig

    return app


# if __name__ == '__main__':
#     app.run_server(debug=True)