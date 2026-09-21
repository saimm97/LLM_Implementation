import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()



def get_sqlalchemy_session():
  url = URL.create(
    drivername=os.environ.get("DB_DRIVER"),
    username=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    database=os.environ.get("DB_NAME"),
    port=os.environ.get("DB_PORT")
  )

  engine = create_engine(url, poolclass=NullPool)
  Session = sessionmaker(bind=engine)
  session = Session()

  return session