from ninja import NinjaAPI
from xepelin_api.gspread import download_gspread, upload_datafrae_to_gspread
from xepelin_api.schema import Message, Rates, Rate
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api = NinjaAPI()

@api.get("/gspread_info", response={200: Rates, 500: Message})
def get_gspread_info_endpoint(request):
    try:
        rates_list = download_gspread()
    except Exception as e:
        return 500, {"message": f"Ups... The following error ocurred: {e}"}
    else:
        return 200, {"rates": rates_list}


@api.post("/update_gspread_rate",  response={200: Message, 500: Message})
def update_gspread_rate_endpoint(request, data: Rate):
    try:
        rates_list = download_gspread()
        df = pd.DataFrame(rates_list)
        row_index = df[df["id Op"] == data.idOp].index.values.astype(int)[0]
        df.iloc[[row_index], [1]] = data.tasa
        upload_datafrae_to_gspread(df)

    except Exception as e:
        return 500, {"message": f"Ups... The following error ocurred: {e}"}

    else:
        response = requests.post(os.environ.get("NOTIFIER_URL"), json=data.json())
        if response.status_code == 200:
            return 200, {"message": "ok"}
        else: 
            return 200, {"message": "Rate changed but unable to notify"}
    

