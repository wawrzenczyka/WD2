# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies
import plotly.express as px
import pandas as pd
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

from treemap_helper import build_pkd_treemap
pkd_fig = build_pkd_treemap()

voivodeship_select = {
    'Cała Polska': '',
    'Mazowieckie': 'MAZOWIECKIE',
    'Dolnośląskie': 'DOLNOŚLĄSKIE',
}

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Dropdown(
        id='voivodeship-input',
        options=[{'label': i, 'value': voivodeship_select[i]} for i in voivodeship_select],
        value=None
    ),
    dcc.Graph(figure=pkd_fig, id='pkd-tree'),
])

from dash.dependencies import Input, Output
@app.callback(
    Output('pkd-tree', 'figure'),
    [Input('voivodeship-input', 'value'),])
def update_graph(voivodeship):
    return build_pkd_treemap(voivodeship=voivodeship)

if __name__ == '__main__':
    app.run_server(debug=True)