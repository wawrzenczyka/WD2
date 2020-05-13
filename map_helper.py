import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

voivodeship_lat_lon_data = pd.read_csv('voi_lat_lon.csv', encoding = 'UTF-8')

def build_map(
        year,
        map_type,
        surv_df,
        wojewodztwa_geo,
        selceted_voivodeships
):
    data = {'geojson': wojewodztwa_geo, 'column': 'MainAddressVoivodeship'}

    map = {'color': 'active', 'max': 43000} \
        if map_type == 0 else {'color': 'TerminatedPercentage', 'max': 80}

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
    
    fig = go.Figure(
        [
            go.Scattermapbox(
                lat=df.lat,
                lon=df.lon,
                mode='text',
                text=df.round(2).TerminatedPercentage.astype(str) + '%',
                textfont = {
                    "color": "black",
                    "family": "Verdana, sans-serif",
                    "size": 12,
                },
                name = '',
                showlegend= False,
                hoverinfo='skip',
            )
        ]
    )

    customdata = df.assign(TerminatedPercentage = df.round(2).TerminatedPercentage.astype(str) + '%')\
                    [['voivodeship', 'TerminatedPercentage', 'active']]
    hovertemplate = 'Województwo %{customdata[0]}<br>' + \
                    'Procent zamkniętych firm: <b>%{customdata[1]}</b><br>' + \
                    'Liczba aktywnych firm: <b>%{customdata[2]}</b><br>'

    if not selceted_voivodeships:
        fig.add_choroplethmapbox(autocolorscale=True, geojson=data['geojson'], customdata=customdata, hovertemplate=hovertemplate, 
                                locations=voivode_df['index'], z=voivode_df[map['color']], zmax=map['max'], zmin=0.0, 
                                featureidkey="properties.nazwa",
                                showscale=True, marker={'opacity': 0.5}, name='')
    else:
        fig.add_choroplethmapbox(autocolorscale=True, geojson=data['geojson'], customdata=customdata, hovertemplate=hovertemplate, 
                                locations=voivode_df['index'], z=voivode_df[map['color']], zmax=map['max'], marker={'opacity': 0.5}, 
                                zmin=0.0, featureidkey="properties.nazwa", name='',
                                showscale=True, selected={'marker': {'opacity': 0.8}}, 
                                unselected={'marker': {'opacity': 0.2}},
                                selectedpoints=selceted_voivodeships)

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

    # fig.update_layout(
    #     mapbox_style="white-bg",
    #     mapbox_center={"lat": 52.10, "lon": 19.42},
    #     mapbox_zoom=5,
    #     margin={"r": 0, "t": 0, "l": 0, "b": 0},
    #     clickmode='event+select'
    # )

    return fig
