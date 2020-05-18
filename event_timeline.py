import pandas as pd
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import datetime

EVENTS_SLIDER = {
    2013: {"label": 'Nowe podatki', 'style': {"color": "#CD5C5C"}},
    2014: {"label": 'Upadki skoków', 'style': {"color": "#FF9933"}},
    2016: {"label": 'Zaostrzenie przepisów', 'style': {"color": "#99FF33"}},
    2016.5: {"label": 'Nowe podatki', 'style': {"color": "#7F00FF"}},
    2017: {"label": 'Kontrole rolników', 'style': {"color": "#00BFFF"}},
}

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


def build_event_timeline(monthly_data, year):
    fig = go.Figure()

    if year in EVENTS_SLIDER:
        if year > int(year):
            years = [year - 0.5, year + 0.5]
            x_label = datetime.datetime.strptime(str(int(year)) + '-06', '%Y-%m')
        else:
            years = [year]
            x_label = datetime.datetime.strptime(str(int(year)) + '-01', '%Y-%m')

        y = monthly_data[monthly_data['MonthOfTermination'] == x_label]['Count'].mean()
        
        fig.add_trace(
            go.Scatter(
                x=[x_label],
                y=[y],
                mode='markers',
                name='markers',
                showlegend=False,
                marker=dict(size=18, opacity=1, color=EVENTS_SLIDER[np.mean(years)]['style']['color']),
                hoverinfo='none',
            )
        )

        fig.add_annotation(
            x=x_label,
            y=y,
            text=EVENTS_SLIDER[year]['label'],
            showarrow=True,
            ax=40,
            ay=-35,
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

    for year in EVENTS_SLIDER.keys():
        if year > int(year):
            years = [year - 0.5, year + 0.5]
            x_label = datetime.datetime.strptime(str(int(np.mean(year))) + '-06', '%Y-%m')
        else:
            years = [year]
            x_label = datetime.datetime.strptime(str(int(np.mean(year))) + '-01', '%Y-%m')

        y = monthly_data[monthly_data['MonthOfTermination'] == x_label]['Count'].mean()

        fig.add_trace(
            go.Scatter(
                x=[x_label],
                y=[y],
                mode='markers',
                name='markers',
                showlegend=False,
                marker=dict(size=18, opacity=0.25, color=EVENTS_SLIDER[year]['style']['color']),
                hoverinfo='none',
                #marker_symbol="star",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=monthly_data['MonthOfTermination'],
            y=monthly_data['Count'],
            mode='lines',
            name='lines',
            showlegend=False,
            text=list(EVENTS_DESCRIPTION.values()),
            hoverinfo='text',
            marker=dict(color='darkblue'),
        )
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#d5d5d5')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#d5d5d5')
    fig.update_layout(
        plot_bgcolor='#ffffff',
        xaxis_title="Lata",
        yaxis_title="Liczba zamkniętych firm",
        title={
                'text': "Liczba zamykanych firm w obrębie miesiąca",
                'y': 0.99,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
        margin=dict(l=100, r=60, t=30, b=0)
    )

    return fig
