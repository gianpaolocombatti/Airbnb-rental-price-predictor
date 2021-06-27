import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import scipy
import index
import predictions
from app import app, server

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


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return index.layout
    elif pathname == '/predictions':
        return predictions.layout
    else:
        return dcc.Markdown('## Page not found')

if __name__ == '__main__':
    app.run_server(debug=True)