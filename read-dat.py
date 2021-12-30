#& C:/Users/felip/AppData/Local/Programs/Python/Python39/python.exe -m IPython --no-autoindent
import pandas as pd
import os
import re
import numpy as np
import sys 

import plotly.express as px

#Categoria
def cat_df(df):
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.startswith('TEF'),
                            'Transferencia','')
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('PAGO DE SERVICIOS|SERVICIOS|LIPIGAS|CHILQUI|PAC SERVICIOS PROFESIONA 20630|53324082-8|65146277-0|MUNIC.VILLA ALEMA|Felipe Itau|UNICEF|YOUTUBE|HBOMAX'),
                            'Cuentas',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('TARJ.CRED.'),
                            'Tarjeta Credito',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('SEGURO|SEG.|COMISION|MANTENCION|COM. MENSUAL|PAT VIDA SECURITY|IMPUESTO'),
                            'Financiero',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('EXPRESS|LIDER|HIPER|JUMBO|PANADERIA|ISABEL|MUNDO VERDE|ANIMAL|DISTRIBUIDORA AUS|12880128-6|12603011-8|TOTTUS'),
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
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('PARIS|RIPLEY|CASAIDEAS|MODELPRO|76554187-5|76795499-9|77288155-K|JUEGO DE LETRAS|GATO ARCANO|MERCADO PAGO|EL CONTAINER|CENCOSUD|AMAZON|O 2 SPORT|DAFITI|FPAY|LINIO'),
                            'Varios',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('MUNDO TRANSFER|NUSKIN') ,
                            'Arigato',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Categoria == '' ,
                            'Indefinido',df.Categoria)

def clean_main(full_path):
    df = pd.read_csv(full_path, sep=";",skiprows=8,dtype={'Fecha': str} ,decimal=',')
    #Fecha
    df.loc[:,'Fecha'] = pd.to_datetime(df.Fecha.str.strip(),format='%d%m%Y', dayfirst=True)
    df.loc[:,'Mes'] = df.Fecha.dt.strftime('%b%Y')
    df = df.fillna(0)

    cat_df(df)

    return df

def build_report(df):
    try:
        sys.argv[1]
    except:
        raise ValueError('You need to specify a month like Dec2021 as an argument')

    analyzed_df = df[df.Mes == sys.argv[1]]
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


#### TC File
def clean_files(dir):
    df = pd.DataFrame()
    files = []
    for file in os.listdir(dir):
        print(file)
        df_tc = pd.read_excel(os.path.join(dir,file),skiprows=49)

        #Remove unnecesary rows and columns
        df_tc = df_tc[(df_tc['Fecha\nOperación'].notna())]
        df_tc = df_tc.dropna(axis=1, how='all') #drop all empty columns
        df_tc.columns = ['Lugar', 'Fecha', 'Codigo Referencia',
            'Descripcion', 'Monto Operacion',
            'Monto Total', 'N Cuota', 'Valor Cuota']
        df_tc = df_tc[(df_tc['N Cuota'] != 'Cargo del Mes') & (df_tc['Descripcion'].str.strip() != 'PAGO')]
        df_tc = df_tc[~df_tc['Descripcion'].str.strip().str.startswith('TOTAL')].reset_index(drop=True)

        cat_df(df_tc)

        #Fix column information - String columns cleansing
        df_tc.loc[:,'Fecha'] = pd.to_datetime(df_tc.Fecha.str.strip(),format='%d/%m/%Y', dayfirst=True)
        df_tc.loc[:,'Lugar'] = df_tc.loc[:,'Lugar'].str.strip()
        df_tc.loc[:,'Lugar'] = df_tc.Lugar.str.replace('VILLA ALEMA','VILLA ALEMANA')
        df_tc.loc[:,'Descripcion'] = df_tc.apply(lambda x: x['Descripcion'][:x['Descripcion'].find('TASA')], axis=1).str.strip()
        remove = re.compile("|".join(df_tc.Lugar.unique().tolist()))
        df_tc.loc[:,'Descripcion'] = df_tc.Descripcion.str.replace(remove,'').str.strip()

        #Fix column information - Money columns cleansing
        df_tc[df_tc.columns[[4,5,7]]] = df_tc[df_tc.columns[[4,5,7]]].replace('[\$.]', '', regex=True).astype(float)

        df = df.append(df_tc)
    df = df.sort_values('Fecha').reset_index(drop=True)
    return df

def main():
    if len(sys.argv) < 3:
        directory = r'C:\Users\felip\Documents\Gastos'
        file = 'ScotiaFS2021.dat'
    else:
        path = os.path.split(sys.argv[2])
        directory = path[0]
        file = path[1]
    
    df = clean_main(os.path.join(directory,file))
    df_tc = clean_files(os.path.join(directory,'EECC'))
    build_report(df)

if __name__ == '__main__':
    main()