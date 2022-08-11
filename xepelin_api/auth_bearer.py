import jwt
import os
from ninja.security import HttpBearer

class InvalidToken(Exception):
    pass

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            jwt.decode(token, os.environ.get("SECRET"), algorithms=os.getenv("ALGORITHM"))
        
        except jwt.ExpiredSignatureError:
            raise InvalidToken
        
        except jwt.InvalidSignatureError:
            raise InvalidToken

        except Exception as e:
            raise InvalidToken
        
        else:
            return token