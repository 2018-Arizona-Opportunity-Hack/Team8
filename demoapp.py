# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

default_data = [{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Arizona', 'size': 'State'},
                {'x': [1, 2, 3], 'y': [1, 2, 3], 'type': 'bar', 'name': 'Phoenix', 'size': 'City'},
                {'x': [1, 2, 3], 'y': [2, 3, 4], 'type': 'bar', 'name': 'Chandler', 'size': 'City'}]

app.layout = html.Div(children=[
    html.H1(children='Hello, PayPal Opportunity Hack 2018! Exploratory demo below.'),

    html.Div(children=['''
        This is built using ''',
        html.A('Dash\n', href="https://plot.ly/products/dash/")
    ]),

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
])

@app.callback(Output('example-graph', 'figure'),
                [#Input('submit-button', 'n_clicks'),
                 Input('dropdown-1', 'value'),
                 Input('dropdown-2', 'value')])
                #[State('input-1-state', 'value'),
                # State('input-2-state', 'value')])
def update_output(drop1, multidrop2):#, input1, input2):
    '''
    inp1y, inp2y = map(lambda x: list(map(float, x.replace(' ', '').split(','))), (input1, input2))
    inp1x, inp2x = map(lambda x: list(range(1, len(x)+1)), (inp1y, inp2y))
    print(inp1x, inp2x, inp1y, inp2y, drop1)
    figure = {
        'data': [
            dict(default_data, **{'type': drop1}),
            #dict({'x': inp1x, 'y': inp1y, 'mode': input3, 'name': 'Phoenix'}, **({'mode': input4} if input4 else {})),

        ]
    }
    '''
    figure = {'data': list((dict(d, **{'type': drop1}) for d in default_data if d['size'] in multidrop2) if multidrop2 else {})}
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
