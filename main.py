from fastapi import FastAPI, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
# from functools import lru_cache
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import time

from src.q_and_a.QA import make_questions_form_jd
from api_input_schema import jd_input, questions_input
from database import get_db, Questions, Job
# from src.speach_to_text.my_s2t import My_Transcriber, websocketStream
from src.speach_to_text.transcribe_streaming import start_transcribing
import os
from google.cloud import speech_v1, speech
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


@app.post("/save_job")
def save_questions(questions: questions_input,db: Session = Depends(get_db)):
    job = Job(
        job_title=questions.job_title,
        job_discription=questions.job_discription)
    db.add(job)
    db.commit()
    db.refresh(job)

    for question in questions.questions:
        db.add(Questions(
            job_id=job.job_id,
            question=question["question"],
            criteria=question["criteria"]
        ))
    
    db.commit()


    return {"status": "success"}

@app.delete("/delete_job/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    # time.sleep(2)
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"status": "success"}


@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job.job_id, 
                    Job.job_title, 
                    Job.job_discription).all()
    
    jobs = [{"job_id": job.job_id, 
             "job_title": job.job_title, 
             "job_discription": job.job_discription} 
             for job in jobs]
    # print(jobs)
    return {"jobs": jobs}

@app.get("/get_all_question")
def get_question_from_db(job_id: int, db: Session = Depends(get_db)):
    questions = db.query(Questions).filter_by(Questions.job_id == job_id).all()
    questions = [{"qid":question.qid,
                  "question":question.question,
                  "criteria": question.criteria} 
                  for question in questions]
    return questions

@app.get("/get_question_by_qid")
def get_question_by_id(job_id: int, qid: int, db: Session = Depends(get_db)):
    question = db.query(Questions)\
        .filter_by(Questions.job_id == job_id & Questions.qid == qid)\
        .one()
    return {"question": question.question, "criteria": question.criteria}



@app.websocket("/speech_to_text")
async def speech_to_text(websocket: WebSocket):
    await websocket.accept()

    print("connected")
    try:

        stream = await start_transcribing(websocket.iter_bytes())
        try:
            async for response in stream:
                # Once the transcription has settled, the first result will contain the
                # is_final result. The other results will be for subsequent portions of
                # the audio.
                text_list = []
                for result in response.results:
                    print(f"Finished: {result.is_final}")
                    print(f"Stability: {result.stability}")
                    alternatives = result.alternatives
                    # The alternatives are ordered from most likely to least.
                    for alternative in alternatives:
                        print(f"Confidence: {alternative.confidence}")
                        print(f"Transcript: {alternative.transcript}")
                        text_list.append(alternative.transcript)

                await websocket.send_text(" ".join(text_list))
        except Exception as e:
            print("Error while processing stream: " + str(e))
            
    except Exception as e:
        print("Error in speech_to_text: " + str(e))
        print("disconnected")
    finally:
        print("disconnected")
        await websocket.close()
        # print("disconnected")

def save_audio(data: bytes,filename: str):
    # Specify the directory to save the audio files
    save_dir = "temp"
    # Generate a unique filename for the audio file
    # filename = generate_filename()
    # Save the audio data to a file
    print(filename)
    with open(os.path.join(save_dir, filename), "ab") as f:
        f.write(data)

def generate_filename():
    # Generate a unique filename for the audio file
    timestamp = int(time.time())
    filename = f"audio_{timestamp}.webm"
    return filename