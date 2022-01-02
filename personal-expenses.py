import pandas as pd
import os
import re
import numpy as np
import sys
from datetime import datetime
import locale

import plotly.express as px

#Categoria
def cat_df(df):
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.startswith('TEF'),
                            'Transferencia','')
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('SUMUP'),
                            'SUMUP',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('PAGO DE SERVICIOS|SERVICIOS|LIPIGAS|CHILQUI|PAC SERVICIOS PROFESIONA 20630|53324082-8|65146277-0|MUNIC.VILLA ALEMA|Felipe Itau|UNICEF|YOUTUBE|HBOMAX'),
                            'Cuentas',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('TARJ.CRED.'),
                            'Tarjeta Credito',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('SEGURO|SEG.|COMISION|MANTENCION|COM. MENSUAL|PAT VIDA SECURITY|IMPUESTO|INTERES'),
                            'Financiero',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('EXPRESS|LIDER|HIPER|JUMBO|PANADERIA|ISABEL|MUNDO VERDE|ANIMAL|DISTRIBUIDORA AUS|12880128-6|TOTTUS|EMPORIO|LUIS SOTO URRA|Rosana serey|Geni ve|Carlos arand|Venta de fru'),
                            'Supermercado',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('MERVAL|PETROBRAS|SHELL|COPEC|ESTACIONAMIEN|LATAM|PETRO LEIVA'),
                            'Transporte',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('GRIDO|RESTAUR|CAFETERIA|GLASGOW|SIN CULPA|HOTEL|ZOO|ENTREFUEGO|CAFE|MISTER DI|KEYER|FUNDACION JARDIN|12603011-8|LA CASA DEL JARDI'),
                            'Salida',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('GIRO REDBANC'),
                            'Efectivo',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('SODIMAC|PLACACENTRO|CONSTRU-MART|LIMARGALA|HOMECENTER|EASY|IMPERIAL|ENKO|CASA MUSA|CONSTRUMART|MK'),
                            'Construccion',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('76810627-4|76989370-9|5335679-6|8671486-8'),
                            'Inversion',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('CEMIN|SALCOBRAND|FARM|DR SIMI|AHUM|ISAPRE'),
                            'Salud',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('PARIS|RIPLEY|CASAIDEAS|MERCADO PAGO|EL CONTAINER|CENCOSUD|O 2 SPORT|DAFITI|FPAY|LINIO|FALABELL|MERCADOPAGO'),
                            'Casa Comercial',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('77288155-K|JUEGO DE LETRAS|GATO ARCANO|MODELPRO|76554187-5|76795499-9|AMAZON|CAFE Y TABLEROS'),
                            'Juegos',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('MUNDO TRANSFER|NUSKIN') ,
                            'Arigato',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Descripcion.str.contains('76574150-5') ,
                            'Trabajo',df.Categoria)
    df.loc[:,'Categoria'] = np.where(df.Categoria == '' ,
                            'Indefinido',df.Categoria)

def clean_td_file(full_path):
    df = pd.read_csv(full_path, sep=";",skiprows=8,dtype={'Fecha': str} ,decimal=',')
    #Fecha
    locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
    df.loc[:,'Fecha'] = pd.to_datetime(df.Fecha.str.strip(),format='%d%m%Y', dayfirst=True)
    df.loc[:,'Mes'] = df.Fecha.dt.strftime('%b%Y')
    df = df.fillna(0)
    df.Descripcion = df.Descripcion.str.strip()

    cat_df(df)

    return df

#### TC File
def clean_tc_files(dir, mes):
    global tc_file
    df = pd.DataFrame()    
    locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
    for file in os.listdir(dir):
        file_words = file.split('-')
        file_dt = datetime.strptime(file_words[4] + file_words[5].split('.')[0], '%B%Y')
        if datetime.strptime(mes, '%b%Y') == file_dt:
            tc_file = file

        df_tc = pd.read_excel(os.path.join(dir,file),skiprows=49)

        #Remove unnecesary rows and columns
        df_tc = df_tc[(df_tc['Fecha\nOperación'].notna())]
        df_tc = df_tc.dropna(axis=1, how='all') #drop all empty columns
        df_tc.columns = ['Lugar', 'FechaOperacion', 'Codigo Referencia',
            'Descripcion', 'Monto Operacion',
            'Monto Total', 'N Cuota', 'Cargos']
        df_tc = df_tc[(df_tc['N Cuota'] != 'Cargo del Mes') & (df_tc['Descripcion'].str.strip() != 'PAGO')]
        df_tc = df_tc[~df_tc['Descripcion'].str.strip().str.startswith('TOTAL')].reset_index(drop=True)

        cat_df(df_tc)
        
        #Fix column information - String columns cleansing
        df_tc.loc[:,'FechaOperacion'] = pd.to_datetime(df_tc.FechaOperacion.str.strip(),format='%d/%m/%Y', dayfirst=True)        
        df_tc.loc[:,'Fecha'] = datetime.strptime(file_words[4] + file_words[5].split('.')[0], '%B%Y').strftime('%Y-%m-%d')
        df_tc.loc[:,'Fecha'] = pd.to_datetime(df_tc.Fecha.str.strip(),format='%Y-%m-%d')
        df_tc.loc[:,'Mes'] = df_tc.Fecha.dt.strftime('%b%Y')

        df_tc.loc[:,'Lugar'] = df_tc.loc[:,'Lugar'].str.strip()
        df_tc.loc[:,'Lugar'] = df_tc.Lugar.str.replace('VILLA ALEMA','VILLA ALEMANA')
        df_tc.loc[:,'Descripcion'] = df_tc.apply(lambda x: x['Descripcion'][:x['Descripcion'].find('TASA')], axis=1).str.strip()
        remove = re.compile("|".join(df_tc.Lugar.unique().tolist()))
        df_tc.loc[:,'Descripcion'] = df_tc.Descripcion.str.replace(remove,'').str.strip()

        #Fix column information - Money columns cleansing
        df_tc[df_tc.columns[[4,5,7]]] = df_tc[df_tc.columns[[4,5,7]]].replace('[\$.]', '', regex=True).astype(float)
        df_tc = df_tc[df_tc.Cargos > 0].reset_index(drop=True)

        df = df.append(df_tc)
    df = df.sort_values('Fecha').reset_index(drop=True)
    return df

