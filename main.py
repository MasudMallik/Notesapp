from fastapi import FastAPI,Form,Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,JSONResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from modules.user_structure import new_user
from pydantic import ValidationError
from pymongo import MongoClient
from dotenv import dotenv_values
from modules.hash_user_data import hash_password,check_password

config=dotenv_values(".env")
client=MongoClient(config["mongodb_url"])
users=client["user_details"]


app=FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")
templates=Jinja2Templates(directory="templates")

@app.get("/",response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@app.get("/register",response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})


@app.post("/register",response_class=HTMLResponse)
async def register(request:Request,
          name:str=Form(...,description="name"),
          email:str=Form(...,description="abc@gmail.com"),
          password:str=Form(...,description="atleast one lower,upper and special characet should be there"),
          confirm_password:str=Form(...)
          ):
    if name and email and password and confirm_password:
        try:
            user=new_user(
                name=name,
                email=email,
                password=password,
                confirm_password=confirm_password
            )
        except ValidationError as e:
            t = []
            for err in e.errors():
                loc = err.get("loc", [])
                if "name" in loc:
                    t.append("Name must contain alphabets only")
                elif "email" in loc:
                    t.append("Give correct email")
                elif "password" in loc:
                    t.append("Give strong password")

            return templates.TemplateResponse(
                "register.html",
                {"request": request, "confirm": t}
            )
        new_hashed_password=hash_password(password)
        print(password,new_hashed_password)
        collections=users["user"]
        collections.insert_one({"name":name,"email":email,"password":new_hashed_password})
        return templates.TemplateResponse("login.html",{"request":request,"confirm":"user succesfully created"})
    
@app.post("/",response_class=HTMLResponse)
def login(request:Request,
          email:str=Form(...,description="enter your email"),
          password:str=Form(...,description="enter your password")):
    if email and password:
        data=users["user"].find_one({"email":email})
        if data:
            password_to_check=data["password"]
            if check_password(password=password,hashed=password_to_check):
                return templates.TemplateResponse("login.html",{"request":request,"confirm":"login succesfull"})
        else:
            return templates.TemplateResponse("register.html",{"request":request,"confirm":"please create your account"})