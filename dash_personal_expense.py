import personal_expenses as pe
import s3_data as s3
from dash import Dash, dcc, html, Input, Output
import os
from datetime import datetime, date

app = Dash(__name__)

path = os.path.dirname(os.path.abspath(__file__))
tc = list(range(2))

#df_td = pe.clean_td_file(os.path.join(path,'Debito'))
#df_tc = pe.clean_tc_files(os.path.join(path,'Credito'))

df_tc = s3.read_from_s3('data_ready/clean_tc.csv')
df_td = s3.read_from_s3('data_ready/clean_td.csv')


df_tc.loc[:,'TC'] = 1
df = df_td[['Fecha', 'Descripcion', 'Cargos', 'Abonos', 'Mes', 'Categoria']].append(df_tc[['Fecha', 'Descripcion', 'Cargos', 'Mes', 'Categoria','TC']]).fillna(0).reset_index(drop=True)

analyzed_df = df[(df.Categoria != 'Tarjeta Credito') & (df.TC.isin(tc))]

colors = {
    'background': '#ffffff',
    'text': '#000000',
    'alt_text': '#000000',
    'chart1':'#835AF1',
    'chart2':'#6fe7db'
}
#161a28 negro
#835AF1 morado
#6fe7db celeste
#b8f7d4 verde

months = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
years = [x for x in range(2021,date.today().year+1)]
all_dates = [x.capitalize()+str(y) for y in years for x in months]
drop_index = all_dates.index(date.today().strftime('%b%Y').capitalize())
dropdown_dates = all_dates[:drop_index+1]
dropdown_dates.reverse()

categorias = ["Cuentas",
                "Supermercado",
                "Transferencia",
                "Construccion",
                "Casa Comercial",
                'Salida',
                'Financiero',
                'Inversion',
                'Juegos',
                'Transporte',
                'Efectivo',
                'Salud',
                'Arigato',
                'Indefinido',
                'SUMUP'
                ]

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div(children=[
        html.H1(
            id='page_title',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        html.Div(id='page_sub_title',
            style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    ]),
    html.Div([
        html.Div([
            html.Br(),
            html.Label('Elige un Mes', style={'color': colors['text']}),    
            dcc.Dropdown(dropdown_dates,
                            date.today().strftime('%b%Y').capitalize(),
                            id='input-mes',
                            style={'backgroundColor': colors['background']}),
        ], style={'width': '10%', 'display': 'inline-block', 'float': 'left', }),
        html.Div(children=[
            dcc.Graph(
                id='month_expense',
                style={'height':'70vh'}
            )
        ], style={'width': '90%', 'display': 'inline-block'}),
    ]),
    html.Div([
        html.Div([
            html.Label('Elige Categoria(s)', style={'color': colors['text']}),    
            dcc.Dropdown(categorias,
                            'Cuentas',
                            id='input-cat',
                            style={'backgroundColor': colors['background']}),
        ], style={'width': '10%', 'display': 'inline-block', 'float': 'left', }),
        html.Div([
            dcc.Graph(
                    id='hist_expense'
                )
        ], style={'width': '90%', 'display': 'inline-block'}),
    ])
])

@app.callback(
    Output(component_id='month_expense', component_property='figure'),
    Output(component_id='page_title', component_property='children'),
    Output(component_id='page_sub_title', component_property='children'),
    Input(component_id='input-mes', component_property='value')
)
def update_output_div(mes):
    month_fig = pe.build_month_report(analyzed_df, mes, colors)
    gastos_mes = analyzed_df[analyzed_df['Mes']== mes.lower()]['Cargos'].sum()
    title = 'Gastos para ' + datetime.strptime(mes,'%b%Y').strftime('%B %Y').capitalize()
    sub_title = 'Monto Total: ' + "${:,.0f}".format(int(gastos_mes))
    return month_fig, title, sub_title

@app.callback(
    Output(component_id='hist_expense', component_property='figure'),
    Input(component_id='input-cat', component_property='value')
)
def update_output_div_hist(categories):
    hist_fig = pe.build_hist_report(analyzed_df, [categories], colors)
    return hist_fig

if __name__ == '__main__':
    app.run_server(host=os.getenv('HOST','0.0.0.0'),port=os.getenv('PORT','8080'), debug=False)