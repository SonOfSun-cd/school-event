from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import get_db, Base, engine
import time

for i in range(30):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except Exception as e:
        print("An error occured while building DB: "+e)
        time.sleep(1)

App = FastAPI()

templates = Jinja2Templates(directory="templates")


@App.get('/')
async def root(
    request: Request,
    db: Session = Depends(get_db)
    ):
    print("sending shit")
    return templates.TemplateResponse(request, "index.html")