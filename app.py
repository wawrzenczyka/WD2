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

surv_df = dataset.load()
surv_removed_df = surv_df[surv_df['Terminated'] == 1]

# TIMELINE DATA
timeline_mock_df = surv_removed_df[
    (surv_removed_df['MainAddressVoivodeship'] == 'mazowieckie') & (surv_removed_df['PKDMainSection'] == 'G')]

timeline_mock_df = pd.DataFrame({'count': timeline_mock_df.groupby("YearOfTermination").size()}).reset_index()

# MAP
with open('assets/wojewodztwa-medium.geojson', encoding='utf8') as woj_json:
    wojewodztwa_geo = json.load(woj_json)

with open('assets/powiaty-medium.geojson', encoding='utf8') as pow_json:
    powiaty_geo = json.load(pow_json)

# map county names to lower
for feature in powiaty_geo['features']:
    feature['properties']['nazwa'] = dataset\
        .replace_polish_chars(str.lower(feature['properties']['nazwa'])\
                              .lstrip('powiat').strip())

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
                    dbc.Col(md=8,
                            className='fill-height',
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
                                                ),
                                        dbc.Col(md=6,
                                                className='fill-height',
                                                children=[
                                                    html.H5('Partition:'),
                                                    dcc.RadioItems(
                                                        id='map-data-radiobuttons',
                                                        options=[
                                                            {'label': 'Voivodes', 'value': 0},
                                                            {'label': 'Counties', 'value': 1}
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
                    dbc.Col(md=4,
                            children=html.Div("TreeMap")
                            )
                ]),
            dbc.Row(
                className='bottom',
                no_gutters=True,
                children=[
                    dbc.Col(md=8,
                            className='fill-height',
                            children=dcc.Graph(
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
                            ),
                    dbc.Col(md=4,
                            children=html.Div("TEXT")
                            ),

                ])
        ]
    )
)


@app.callback(
    Output('map', 'figure'),
    [
        Input('year-slider', 'value'),
        Input('map-type-radiobuttons', 'value'),
        Input('map-data-radiobuttons', 'value')
    ])
def update_map(year, map_type, data_type):
    data = {'geojson': wojewodztwa_geo, 'column': 'MainAddressVoivodeship'} \
        if data_type == 0 else {'geojson': powiaty_geo, 'column': 'MainAddressCounty'}

    map = {'color': 'active', 'range': (0, 43000)} \
        if map_type == 0 else {'color': 'TerminatedPercentage', 'range': (0, 80)}

    terminated = surv_df[surv_df['YearOfTermination'] <= year][data['column']].value_counts()
    all = surv_df[data['column']].value_counts()
    voivode_df = pd.concat([terminated, all], axis=1, keys=['terminated', 'all'], sort=True).reset_index()
    voivode_df['TerminatedPercentage'] = voivode_df['terminated'] / voivode_df['all'] * 100.0
    voivode_df['active'] = voivode_df['all'] - voivode_df['terminated']

    fig = px.choropleth_mapbox(voivode_df,
                               geojson=data['geojson'],
                               locations='index',
                               featureidkey='properties.nazwa',
                               color=map['color'],
                               opacity=0.5,
                               range_color=map['range'],
                               hover_name='index',
                               hover_data=[map['color']],
                               labels={
                                   'active': 'Number of active companies',
                                   'TerminatedPercentage': '% of terminated companies'
                               },
                               title='Map'
                               )
    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_center={"lat": 52.10, "lon": 19.42},
        mapbox_zoom=5,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
