from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from typing import List
from sqlalchemy.orm import Session
from .db import get_db, Base, engine
import os
from fastapi_csrf_protect import CsrfProtect
from starlette.middleware.sessions import SessionMiddleware
from . import schemas, models
import time
import datetime

for i in range(30):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except Exception as e:
        print("An error occured while building DB:", str(e))
        time.sleep(1)


SECRET_KEY = os.environ.get('SECRET_KEY', 'MySecretKeyForSessions')
CSRF_SECRET = os.environ.get('CSRF_SECRET', 'AnotherSecretKeyForCSRF')
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
#app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="backend/templates")

@CsrfProtect.load_config
def get_csrf_config():
    return [
        ('secret_key', CSRF_SECRET),
        ('csrf_methods', {'POST', 'PUT', 'PATCH', 'DELETE'})
    ]

@app.get('/index')
async def index(
    request: Request,
    db: Session = Depends(get_db)
    ):
    return templates.TemplateResponse(request, "index.html")


@app.get('/admin')
async def admin(
    request: Request,
    db: Session = Depends(get_db)
    ):
    return templates.TemplateResponse(request, "admin_access.html")

@app.get('/registration_form')
async def form(
    request: Request,
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends()
    ):
    token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(request, "form.html", {"token": token})
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@app.post('/registration_form/validate')
async def form_validate(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(...),
    form_token: str = Form(..., alias="csrf_token"),
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends()
):
    csrf_protect.validate_csrf(form_token, request)
    if not phone_number and not email:
        print("A problem occured during validation: no contact info provided")
        return RedirectResponse("/registration_form", status_code=303)
    try:
        validated_data = schemas.CreateRegistration(name=name, email=email, phone_number=phone_number)
    except Exception as e:
        print("A problem occured during validation: " + str(e))
        return RedirectResponse("/registration_form", status_code=303)
    db.add(models.Registration(name=validated_data.name, email=validated_data.email, phone_number=validated_data.phone_number, datetime=datetime.datetime.now()))
    db.commit()
    return RedirectResponse("/index", status_code=303)


@app.post('/admin/confirm')
async def fetch_registrations(
    request: Request,
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'SuperSecretAdminPass')
    if password == ADMIN_PASSWORD:
        registrations = db.query(models.Registration).all()
        return templates.TemplateResponse(request, "admin.html", {"registrations": registrations})
    return {"message": "you are not allowed on this page"}



@app.post('/admin/delete/{registration_id}')
async def delete_registration(
    request: Request,
    registration_id: int,
    db: Session = Depends(get_db),
):
    registration = db.query(models.Registration).filter(models.Registration.id == registration_id).first()
    if registration:
        db.delete(registration)
        db.commit()
    return RedirectResponse("/admin/confirm", status_code=303)

@app.get('/{path:path}')
async def redirect_to_index(
    path: str,
):
    return RedirectResponse("/index", status_code=303)