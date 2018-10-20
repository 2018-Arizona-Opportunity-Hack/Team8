# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello, PayPal Opportunity Hack 2018!'),

    html.Div(children=['''
        This is built using ''',
        html.A('Dash\n', href="https://plot.ly/products/dash/")]),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Arizona'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'line', 'name': 'Chandler'},
                {'x': [1, 2, 3], 'y': [3, 5, 1], 'type': 'line', 'name': 'Phoenix'},

            ],
            'layout': {
                'title': 'Dash Data Visualization (dummy data)'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
