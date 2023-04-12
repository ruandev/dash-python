import pandas as pd
from dash import dash_table
from dask import delayed


def format_column_date(column):
    column = pd.to_datetime(column, errors='coerce')
    column = column.dt.strftime('%d/%m/%Y')
    return column


def remove_columns(dataframe, columns):
    for column in columns:
        dataframe = dataframe.drop(column, axis=1)

    return dataframe


def generate_table(dataframe, aba):
    return dash_table.DataTable(
        id="tabela-" + aba,
        columns=[{'name': coluna, 'id': coluna} if coluna != 'DATA TICKET' else {'name': coluna, 'id': coluna,
                                                                                 'type': 'datetime'} for coluna in
                 dataframe.columns],
        data=dataframe.to_dict('records'),
        page_size=20,
        style_table={'className': 'table'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#004b75a6'},
                                {'if': {'row_index': 'even'}, 'backgroundColor': '#FFFFFF'}])

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
