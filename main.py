from fastapi import FastAPI,Form,Request,BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from modules.user_structure import new_user
from pydantic import ValidationError
from pymongo import MongoClient
from modules.hash_user_data import hash_password,check_password
from modules.jwt_token import create_token,decode_token
import os
from dotenv import load_dotenv
from bson import ObjectId
from google import genai
load_dotenv()
def check_password_streanth(password:str):
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

db=MongoClient(os.getenv("mongodb_url"))
users=db["user_details"]


app=FastAPI(title="Note storing app",description="you can store notes and summaries it using gemini-api")
app.mount("/static",StaticFiles(directory="static"),name="static")
templates=Jinja2Templates(directory="templates")

@app.get("/",response_class=HTMLResponse)
async def login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@app.get("/register",response_class=HTMLResponse)
async def register(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})


@app.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse("/", status_code=302)
    try:
        details = decode_token(token)
    except Exception:
        response = RedirectResponse("/", status_code=302)
        response.delete_cookie("token")
        return response
    else:
        name = details.get("name")
        users = db["user_added_tasks"]
        individual_user = users[name]
        data = list(individual_user.find())  
        return templates.TemplateResponse("home.html", {"request": request, "name": name, "data": data})


@app.get("/settings",response_class=HTMLResponse)
async def settings_page(request:Request):
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
            return templates.TemplateResponse("settings.html",{"request":request,"data_id":data["_id"],"name":data["name"],"email":data["email"]}) 
    


@app.get("/add_task",response_class=HTMLResponse)
async def add_task(request:Request):
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

@app.get("/show_task",response_class=HTMLResponse)
async def show_task(request:Request):
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
            return templates.TemplateResponse("show_task.html",{"request":request})

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
                    t.append("password must containatleast one lower,upper and special characet should be there")

            return templates.TemplateResponse(
                "register.html",
                {"request": request, "confirm": t}
            )
        new_hashed_password=hash_password(password)
        check=users["user"]
        if check.find_one({"email":email}):
            return templates.TemplateResponse("login.html",{"request":request,"confirm":"you already have an account"})
        collections=users["user"]
        collections.insert_one({"name":name,"email":email,"password":new_hashed_password})
        return templates.TemplateResponse("login.html",{"request":request,"confirm":"user succesfully created"})
    
@app.post("/",response_class=HTMLResponse)
async def login(request:Request,
          email:str=Form(...,description="enter your email"),
          password:str=Form(...,description="enter your password")):
    if email and password:
        data=users["user"].find_one({"email":email})
        if data:
            password_to_check=data["password"]
            if check_password(password=password,hashed=password_to_check):
                token=create_token({"email":email,"name":data["name"]})
                users_=db["user_added_tasks"]
                name=data["name"]
                individual_user=users_[name]
                notes=list(individual_user.find())
            
                response=templates.TemplateResponse("home.html",{"request":request,"name":data["name"],"data":notes})
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

