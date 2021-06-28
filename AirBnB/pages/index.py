import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


column1 = dbc.Col(
    [
        dcc.Markdown(
            """

            ## This app will enable Airbnb Hosts decide what is the ideal price of their listings dependant on location,type of home, rooms and number of bathrooms. 
            
            
            """
        ),
        dcc.Link(dbc.Button('Check it out!', color='primary'), href='/create')
    ],
    md=4,
)

column2 = dbc.Col(
    [
        html.Img(src='../assets/airbnb-host.jpeg', className='img-fluid', style = {'height': '350px'})
    ]
)

layout = dbc.Row([column1, column2])