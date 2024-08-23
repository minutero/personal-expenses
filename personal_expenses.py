import pandas as pd
import os
import re
import numpy as np
import sys
from datetime import datetime
import locale

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#
#df[df.Categoria =='Indefinido']["Cargos"].sum()
# Categoria
def cat_df(df):
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.startswith("TEF"), "Transferencia", ""
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.lower().str.contains("sumup"), "SUMUP", df.Categoria
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains(
            "ASEO DOMICILIARIO|PAGO DE SERVICIOS|SERVICIOS|LIPIGAS|CHILQUI|PAC SERVICIOS PROFESIONA 20630|53324082-8|65146277-0|MUNIC.VILLA ALEMA|Felipe Itau|UNICEF|YOUTUBE|HBOMAX"
        ),
        "Cuentas",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains("TARJ.CRED."), "Tarjeta Credito", df.Categoria
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains(
            "SERVICIO DE ACTIVIDAD MENSUAL|SEGURO|SEG.|COMISION|MANTENCION|COM. MENSUAL|PAT VIDA SECURITY|IMPUESTO|INTERES"
        ),
        "Financiero",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains(
            "FRUTOS SECOS|LIQUIMAX|EXPENDIO DE ALIME|EXPRESS|LIDER|HIPER|JUMBO|PANADERIA|ISABEL|MUNDO VERDE|ANIMAL|DISTRIBUIDORA AUS|12880128-6|TOTTUS|EMPORIO|LUIS SOTO URRA|Rosana serey|Geni ve|Carlos arand|Venta de fru|PANIFICADORA"
        ),
        "Supermercado",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains(
            "MERVAL|PETROBRAS|SHELL|COPEC|ESTACIONAMIEN|LATAM|PETRO LEIVA"
        ),
        "Transporte",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains(
            "GASTRONOMICA|PISO 2|DOGGIS|REDKIDS|CARNALES|PJD|PUNTO TICKET|JUAN MAESTRO|CINE|GRIDO|RESTAUR|CAFETERIA|GLASGOW|SIN CULPA|HOTEL|ZOO|ENTREFUEGO|CAFE|MISTER DI|KEYER|FUNDACION JARDIN|12603011-8|LA CASA DEL JARDI"
        ),
        "Salida",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains("GIRO REDBANC"), "Efectivo", df.Categoria
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains(
            "SODIMAC|PLACACENTRO|CONSTRU-MART|LIMARGALA|HOMECENTER|EASY|IMPERIAL|ENKO|CASA MUSA|CONSTRUMART|MK"
        ),
        "Construccion",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains("76513680-6|76810627-4|76989370-9|DIVISAS"),
        "Inversion",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains("CEMIN|SALCOBRAND|FARM|DR SIMI|AHUM|ISAPRE"),
        "Salud",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains(
            "PARIS|RIPLEY|CASAIDEAS|MERCADO PAGO|EL CONTAINER|CENCOSUD|O 2 SPORT|DAFITI|FPAY|LINIO|FALABELL|MERCADOPAGO|SHESAN"
        ),
        "Casa Comercial",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains(
            "COMICS|77288155-K|JUEGO DE LETRAS|GATO ARCANO|MODELPRO|76554187-5|76795499-9|AMAZON|CAFE Y TABLEROS"
        ),
        "Juegos",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains("MUNDO TRANSFER|NUSKIN"), "Arigato", df.Categoria
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.upper().str.contains("GOOGLE PLAY|NETFLIX|DISNEY|MELIMAS"),
        "Servicios Digitales",
        df.Categoria,
    )
    df.loc[:, "Categoria"] = np.where(
        df.Descripcion.str.contains("PAGO EN EFECTIVO|DEPOSITO A PLAZO|5335679-6|8671486-8"), "Excluir", df.Categoria
    )
    df.loc[:, "Categoria"] = np.where(df.Categoria == "", "Indefinido", df.Categoria)