def build_month_report(df, mes , tc):
    locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
    analyzed_df = df[(df.Mes.str.lower() == mes.lower()) & (df.Categoria != 'Tarjeta Credito') & (df.TC.isin(tc))]
    analyzed_df.loc[:,'TC'] = analyzed_df.TC.apply(np.int64).astype(str)
    total_cat = pd.DataFrame(analyzed_df[['Categoria','Cargos']].groupby('Categoria').sum()).reset_index()
    
    fig =px.bar(analyzed_df, x='Categoria', y='Cargos',
            hover_name="Descripcion",            
            color='TC',
            title='Gastos para ' + datetime.strptime(mes, '%b%Y').strftime('%B %Y') + ' (Total: ' + "${:,.0f}".format(int(total_cat.Cargos.sum())) + ')',
            color_discrete_map={"0": 'indianred',"1":'darksalmon'},
            category_orders={"Categoria": ["Cuentas",
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
                                            'Trabajo',
                                            'Arigato',
                                            'Indefinido'
                                            ]}
            )
    fig.update_xaxes(title='')
    fig.update_yaxes(title='Monto')
    fig.update_layout(title_font_size = 25)

    for i, t in total_cat.iterrows():        
        fig.add_annotation(x=t.Categoria ,y=t.Cargos+10000 ,text="${:,.0f}".format(t.Cargos),showarrow=False)
    
    note = 'Este reporte se construyo con ' + td_file + ' y ' + tc_file
    fig.add_annotation(
        showarrow=False,
        text=note,
        font=dict(size=10), 
        xref='x domain',
        x=0.5,
        yref='y domain',
        y=-0.1
        )
    fig.show()
    '''
    analyzed_df[['Mes','Cargos','Categoria']].groupby(['Mes','Categoria']).max()

    col = ['Fecha','Descripcion','Categoria','TC']
    analyzed_df[col + ['Cargos']][~analyzed_df.Descripcion.str.contains('16332063-0|16261568-8')].nlargest(5,'Cargos')
    analyzed_df[col + ['Abonos']].nlargest(5,'Abonos')
    '''
def build_hist_report(df,tc):    
    analyzed_df = df[(df.Categoria != 'Tarjeta Credito') & (df.TC.isin(tc))].groupby(['Categoria','Mes']).sum().reset_index()
    means_df = analyzed_df.groupby('Categoria').mean().reset_index()
    cat_order = ["Cuentas",
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
                'Trabajo',
                'Arigato',
                'Indefinido',
                'SUMUP'
                ]
    means_df['Categoria'] = pd.Categorical(means_df['Categoria'], cat_order)
    means_df.sort_values('Categoria', inplace=True)

    fig = px.area(analyzed_df,x='Mes',  y='Cargos',
                facet_col='Categoria',
                facet_col_wrap=4,
                color='Categoria',
                category_orders={"Categoria": cat_order})

    for i, j in means_df.iterrows():
        print(1,j.Categoria,int(i/4) +1,4 if (i+1)%4 == 0 else (i+1)%4, j.Cargos)
        fig.add_hline(y=j.Cargos, line_dash="dot",
                col=4 if (i+1)%4 == 0 else (i+1)%4, 
                row= int(i/4) +1,
                annotation_text="${:,.0f}".format(int(j.Cargos)),
                annotation_position="top right")

    #fig.update_xaxes(title='')
    #fig.update_yaxes(title='')
    #fig.update_layout(title_font_size = 25)
    fig.show()

def main():
    try:
        mes = sys.argv[1]
    except:        
        raise TypeError("No se especifico 1 argumento requerido: 'mes'. Ej: Dic2021")

    try:
        tc = list(range(int(sys.argv[2])+1))
    except:
        tc = list(range(2))

    if len(sys.argv) < 4:
        path = os.path.join(sys.path[0],'ScotiaFS2021.dat')        
    else:
        path = sys.argv[3]
    
    global td_file
    directory = os.path.split(path)[0]
    td_file = os.path.split(path)[1]

    df = clean_td_file(path)
    df_tc = clean_tc_files(os.path.join(directory,'EECC'), mes)
    df_tc.loc[:,'TC'] = 1
    full_df = df[['Fecha', 'Descripcion', 'Cargos', 'Abonos', 'Mes', 'Categoria']].append(df_tc[['Fecha', 'Descripcion', 'Cargos', 'Mes', 'Categoria','TC']]).fillna(0).reset_index(drop=True)
    
    build_month_report(full_df, mes, tc)
    build_hist_report(full_df, tc)
    
if __name__ == '__main__':
    main()