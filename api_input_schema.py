from pydantic import BaseModel


class jd_input(BaseModel):
    job_discription: str

class questions_input(BaseModel):
    job_title: str
    job_discription: str
    questions: list

class answers_input(BaseModel):
    answers : list
    