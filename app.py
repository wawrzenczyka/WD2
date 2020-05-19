# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from treemap_helper import build_pkd_treemap
from map_helper import build_map
import event_timeline
import os
from joblib import load
import visdcc
import base64

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

BUISSNES_MAPPING = [
    {'label': 'studio fizjoterapeutyczne', 'value': 'Q_86'},
    {'label': 'biuro księgowe', 'value': 'M_69'},
    {'label': 'muzeum', 'value': 'R_91'},
    {'label': 'kasyno', 'value': 'R_92'},
    {'label': 'statek', 'value': 'H_50'},
    {'label': 'firmę opiekuńczą', 'value': 'Q_88'},
]
LICENCED_BUISSNES = ['Q_86', 'M_69', 'R_92', 'H_50', 'Q_88']

SEX_MAPPING = [
    {'label': 'kobietą', 'value': 'F'},
    {'label': 'mężczyzną', 'value': 'M'}
]

VOIVODESHIPS_MAPPING = [
    {'label': 'Mazowieckiego', 'value': 'mazowieckie'},
    {'label': 'Wielkopolskiego', 'value': 'wielkopolskie'},
    {'label': 'Warmińsko-Mazurskiego', 'value': 'warminsko-mazurskie'},
    {'label': 'Zachodniopomorskiego', 'value': 'zachodniopomorskie'},
    {'label': '', 'value': 'na'},
]

# LOAD DATA
surv_df = pd.read_csv(os.path.join(THIS_FOLDER, 'data',
                                   'ceidg_data_formated.csv'), encoding="utf-8")
surv_removed_df = surv_df[surv_df['Terminated'] == 1]
surv_removed_df = surv_removed_df.assign(
    MonthOfTermination=pd.to_datetime(pd.to_datetime(surv_removed_df.DateOfTermination).dt.to_period('M').astype(str),
                                      format='%Y-%m'))
full_daterange = pd.DataFrame({
    'MonthOfTermination': pd.date_range(start='2011-01-01', end='2020-01-02', freq='MS')
})

# Global first-page variables
voivodeship = ''
pkd_section = ''

map_type_options = ['Active companies', '% of terminated companies']
external_scripts = [
    'https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js'
]
# Treemap init
pkd_fig = build_pkd_treemap()

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    './styles.css',
], external_scripts=external_scripts)

server = app.server

# PREDICTION MODEL
clf = load('model.joblib')

analytics_image_filename = os.path.join(THIS_FOLDER, 'assets', 'Images', 'map_image.PNG') # replace with your own image
analytics_image = base64.b64encode(open(analytics_image_filename, 'rb').read())
prediction_image_filename = os.path.join(THIS_FOLDER, 'assets', 'Images', 'prediction_image.png') # replace with your own image
prediction_image = base64.b64encode(open(prediction_image_filename, 'rb').read())

