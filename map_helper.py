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

    colorscale = np.array(px.colors.sequential.Viridis)
    color_values = (df[map['color']] / map['max']) * (len(colorscale) - 1)

    color_min_index = np.floor(color_values).astype(int)
    color_max_index = np.ceil(color_values).astype(int)

    min_colors = colorscale[color_min_index.tolist()]
    max_colors = colorscale[color_max_index.tolist()]

    colors = pd.DataFrame({'min_color': min_colors, 'max_color': max_colors})
    r_min = colors.min_color.str.slice(1, 3).apply(int, base=16)
    g_min = colors.min_color.str.slice(3, 5).apply(int, base=16)
    b_min = colors.min_color.str.slice(5, 7).apply(int, base=16)
    r_max = colors.max_color.str.slice(1, 3).apply(int, base=16)
    g_max = colors.max_color.str.slice(3, 5).apply(int, base=16)
    b_max = colors.max_color.str.slice(5, 7).apply(int, base=16)

    r = (r_min + (r_max - r_min) * (color_values - color_min_index))
    g = (g_min + (g_max - g_min) * (color_values - color_min_index))
    b = (b_min + (b_max - b_min) * (color_values - color_min_index))
    y = 0.2126 * (r / 255) + 0.7152 * (g / 255) + 0.0722 * (b / 255)

    text_color = np.where(y > 0.5, "black", "white").tolist()

    fig = go.Figure()

    customdata = df.assign(TerminatedPercentage=df.round(2).TerminatedPercentage.astype(str) + '%') \
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

    for i in range(0, 16):
        fig.add_scattermapbox(
            lat=[df.lat[i]],
            lon=[df.lon[i]],
            mode='text',
            text=[label_text[i]],
            textfont={
                "color": text_color[i],
                "family": 'Verdana, sans-serif',
                "size": 12,
            },
            name='',
            showlegend=False,
            hoverinfo='skip'
        )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            accesstoken='pk.eyJ1Ijoid2QydGVhbSIsImEiOiJja2E0MjMyNDcwcHliM2VvZ25ycTV4MTBuIn0.7pvFq64tRzS_FgMCGcBljQ',
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=52.10,
                lon=19.42
            ),
            pitch=0,
            zoom=5.1
            # style="white-bg"
        ),
        clickmode='event+select'
    )

    return fig
