from jwt import encode,decode,exceptions,InvalidTokenError,ExpiredSignatureError
import datetime
import os
def create_token(data):
    data["iat"]=datetime.datetime.utcnow()
    data["exp"]=datetime.datetime.utcnow()+datetime.timedelta(minutes=30)
    token=encode(data,os.getenv("SECRET_KEY"),algorithm=os.getenv("ALGORITHM"))
    return token
def decode_token(token):
    try:
        data=decode(token,os.getenv("SECRET_KEY"),algorithms=[os.getenv("ALGORITHM")])
    except InvalidTokenError:
        return None
    except ExpiredSignatureError:
        return None
    else:
        return data
