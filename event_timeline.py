import pandas as pd
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np

EVENTS = [
    {'years': [2013], 'text': 'Nowe podatki', 'ax': 30, 'ay': -25},
    {'years': [2014], 'text': 'Upadki skoków', 'ax': 30, 'ay': -25},
    {'years': [2016], 'text': 'Zaostrzenie przepisów', 'ax': 20, 'ay': -85},
    {'years': [2016, 2017], 'text': 'Nowe podatki', 'ax': 40, 'ay': -55},
    {'years': [2017], 'text': 'Kontrole rolników', 'ax': 60, 'ay': -25},
]

EVENTS_DESCRIPTION = {
    2011: '',
    2012: '',
    2013: 'nowe wartości stóp procentowych',
    2014: 'upadki instytucji finansowych spółdzielczej kasy oszczędnościowo-kredytowej',
    2015: '',
    2016: 'Prawo działalności gospodarczej zastępuje ustawę o swobodzie działalności gospodarczej, <br>'
          'nowa interpretacja przepisów podatkowych. Koszt pracy wlasciciela nie mogą stanowić kosztów uzyskania przychodu',
    2017: 'ośrodki doradztwa roliniczego nie podlegają wojewodom a bezpośrednio ministerstwu rolnictwa',
    2018: '',
    2019: '',
    2020: '',
}


def build_event_timeline(timeline_mock_df):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=timeline_mock_df['YearOfTermination'],
            y=timeline_mock_df['count'],
            mode='lines',
            name='lines',
            showlegend=False,
            text=list(EVENTS_DESCRIPTION.values()),
            hoverinfo='text',
        )
    )

    for event in EVENTS:
        years = event['years']
        y = timeline_mock_df[timeline_mock_df['YearOfTermination'].isin(years)]['count'].mean()
        fig.add_annotation(
            x=np.mean(years),
            y=y,
            text=event['text'],
            showarrow=True,
            ax=event['ax'],
            ay=event['ay'],
            bordercolor="#c7c7c7",
            borderwidth=1,
            borderpad=3,
            bgcolor="#ff7f0e",
            opacity=0.8,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#636363",
            align="center",
        )

    return fig