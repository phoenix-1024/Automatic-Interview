from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache


from src.q_and_a.QA import make_questions_form_jd
from api_input_schema import jd_input, questions_input
from database import get_db, Questions

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate_questions")
def generate_questions(jd: jd_input):

    return make_questions_form_jd(jd.job_discription)


@app.post("/save_questions")
def save_questions(questions: questions_input,db = Depends(get_db)):
    db.add(Questions(
        job_title=questions.job_title,
        job_discription=questions.job_discription,
        questions=questions.questions))
    db.commit()
    return {"status": "success"}

@app.get("/jobs")
def get_jobs(db = Depends(get_db)):
    jobs = db.query(Questions).all()
    jobs = [{"job_title": job.job_title, "job_discription": job.job_discription} for job in jobs]
    # print(jobs)
    return {"jobs": jobs}