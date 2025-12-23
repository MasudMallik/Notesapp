from bcrypt import hashpw,checkpw,gensalt

def hash_password(password:str)->bytes:
    hash_pw=hashpw(password.encode("Utf-8"),gensalt(12))
    return hash_pw
def check_password(password:str,hashed:bytes)->bool:
    return checkpw(password.encode("Utf-8"),hashed)