from jwt import encode,decode,exceptions,InvalidTokenError,ExpiredSignatureError
import datetime
from dotenv import dotenv_values
keys=dotenv_values(".env")
def create_token(data):
    data["iat"]=datetime.datetime.utcnow()
    data["exp"]=datetime.datetime.utcnow()+datetime.timedelta(minutes=30)
    token=encode(data,keys["SECRET_KEY"],algorithm=keys["ALGORITHM"])
    return token
def decode_token(token):
    try:
        data=decode(token,keys["SECRET_KEY"],algorithms=[keys["ALGORITHM"]])
    except InvalidTokenError:
        return None
    except ExpiredSignatureError:
        return None
    else:
        return data
