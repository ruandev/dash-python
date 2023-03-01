from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd
from flask_caching import Cache

app = Dash(__name__, external_stylesheets=[
    'https://raw.githubusercontent.com/ruandev/dash-python/main/assets/styles.css'
])

# Configuração do cache do Flask
cache = Cache(app.server, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 3600  # 1 hora de cache
})


# Leitura do arquivo Excel
@cache.memoize()
def ler_arquivo_excel():
    arquivo_excel = pd.ExcelFile("https://github.com/ruandev/dash-python/raw/main/Controle_Investimentos.xlsx",
                                 engine='openpyxl')
    colunas_utilizadas = range(2, 28)
    planilha_ba = pd.read_excel(arquivo_excel, sheet_name="CONTROLE (BA)", header=3, usecols=colunas_utilizadas)
    planilha_rj = pd.read_excel(arquivo_excel, sheet_name="CONTROLE (RJ)", header=3, usecols=colunas_utilizadas)
    planilha_sp = pd.read_excel(arquivo_excel, sheet_name="CONTROLE (SP)", header=3, usecols=colunas_utilizadas)
    arquivo_excel.close()
    planilha_nacional = pd.concat([planilha_ba, planilha_rj, planilha_sp])
    return planilha_ba, planilha_rj, planilha_sp, planilha_nacional


df_ba, df_rj, df_sp, df_nacional = ler_arquivo_excel()


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

    html.Div(id='container_table')
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
