import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

voivodeship_lat_lon_data = pd.read_csv(os.path.join(THIS_FOLDER, 'data', 'voi_lon_lat.csv'), encoding = 'UTF-8')

def build_map(
        year,
        map_type,
        surv_df,
        wojewodztwa_geo,
        selceted_voivodeships
):
    data = {'geojson': wojewodztwa_geo, 'column': 'MainAddressVoivodeship'}

    map = {'color': 'active', 'min': 0, 'max': 44108} \
        if map_type == 0 else {'color': 'TerminatedPercentage', 'min': 0, 'max': 80}

    terminated = surv_df[surv_df['YearOfTermination']
                         <= year][data['column']].value_counts()
    all = surv_df[data['column']].value_counts()
    voivode_df = pd.concat([terminated, all], axis=1, keys=[
                           'terminated', 'all'], sort=True).reset_index()
    voivode_df['TerminatedPercentage'] = voivode_df['terminated'] / \
        voivode_df['all'] * 100.0
    voivode_df['active'] = voivode_df['all'] - voivode_df['terminated']


    df = voivode_df.merge(voivodeship_lat_lon_data,
        left_on = 'index',
        right_on = 'voivodeship'
    )

    label_text = df.round(2).TerminatedPercentage.astype(str) + '%' if map['color']=='TerminatedPercentage' else df.active.astype(str)

    colorscale = np.array(px.colors.sequential.Viridis)
    color_values = (voivode_df[map['color']]/map['max'])*(len(colorscale)-1)

    color_min_index = np.floor(color_values).astype(int)
    color_max_index = np.ceil(color_values).astype(int)

    min_colors = colorscale[color_min_index.tolist()]
    max_colors = colorscale[color_max_index.tolist()]

    colors = pd.DataFrame({'min_color': min_colors, 'max_color': max_colors})
    r_min = colors.min_color.str.slice(1,3).apply(int, base=16)
    g_min = colors.min_color.str.slice(3,5).apply(int, base=16)
    b_min = colors.min_color.str.slice(5,7).apply(int, base=16)
    r_max = colors.max_color.str.slice(1,3).apply(int, base=16)
    g_max = colors.max_color.str.slice(3,5).apply(int, base=16)
    b_max = colors.max_color.str.slice(5,7).apply(int, base=16)

    r = (r_min+(r_max-r_min)*(color_values-color_min_index))
    g = (g_min+(g_max-g_min)*(color_values-color_min_index)) 
    b = (b_min+(b_max-b_min)*(color_values-color_min_index))
    y = 0.2126*(r/255) + 0.7152*(g/255) + 0.0722*(b/255)

    text_color = np.where(y>0.5,"black","white").tolist()

    fig = go.Figure()

    customdata = df.assign(TerminatedPercentage = df.round(2).TerminatedPercentage.astype(str) + '%')\
                    [['voivodeship', 'TerminatedPercentage', 'active']]
    hovertemplate = 'Województwo %{customdata[0]}<br>' + \
                    'Procent zamkniętych firm: <b>%{customdata[1]}</b><br>' + \
                    'Liczba aktywnych firm: <b>%{customdata[2]}</b><br>'

    if not selceted_voivodeships:
        fig.add_choroplethmapbox(colorscale=colorscale, geojson=data['geojson'], customdata=customdata, hovertemplate=hovertemplate, 
                                locations=voivode_df['index'], z=voivode_df[map['color']], zmax=map['max'], zmin=map['min'], 
                                featureidkey="properties.nazwa",
                                showscale=True, marker={'opacity': 0.7}, name='', below=True)
    else:
        fig.add_choroplethmapbox(colorscale=colorscale, geojson=data['geojson'], customdata=customdata, hovertemplate=hovertemplate, 
                                locations=voivode_df['index'], z=voivode_df[map['color']], zmax=map['max'], marker={'opacity': 0.5}, 
                                zmin=map['min'], featureidkey="properties.nazwa", name='',
                                showscale=True, selected={'marker': {'opacity': 0.7}}, 
                                unselected={'marker': {'opacity': 0.2}},
                                selectedpoints=selceted_voivodeships, below=True)

    for i in range(0,16):
        fig.add_scattermapbox(
            lat=[df.lat[i]],
            lon=[df.lon[i]],
            mode='text',
            text=[label_text[i]],
            textfont = {
                "color": text_color[i],
                "family": 'Verdana, sans-serif',
                "size": 12,
            },
            name = '',
            showlegend= False,
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
            # style="white-bg"
        ), 
        clickmode='event+select'
    )
    
    return fig