app.layout = html.Div(
    children=[
        html.Div(
            id='main',
            className='scroll-container',
            children=[
                html.Section(
                    id='title-section',
                    children=html.Div(
                        className='screen-height',
                        style = {'align-items': 'center', 'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center'},
                        children=[
                            html.H1("Jednoosobowe działalności gospodarcze"),
                            html.H2("Szczegółowa analiza rynku w latach 2011 - 2020", style = {'margin-bottom': '20px'}),
                            html.Div([
                                html.Div("9 ", style = {'font-size': 60}),
                                html.Div("", style = {'width': '10px'}),
                                html.Div("lat", style = {'font-size': 25}),
                                html.Div("", style = {'width': '50px'}),
                                html.Div("280 000 ", style = {'font-size': 60}),
                                html.Div("", style = {'width': '10px'}),
                                html.Div("firm", style = {'font-size': 25}),
                                html.Div("", style = {'width': '50px'}),
                                html.Div("5 ", style = {'font-size': 60}),
                                html.Div("", style = {'width': '10px'}),
                                html.Div("wydarzeń", style = {'font-size': 25}),
                            ], style = {'align-items': 'center', 'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center'}),
                            html.Div([
                                html.Div([
                                    html.H4("Przekrój przestrzenny oraz gospodarczy działalności"),
                                    html.Div([
                                        html.Img(src='data:image/png;base64,{}'.format(analytics_image.decode()),
                                        height=250)
                                    ]),
                                    html.Div("W jakim regionie firmy przetrwały najdłużej?", style = {'font-size': 18}),
                                    html.Div("Które rodzaje działalności mają nawiększe szanse na sukces?", style = {'font-size': 18}),
                                    html.Div("Kiedy najczęściej upadają firmy?", style = {'font-size': 18}),
                                    dcc.Link("Sprawdź", href = '#1', style = {'font-size': 18}, id = 'analysis-button'),
                                ], style = {'align-items': 'center', 'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center'}),
                                html.Div("", style = {'width': '100px'}),
                                html.Div([
                                    html.H4("Predykcja życia firmy"),
                                    html.Div([
                                        html.Img(src='data:image/png;base64,{}'.format(prediction_image.decode()),
                                        height=250)
                                    ]),
                                    html.Div("Jakie są Twoje szanse na sukces?", style = {'font-size': 18}),
                                    html.Div("", style = {'font-size': 18}),
                                    html.Div("", style = {'font-size': 18}),
                                    dcc.Link("Sprawdź", href = '#2', style = {'font-size': 18}, id = 'prediction-button'),                                    
                                ], style = {'align-items': 'center', 'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'align-self': 'flex-start'}),
                            ], style = {'align-items': 'center', 'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center', 
                                        'padding-top': '50px'}),
                        ]
                    )
                ),
                html.Section(
                    id='map-section',
                    children=html.Div(
                        className='screen-height',
                        children=[
                            html.Div(
                                className='section',
                                children=[
                                    dbc.Row(
                                        className='year-section',
                                        children=[
                                            dbc.Col(md=2,
                                                    children=html.H3(
                                                        "Rok:", id='year')
                                                    ),
                                            dbc.Col(md=7,
                                                    children=daq.Slider(
                                                        color="default",
                                                        id='year-slider',
                                                        min=2011,
                                                        max=2020,
                                                        step=0.5,
                                                        value=2020,
                                                        marks={year + 0.01: str(int(year))
                                                               for year in range(2011, 2021)},
                                                        targets=event_timeline.EVENTS_SLIDER,
                                                    ),
                                                    ),
                                            dbc.Col(md=3,
                                                    children=[
                                                        dbc.Button(
                                                            id='start-tour',
                                                            href="javascript:customStartIntro();",
                                                            children="Przewodnik po aplikacji",
                                                            color='primary'
                                                        )
                                                    ]
                                                    )
                                        ]
                                    ),
                                    dbc.Row(
                                        className='top',
                                        no_gutters=True,
                                        children=[
                                            dbc.Col(md=6,
                                                    className='box',
                                                    children=[
                                                        dbc.Row(
                                                            id='map-filters',
                                                            no_gutters=True,
                                                            children=[
                                                                html.H5(
                                                                    'Filtry:'),
                                                                dcc.RadioItems(
                                                                    id='map-type-radiobuttons',
                                                                    labelClassName='map-type-radiobuttons-items',
                                                                    options=[
                                                                        {'label': 'Liczba aktywnych firm',
                                                                         'value': 0},
                                                                        {'label': '% zamkniętych firm',
                                                                         'value': 1}
                                                                    ],
                                                                    value=0
                                                                )
                                                            ]
                                                        ),
                                                        dcc.Graph(
                                                            id='map',
                                                            className='fill-height',
                                                            config={
                                                                'displayModeBar': False,
                                                                'scrollZoom': True
                                                            },
                                                        ),
                                                        html.Div(id="output")
                                                    ]
                                                    ),
                                            dbc.Col(md=6,
                                                    className='box',
                                                    children=[
                                                        dcc.Graph(
                                                            id='timeline',
                                                            className='fill-height',
                                                            config={
                                                                'displayModeBar': False,
                                                                'scrollZoom': False
                                                            },
                                                        )
                                                    ]
                                                    )
                                        ]),
                                    dbc.Row(
                                        className='bottom',
                                        no_gutters=True,
                                        children=[
                                            dbc.Col(md=12,
                                                    className='box',
                                                    children=[
                                                        dcc.Graph(
                                                            figure=pkd_fig,
                                                            id='pkd-tree',
                                                            className='fill-height',

                                                        ),
                                                    ]
                                                    )
                                        ]),
                                    html.Div(id='selected-voivodeship',
                                             style={'display': 'none'}, children=''),
                                    html.Div(id='selected-pkd-section',
                                             style={'display': 'none'}, children=''),
                                    html.Div(id='selected-voivodeship-indices',
                                             style={'display': 'none'}, children=''),
                                    html.Div(id='scroll-blocker', className='scroll')
                                ]
                            ),
                            html.Hr(),
                        ]
                    )
                ),
                html.Section(
                    id='prediction-section',
                    children=html.Div(
                        className='screen-height',
                        children=[html.Div(
                            id='prediction',
                            style={'text-align': 'center'},
                            children=[
                                html.Div(
                                    style={'width': 'fit-content',
                                           'display': 'inline-block'},
                                    id='prediction-input',
                                    children=[
                                        html.H1(
                                            id='prediction-header',
                                            children='Ile przetrwa twój biznes?',
                                            style={'font-weight': 'bold'}
                                        ),

                                        html.Plaintext("Jestem ", style={
                                            'display': 'inline-block', 'font-size': '12pt'}),
                                        dcc.Dropdown(
                                            id='sex',
                                            options=SEX_MAPPING,
                                            value='M',
                                            style=dict(
                                                width=100,
                                                display='inline-block',
                                                verticalAlign="middle",
                                                textAlign="left"
                                            )
                                        ),

                                        html.Plaintext(", mam ", style={
                                            'display': 'inline-block', 'font-size': '12pt'}),
                                        dcc.Dropdown(
                                            id='business-type',
                                            options=BUISSNES_MAPPING,
                                            value='Q_86',
                                            style=dict(
                                                width=210,
                                                display='inline-block',
                                                verticalAlign="middle",
                                                textAlign="left"
                                            )
                                        ),

                                        html.Plaintext(", jestem z województwa ", style={
                                            'display': 'inline-block', 'font-size': '12pt'}),
                                        dcc.Dropdown(
                                            id='voivodeship',
                                            options=VOIVODESHIPS_MAPPING,
                                            value='mazowieckie',
                                            style=dict(
                                                width=190,
                                                display='inline-block',
                                                verticalAlign="middle",
                                                textAlign="left"
                                            )
                                        ),

                                        html.Div([
                                            html.Plaintext(
                                                " i ", style={'display': 'inline-block', 'font-size': '12pt'}),

                                            dcc.Dropdown(
                                                id='is_licence',
                                                options=[
                                                    {'label': 'mam licencje',
                                                        'value': 1},
                                                    {'label': 'nie mam licencji',
                                                        'value': 0},
                                                ],
                                                value=0,
                                                style=dict(
                                                    width=135,
                                                    display='inline-block',
                                                    verticalAlign="middle",
                                                    padding='0',
                                                    textAlign="left"
                                                )
                                            ),
                                        ], id='to_hide', style={'display': 'inline-block'},

                                        ),

                                        html.Plaintext(
                                            ". ", style={'display': 'inline-block', 'font-size': '12pt'}),
                                        dcc.Dropdown(
                                            id='is_shareholder',
                                            options=[
                                                {'label': 'Posiadam udziały',
                                                    'value': 1},
                                                {'label': 'Nie posiadam udziałów',
                                                    'value': 0},
                                            ],
                                            value=0,
                                            style=dict(
                                                width=185,
                                                display='inline-block',
                                                verticalAlign="middle",
                                                padding='0',
                                                textAlign="left"
                                            )
                                        ),
                                        html.Plaintext(" w innych firmach. ", style={
                                            'display': 'inline-block', 'font-size': '12pt'}),

                                        html.Div([
                                            html.Plaintext(
                                                "Mój e-mail to ",
                                                style={'display': 'inline-block', 'font-size': '12pt'}),
                                            dcc.Input(id="email", type="text", value="", placeholder="",
                                                      style=dict(display='inline-block')),
                                            html.Plaintext(", mój numer telefonu to ", style={
                                                'display': 'inline-block', 'font-size': '12pt'}),
                                            dcc.Input(id="phone_number", type="text", value="",
                                                      placeholder="", style=dict(display='inline-block')),
                                            html.Plaintext(
                                                ". ", style={'display': 'inline-block', 'font-size': '12pt'}),
                                        ])
                                    ]
                                ),
                                html.Div(
                                    id='pred-output',
                                    children=[
                                        html.Plaintext("Twoja firma przetrwa", style={
                                            'display': 'block', 'text-align': 'center', 'font-size': '14pt',
                                            'margin-top': '100px',
                                            'margin-bottom': '0px'}),
                                        html.Div(id="prediction-output"),

                                        html.Hr(),

                                        dcc.Graph(id='bankrupcy_proba-graph')
                                    ]
                                )
                            ]
                        )]
                    )
                )
            ]),
        visdcc.Run_js(id='javascript',
                      run='''
                            new fullScroll({	
                                mainElement: 'main', 
                                sections:['title-section', 'map-section','prediction-section'],
                                displayDots: true,
                                dotsPosition: 'right',
                                animateTime: 0.7,
                                animateFunction: 'ease'	
                            });
                            '''
                      ),
    ]
)

@app.callback(
    Output('map', 'figure'),
    [
        Input('year-slider', 'value'),
        Input('map-type-radiobuttons', 'value'),
        Input('selected-voivodeship-indices', 'children'),
    ])
def update_map(year, map_type, selceted_voivodeships):
    return build_map(int(year), map_type, selceted_voivodeships)


@app.callback(
    [
        Output('selected-voivodeship', 'children'),
        Output('selected-voivodeship-indices', 'children')
    ],
    [
        Input('map', 'selectedData')
    ])
def select_voivodeship(selectedVoivodeship):
    if selectedVoivodeship is None:
        return [], []
    selected_voivodeship = [item['location'].upper()
                            for item in selectedVoivodeship['points']]
    selected_voivodeship_indices = [item['pointIndex']
                                    for item in selectedVoivodeship['points']]
    return selected_voivodeship, selected_voivodeship_indices


@app.callback(
    [
        Output('selected-pkd-section', 'children'),
    ],
    [
        Input('pkd-tree', 'clickData'),
        Input('map', 'selectedData'),
    ],
    [
        State('selected-pkd-section', 'children')
    ])
def select_pkd_section(click, mapClick, old):
    ctx = dash.callback_context
    clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    if clicked == 'map':
        # on voivodeship change
        return ['']

    if click is None:
        # on startup
        return ['']

    label = click['points'][0]['label']
    parent = click['points'][0]['parent']

    if 'entry' in click['points'][0] and label == click['points'][0]['entry']:
        # zooming out
        if parent == 'Wszystkie sekcje PKD':
            selected_section = ''
        else:
            if label == 'Wszystkie sekcje PKD':
                # you are in root and click root
                selected_section = ''
            else:
                selected_section = parent.split(' ')[1]
    else:
        # zooming in
        if label == 'Wszystkie sekcje PKD':
            selected_section = ''
        else:
            selected_section = click['points'][0]['label'].split(' ')[1]

    return [selected_section]


@app.callback(
    [
        Output('pkd-tree', 'figure'),
    ],
    [
        Input('selected-voivodeship', 'children'),
    ])
def redraw_treemap(voivodeship):
    voivodeship = [voiv.lower() for voiv in voivodeship]
    return [build_pkd_treemap(voivodeship=voivodeship)]


@app.callback(
    [
        Output('timeline', 'figure'),
    ],
    [
        Input('year-slider', 'value'),
        Input('selected-voivodeship', 'children'),
        Input('selected-pkd-section', 'children'),
    ])
def redraw_timeline(year, voivodeship, pkd_section):
    data = surv_removed_df

    if voivodeship != []:
        data = data[np.isin(data['MainAddressVoivodeship'], [
            voiv.lower() for voiv in voivodeship])]
    if pkd_section != '':
        if pkd_section.isalpha():
            # section (eg. A, B, C...)
            data = data[data['PKDMainSection'] == pkd_section]
        else:
            # division (eg. 47)
            data = data[data['PKDMainDivision'] == float(pkd_section)]

    monthly_data = data[["MonthOfTermination", "Count"]] \
        .groupby(["MonthOfTermination"]) \
        .sum().reset_index()

    monthly_data_filled = full_daterange.merge(
        monthly_data,
        on='MonthOfTermination',
        how='left'
    ).fillna(0)

    return [event_timeline.build_event_timeline(monthly_data_filled, year)]


# PREDICTION CALLBACKS
@app.callback(
    Output(component_id='to_hide', component_property='style'),
    [Input(component_id='business-type', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state in LICENCED_BUISSNES:
        return {'display': 'inline-block'}
    else:
        return {'display': 'none'}


@app.callback(
    [Output(component_id='prediction-output', component_property='children'),
     Output('prediction-output', 'style')],
    [Input(component_id='sex', component_property='value'),
     Input(component_id='business-type', component_property='value'),
     Input(component_id='voivodeship', component_property='value'),
     Input(component_id='is_licence', component_property='value'),
     Input(component_id='is_shareholder', component_property='value'),
     Input(component_id='email', component_property='value'),
     Input(component_id='phone_number', component_property='value')]
)
def predict(sex, PKD_Div_Sec, voivodeship, licence, shareholder, email, phone_number):
    X = {'HasLicences': [licence > 0], 'PKDMainDivision': [PKD_Div_Sec.split('_')[1]],
         'PKDMainSection': [PKD_Div_Sec.split('_')[0]], 'MainAddressVoivodeship': [voivodeship],
         'ShareholderInOtherCompanies': [shareholder > 0], 'IsPhoneNo': [phone_number != ""],
         'IsEmail': [email != ""], 'Sex': [sex]}
    pred = int(clf.predict(pd.DataFrame(X).astype(str))[0])
    prediction = {
        0: "mniej niż rok",
        1: "niecałe 2 lata",
        2: "niecałe 3 lata",
        3: "niecałe 4 lata",
        4: "4-5 lat",
        5: "ponad 5 lat",
        6: "ponad 6 lat",
        7: "ponad 7 lat",
        8: "ponad 8 lat",
    }.get(pred, "4-5 lat")
    return prediction, {'color': "red", 'font-size': '40pt', 'text-align': 'center'}


@app.callback(
    Output(component_id='bankrupcy_proba-graph', component_property='figure'),
    [Input(component_id='sex', component_property='value'),
     Input(component_id='business-type', component_property='value'),
     Input(component_id='voivodeship', component_property='value'),
     Input(component_id='is_licence', component_property='value'),
     Input(component_id='is_shareholder', component_property='value'),
     Input(component_id='email', component_property='value'),
     Input(component_id='phone_number', component_property='value')]
)
def plot_proba(sex, PKD_Div_Sec, voivodeship, licence, shareholder, email, phone_number):
    X = {'HasLicences': [licence > 0], 'PKDMainDivision': [PKD_Div_Sec.split('_')[1]],
         'PKDMainSection': [PKD_Div_Sec.split('_')[0]], 'MainAddressVoivodeship': [voivodeship],
         'ShareholderInOtherCompanies': [shareholder > 0], 'IsPhoneNo': [phone_number != ""],
         'IsEmail': [email != ""], 'Sex': [sex]}

    proba = clf.predict_proba(pd.DataFrame(X).astype(str))[0]
    return {
        'data': [
            {'x': ['0-11', '12-23', '24-35', '36-47', '48-59', '60-71',
                   '72-83', '84-95', '96+'], 'y': proba, 'type': 'bar'},
        ],
        'layout': {
            'title': 'Prawdopodobieństwo upadku firmy w przedziałach miesięcznych',
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)
