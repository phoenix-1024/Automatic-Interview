from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.q_and_a.QA import make_questions_form_jd
from api_input_schema import jd_input, questions_input
from database import get_db, Questions
# from frontend_router import router

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

# app.include_router(router)
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def read_root():
    # Serve your index.html file
    return FileResponse("frontend/index.html")


# @router.get("/generate_questions")
# async def read_page1():
#     return FileResponse("frontend/generate_questions.html")


# @router.get("/select_jobs")
# async def read_page2():
#     return FileResponse("frontend/select_jobs.html")


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
