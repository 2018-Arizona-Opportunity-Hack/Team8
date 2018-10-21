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

app.layout = html.Div(id='page-content')

@server.route('/')
def home_page():
    return """
        <html>
            <head>
                <link rel="shortcut icon" type="image/png" href="/favicon.ico"/>
            </head>
            <body>
                <h1>Food Bank Manager tools homepage.</h1>
                <br>
                <a href="/viz">Navigate to Visualization page.</a>
                <br>
                <a href="/download">Navigate to Food Bank Manager Scraping Tool.</a>
                <br>
                <a href="/csv-for-excel-tool">Navigate to CSV month update for Excel tool.</a>
                <br>
            </body>
        </html>
    """

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
                <link rel="stylesheet" type="text/css" href="assets/style.css">
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

@server.route('/data', methods=['POST'])
def get_data():
    if request.method != 'POST':
        return 'Bad Request'
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    search_args = FBM.create_search_args(start_date, end_date)
    donations, entries = FBM.fetch_all_fbm_csv_data(search_args)
    return jsonify(FBM.csv_to_dictionary(donations, transpose = True))
    

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

    donations, entries = FBM.fetch_last_fbm_report()
    result = FBM.create_summary_csv(donations)

    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=result.csv"

    return response


if __name__ == '__main__':
    server.run(debug=True)
