# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions']=True

default_data = [{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Arizona', 'size': 'State'},
                {'x': [1, 2, 3], 'y': [1, 2, 3], 'type': 'bar', 'name': 'Phoenix', 'size': 'City'},
                {'x': [1, 2, 3], 'y': [2, 3, 4], 'type': 'bar', 'name': 'Chandler', 'size': 'City'}]

app.layout = html.Div(children=[

    ### Header section
    html.H1(children='Hello, PayPal Opportunity Hack 2018! Exploratory demo below.'),
    html.Div(children=['''This is built using ''',
                       html.A('Dash\n', href="https://plot.ly/products/dash/")
    ]),
    html.Br(),

    ### Link section
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # TODO : Format "Navigate to..."
    dcc.Link('Navigate to Home', href='/'),
    html.Br(),
    dcc.Link('Navigate to Config Page.', href='/config'),
    html.Br(),
    dcc.Link('Navigate to UI Demo.', href='/ui-demo'),
    html.Br(),
    dcc.Link('Navigate to CSV month update for Excel tool.', href='/csv-for-excel-tool'),
    html.Br(),
    dcc.Link('Navigate to Food Bank Manager Scraping Tool.', href='/fbm-tool'),

    # content will be rendered in this element
    html.Div(id='page-content')
])


# Link Callback
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/ui-demo':
        return [
            html.Div([
                #dcc.Input(id='input-1-state', type='text', value='1,2,3'),
                #dcc.Input(id='input-2-state', type='text', value='4,3,2'),
                dcc.Dropdown(
                    id='dropdown-2',
                    options=[
                        {'label': s, 'value': s} for s in tuple(set(d['size'] for d in default_data))
                    ],
                    multi=True#,value=[d['name'] for d in default_data]
                ),
                dcc.Dropdown(
                    id='dropdown-1',
                    options=[
                        {'label': 'Bar Chart', 'value': 'bar'},
                        {'label': 'Line Chart', 'value': 'line'}
                    ],
                    value='line'
                ),
                #html.Button(id='submit-button', children='Submit'),
                html.Div(id='output-state')
            ]),

            dcc.Graph(
                id='example-graph',
                figure={
                    'data': [
                        default_data
                    ],
                    'layout': {
                        'title': 'Dash Data Visualization (dummy data)'
                    }
                }
            )
        ]
    else:
        return html.Div([
            html.H3('Default page: You are on page {}'.format(pathname))
        ])


# Graph Callback
@app.callback(Output('example-graph', 'figure'),
                [Input('dropdown-1', 'value'),
                 Input('dropdown-2', 'value')])
def update_output(drop1, multidrop2):
    figure = {'data': list((dict(d, **{'type': drop1}) for d in default_data if d['size'] in multidrop2) if multidrop2 else {})}
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