@app.post("/add_task",response_class=HTMLResponse)
async def add_task(request:Request,
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
            users=db["user_added_tasks"]
            individual_user=users[name]
            individual_user.insert_one({"Title": title,"Description":description})
            data=list(individual_user.find())
            return templates.TemplateResponse("home.html",{"request":request,"name":name,"data":data})

##
@app.get("/view_task/{task_id}",response_class=HTMLResponse)
async def show_task(request:Request,task_id):
    token=request.cookies.get("token")
    if not token:
        response=RedirectResponse("/",status_code=302)
        response.delete_cookie()
        return response
    else:
        try:
            data=decode_token(token=token)
        except Exception as e:
            response=RedirectResponse("/",status_code=302)
            response.delete_cookie()
            return response
        else:
            usersdet=db["user_added_tasks"]
            name=data.get("name")
            ind_usr=usersdet[name]
            notes=ind_usr.find_one({"_id":ObjectId(task_id)})
            return templates.TemplateResponse("show_task.html",{"request":request,"notes":notes,"name":name})
        
@app.get("/edit_task/{task_id}")
async def edit_data(request:Request,task_id):
    token=request.cookies.get("token")
    if not token:
        response=RedirectResponse("/",status_code=302)
        response.delete_cookie()
        return response
    else:
        try:
            data=decode_token(token=token)
        except Exception as e:
            response=RedirectResponse("/",status_code=302)
            response.delete_cookie()
            return response
        else:
            usersdet=db["user_added_tasks"]
            name=data.get("name")
            ind_usr=usersdet[name]
            notes=ind_usr.find_one({"_id":ObjectId(task_id)})
            return templates.TemplateResponse("edit_task.html",{"request":request,"notes":notes,"name":name})
        
@app.post("/update_task/{task_id}",response_class=HTMLResponse)
async def update_note(request:Request,task_id,title:str=Form(...,description="title of your task"),
             description:str=Form(...,description="description of your task")):
    token=request.cookies.get("token")
    if not token:
        response=RedirectResponse("/",status_code=302)
        response.delete_cookie()
        return response
    else:
        try:
            data=decode_token(token=token)
        except Exception as e:
            response=RedirectResponse("/",status_code=302)
            response.delete_cookie()
            return response
        else:
            usersdet=db["user_added_tasks"]
            name=data.get("name")
            ind_usr=usersdet[name]
            n=ind_usr.update_one({"_id": ObjectId(task_id)},
        {"$set": {"Title": title, "Description": description}}
)
        data = list(ind_usr.find())  
        return templates.TemplateResponse("home.html", {"request": request, "name": name, "data": data})
    
@app.post("/delete_task/{task_id}",response_class=HTMLResponse)
async def delete_task(request:Request,task_id):
    token=request.cookies.get("token")
    if not token:
        response=RedirectResponse("/",status_code=302)
        response.delete_cookie()
        return response
    else:
        try:
            data=decode_token(token=token)
        except Exception as e:
            response=RedirectResponse("/",status_code=302)
            response.delete_cookie()
            return response
        else:
            usersdet=db["user_added_tasks"]
            name=data.get("name")
            ind_usr=usersdet[name]
            notes=ind_usr.delete_one({"_id":ObjectId(task_id)})
            return RedirectResponse("/home",status_code=302)


@app.get("/summary_task/{task_id}",response_class=HTMLResponse)
async def summary(request:Request,task_id):
    token=request.cookies.get("token")
    if not token:
        response=RedirectResponse("/",status_code=302)
        response.delete_cookie()
        return response
    else:
        try:
            data=decode_token(token=token)
        except Exception as e:
            response=RedirectResponse("/",status_code=302)
            response.delete_cookie()
            return response
        else:
            usersdet=db["user_added_tasks"]
            name=data.get("name")
            ind_usr=usersdet[name]
            notes=ind_usr.find_one({"_id":ObjectId(task_id)})
            apikey=os.getenv("apikey_gemini")
            ai=genai.Client(api_key=apikey)
            title=notes["Title"]
            des=notes["Description"]
            response = ai.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"I am providing you the topics and notes:description. generate summary of this datas in less than 150 words the details are 'title of the topic':{title} and the 'description':{des}",
            )
            return templates.TemplateResponse("summary.html",{"request":request,"name":name,"title":title,"description":des,"summary":response.text})
@app.post("/change_password/{email}", response_class=HTMLResponse)
async def change_password(
    request: Request,
    email: str,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    

    users = db["user_details"]
    ind = users["user"]
    data=ind.find_one({"email":email})

    user = ind.find_one({"email": email})
    if not user:
        return templates.TemplateResponse(
            "settings.html",
            {"request": request, "error": "User not found","data_id":data["_id"],"name":data["name"],"email":data["email"]}
        )

    stored_hash = user["password"]

    if not check_password(password=current_password,hashed=stored_hash):
        return templates.TemplateResponse(
            "settings.html",
            {"request": request, "error": "Incorrect current password","data_id":data["_id"],"name":data["name"],"email":data["email"]}
        )

    if new_password != confirm_password:
        return templates.TemplateResponse(
            "settings.html",
            {"request": request, "error": "Passwords do not match","data_id":data["_id"],"name":data["name"],"email":data["email"]}
        )
    try:
        check_password_streanth(new_password)
    except ValueError as e:
        return templates.TemplateResponse(
            "settings.html",
            {"request": request, "error": str(e)}
        )
    else:
        new_hash = hash_password(new_password)
        ind.update_one({"email": email}, {"$set": {"password": new_hash}})
        return templates.TemplateResponse("settings.html",{"request":request,"error":"password succesfully changed","data_id":data["_id"],"name":data["name"],"email":data["email"]})
