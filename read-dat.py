#& C:/Users/felip/AppData/Local/Programs/Python/Python39/python.exe -m IPython --no-autoindent
import pandas as pd
import os
import re
import numpy as np

import plotly.express as px

directory = r'C:\Users\felip\Documents\Gastos'
file = 'ScotiaFS2021.dat'

df = pd.read_csv(os.path.join(directory,file), sep=";",skiprows=8,dtype={'Fecha': str} ,decimal=',')
#Fecha
df.loc[:,'Fecha'] = pd.to_datetime(df.Fecha.str.strip(),format='%d%m%Y', dayfirst=True)
df.loc[:,'Mes'] = df.Fecha.dt.strftime('%b%Y')
df = df.fillna(0)

#Categoria
def cat_df(df):
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.startswith('TEF'),
                            'Transferencia','')
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('PAGO DE SERVICIOS|SERVICIOS|LIPIGAS|CHILQUI|PAC SERVICIOS PROFESIONA 20630|53324082-8|65146277-0|MUNIC.VILLA ALEMA|Felipe Itau|UNICEF|YOUTUBE'),
                            'Cuentas',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('TARJ.CRED.'),
                            'Tarjeta Credito',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('SEGURO|SEG.|COMISION|MANTENCION|COM. MENSUAL|PAT VIDA SECURITY'),
                            'Financiero',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('EXPRESS|LIDER|HIPER|JUMBO|PANADERIA|ISABEL|MUNDO VERDE|ANIMAL|DISTRIBUIDORA AUS|12880128-6|12603011-8'),
                            'Supermercado',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('MERVAL|PETROBRAS|SHELL|COPEC|ESTACIONAMIEN'),
                            'Transporte',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('GRIDO|RESTAUR|CAFETERIA|GLASGOW|SIN CULPA|HOTEL|ZOO|ENTREFUEGO|CAFE|MISTER DI|KEYER|FUNDACION JARDIN'),
                            'Salida',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('GIRO REDBANC'),
                            'Efectivo',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('SODIMAC|PLACACENTRO|CONSTRU-MART|LIMARGALA|HOMECENTER|EASY|IMPERIAL|ENKO|CASA MUSA|CONSTRUMART|MK'),
                            'Construccion',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('76810627-4|76989370-9|5335679-6|8671486-8'),
                            'Inversion',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('SUMUP'),
                            'SUMUP',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('CEMIN|SALCOBRAND|FARM|DR SIMI|AHUM'),
                            'Salud',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('PARIS|RIPLEY|CASAIDEAS|MODELPRO|76554187-5|76795499-9|77288155-K|JUEGO DE LETRAS|GATO ARCANO|MERCADO PAGO|EL CONTAINER|CENCOSUD'),
                            'Varios',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('MUNDO TRANSFER') ,
                            'Arigato',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Categoria == '' ,
                            'Indefinido',df.Categoria)

cat_df(df)

'''
g = df[df.Cargos > 0].groupby('Categoria')['Descripcion'].apply(lambda x: list(np.unique(x)))
g['Cuentas']
df[(df.Categoria == 'Transferencia') & (df.Cargos > 0) & ~(df.Descripcion.str.contains('15504340-7'))].groupby('Mes').sum()

df[(df.Descripcion.str.contains('16261568-8')) & (df.Cargos > 0)]
'''

analyzed_df = df[df.Mes == 'Dec2021']
fig = px.histogram(analyzed_df, y='Mes', x='Cargos',color="Categoria",
             barmode='stack'
            )
fig.update_layout(
    yaxis = dict(autorange="reversed")
)
fig.show()

analyzed_df[['Mes','Cargos','Categoria']].groupby(['Mes','Categoria']).max()

col = ['Fecha','Descripcion','Categoria']
analyzed_df[col + ['Cargos']].nlargest(5,'Cargos')
analyzed_df[col + ['Abonos']].nlargest(5,'Abonos')



df_tc = pd.read_excel(os.path.join(directory,'EECC','Estado-de-Cuenta-Scotiabank-Diciembre-2021.xls'),skiprows=49)

#Remove unnecesary rows and columns
df_tc = df_tc[(df_tc['Fecha\nOperación'].notna())]
df_tc = df_tc.dropna(axis=1, how='all') #drop all empty columns
df_tc.columns = ['Lugar', 'Fecha', 'Codigo Referencia',
       'Descripcion', 'Monto Operacion',
       'Monto Total', 'N Cuota', 'Valor Cuota']
df_tc = df_tc[(df_tc['N Cuota'] != 'Cargo del Mes') & (df_tc['Descripcion'] != 'PAGO')]
df_tc = df_tc[~df_tc['Descripcion'].str.strip().str.startswith('TOTAL')].reset_index(drop=True)

#Fix column information - String columns cleansing
df_tc.loc[:,'Lugar'] = df_tc.loc[:,'Lugar'].str.strip()
df_tc.loc[:,'Lugar'] = df_tc.Lugar.str.replace('VILLA ALEMA','VILLA ALEMANA')
df_tc.loc[:,'Descripcion'] = df_tc.apply(lambda x: x['Descripcion'][:x['Descripcion'].find('TASA')], axis=1).str.strip()
remove = re.compile("|".join(df_tc.Lugar.unique().tolist()))
df_tc.loc[:,'Descripcion'] = df_tc.Descripcion.str.replace(remove,'').str.strip()

#Fix column information - Money columns cleansing
df_tc[df_tc.columns[[4,5,7]]] = df_tc[df_tc.columns[[4,5,7]]].replace('[\$.]', '', regex=True).astype(float)

cat_df(df_tc)

df_tc.groupby('Categoria').sum()
df_tc[col + ['Valor Cuota']].nlargest(5,'Valor Cuota')
df_tc.sort_values('Categoria')