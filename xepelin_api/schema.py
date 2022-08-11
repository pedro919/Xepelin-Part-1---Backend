from ninja import Schema

class UserSchema(Schema):
    username: str
    password: str

class MessageSchema(Schema):
    msg: str

class RatesSchema(Schema):
    rates: list

class RateSchema(Schema):
    idOp: int
    tasa: float
    email: str