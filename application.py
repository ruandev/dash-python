import base64
import locale
import pdb
from io import BytesIO

import dask.dataframe as dd
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, callback_context, no_update
from dash import html, dcc
from dask import delayed

from data import read_sheet, read_excel_file, all_contracts
from functions import generate_table

URL_LOGO_FILE = 'https://raw.githubusercontent.com/ruandev/dash-python/main/assets/logo.jpg'
URL_HELPDESK = 'https://helpdesk.priner.com.br/support/catalog/items/96'
URL_CSS_FILE = 'assets/styles.css'
COLUMN_VALUE_ITEM = 'VALOR [R$]'

# define a localização para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

app = Dash(__name__, external_stylesheets=[URL_CSS_FILE], suppress_callback_exceptions=True)
server = app.server

# Lê o arquivo excel
arquivo_excel = read_excel_file()

# Lê as planilhas
df_ba = read_sheet(arquivo_excel, "CONTROLE (BA)")
df_rj = read_sheet(arquivo_excel, "CONTROLE (RJ)")
df_sp = read_sheet(arquivo_excel, "CONTROLE (SP)")

# Junta todas as planilhas em uma
df_nacional = pd.concat([df_ba, df_rj, df_sp])
dask_df_nacional = dd.from_pandas(df_nacional, npartitions=10)

# Quantificar a coluna ['VALOR [R$]']
investimento_por_contrato = df_nacional.groupby('CONTRATO SOLIC')[COLUMN_VALUE_ITEM].sum()
df_investimento_contrato = pd.DataFrame(investimento_por_contrato).reset_index()
df_ba[[COLUMN_VALUE_ITEM]] = df_ba[[COLUMN_VALUE_ITEM]].applymap(lambda x: locale.currency(x, grouping=True))
df_rj[[COLUMN_VALUE_ITEM]] = df_rj[[COLUMN_VALUE_ITEM]].applymap(lambda x: locale.currency(x, grouping=True))
df_sp[[COLUMN_VALUE_ITEM]] = df_sp[[COLUMN_VALUE_ITEM]].applymap(lambda x: locale.currency(x, grouping=True))

df_investimento_contrato = df_investimento_contrato.sort_values(by=COLUMN_VALUE_ITEM, ascending=False)

grafico_contrato = px.bar(df_investimento_contrato,
                          x="CONTRATO SOLIC",
                          y=COLUMN_VALUE_ITEM,
                          text=df_investimento_contrato[COLUMN_VALUE_ITEM].apply(
                              lambda x: locale.currency(x, grouping=True)),
                          log_y=True,
                          category_orders={"CONTRATO SOLIC": df_investimento_contrato["CONTRATO SOLIC"].tolist()})
grafico_contrato.update_xaxes(title='Contrato')
grafico_contrato.update_yaxes(title='Valor do Investimento')
grafico_contrato.update_layout(xaxis_tickangle=-90, height=700)

# Formatação da coluna de valor e adição do símbolo de real
df_nacional[[COLUMN_VALUE_ITEM]] = df_nacional[[COLUMN_VALUE_ITEM]].applymap(
    lambda x: locale.currency(x, grouping=True))
df_investimento_contrato[[COLUMN_VALUE_ITEM]] = df_investimento_contrato[[COLUMN_VALUE_ITEM]].applymap(
    lambda x: locale.currency(x, grouping=True))


@delayed
def get_data_dask(valor):
    if valor == 'BA':
        return dd.from_pandas(df_ba, npartitions=1)
    elif valor == 'SP':
        return dd.from_pandas(df_sp, npartitions=1)
    elif valor == 'RJ':
        return dd.from_pandas(df_rj, npartitions=1)
    else:
        return dd.from_pandas(df_nacional, npartitions=1)


@delayed
def filter_data(data, contrato):
    if contrato != "TODOS OS CONTRATOS":
        data = data.loc[data['CONTRATO SOLIC'] == contrato, :]
    return data


@delayed
def generate_data(data):
    # converter o Dask DataFrame para um pandas DataFrame
    df = data.compute()
    return df.to_dict('records')


