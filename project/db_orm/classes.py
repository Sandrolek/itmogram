from sqlalchemy import Column, String, Date, Integer, Numeric, ForeignKey

from .base import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    email = Column(String)

    def __init__(self, name, email, password):
        self.name = name
        self.password = password
        self.email = email


class Rooms(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    owner_id = ForeignKey("users.id")

    def __init__(self, name, code, owner_id):
        self.name = name
        self.code = code
        self.owner_id = owner_id


class Messages(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    email = Column(String)

    def __init__(self, name, email, password):
        self.name = name
        self.password = password
        self.email = email