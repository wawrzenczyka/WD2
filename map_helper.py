import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


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
    voivode_df['active'] = (voivode_df['all'] - voivode_df['terminated']).astype(float)

    fig = go.Figure()
    if not selceted_voivodeships:
        fig.add_choroplethmapbox(autocolorscale=True, geojson=data['geojson'], customdata=voivode_df, locations=voivode_df['index'],
                                z=voivode_df[map['color']], zmax=map['max'], zmin=0.0, featureidkey="properties.nazwa",
                                showscale=True, hoverinfo='location', marker={'opacity': 0.5})
    else:
        fig.add_choroplethmapbox(autocolorscale=True, geojson=data['geojson'], customdata=voivode_df, locations=voivode_df['index'],
                                z=voivode_df[map['color']], zmax=map['max'], marker={'opacity': 0.5}, zmin=0.0, featureidkey="properties.nazwa",
                                showscale=True, hoverinfo='location', selected={'marker': {'opacity': 0.8}}, 
                                unselected={'marker': {'opacity': 0.2}},
                                selectedpoints=selceted_voivodeships)

    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_center={"lat": 52.10, "lon": 19.42},
        mapbox_zoom=5,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        clickmode='event+select'
    )

    return fig
