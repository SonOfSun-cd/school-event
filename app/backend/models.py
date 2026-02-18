from sqlalchemy import Column, Integer, String
from db import Base



class Registration(Base):
    __tablename__ = "registration"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    surname = Column(String)
