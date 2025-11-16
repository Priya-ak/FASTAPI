from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
URL_DATABASE = 'postgresql://postgres:Priya36@localhost:5432/priya'
engine = create_engine(URL_DATABASE)
sessionmaker = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base= declarative_base()
