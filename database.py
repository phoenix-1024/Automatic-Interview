from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create an SQLite database engine
engine = create_engine('sqlite:///my_database.db')  # "echo=True" enables logging

# Create a base class for our ORM models
Base = declarative_base()

# Define a model class
class Job(Base):
    __tablename__ = 'job'

    job_id = Column(Integer, primary_key=True)
    job_title = Column(String)
    job_discription = Column(String)
    questions = Column(JSON)

class Questions(Base):
    __tablename__ = "questions"

    qid = Column(Integer, primary_key=True)
    # setting ondelete cascade to delete all questions if a job is deleted
    job_id = ForeignKey(Job.job_id, ondelete="CASCADE")
    question = Column(String)
    criteria = Column(String)


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