app.layout = html.Div(children=[
    html.Link(
        rel='icon',
        type='image/png',
        href='https://www.priner.com.br/wp-content/themes/priner/images/favicon.png'
    ),
    html.Header(
        children=[
            html.H1(children='Controle de Investimentos'),
            html.Img(src=URL_LOGO_FILE)
        ]
    ),
    dcc.Tabs(
        value="tab-1",
        children=[
            dcc.Tab(
                value="tab-1",
                label="Acompanhamento de Solicitações",
                children=[
                    html.Div(className="row",
                             children=[
                                 html.Div(className="filters",
                                          children=[
                                              html.Div(
                                                  className="group-field",
                                                  children=[
                                                      html.Label(children="Base", htmlFor="dropdown"),
                                                      dcc.Dropdown(
                                                          id='dropdown',
                                                          className="filter-field",
                                                          options=[
                                                              {'label': 'Nacional', 'value': 'N'},
                                                              {'label': 'Bahia', 'value': 'BA'},
                                                              {'label': 'São Paulo', 'value': 'SP'},
                                                              {'label': 'Rio de Janeiro', 'value': 'RJ'}
                                                          ],
                                                          value='N',
                                                          clearable=False
                                                      ), ]),
                                              html.Div(
                                                  className="group-field",
                                                  children=[
                                                      html.Label(children="Contratos",
                                                                 htmlFor="dropdown-contratos"),
                                                      dcc.Dropdown(
                                                          id='dropdown-contratos',
                                                          className="filter-field",
                                                          value="TODOS OS CONTRATOS",
                                                          clearable=False
                                                      ), ]), ]),
                                 html.Div(
                                     className="filterPC",
                                     children=[html.Div(
                                         children=[
                                             html.Label(children="N° PC", htmlFor="input-pc"),
                                             dcc.Input(
                                                 id='input-pc',
                                                 className="filter-field",
                                                 value=''
                                             ), ]),
                                         html.Button('Filtrar', id='botao-filtrar', className="btn")])
                             ]),
                    html.Div(id='container_table'),
                    html.A(
                        'Download Excel',
                        id='download-link',
                        className="btn",
                        download='tabela.xlsx',
                        href='',
                        target='_blank',
                    ),
                ]),
            dcc.Tab(
                label="Itens Disponíveis",
                value="tab-2",
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                className="filters",
                                children=[
                                    html.Div(
                                        className="group-field",
                                        children=[
                                            html.Label(children="Contratos",
                                                       htmlFor="dropdown-contratos-itens-disponiveis"),
                                            dcc.Dropdown(
                                                id='dropdown-contratos-itens-disponiveis',
                                                className="filter-field",
                                                options=all_contracts(df_nacional),
                                                value="TODOS OS CONTRATOS",
                                                clearable=False
                                            ),
                                        ]),
                                    html.A(
                                        className="btn",
                                        href=URL_HELPDESK,
                                        target="_blank",
                                        children=[
                                            html.Button('Solicitar equipamentos')
                                        ]
                                    ),
                                ]
                            ),

                            html.Div(id='container_table_itens_disponiveis'),
                        ]
                    )
                ]
            ),
            dcc.Tab(
                value="tab-3",
                label="Investimento por Contrato",
                children=[
                    html.Div(
                        children=[
                            html.H2(children='Soma de valores pagos por contrato'),
                            generate_table(df_investimento_contrato, "aba-3"),
                            dcc.Graph(
                                id='graf-contrato',
                                figure=grafico_contrato
                            ),
                        ]
                    )
                ]
            )
        ]
    ),
])


@app.callback(
    Output('dropdown-contratos', 'options'),
    [Input('dropdown', 'value')]
)
def update_dropdown_contratos(valor):
    if valor == 'BA':
        options = list(df_ba['CONTRATO SOLIC'].unique())
        options.append("TODOS OS CONTRATOS")
        return options
    elif valor == 'SP':
        options = list(df_sp['CONTRATO SOLIC'].unique())
        options.append("TODOS OS CONTRATOS")
        return options
    elif valor == 'RJ':
        options = list(df_rj['CONTRATO SOLIC'].unique())
        options.append("TODOS OS CONTRATOS")
        return options
    else:
        options = list(df_nacional['CONTRATO SOLIC'].unique())
        options.append("TODOS OS CONTRATOS")
        return options


@app.callback(
    Output('container_table', 'children'),
    [Input('dropdown', 'value'),
     Input('dropdown-contratos', 'value'),
     Input('botao-filtrar', 'n_clicks')],
    [State('input-pc', 'value')]
)
def update_table(valor, contrato, n_clicks, filtro_pc):
    triggered_input = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_input == 'botao-filtrar' and filtro_pc != '':
        if n_clicks is None:
            return no_update
        else:
            # pdb.set_trace()
            filter_by_num_pc = (df_nacional['Nº PC'] == float(filtro_pc)) | (df_nacional['Nº PC'] == filtro_pc)
            data = df_nacional.loc[filter_by_num_pc]
            return generate_table(data, "aba-1")
    else:
        data = get_data_dask(valor)
        data = filter_data(data, contrato)
        data = generate_data(data)
        return generate_table(pd.DataFrame(data.compute()), "aba-1")


@app.callback(
    Output('container_table_itens_disponiveis', 'children'),
    [Input('dropdown-contratos-itens-disponiveis', 'value')]
)
def update_table_itens_disponiveis(contrato):
    filtro_dask = (dask_df_nacional["DATA REAL DE ENTREGA"].notnull()) & (
        dask_df_nacional["DATA DE ENVIO P/ OBRA"].isnull())

    if contrato != "TODOS OS CONTRATOS":
        filtro_dask = filtro_dask & (dask_df_nacional['CONTRATO SOLIC'] == contrato)

    return generate_table(dask_df_nacional.loc[filtro_dask, ["NOME DO ITEM",
                                                             "CONTRATO SOLIC",
                                                             "FILIAL",
                                                             "NÚMERO DO PATRIMÔNIO",
                                                             "DATA REAL DE ENTREGA"]].compute(), "aba-2")


# Função para atualizar o link de download
@app.callback(
    Output('download-link', 'href'),
    Input('tabela-aba-1', 'data'),
    Input('tabela-aba-1', 'columns'))
def update_download_link(data, columns):
    df = pd.DataFrame(data, columns=[c['name'] for c in columns])
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    excel_binary = excel_file.read()
    excel_base64 = base64.b64encode(excel_binary).decode('utf-8')
    href_data_excel = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_base64}'
    return href_data_excel


app.title = "Controle de Investimentos | Priner"

if __name__ == '__main__':
    app.run_server(debug=True)