def clean_td_file(dir):
    df = pd.DataFrame()
    for file in os.listdir(dir):
        df_td = pd.read_csv(
            os.path.join(dir, file),
            sep=";",
            skiprows=8,
            dtype={"Fecha": str},
            decimal=",",
        )

        # Fecha
        locale.setlocale(locale.LC_ALL, "es_ES.utf8")
        df_td.loc[:, "Fecha"] = pd.to_datetime(
            df_td.Fecha.str.strip(), format="%d%m%Y", dayfirst=True
        ).dt.date
        df_td.loc[:, "Mes"] = df_td.Fecha.apply(lambda x: x.strftime("%b%Y"))
        df_td = df_td.fillna(0)
        df_td.Descripcion = df_td.Descripcion.str.strip()

        cat_df(df_td)

        df = pd.concat([df, df_td])

    return df


#### TC File
def clean_tc_files(dir):
    df = pd.DataFrame()
    locale.setlocale(locale.LC_ALL, "es_ES.utf8")
    for file in os.listdir(dir):
        file_words = file.split("-")
        file_dt = datetime.strptime(file_words[4] + file_words[5].split(".")[0], "%B%Y")

        df_tc = pd.read_excel(os.path.join(dir, file), skiprows=49)

        # Remove unnecesary rows and columns
        df_tc = df_tc[(df_tc["Fecha\nOperación"].notna())]
        df_tc = df_tc.dropna(axis=1, how="all")  # drop all empty columns
        df_tc.columns = [
            "Lugar",
            "FechaOperacion",
            "Codigo Referencia",
            "Descripcion",
            "Monto Operacion",
            "Monto Total",
            "N Cuota",
            "Cargos",
        ]
        df_tc = df_tc[
            (df_tc["N Cuota"] != "Cargo del Mes")
            & (df_tc["Descripcion"].str.strip() != "PAGO")
        ]
        df_tc = df_tc[
            ~df_tc["Descripcion"].str.strip().str.startswith("TOTAL")
        ].reset_index(drop=True)

        cat_df(df_tc)

        # Fix column information - String columns cleansing
        df_tc.loc[:, "FechaOperacion"] = pd.to_datetime(
            df_tc.FechaOperacion.str.strip(), format="%d/%m/%Y", dayfirst=True
        ).dt.date
        df_tc.loc[:, "Fecha"] = datetime.strptime(
            file_words[4] + file_words[5].split(".")[0], "%B%Y"
        ).strftime("%Y-%m-%d")
        df_tc.loc[:, "Fecha"] = pd.to_datetime(
            df_tc.Fecha.str.strip(), format="%Y-%m-%d"
        ).dt.date
        df_tc.loc[:, "Mes"] = df_tc.Fecha.apply(lambda x: x.strftime("%b%Y"))

        df_tc.loc[:, "Lugar"] = df_tc.loc[:, "Lugar"].str.strip()
        df_tc.loc[:, "Lugar"] = df_tc.Lugar.str.replace("VILLA ALEMA", "VILLA ALEMANA")
        df_tc.loc[:, "Descripcion"] = df_tc.apply(
            lambda x: x["Descripcion"][: x["Descripcion"].find("TASA")], axis=1
        ).str.strip()
        remove = re.compile("|".join(df_tc.Lugar.unique().tolist()))
        df_tc.loc[:, "Descripcion"] = df_tc.Descripcion.str.replace(
            remove, "", regex=True
        ).str.strip()

        # Fix column information - Money columns cleansing
        df_tc[df_tc.columns[[4, 5, 7]]] = (
            df_tc[df_tc.columns[[4, 5, 7]]]
            .replace("[\$.]", "", regex=True)
            .astype(float)
        )
        df_tc = df_tc[df_tc.Cargos > 0].reset_index(drop=True)

        df = pd.concat([df, df_tc])
    df = df.sort_values("Fecha").reset_index(drop=True)
    return df


