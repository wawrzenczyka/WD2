# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import json
from treemap_helper import build_pkd_treemap
from map_helper import build_map
import event_timeline
import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


surv_df = pd.read_csv(os.path.join(THIS_FOLDER, 'data', 'ceidg_data_formated.csv'), encoding="utf-8")
surv_removed_df = surv_df[surv_df['Terminated'] == 1]

# Global first-page variables
voivodeship = ''
pkd_section = ''

# TIMELINE DATA
timeline_mock_df = surv_removed_df[
    (surv_removed_df['MainAddressVoivodeship'] == 'mazowieckie') & (surv_removed_df['PKDMainSection'] == 'G')]

timeline_mock_df = pd.DataFrame(
    {'count': timeline_mock_df.groupby("YearOfTermination").size()}).reset_index()

# MAP
with open(os.path.join(THIS_FOLDER, 'assets', 'wojewodztwa-min.geojson'), encoding='utf8') as woj_json:
    wojewodztwa_geo = json.load(woj_json)

map_type_options = ['Active companies', '% of terminated companies']

# Treemap init
pkd_fig = build_pkd_treemap()

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    './first-tab.css'
])
app.layout = html.Div(
    className='main-wrapper',
    children=html.Div(
        className='section',
        children=[
            dbc.Row(
                children=[
                    dbc.Col(md=2,
                            children=html.H3("Year:")
                            ),
                    dbc.Col(md=2,
                            children=daq.Slider(
                                color="default",
                                id='year-slider',
                                min=2011,
                                max=2020,
                                step=0.5,
                                value=2020,
                                size=1000,
                                marks={year+0.01: str(int(year))
                                       for year in range(2011, 2021)},
                                targets=event_timeline.EVENTS_SLIDER,
                            ),
                            )
                ]
            ),
            dbc.Row(
                className='top',
                no_gutters=True,
                children=[
                    dbc.Col(md=6,
                            className='box',
                            children=[
                                dbc.Row(
                                    no_gutters=True,
                                    children=[
                                        dbc.Col(md=6,
                                                className='fill-height',
                                                children=[
                                                    html.H5('Filter:'),
                                                    dcc.RadioItems(
                                                        id='map-type-radiobuttons',
                                                        options=[
                                                            {'label': 'Active companies',
                                                                'value': 0},
                                                            {'label': '% of terminated companies',
                                                                'value': 1}
                                                        ],
                                                        value=0,
                                                        labelStyle={
                                                            'display': 'inline-block',
                                                            'padding': 5
                                                        }
                                                    )
                                                ]
                                                )
                                    ]
                                ),
                                dcc.Graph(
                                    id='map',
                                    className='fill-height',
                                    config={
                                        'displayModeBar': False,
                                        'scrollZoom': False
                                    },
                                ),
                                html.Div(id="output")
                                ]
                            ),
                    dbc.Col(md=6,
                            className='box',
                            children=[
                                dcc.Graph(
                                    className='fill-height',
                                    id='timeline',
                                )
                            ]
                            )
                ]),
            dbc.Row(
                className='bottom',
                no_gutters=True,
                children=[
                    dbc.Col(md=12,
                            children=[
                                dcc.Graph(figure=pkd_fig, id='pkd-tree', className='fill-height'),
                            ]
                        )
                ]),
            html.Div(id='selected-voivodeship', style={'display': 'none'}, children=''),
            html.Div(id='selected-pkd-section', style={'display': 'none'}, children=''),
            html.Div(id='selected-voivodeship-indices', style={'display': 'none'}, children='')
        ]
    )
)

@app.callback(
    Output('map', 'figure'),
    [
        Input('year-slider', 'value'),
        Input('map-type-radiobuttons', 'value'),
        Input('selected-voivodeship-indices', 'children'),
    ])
def update_map(year, map_type, selceted_voivodeships):
    return build_map(int(year), map_type, surv_df, wojewodztwa_geo, selceted_voivodeships)

@app.callback(
    [
        Output('selected-voivodeship', 'children'),
        Output('selected-voivodeship-indices', 'children')
    ],
    [
        Input('map', 'selectedData')
    ])
def select_voivodeship(selectedVoivodeship):
    if selectedVoivodeship is None:
        return [], []
    selected_voivodeship = [item['location'].upper() for item in selectedVoivodeship['points']]
    selected_voivodeship_indices = [item['pointIndex'] for item in selectedVoivodeship['points']]
    return selected_voivodeship, selected_voivodeship_indices

@app.callback(
    [
        Output('selected-pkd-section', 'children'),
    ],
    [
        Input('pkd-tree', 'clickData'),
        Input('map', 'clickData'),
    ],
    [
        State('selected-pkd-section', 'children')
    ])
def select_pkd_section(click, mapClick, old):
    ctx = dash.callback_context
    clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    if clicked == 'map':
        # on voivodeship change
        return ['']

    if click is None:
        # on startup
        return ['']

    label = click['points'][0]['label']
    parent = click['points'][0]['parent']

    if 'entry' in click['points'][0] and label == click['points'][0]['entry']:
        # zooming out
        if parent == 'Wszystkie sekcje PKD':
            selected_section = ''
        else:
            if label == 'Wszystkie sekcje PKD':
                # you are in root and click root
                selected_section = ''
            else:
                selected_section = parent.split(' ')[1]
    else:
        # zooming in
        if label == 'Wszystkie sekcje PKD':
            selected_section = ''
        else:
            selected_section = click['points'][0]['label'].split(' ')[1]

    return [selected_section]

@app.callback(
    [
        Output('pkd-tree', 'figure'),
    ],
    [
        Input('selected-voivodeship', 'children'),
    ])
def redraw_treemap(voivodeship):
    return build_pkd_treemap(voivodeship=voivodeship),

@app.callback(
    [
        Output('timeline', 'figure'),
    ],
    [
        Input('year-slider', 'value'),
        Input('selected-voivodeship', 'children'),
        Input('selected-pkd-section', 'children'),
    ])
def redraw_timeline(year, voivodeship, pkd_section):
    data = surv_removed_df

    if voivodeship != []:
        data = data[np.isin(data['MainAddressVoivodeship'], [voiv.lower() for voiv in voivodeship])]
    if pkd_section != '':
        if pkd_section.isalpha():
            # section (eg. A, B, C...)
            data = data[data['PKDMainSection'] == pkd_section]
        else:
            # division (eg. 47)
            data = data[data['PKDMainDivision'] == float(pkd_section)]

    data = pd.DataFrame({'count': data.groupby("YearOfTermination").size()}).reset_index()
    return [event_timeline.build_event_timeline(data, year)]


if __name__ == '__main__':
    app.run_server(debug=True)
