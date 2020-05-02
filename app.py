# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

BUISSNES_MAPPING = [
	{'label': 'studio fizjoterapełtyczne', 'value': 'Q_86'},
	{'label': 'biuro księgowe', 'value': 'M_69'},
	{'label': 'muzeum', 'value': 'R_91'},
	{'label': 'kasyno', 'value': 'R_92'},
	{'label': 'statek', 'value': 'H_50'},
	{'label': 'firmę opikuńczą', 'value': 'Q_88'},
]
LICENCED_BUISSNES = ['Q_86', 'M_69', 'R_92', 'H_50', 'Q_88']

VOIVODESHIPS_MAPPING = [
	{'label': 'Mazowieckiego', 'value': 'mazowieckie'},
	{'label': 'Wielkopolskie', 'value': 'wielkopolskie'},
	{'label': 'Warminsko-Mazurskie', 'value': 'warminskomazurskie'},
	{'label': 'Zachodniopomorskie', 'value': 'zachodniopomorskie'},
	{'label': '', 'value': 'na'},
]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Ile przetrwa twój biznes?'),

    html.Plaintext("Mam ", style=dict(display='inline-block')),
    dcc.Dropdown(
        id='business-type',
        options=BUISSNES_MAPPING,
        value='Q_86',
	style=dict(
            width=200,
	    display='inline-block',
            verticalAlign="middle"
        )
    ),

    html.Plaintext(", jestem z województwa ", style=dict(display='inline-block')),
    dcc.Dropdown(
        id='voivodeship',
        options=VOIVODESHIPS_MAPPING,
        value='mazowieckie',
	style=dict(
            width=170,
	    display='inline-block',
            verticalAlign="middle"
        )
    ),

    html.Plaintext(" ", style=dict(display='inline-block')),

    html.Div([
        html.Plaintext(" i ", style=dict(display='inline-block')),

	dcc.Dropdown(
		id='is_licence',
		options=[
		    {'label': 'licencje', 'value': 1},
		    {'label': 'nie mam licencji', 'value': 0},
		],
		value=0,
		style=dict(
		    width=135,
		    display='inline-block',
		    verticalAlign="middle",
		    padding='0',
		)
    	),
	], id='to_hide', style= {'display': 'inline-block'},
        
    ),
    

    html.Plaintext(".  ", style=dict(display='inline-block')),
    dcc.Dropdown(
        id='is_shareholder',
        options=[
            {'label': 'Posiadam udziały', 'value': 1},
            {'label': 'Nie posiadam udziałów', 'value': 0},
        ],
        value=0,
	style=dict(
            width=185,
	    display='inline-block',
            verticalAlign="middle",
	    padding='0',
        )
    ),
    html.Plaintext(" w innych firmach. ", style=dict(display='inline-block')),

    html.Plaintext("Moj emial to "),
    dcc.Input(id="email", type="text", placeholder="", style=dict(display='block')),

    html.Plaintext("Moj numer telefonu to ", style=dict(display='block')),	
    dcc.Input(id="phone_number", type="text", placeholder="", style=dict(display='block')),
    
    html.Plaintext("Twoja firma przetrwa:", style=dict(display='block')),
    dcc.Input(id="output", type="text", placeholder=""),


    dcc.Graph(id='bankrupcy_proba-graph')

])

@app.callback(
   Output(component_id='to_hide', component_property='style'),
   [Input(component_id='business-type', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state in LICENCED_BUISSNES:
        return  {'display': 'inline-block'}
    else:
        return {'display': 'none'}


@app.callback(
   Output(component_id='output', component_property='value'),
   [Input(component_id='business-type', component_property='value'),
    Input(component_id='voivodeship', component_property='value'),
    Input(component_id='is_licence', component_property='value'),
    Input(component_id='is_shareholder', component_property='value'),
    Input(component_id='email', component_property='value'),
    Input(component_id='phone_number', component_property='value')]
   )
def predict(PKD_Div_Sec, voivodeship, licence, shareholder, email, phone_number):
    txt = ''
    for x in [PKD_Div_Sec, voivodeship, licence, shareholder, email, phone_number]:
        txt += str(x)
    return txt


@app.callback(
   Output(component_id='bankrupcy_proba-graph', component_property='figure'),
   [Input(component_id='business-type', component_property='value'),
    Input(component_id='voivodeship', component_property='value'),
    Input(component_id='is_licence', component_property='value'),
    Input(component_id='is_shareholder', component_property='value'),
    Input(component_id='email', component_property='value'),
    Input(component_id='phone_number', component_property='value')]
   )
def plot_proba(PKD_Div_Sec, voivodeship, licence, shareholder, email, phone_number):
    return  {
            'data': [
                {'x': [1, 2, 3], 'y': [licence, 4, 2], 'type': 'bar'},
            ],
            'layout': {
                'title': 'Prawdopodobienstwo updaku firmy w przedzialach miesiecznych'
            }
        }

if __name__ == '__main__':
    app.run_server(debug=True)
