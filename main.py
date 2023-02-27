from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd

app = Dash(__name__, external_stylesheets=['assets/styles.css'])

df_ba = pd.read_excel("Controle_Investimentos.xlsx", sheet_name="CONTROLE (BA)", header=3, usecols=range(2, 28))
df_rj = pd.read_excel("Controle_Investimentos.xlsx", sheet_name="CONTROLE (RJ)", header=3, usecols=range(2, 28))
df_sp = pd.read_excel("Controle_Investimentos.xlsx", sheet_name="CONTROLE (SP)", header=3, usecols=range(2, 28))
df_nacional = pd.concat([df_ba, df_rj, df_sp])


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


# @app.callback(
#     Output('container_table', 'children'),
#     [Input('dropdown', 'value')]
# )
# def update_table(valor):
#     match valor:
#         case 'BA':
#             return generate_table(df_ba)
#         case 'SP':
#             return generate_table(df_sp)
#         case 'RJ':
#             return generate_table(df_rj)
#         case _:
#             return generate_table(df_nacional)


@app.callback(
    Output('dropdown-contratos', 'options'),
    [Input('dropdown', 'value')]
)
def update_dropdown_contratos(valor):
    match valor:
        case 'BA':
            options = list(df_ba['CONTRATO SOLIC'].unique())
            options.append("TODOS OS CONTRATOS")
            return options
        case 'SP':
            options = list(df_sp['CONTRATO SOLIC'].unique())
            options.append("TODOS OS CONTRATOS")
            return options
        case 'RJ':
            options = list(df_rj['CONTRATO SOLIC'].unique())
            options.append("TODOS OS CONTRATOS")
            return options
        case _:
            options = list(df_nacional['CONTRATO SOLIC'].unique())
            options.append("TODOS OS CONTRATOS")
            return options


@app.callback(
    Output('container_table', 'children'),
    [Input('dropdown', 'value'),
     Input('dropdown-contratos', 'value')]
)
def update_table(valor, contrato):
    data = df_nacional
    match valor:
        case 'BA':
            data = df_ba
        case 'SP':
            data = df_sp
        case 'RJ':
            data = df_rj
        case _:
            data = df_nacional

    if contrato != "TODOS OS CONTRATOS":
        data = data.loc[data['CONTRATO SOLIC'] == contrato, :]

    return generate_table(data)


if __name__ == '__main__':
    app.run_server(debug=True)
