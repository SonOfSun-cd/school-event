from fastapi import FastAPI, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from typing import List
from sqlalchemy.orm import Session
from db import get_db, Base, engine
import os
from fastapi_csrf_protect import CsrfProtect
from starlette.middleware.sessions import SessionMiddleware
import schemas, models
import time

for i in range(30):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except Exception as e:
        print("An error occured while building DB:", str(e))
        time.sleep(1)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="I-LOVE-SCHOOL-1150<3")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@CsrfProtect.load_config
def get_csrf_config():
    return [
        ('secret_key', 'I-LOVE-MIET-TOO'),
        ('csrf_methods', {'POST', 'PUT', 'PATCH', 'DELETE'})
    ]

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
    email: str = Form(...),
    form_token: str = Form(..., alias="csrf_token"),
    db: Session = Depends(get_db),
    csrf_protect: CsrfProtect = Depends()
):
    csrf_protect.validate_csrf(form_token, request)
    try:
        validated_data = schemas.CreateRegistration(name=name, surname=surname, email=email)
    except Exception as e:
        print("A problem occured during validation: " + str(e))
        return RedirectResponse("/registration_form", status_code=303)
    db.add(models.Registration(name=validated_data.name, surname=validated_data.surname, email=validated_data.email))
    db.commit()
    return RedirectResponse("/registration_form", status_code=303)


@app.post('/admin/confirm')
async def fetch_registrations(
    request: Request,
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'G1ad0s3F1')
    if password == ADMIN_PASSWORD:
        registrations = db.query(models.Registration).all()
        return templates.TemplateResponse(request, "admin.html", {"registrations": registrations})
    return {"message": "you are not allowed on this page"}


@app.get('/{path:path}')
async def redirect_to_register(
    path: str,
):
    return RedirectResponse("/registration_form", status_code=303)