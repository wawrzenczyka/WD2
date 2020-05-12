# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import json
import dataset
from treemap_helper import build_pkd_treemap
from map_helper import build_map

surv_df = dataset.load()
surv_removed_df = surv_df[surv_df['Terminated'] == 1]

pkd_fig = build_pkd_treemap()

voivodeship_select = {
    'Cała Polska': '',
    'Mazowieckie': 'MAZOWIECKIE',
    'Dolnośląskie': 'DOLNOŚLĄSKIE',
}

# TIMELINE DATA
timeline_mock_df = surv_removed_df[
    (surv_removed_df['MainAddressVoivodeship'] == 'mazowieckie') & (surv_removed_df['PKDMainSection'] == 'G')]

timeline_mock_df = pd.DataFrame({'count': timeline_mock_df.groupby("YearOfTermination").size()}).reset_index()

# MAP
with open('assets/wojewodztwa-min.geojson', encoding='utf8') as woj_json:
    wojewodztwa_geo = json.load(woj_json)

map_type_options = ['Active companies', '% of terminated companies']

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
                    dbc.Col(md=1,
                            children=html.H3("Year:")
                            ),
                    dbc.Col(md=11,
                            children=dcc.Slider(
                                id='year-slider',
                                min=2011,
                                max=2020,
                                step=1,
                                value=2020,
                                marks={year: str(year) for year in range(2011, 2021)}
                            )
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
                                    children=
                                    [
                                        dbc.Col(md=6,
                                                className='fill-height',
                                                children=[
                                                    html.H5('Filter:'),
                                                    dcc.RadioItems(
                                                        id='map-type-radiobuttons',
                                                        options=[
                                                            {'label': 'Active companies', 'value': 0},
                                                            {'label': '% of terminated companies', 'value': 1}
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
                                    className='fill-height'
                                )]
                            ),
                    dbc.Col(md=6,
                            className='box',
                            children=[
                                dcc.Graph(
                                    className='fill-height',
                                    id='timeline',
                                    responsive=False,
                                    figure={
                                        'data': [dict(
                                            x=timeline_mock_df['YearOfTermination'],
                                            y=timeline_mock_df['count']
                                        )]
                                    }
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
                                dcc.Dropdown(
                                    id='voivodeship-input',
                                    options=[{'label': i, 'value': voivodeship_select[i]} for i in voivodeship_select],
                                    value=None
                                ),
                                dcc.Graph(figure=pkd_fig, id='pkd-tree', className='fill-height'),
                            ]
                            )
                ])
        ]
    )
)


@app.callback(
    Output('map', 'figure'),
    [
        Input('year-slider', 'value'),
        Input('map-type-radiobuttons', 'value')
    ])
def update_map(year, map_type):
    return build_map(year, map_type, surv_df, wojewodztwa_geo)


@app.callback(
    Output('pkd-tree', 'figure'),
    [Input('voivodeship-input', 'value')])
def update_graph(voivodeship):
    return build_pkd_treemap(voivodeship=voivodeship)


if __name__ == '__main__':
    app.run_server(debug=True)
