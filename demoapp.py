# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask import Flask, render_template, request, jsonify,\
     send_from_directory, abort, redirect,url_for, stream_with_context,\
     Response, make_response
import food_bank_manager as FBM

server = Flask(__name__)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,server=server, url_base_pathname='/dashapp/')
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
    html.Br(),
    dcc.Link('Navigate to Visualization page.', href='/viz'),

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

@server.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'heart_logo_transparent.png',
                               mimetype='image/vnd.microsoft.icon')

@server.route('/csv-for-excel-tool')
def form():
    return """
        <html>
            <head>
                <link rel="shortcut icon" type="image/png" href="/favicon.ico"/>
            </head>
            <body>
                <h1>Transform a file demo</h1>

                <form action="/transform" method="post" enctype="multipart/form-data">
                    <input type="file" name="data_file" />
                    <input type="submit" />
                </form>
            </body>
        </html>
    """

@server.route('/viz')
def viz_page():
    return send_from_directory('assets','index.html')

@server.route('/transform', methods=["POST"])
def transform_view():
    file = request.files['data_file']
    if not file:
        return "No file"

    month = request.args.get('month', None)
    year = request.args.get('year', None)

    csv_text = file.stream.read().decode("utf-8")
    result = FBM.create_summary_csv(csv_text)

    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=result.csv"

    return response

@server.route('/download')
def download_summary():
    month = request.args.get('month', None)
    year = request.args.get('year', None)

    csv_text = FBM.fetch_last_fbm_report()
    result = FBM.create_summary_csv(csv_text)

    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=result.csv"

    return response

# Graph Callback
@app.callback(Output('example-graph', 'figure'),
                [Input('dropdown-1', 'value'),
                 Input('dropdown-2', 'value')])
def update_output(drop1, multidrop2):
    figure = {'data': list((dict(d, **{'type': drop1}) for d in default_data if d['size'] in multidrop2) if multidrop2 else {})}
    return figure

if __name__ == '__main__':
    server.run(debug=True)
