from jwt import encode,decode,exceptions,InvalidTokenError,ExpiredSignatureError
import datetime
def create_token(data):
    data["iat"]=datetime.datetime.utcnow()
    data["exp"]=datetime.datetime.utcnow()+datetime.timedelta(minutes=30)
    token=encode(data,SECRET_KEY,algorithm="ALGORITHM")
    return token
def decode_token(token):
    try:
        data=decode(token,SECRET_KEY,algorithms=["ALGORITHM"])
    except InvalidTokenError:
        return None
    except ExpiredSignatureError:
        return None
    else:
        return data
