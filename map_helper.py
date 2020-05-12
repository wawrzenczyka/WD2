import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def build_map(
        year,
        map_type,
        surv_df,
        wojewodztwa_geo
):
    data = {'geojson': wojewodztwa_geo, 'column': 'MainAddressVoivodeship'}

    map = {'color': 'active', 'range': (0, 43000)} \
        if map_type == 0 else {'color': 'TerminatedPercentage', 'range': (0, 80)}

    terminated = surv_df[surv_df['YearOfTermination']
                         <= year][data['column']].value_counts()
    all = surv_df[data['column']].value_counts()
    voivode_df = pd.concat([terminated, all], axis=1, keys=[
                           'terminated', 'all'], sort=True).reset_index()
    voivode_df['TerminatedPercentage'] = voivode_df['terminated'] / \
        voivode_df['all'] * 100.0
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
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        clickmode='event+select'
    )
    return fig
