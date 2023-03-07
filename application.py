import locale
from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd
import plotly.express as px

COLUMNS_TO_DELETE = ["DESCRICAO DO PRODUTO", "MARCA", "MODELO", "COMPRADOR", "DATA PREV ENTREGA", "Nº NF ENVIO P/ OBRA",
                     "STATUS PC", "STATUS OC"]

URL_CSS_FILE = 'https://raw.githubusercontent.com/ruandev/dash-python/main/assets/styles.css'
URL_EXCEL_FILE = "https://github.com/ruandev/dash-python/raw/main/Controle_Investimentos.xlsx"
COLUMN_NAME_ITEM = 'NOME DO ITEM'
COLUMN_VALUE_ITEM = 'VALOR [R$]'
USED_COLUMNS = range(2, 28)

# define a localização para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

app = Dash(__name__, external_stylesheets=[URL_CSS_FILE])
server = app.server

# Lê o arquivo excel
arquivo_excel = pd.ExcelFile(URL_EXCEL_FILE, engine='openpyxl')


def format_column_date(column):
    column = pd.to_datetime(column)
    column = column.dt.strftime('%d/%m/%Y')
    return column


def remove_columns(dataframe, columns):
    for column in columns:
        dataframe = dataframe.drop(column, axis=1)

    return dataframe


# Define função para ler e tratar planilhas
def read_sheet(sheet_name):
    df = pd.read_excel(arquivo_excel, sheet_name=sheet_name, header=3, usecols=USED_COLUMNS)
    df.dropna(subset=[COLUMN_NAME_ITEM], inplace=True)
    df['DATA TICKET'] = format_column_date(df['DATA TICKET'])
    df['DATA OC'] = format_column_date(df['DATA OC'])
    df[COLUMN_VALUE_ITEM] = df[COLUMN_VALUE_ITEM].fillna(0.0).replace('-', 0.0).astype(float)
    df.drop(columns=COLUMNS_TO_DELETE, inplace=True)
    return df


# Lê as planilhas
df_ba = read_sheet("CONTROLE (BA)")
df_rj = read_sheet("CONTROLE (RJ)")
df_sp = read_sheet("CONTROLE (SP)")

# Junta todas as planilhas em uma
df_nacional = pd.concat([df_ba, df_rj, df_sp])

# Quantificar a coluna ['VALOR [R$]']
investimento_por_fornecedor = df_nacional.groupby('FORNECEDOR')[COLUMN_VALUE_ITEM].sum()
df_investimento_fornecedor = pd.DataFrame(investimento_por_fornecedor).reset_index()
investimento_por_contrato = df_nacional.groupby('CONTRATO SOLIC')[COLUMN_VALUE_ITEM].sum()
df_investimento_contrato = pd.DataFrame(investimento_por_contrato).reset_index()
df_ba[[COLUMN_VALUE_ITEM]] = df_ba[[COLUMN_VALUE_ITEM]].applymap(lambda x: locale.currency(x, grouping=True))
df_rj[[COLUMN_VALUE_ITEM]] = df_rj[[COLUMN_VALUE_ITEM]].applymap(lambda x: locale.currency(x, grouping=True))
df_sp[[COLUMN_VALUE_ITEM]] = df_sp[[COLUMN_VALUE_ITEM]].applymap(lambda x: locale.currency(x, grouping=True))

grafico_fornecedores = px.pie(df_investimento_fornecedor,
                              names='FORNECEDOR',
                              labels='FORNECEDOR',
                              values=COLUMN_VALUE_ITEM)
grafico_contrato = px.pie(df_investimento_contrato, names="CONTRATO SOLIC", values=COLUMN_VALUE_ITEM)
# Formatação da coluna de valor e adição do símbolo de real
df_investimento_fornecedor[[COLUMN_VALUE_ITEM]] = df_investimento_fornecedor[[COLUMN_VALUE_ITEM]].applymap(
    lambda x: locale.currency(x, grouping=True))
df_nacional[[COLUMN_VALUE_ITEM]] = df_nacional[[COLUMN_VALUE_ITEM]].applymap(
    lambda x: locale.currency(x, grouping=True))
df_investimento_contrato[[COLUMN_VALUE_ITEM]] = df_investimento_contrato[[COLUMN_VALUE_ITEM]].applymap(
    lambda x: locale.currency(x, grouping=True))


def generate_table(dataframe):
    return dash_table.DataTable(
        columns=[{'name': coluna, 'id': coluna} if coluna != 'DATA TICKET' else {'name': coluna, 'id': coluna,
                                                                                 'type': 'datetime'} for coluna in
                 dataframe.columns],
        data=dataframe.to_dict('records'),
        page_size=10,
        style_table={'className': 'table'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#DDDDDD'},
                                {'if': {'row_index': 'even'}, 'backgroundColor': '#FFFFFF'}])


app.layout = html.Div(children=[
    html.H1(children='Controle de Investimentos'),

    dcc.Tabs(
        value="tab-1",
        children=[
            dcc.Tab(
                value="tab-1",
                label="Estoque",
                children=[
                    html.Div(className="filters",
                             children=[
                                 html.Div(
                                     className="group-field",
                                     children=[
                                         html.Label(children="Base", htmlFor="dropdown-contratos"),
                                         dcc.Dropdown(
                                             id='dropdown',
                                             className="filter-field",
                                             options=[
                                                 {'label': 'Nacional', 'value': 'N'},
                                                 {'label': 'Bahia', 'value': 'BA'},
                                                 {'label': 'São Paulo', 'value': 'SP'},
                                                 {'label': 'Rio de Janeiro', 'value': 'RJ'}
                                             ],
                                             value='N'
                                         ), ]),
                                 html.Div(
                                     className="group-field",
                                     children=[
                                         html.Label(children="Contratos", htmlFor="dropdown-contratos"),
                                         dcc.Dropdown(
                                             id='dropdown-contratos',
                                             className="filter-field",
                                             value="TODOS OS CONTRATOS"
                                         ), ]), ]),

                    html.Div(id='container_table'),
                ]),
            dcc.Tab(
                label="Investimento por Fornecedor",
                value="tab-2",
                children=[
                    html.Div(
                        children=[
                            html.H2(children='Soma de valores pagos por fornecedor'),
                            dcc.Graph(
                                id='graf-fornecedor',
                                figure=grafico_fornecedores
                            )
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
     Input('dropdown-contratos', 'value')]
)
def update_table(valor, contrato):
    if valor == 'BA':
        data = df_ba
    elif valor == 'SP':
        data = df_sp
    elif valor == 'RJ':
        data = df_rj
    else:
        data = df_nacional

    if contrato != "TODOS OS CONTRATOS":
        data = data.loc[data['CONTRATO SOLIC'] == contrato, :]

    return generate_table(data)


if __name__ == '__main__':
    # application.run(host='0.0.0.0', port='8080')
    app.run_server(debug=True)
