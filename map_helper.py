import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import json

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(THIS_FOLDER, 'assets', 'wojewodztwa-min.geojson'), encoding='utf8') as woj_json:
    wojewodztwa_geo = json.load(woj_json)

voivodes_by_year = pd.read_csv(os.path.join(THIS_FOLDER, 'data', 'voivoides_by_year.csv'), encoding='UTF-8')


def build_map(
        year,
        map_type,
        selceted_voivodeships
):
    global wojewodztwa_geo
    global voivodes_by_year
    map = {
        'color': 'active',
        'min': 0,
        'max': 44108
    } if map_type == 0 else {
        'color': 'TerminatedPercentage',
        'min': 0,
        'max': 80
    }

    df = voivodes_by_year[['MainAddressVoivodeship', 'all', 'lon', 'lat', str(year)]].rename(
        columns={str(year): 'terminated'})
    df['TerminatedPercentage'] = df['terminated'] / df['all'] * 100.0
    df['active'] = df['all'] - df['terminated']

    label_text = df.round(2).TerminatedPercentage.astype(str) + '%' if map['color'] == 'TerminatedPercentage' else df[
        'active'].astype(str)

    colorscale = 'Balance'
    y = df[map['color']] / map['max']
    black_indexes, *_ = np.where((0.75 >= y) & (y >= 0.25))
    white_indexes, *_ = np.where((y > 0.75) | (y < 0.25))

    fig = go.Figure()

    customdata = df.assign(TerminatedPercentage=df.round(2).TerminatedPercentage.astype(str) + '%')\
        [['MainAddressVoivodeship', 'TerminatedPercentage', 'active']]
    hovertemplate = 'Województwo %{customdata[0]}<br>' + \
                    'Procent zamkniętych firm: <b>%{customdata[1]}</b><br>' + \
                    'Liczba aktywnych firm: <b>%{customdata[2]}</b><br>'

    if not selceted_voivodeships:
        fig.add_choroplethmapbox(colorscale=colorscale, geojson=wojewodztwa_geo, customdata=customdata,
                                 hovertemplate=hovertemplate,
                                 locations=df['MainAddressVoivodeship'], z=df[map['color']], zmax=map['max'],
                                 zmin=map['min'],
                                 featureidkey="properties.nazwa",
                                 showscale=True, marker={'opacity': 0.7}, name='', below=True)
    else:
        fig.add_choroplethmapbox(colorscale=colorscale, geojson=wojewodztwa_geo, customdata=customdata,
                                 hovertemplate=hovertemplate,
                                 locations=df['MainAddressVoivodeship'], z=df[map['color']], zmax=map['max'],
                                 marker={'opacity': 0.5},
                                 zmin=map['min'], featureidkey="properties.nazwa", name='',
                                 showscale=True, selected={'marker': {'opacity': 0.7}},
                                 unselected={'marker': {'opacity': 0.2}},
                                 selectedpoints=selceted_voivodeships, below=True)

    for i, color in zip([black_indexes, white_indexes], ["black", "white"]):
        fig.add_scattermapbox(
            lat=df.lat[i],
            lon=df.lon[i],
            mode='text',
            text=label_text[i],
            textfont={
                "color": color,
                "family": 'Verdana, sans-serif',
                "size": 12,
            },
            name='',
            showlegend=False,
            hoverinfo='skip'
        )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 35},
        mapbox=dict(
            accesstoken='pk.eyJ1Ijoid2QydGVhbSIsImEiOiJja2E0MjMyNDcwcHliM2VvZ25ycTV4MTBuIn0.7pvFq64tRzS_FgMCGcBljQ',
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=52.10,
                lon=19.42
            ),
            pitch=0,
            zoom=5.1
        ),
        clickmode='event+select'
    )

    return fig
