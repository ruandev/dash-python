import pandas as pd
from dash import dash_table
from dask import delayed





@delayed
def generate_data(data):
    # converter o Dask DataFrame para um pandas DataFrame
    df = data.compute()
    return df.to_dict('records')
