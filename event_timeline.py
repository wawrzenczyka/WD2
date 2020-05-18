import pandas as pd
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import datetime

# wanted style {"color": 'darkblue', "font-size": 10, "line-height": 10, "font-weight": 200}

EVENTS_SLIDER = {
    2013: {"label": 'Nowe podatki', "date": "2012-07-01" ,'style': {"color": 'darkblue'}},
    2014: {"label": 'Upadki skoków', "date": "2014-05-01" , 'style': {"color": 'darkblue'}},
    2016: {"label": 'Zaostrzenie przepisów', "date": "2015-04-01" , 'style': {"color": 'darkblue'}},
    2016.5: {"label": 'Nowe podatki', "date": "2015-10-01" , 'style': {"color": 'darkblue'}},
    2017: {"label": 'Kontrole rolników', "date": "2016-07-01" , 'style': {"color": 'darkblue'}},
}

EVENTS_DESCRIPTION = {
    "2012-07-01": 'nowe wartości stóp procentowych',
    "2014-05-01": 'upadki instytucji finansowych spółdzielczej kasy oszczędnościowo-kredytowej',
    "2015-04-01": 'Prawo działalności gospodarczej zastępuje ustawę o swobodzie działalności gospodarczej',
    "2015-10-01": 'nowa interpretacja przepisów podatkowych. Koszt pracy właściciela nie mogą stanowić kosztów uzyskania przychodu',
    "2016-07-01": 'ośrodki doradztwa roliniczego nie podlegają wojewodom a bezpośrednio ministerstwu rolnictwa',
}


def build_event_timeline(monthly_data, year):
    fig = go.Figure()

    if year in EVENTS_SLIDER:
        x_label = EVENTS_SLIDER[year]['date']
        y = monthly_data[monthly_data['MonthOfTermination'] == x_label]['Count'].iloc[0]

        fig.add_trace(
            go.Scatter(
                x=[x_label],
                y=[y],
                mode='markers',
                name='markers',
                showlegend=False,
                marker=dict(size=18, opacity=1, color=EVENTS_SLIDER[year]['style']['color']),
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
            bgcolor="#DED6CC",
            opacity=0.8,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#636363",
            align="center",
        )

    for event_year in EVENTS_SLIDER.keys():
        x_label = EVENTS_SLIDER[event_year]['date']
        y = monthly_data[monthly_data['MonthOfTermination'] == x_label]['Count'].iloc[0]

        fig.add_trace(
            go.Scatter(
                x=[x_label],
                y=[y],
                mode='markers',
                name='markers',
                showlegend=False,
                marker=dict(size=18, opacity=0.35, color=EVENTS_SLIDER[event_year]['style']['color']),
                hoverinfo='none',
                #marker_symbol="star",
            )
        )

    monthly_data["event_desc"] = ""
    for date, event_desc in EVENTS_DESCRIPTION.items():
        monthly_data.loc[monthly_data["MonthOfTermination"] == date, "event_desc"] = event_desc

    fig.add_trace(
        go.Scatter(
            x=monthly_data['MonthOfTermination'],
            y=monthly_data['Count'],
            mode='lines+markers',
            name='lines',
            showlegend=False,
            text=list(monthly_data["event_desc"].values),
            hoverinfo='text',
            marker=dict(color='darkblue', size=18, opacity=0),
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
