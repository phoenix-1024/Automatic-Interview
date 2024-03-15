from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.q_and_a.QA import make_questions_form_jd
from api_input_schema import jd_input

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate_questions")
def generate_questions(jd: jd_input):
    return make_questions_form_jd(jd.job_discription)
    