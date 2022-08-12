from email import header
import json
import pandas as pd
import gspread
from dotenv import load_dotenv
from gspread_dataframe import set_with_dataframe
import os
import json

load_dotenv()

def download_gspread():
    credentials = json.loads(os.environ.get("GCLOUD_CREDENTIALS"))
    gc = gspread.service_account_from_dict(credentials)
    sh = gc.open_by_key(os.environ.get("SPREADSHEET_KEY"))
    worksheet = sh.get_worksheet(0)
    df = pd.DataFrame(worksheet.get_all_values())
    df = df.drop(df.index[0])
    df.columns = ["idOp", "rate", "email"]
    df["idOp"] = pd.to_numeric(df["idOp"])
    df["rate"] = df["rate"].apply(lambda x: float(x.replace(",", ".")))
    return df.to_dict('records')

def upload_datafrae_to_gspread(df):
    credentials = json.loads(os.environ.get("GCLOUD_CREDENTIALS"))
    gc = gspread.service_account_from_dict(credentials)
    sh = gc.open_by_key(os.environ.get("SPREADSHEET_KEY"))
    worksheet = sh.get_worksheet(0)
    worksheet.clear()
    set_with_dataframe(worksheet, df)