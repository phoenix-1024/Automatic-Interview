from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create an SQLite database engine
engine = create_engine('sqlite:///my_database.db')  # "echo=True" enables logging

# Create a base class for our ORM models
Base = declarative_base()

# Define a model class
class Questions(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    job_title = Column(String)
    job_discription = Column(String)
    questions = Column(JSON)

# Create the database tables
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)

# we need to close the db after it is used
def get_db():
    try:
        db = Session()
        yield db
    finally:
        db.close()