from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
import json

with open("db_conf.json") as conf_file:
    config = json.load(conf_file)

host =      config["host"]
database =  config["database"]
user =      config["user"]
password =  config["password"]
port =      config["port"]

url = URL.create(
    drivername="postgresql",
    username=user,
    host=host,
    database=database,
    password=password,
    port=port
)

engine = create_engine(url)
# use session_factory() to get a new Session
_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()

