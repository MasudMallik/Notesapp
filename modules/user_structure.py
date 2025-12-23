from pydantic import BaseModel,EmailStr,Field,validator,model_validator
class new_user(BaseModel):
    name:str=Field(...,min_length=2,max_length=30)
    email:EmailStr=Field(...)
    password:str=Field(...,min_length=4,max_length=30)
    confirm_password:str=Field(...)

    @validator("name")
    def check_name(cls,name):
        name=name.replace(" ","")
        if not name.isalpha():
            raise ValueError("name only contains alphabets")
        return name
    @validator("password")
    def check_pass(cls,password):
        check={"upper":0,
                "lower":0,
                "digit":0,
                "special character":0
                }
        for i in password:
            if i.isalpha():
                if i.isupper():
                     check["upper"]+=1
                else:
                    check["lower"]+=1
            elif i.isdigit():
                check["digit"]+=1
            elif not (i.isalpha() and i.isdigit()):
                check["special character"]+=1
        for key,value in check.items():
            if value==0:
                raise ValueError(f"password must contain {key}")
        return password
    @model_validator(mode="after")
    def check_password_confirm(cls,v):
        if v.password!=v.confirm_password:
            raise ValueError("password and confirm password dosent match")
        return v

            
                 