from ninja import NinjaAPI
from xepelin_api.gspread import download_gspread, upload_datafrae_to_gspread
from xepelin_api.schema import MessageSchema, RatesSchema, RateSchema, UserSchema
from xepelin_api.models import User
from datetime import datetime, timedelta
import pandas as pd
import requests
import os
import jwt
from django.contrib.auth.hashers import check_password
from xepelin_api.auth_bearer import AuthBearer, InvalidToken
from dotenv import load_dotenv

load_dotenv()

api = NinjaAPI()

@api.post("/authenticate", response={200: MessageSchema, 401: MessageSchema})
def authenticate_endpoint(request, user:UserSchema):
    try:
        db_user = User.objects.get(username=user.username)
    
    except User.DoesNotExist as e:
        authentication_error = MessageSchema(msg="Invalid username or password")
        return 401, authentication_error
    
    else:
        authenticated = check_password(user.password, db_user.password)
        if authenticated:
            enconded_jwt = jwt.encode({"username": user.username, "exp": datetime.now() + timedelta(hours=1)}, os.environ.get("SECRET"), algorithm=os.environ.get("ALGORITHM"))
            authenticated_message = MessageSchema(msg=enconded_jwt)
            return 200, authenticated_message
        authentication_error = MessageSchema(msg="Invalid username or password")
        return 401, authentication_error


@api.get("/gspread_info", response={200: RatesSchema, 500: MessageSchema}, auth=AuthBearer())
def get_gspread_rates_endpoint(request):
    try:
        rates_list = download_gspread()
    except Exception as e:
        return 500, MessageSchema(msg=f"Ups... The following error ocurred: {e}")
    else:
        return 200, RatesSchema(rates=rates_list)


@api.post("/update_gspread_rate",  response={200: MessageSchema, 500: MessageSchema}, auth=AuthBearer())
def update_gspread_rate_endpoint(request, data: RateSchema):
    try:
        rates_list = download_gspread()
        df = pd.DataFrame(rates_list)
        row_index = df[df["idOp"] == data.idOp].index.values.astype(int)[0]
        df.iloc[[row_index], [1]] = data.tasa
        upload_datafrae_to_gspread(df)

    except Exception as e:
        return 500, MessageSchema(msg=f"Ups... The following error ocurred: {e}")

    else:
        response = requests.post(os.environ.get("NOTIFIER_URL"), json=data.json(), headers={'Content-type': 'application/json'})
        if response.status_code == 200:
            return 200, MessageSchema(msg="ok")
        else: 
            return 200, MessageSchema(msg="Rate changed but unable to notify")


@api.post("/update_gspread_email",  response={200: MessageSchema, 500: MessageSchema}, auth=AuthBearer())
def update_gspread_email_endpoint(request, data: RateSchema):
    try:
        rates_list = download_gspread()
        df = pd.DataFrame(rates_list)
        row_index = df[df["idOp"] == data.idOp].index.values.astype(int)[0]
        df.iloc[[row_index], [2]] = data.email
        upload_datafrae_to_gspread(df)

    except Exception as e:
        return 500, MessageSchema(msg=f"Ups... The following error ocurred: {e}")

    else:
        return 200, MessageSchema(msg="ok")
    

@api.exception_handler(InvalidToken)
def on_invalid_token(request, exc):
    return api.create_response(request, {"detail": "Invalid token supplied"}, status=401)