def build_month_report(
    df,
    mes=None,
    colors={
        "background": "#ffffff",
        "text": "#000000",
        "chart1": "#000000",
        "chart2": "#ffcc66",
    },
):
    locale.setlocale(locale.LC_ALL, "es_ES.utf8")
    if mes is None:
        mes = datetime.now().strftime("%b%Y")
    df = df[df.Categoria != "Excluir"]
    df = df[(df.Mes.str.lower() == mes.lower())]
    df.loc[:, "TC"] = df.TC.apply(np.int64).astype(str)
    df.loc[:, "Fecha"] = df.Fecha.apply(lambda x: x.strftime("%A %d"))
    total_cat = pd.DataFrame(
        df[["Categoria", "Cargos"]].groupby("Categoria").sum()
    ).reset_index()

    fig = px.bar(
        df,
        x="Categoria",
        y="Cargos",
        hover_name="Descripcion",
        hover_data=["Fecha"],
        color="TC",
        color_discrete_map={"0": colors["chart1"], "1": colors["chart2"]},
        category_orders={
            "Categoria": [
                "Cuentas",
                "Supermercado",
                "Transferencia",
                "Construccion",
                "Casa Comercial",
                "Salida",
                "Financiero",
                "Inversion",
                "Juegos",
                "Transporte",
                "Efectivo",
                "Salud",
                "Arigato",
                "Indefinido",
            ]
        },
    )
    fig.update_xaxes(title="", showgrid=False)
    fig.update_yaxes(title="", showgrid=False, showticklabels=False)
    fig.update_layout(title_font_size=25)
    fig.update_layout(
        {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": colors["background"],
        }
    )
    fig.update_layout(
        font_color=colors["text"],
        title_font_color=colors["text"],
        legend_title_font_color=colors["text"],
    )
    for i, t in total_cat.iterrows():
        fig.add_annotation(
            x=t.Categoria,
            y=t.Cargos + 10000,
            text="${:,.0f}".format(t.Cargos),
            showarrow=False,
            font=dict(color=colors["text"]),
        )

    return fig
    """
    analyzed_df[['Mes','Cargos','Categoria']].groupby(['Mes','Categoria']).max()

    col = ['Fecha','Descripcion','Categoria','TC']
    analyzed_df[col + ['Cargos']][~analyzed_df.Descripcion.str.contains('16332063-0|16261568-8')].nlargest(5,'Cargos')
    analyzed_df[col + ['Abonos']].nlargest(5,'Abonos')
    """


def build_hist_report(
    df,
    categories=None,
    colors={
        "background": "#ffffff",
        "text": "#000000",
        "chart1": "#8fce00",
        "chart2": "#ffcc66",
    },
):
    if categories is None:
        categories = df["Categoria"].unique()
    df = df[df.Categoria != "Excluir"]
    filtered_df = (
        df[df["Categoria"].isin(categories)][["Categoria", "Mes", "Cargos", "Abonos"]]
        .groupby(["Categoria", "Mes"])
        .sum()
        .reset_index()
    )
    month_order = [
        "ene",
        "feb",
        "mar",
        "abr",
        "may",
        "jun",
        "jul",
        "ago",
        "sep",
        "oct",
        "nov",
        "dic",
    ]
    years_in_data = sorted(set([y[-4:] for y in filtered_df["Mes"].unique()]))
    date_order = [month + "." + year for year in years_in_data for month in month_order]
    filtered_df.loc[:, "Mes"] = pd.Categorical(filtered_df["Mes"], date_order)
    filtered_df.sort_values(["Categoria", "Mes"], inplace=True)

    means_df = (
        filtered_df[["Categoria", "Cargos", "Abonos"]]
        .groupby("Categoria")
        .mean()
        .reset_index()
    )

    full_cat_order = [
        "Cuentas",
        "Supermercado",
        "Transferencia",
        "Construccion",
        "Casa Comercial",
        "Salida",
        "Financiero",
        "Inversion",
        "Juegos",
        "Transporte",
        "Efectivo",
        "Salud",
        "Arigato",
        "Indefinido",
        "SUMUP",
        "Excluir",
    ]
    cat_order = [x for x in categories if x in full_cat_order]
    means_df.loc[:, "Categoria"] = pd.Categorical(means_df["Categoria"], cat_order)
    means_df = means_df.sort_values("Categoria", ascending=False).reset_index(drop=True)

    fig = make_subplots(len(categories), 1)
    for i, cat in enumerate(categories):
        category_df = filtered_df[filtered_df["Categoria"] == cat]
        fig.add_trace(
            go.Scatter(
                x=category_df["Mes"],
                y=category_df["Cargos"],
                fill="tozeroy",
                fillcolor=colors["chart1"],
                line=dict(color=colors["chart2"], width=0.5),
                # marker=dict(color=colors['chart2']),
                name=cat,
            ),
            i + 1,
            1,
        )
        try:
            cargo_cat = means_df[means_df["Categoria"] == cat]["Cargos"].iloc[0]
        except:
            cargo_cat = 0
        fig.add_shape(
            type="line",
            xref="paper",
            x0=0,
            x1=1,
            yref="y" + str(i + 1),
            y0=cargo_cat,
            y1=cargo_cat,
            line=dict(
                color=colors["text"],
                width=3,
                dash="dot",
            ),
        )
        fig.add_annotation(
            x=1,
            y=cargo_cat,
            text="${:,.0f}".format(int(cargo_cat)),
            showarrow=False,
            yref="y" + str(i + 1),
            xref="paper",
            yshift=10,
            font=dict(color=colors["text"]),
        )
    fig.update_layout(hovermode="x")
    fig.update_xaxes(title="", showgrid=False, showticklabels=False)
    fig.update_yaxes(title="", showgrid=False, showticklabels=False)

    fig.update_layout(
        {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": colors["background"],
        }
    )
    fig.update_layout(
        font_color=colors["text"],
        title_font_color=colors["text"],
        legend_title_font_color=colors["text"],
    )

    return fig


