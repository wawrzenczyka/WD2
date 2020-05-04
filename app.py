# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import dataset
import voivodes

surv_df = dataset.load()

surv_removed_df = surv_df[surv_df['Terminated'] == 1]

# TIMELINE DATA
timeline_mock_df = surv_removed_df[
    (surv_removed_df['MainAddressVoivodeship'] == 'mazowieckie') & (surv_removed_df['PKDMainSection'] == 'G')]

timeline_mock_df = pd.DataFrame({'count': timeline_mock_df.groupby("YearOfTermination").size()}).reset_index()

# MAP
with open('assets/wojewodztwa-medium.geojson', encoding='utf8') as woj_json:
    wojewodztwa_geo = json.load(woj_json)

mock_map_df = pd.DataFrame(
    {
        'woj_id': [i for i in range(16)],
        'mock_val': [i for i in range(16)]
    }
)

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
                            children=dcc.Graph(
                                id='map',
                                className='fill-height'
                            )
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
    [Input('year-slider', 'value')])
def update_map(year):
    terminated = surv_df[surv_df['YearOfTermination'] <= year]['MainAddressVoivodeship'].value_counts()
    all = surv_df['MainAddressVoivodeship'].value_counts()
    voivode_df = pd.concat([terminated, all], axis=1, keys=['terminated', 'all']).reset_index()
    voivode_df['TerminatedPercentage'] = voivode_df['terminated'] / voivode_df['all'] * 100.0
    fig = px.choropleth_mapbox(voivode_df,
                               geojson=wojewodztwa_geo,
                               locations='index',
                               featureidkey='properties.nazwa',
                               range_color=(0, 80),
                               color='TerminatedPercentage',
                               opacity=0.5,
                               hover_name='index',
                               labels={
                                   'TerminatedPercentage': 'Terminated %'
                               },
                               title='Voivodes map'
                               )
    scatter = go.Scattermapbox(
        lat=voivode_df['index'].map(voivodes.get_lat_dict()),
        lon=voivode_df['index'].map(voivodes.get_lon_dict()),
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=(voivode_df['all'] - voivode_df['all'].min())
            / (voivode_df['all'].max() - voivode_df['all'].min()) * 100,
            color='black'
        )
    )
    fig.append_trace(scatter, 1, 1)
    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_center={"lat": 52.10, "lon": 19.42},
        mapbox_zoom=5,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
