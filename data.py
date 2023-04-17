import pandas as pd
from functions import format_column_date



# Lê o arquivo excel



def all_contracts(df_nacional):
    contracts = list(df_nacional['CONTRATO SOLIC'].unique())
    contracts.append("TODOS OS CONTRATOS")
    return contracts
