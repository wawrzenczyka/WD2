# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json
import dataset


surv_df = dataset.load()

surv_removed_df = surv_df[surv_df['Terminated'] == 1]

# TIMELINE DATA
timeline_mock_df = surv_removed_df[(surv_removed_df['MainAddressVoivodeship'] == 'mazowieckie') & (surv_removed_df['PKDMainSection'] == 'G')]

timeline_mock_df = pd.DataFrame({'count': timeline_mock_df.groupby("YearOfTermination").size()}).reset_index()


#MAP
with open('assets/wojewodztwa-medium.geojson') as woj_json:
    wojewodztwa_geo = json.load(woj_json)

woj_ids = {
    0: 'śląskie',
    1: 'opolskie',
    2: 'wielkopolskie',
    3: 'zachodniopomorskie',
    4: 'świętokrzyskie',
    5: 'kujawsko-pomorskie',
    6: 'podlaskie',
    7: 'dolnośląskie',
    8: 'podkarpackie',
    9: 'małopolskie',
    10: 'pomorskie',
    11: 'warmińsko-mazurskie',
    12: 'łódźkie',
    13: 'mazowieckie',
    14: 'lubelskie',
    15: 'lubuskie'
}
woj_df = pd.DataFrame({
    'id': list(woj_ids.keys()),
    'voivode': list(woj_ids.values())
})

mock_map_df = pd.DataFrame(
    {
        'woj_id': [i for i in range(16)],
        'mock_val': [i for i in range(16)]
    }
)
fig = px.choropleth_mapbox(woj_df, geojson=wojewodztwa_geo,
                           locations='id', color='id',
                           zoom=5.5, center={"lat": 52.10, "lon": 19.42},
                           opacity=0.5,
                           hover_name='voivode',
                           title='Map title'
                           )
fig.update_layout(mapbox_style="white-bg")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


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
                                    className='fill-height',
                                    figure=fig
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


if __name__ == '__main__':
    app.run_server(debug=True)
