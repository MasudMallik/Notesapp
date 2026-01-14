from fastapi import FastAPI,Form,Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,JSONResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from modules.user_structure import new_user
from pydantic import ValidationError
from pymongo import MongoClient
from modules.hash_user_data import hash_password,check_password
from modules.jwt_token import create_token,decode_token
import os

client=MongoClient(os.getenv("mongodb_url"))
users=client["user_details"]


app=FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")
templates=Jinja2Templates(directory="templates")

@app.get("/",response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@app.get("/register",response_class=HTMLResponse)
def register(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})


@app.get("/home",response_class=HTMLResponse)
def home_page(request:Request):
    return templates.TemplateResponse("home.html",{"request":request})

@app.get("/settings",response_class=HTMLResponse)
def settings_page(request:Request):
    token=request.cookies.get("token")
    if not token:
        return RedirectResponse("/",status_code=302)
    else:
        try:
            details=decode_token(token)
        except Exception:
            response=RedirectResponse("/",status_code=302)
            response.delete_cookie("token")
            return response
        else:
            details_from_db=users["user"]
            data=details_from_db.find_one({"email":details["email"]})
            return templates.TemplateResponse("settings.html",{"request":request,"name":data["name"],"email":data["email"],"password":data["password"]}) 
    


@app.get("/add_task",response_class=HTMLResponse)
def add_task(request:Request):
    tok=request.cookies.get("token")
    if not tok:
        return RedirectResponse("/",status_code=302)
    else:
        try:
            data=decode_token(tok)
        except Exception:
            response=RedirectResponse("/",status_code=302)
            response.delete_cookie("token")
            return response
        else:
            name=data.get("name")
            return templates.TemplateResponse("add_task.html",{"request":request,"name":name})


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
                token=create_token({"email":email,"name":data["name"]})
                response=templates.TemplateResponse("home.html",{"request":request,"name":data["name"]})
                response.set_cookie(key="token",value=token,httponly=True)
                return response
            else:
                return templates.TemplateResponse("login.html",{"request":request,"confirm":"password didn't match"})
        else:
            return templates.TemplateResponse("register.html",{"request":request,"confirm":"please create your account"})
        
@app.get("/logout",response_class=HTMLResponse)
async def logout(request:Request):
    response=RedirectResponse("/",status_code=302)
    response.delete_cookie("token")
    return response

###################     ###############
@app.post("/add_task",response_class=HTMLResponse)
def add_task(request:Request,
             title:str=Form(...,description="title of your task"),
             description:str=Form(...,description="description of your task")):
    user=request.cookies.get("token")
    if not user:
        return RedirectResponse("/",status_code=302)
    else:
        try:
            data=decode_token(user)
        except Exception:
            response=RedirectResponse("/",status_code=302)
            response.delete_cookie("token")
            return response
        else:
            name=data.get("name")
            users=client["user_added_tasks"]
            individual_user=users[name]
            individual_user.insert_one({"Title": title,"Description":description})
            

            return templates.TemplateResponse("home.html",{"request":request})
    print(title,description)
    return templates.TemplateResponse("home.html",{"request":request})
