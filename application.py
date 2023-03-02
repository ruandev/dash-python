import locale
from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd

url_css_file = 'https://raw.githubusercontent.com/ruandev/dash-python/main/assets/styles.css'
url_excel_file = "https://github.com/ruandev/dash-python/raw/main/Controle_Investimentos.xlsx"
column_name = 'NOME DO ITEM'
value_column = 'VALOR [R$]'
colunas_utilizadas = range(2, 28)

# define a localização para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

app = Dash(__name__, external_stylesheets=[url_css_file])
server = app.server

# Lê o arquivo excel
arquivo_excel = pd.ExcelFile(url_excel_file,
                             engine='openpyxl')


def format_column_date(column):
    column = pd.to_datetime(column)
    column = column.dt.strftime('%d/%m/%Y')
    return column


# Lê as planilhas
df_ba = pd.read_excel(arquivo_excel, sheet_name="CONTROLE (BA)", header=3, usecols=colunas_utilizadas)
df_ba = df_ba.dropna(subset=[column_name])
df_ba['DATA TICKET'] = format_column_date(df_ba['DATA TICKET'])
df_rj = pd.read_excel(arquivo_excel, sheet_name="CONTROLE (RJ)", header=3, usecols=colunas_utilizadas)
df_rj = df_rj.dropna(subset=[column_name])
df_rj['DATA TICKET'] = format_column_date(df_rj['DATA TICKET'])
df_sp = pd.read_excel(arquivo_excel, sheet_name="CONTROLE (SP)", header=3, usecols=colunas_utilizadas)
df_sp = df_sp.dropna(subset=[column_name])
df_sp['DATA TICKET'] = format_column_date(df_sp['DATA TICKET'])

# Junta todas as planilhas em uma
df_nacional = pd.concat([df_ba, df_rj, df_sp])

# Configurar a coluna ['VALOR [R$]'] para quantificar sem erros
df_nacional[value_column] = df_nacional[value_column].fillna(0.0)
df_nacional[value_column] = df_nacional[value_column].replace('-', 0.0)
df_nacional[value_column] = df_nacional[value_column].astype(float)

# Quantificar a coluna ['VALOR [R$]']
investimento_por_fornecedor = df_nacional.groupby('FORNECEDOR')[value_column].sum()
df_investimento_fornecedor = pd.DataFrame(investimento_por_fornecedor).reset_index()
investimento_por_contrato = df_nacional.groupby('CONTRATO SOLIC')[value_column].sum()
df_investimento_contrato = pd.DataFrame(investimento_por_contrato).reset_index()

# Formatação da coluna e adição do símbolo de real
df_investimento_fornecedor[value_column] = df_investimento_fornecedor[value_column].apply(
    lambda x: locale.currency(x, grouping=True))
df_investimento_contrato[value_column] = df_investimento_contrato[value_column].apply(
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
    html.H1(children='Estoque'),
    html.H2(children='Algum texto legal... sem ideia por enquanto'),

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
                            dash_table.DataTable(
                                id='table_fornecedor',
                                columns=[{"name": i, "id": i} for i in df_investimento_fornecedor.columns],
                                data=df_investimento_fornecedor.to_dict('records'),
                                page_size=10,
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
                            dash_table.DataTable(
                                id='table_contrato',
                                columns=[{"name": i, "id": i} for i in df_investimento_contrato.columns],
                                data=df_investimento_contrato.to_dict('records'),
                                page_size=10,
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
