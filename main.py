from fastapi import FastAPI, Depends, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
# from functools import lru_cache
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
import time

from src.q_and_a.QA import make_questions_form_jd, judge_answer, judge_interview_answer
from api_input_schema import jd_input, questions_input, answers_input
from database import get_db, Questions, Job, Results, Session
# from src.speach_to_text.my_s2t import My_Transcriber, websocketStream
# from src.speach_to_text.transcribe_streaming import start_transcribing
from src.rev_ai.async_streamingclient import RevAiAsyncStreamingClient
from rev_ai import MediaConfig
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# from frontend_router import router

app = FastAPI()
RUNNING = 'RUNNING'
COMPLETED = 'COMPLETED'

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
async def generate_questions(jd: jd_input):

    return await make_questions_form_jd(jd.job_discription)


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
    tables = [Questions, Results]
    for table in tables:
        entries = db.query(table).filter(table.job_id == job_id).all()
        for entri in entries:
            db.delete(entri)
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

    questions = db.query(Questions).filter_by(job_id = job_id).all()
    if questions:
        questions = [{"qid":question.qid,
                    "question":question.question,
                    "job_id": job_id
                    } 
                    for question in questions]
        return {"questions": questions}
    else:
        raise Exception("Job not found")

@app.post("/submit_answers")
async def submit_answers(
        answers: answers_input, 
        b : BackgroundTasks
        ):
    db = Session()
    data_dict_list = answers.answers
    job_id = data_dict_list[0]['job_id']

    questions = db.query(Questions).filter_by(job_id = job_id).all()
    cretrias = {
        question.qid: question.criteria
        for question in questions
    }

    for data_dict in data_dict_list:
        data_dict['cretria'] = cretrias[data_dict['qid']]
    r = Results(job_id = job_id,status = RUNNING)
    db.add(r)
    db.commit()
    # asyncio.create_task(evaluation_task(data_dict_list,r,db))
    b.add_task(evaluation_task,data_dict_list,r,db)
    return {"message": "success"}


@app.get("/get_all_results")
def get_all_results(
    db: Session = Depends(get_db)):
    results = db.query(Results,Job).filter(Results.job_id == Job.job_id).all()
    response = [{
                'rid':result.Results.rid, 
                'job_id':result.Results.job_id, 
                'job_name':result.Job.job_title,
                'status':result.Results.status,
                }
                for result in results]

    return { "results" : response }

@app.get("/get_results_by_id")
def get_result_by_id(
    rid: str,
    db: Session = Depends(get_db)):
    result = db.query(Results).filter_by(rid = rid).first()
    response = {
                'rid':result.rid, 
                'job_id':result.job_id, 
                'result': result.result,
                'status':result.status,
                }
    return response

async def evaluation_task(data_dict_list,r,db):
    
    # Run fun in parallel for each set of inputs
    tasks = [
        judge_interview_answer(
            **data_dict
        ) 
        for data_dict in data_dict_list
    ]
    # Gather the results
    results = await asyncio.gather(*tasks)
    evaluation_result = {}
    evaluation_result['results'] = results
    evaluation_result['avg_score'] = sum([result['score'] for result in results])/len(results)
    # print(evaluation_result)
    
    r.result = evaluation_result
    r.status = COMPLETED
    db.commit()
    db.close()
    print("should be updated now.")


@app.get("/get_question_by_qid")
def get_question_by_id(job_id: int, qid: int, db: Session = Depends(get_db)):
    question = db.query(Questions)\
        .filter_by(Questions.job_id == job_id & Questions.qid == qid)\
        .one()
    return {"question": question.question, "criteria": question.criteria}


async def my_web_socket_itrator(websocket: WebSocket):
    while True:
        try:
            data = await websocket.receive()
            # print(data.keys())
            if 'text' in data.keys():
                if data['text'] == "stop":
                    print("stopping speech to text")
                    break
                else:
                    print("Received text: ", data['text'])
            elif 'bytes' in data.keys():
                print("Received bytes")
                yield data['bytes']
            else:
                print(data.keys())
                print(data['type'])

        except Exception as e:
            print("Error in my_web_socket_itrator: " + str(e),type(e))
            break


@app.websocket("/speech_to_text")
async def speech_to_text(websocket: WebSocket):
    await websocket.accept()
    config = MediaConfig(content_type="audio/opus",layout="interleaved",rate=48000)
    rev_stt = RevAiAsyncStreamingClient(
        access_token=os.environ.get("REVAI_ACCESS_TOKEN"),
        config=config
    )
    print("connected")
    try:
         
        while True:
            signal_data = await websocket.receive()
            # signal_data = await websocket.receive()
            if 'text' in signal_data.keys() and  signal_data['text'] == "start":
                print("starting speech to text")
                stream = await rev_stt.start(my_web_socket_itrator(websocket))
                async for response in stream:
                    
                    text = ''
                    
                    if response['type'] == 'final':
                        for element in response['elements']:
                            text += element['value']
                        print(response)
                        await websocket.send_text(text + " ")
                    
    except Exception as e:
        print("Error in speech_to_text: " + str(e),type(e))
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