def draw_hist_plot(tc, path):

    df_td = clean_td_file(os.path.join(path, "Debito"))
    df_tc = clean_tc_files(os.path.join(path, "Credito"))
    df_tc.loc[:, "TC"] = 1
    df = (
        pd.concat(
            [
                df_td[["Fecha", "Descripcion", "Cargos", "Abonos", "Mes", "Categoria"]],
                df_tc[["Fecha", "Descripcion", "Cargos", "Mes", "Categoria", "TC"]],
            ]
        )
        .fillna(0)
        .reset_index(drop=True)
    )

    analyzed_df = df[(df.Categoria != "Tarjeta Credito") & (df.TC.isin(tc))]
    hist_fig = build_hist_report(analyzed_df)

    return hist_fig


def draw_month_plot(tc, path):
    try:
        mes = sys.argv[2]
    except:
        raise TypeError("No se especifico 1 argumento requerido: 'mes'. Ej: Dic2021")

    df_td = clean_td_file(os.path.join(path, "Debito"), mes)
    df_tc = clean_tc_files(os.path.join(path, "Credito"), mes)
    df_tc.loc[:, "TC"] = 1
    df = (
        df_td[["Fecha", "Descripcion", "Cargos", "Abonos", "Mes", "Categoria"]]
        .append(df_tc[["Fecha", "Descripcion", "Cargos", "Mes", "Categoria", "TC"]])
        .fillna(0)
        .reset_index(drop=True)
    )

    analyzed_df = df[(df.Categoria != "Tarjeta Credito") & (df.TC.isin(tc))]

    month_fig = build_month_report(analyzed_df, mes)

    return month_fig


def main():
    try:
        plot_type = sys.argv[1]
    except:
        raise TypeError(
            "No se especifico 1 argumento requerido: 'tipo de grafico'. Opciones validas: hist, mes"
        )

    try:
        tc = list(range(int(sys.argv[3]) + 1))
    except:
        tc = list(range(2))

    if len(sys.argv) < 5:
        path = os.path.dirname(os.path.abspath(__file__))
    else:
        path = sys.argv[4]

    if plot_type == "hist":
        fig_toshow = draw_hist_plot(tc, path)
    elif plot_type == "mes":
        fig_toshow = draw_month_plot(tc, path)
    else:
        raise TypeError(
            "No se especifico 'tipo de grafico' valido. Opciones validas: hist, mes"
        )

    fig_toshow.show()


if __name__ == "__main__":
    main()
