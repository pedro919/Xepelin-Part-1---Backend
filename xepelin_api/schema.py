from ninja import Schema

class Message(Schema):
    message: str

class Rates(Schema):
    rates: list

class Rate(Schema):
    idOp: int
    tasa: float
    email: str