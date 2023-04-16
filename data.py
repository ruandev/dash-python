import pandas as pd
from functions import format_column_date

URL_EXCEL_FILE = "https://github.com/ruandev/files/raw/main/Controle_Investimentos_1504.xlsx"
COLUMNS_TO_DELETE = ["DESCRICAO DO PRODUTO", "MARCA", "MODELO", "COMPRADOR", "DATA PREV ENTREGA", "Nº NF ENVIO P/ OBRA",
                     "STATUS PC", "STATUS OC"]
COLUMN_NAME_ITEM = 'NOME DO ITEM'
COLUMN_VALUE_ITEM = 'VALOR [R$]'
USED_COLUMNS = range(2, 28)


# Lê o arquivo excel
def read_excel_file():
    arquivo_excel = pd.ExcelFile(URL_EXCEL_FILE, engine='openpyxl')
    return arquivo_excel


# Define função para ler e tratar planilhas
def read_sheet(arquivo_excel, sheet_name):
    df = pd.read_excel(arquivo_excel, sheet_name=sheet_name, header=3, usecols=USED_COLUMNS)
    df.dropna(subset=[COLUMN_NAME_ITEM], inplace=True)
    df['DATA TICKET'] = format_column_date(df['DATA TICKET'])
    df['DATA OC'] = format_column_date(df['DATA OC'])
    df['DATA PC'] = format_column_date(df['DATA PC'])
    df['DATA DE ENVIO P/ OBRA'] = format_column_date(df['DATA DE ENVIO P/ OBRA'])
    df['DATA REAL DE ENTREGA'] = format_column_date(df['DATA REAL DE ENTREGA'])
    df[COLUMN_VALUE_ITEM] = df[COLUMN_VALUE_ITEM].fillna(0.0).replace('-', 0.0).astype(float)
    df['CONTRATO SOLIC'] = df['CONTRATO SOLIC'].fillna('SEM CONTRATO')
    df.drop(columns=COLUMNS_TO_DELETE, inplace=True)
    df.fillna(value='', inplace=True)
    return df


def all_contracts(df_nacional):
    contracts = list(df_nacional['CONTRATO SOLIC'].unique())
    contracts.append("TODOS OS CONTRATOS")
    return contracts
