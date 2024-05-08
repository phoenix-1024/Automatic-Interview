import re
import ast
import json
from ..llama_3.model import model

async def judge_answer(q,a,c):
  response = await model.generate_content(f"""
  you are a teaching assistent ai who will help students correct their answers.

  for a given question, criteria and student answer tell the student what they did correct and where they have to improve their understanding of the subject.

  input:
  ```
  question: {q}
  criteria: {c}
  student answer: {a}

  output format
  ```
  Correct points:
  1.
  2.
  ...
  Points to improve:
  1.
  2.
  ...

  summery:
  Overall,...
  ```

  end your summary with words of Encouragement like good job! or keep up the effort etc.
  do not repeate the inputs in your response

  """)
  return response

async def refine_question_wrt_criteria(question,criteria):
  response = await model.generate_content(f"""
  You are a model student with best grades.
  Answer the following question. try to be consise and presise.
  question:{question}

  do not repeate the input in your response
  """
  )
  # display(Markdown(response.text))
  model_answer = response
  judjement = judge_answer(question,model_answer,criteria)
  # display(Markdown(judjement))


  #  The assessment model determines if the student has been unfairly penalized due to omission of requirements (or a lack of clarity) in the original question text

  response = await model.generate_content(f'''
  You are a AI teaching assistent.
  for a given question, answer, evaluation criteria and evaluation.
  determine if the student has been unfairly penalized due to omission of requirements (or a lack of clarity) in the original question text.

  question: {question}
  criteria: {criteria}
  answer: {model_answer}
  evaluation: {judjement}

  output format
  ```
  student is being fairly/unfairly judged.

  reason:
  ```
  You need to strictly follow the output format.
  '''
  )

  is_fair = re.search(r"student is being (fairly|unfairly) judged\.",response)
  if is_fair is not None and is_fair[1].lower() == "unfairly":
      response = await model.generate_content(f'''
      you are a teaching assistent AI.
      a question is evaluated based on the grading criteria.
      students are getting unfairly penalized due to omission of requirements (or a lack of clarity) in the original question text.
      given the question and grading criteria, suggest a list of alternative questions such that they better encompass the requirements of the grading criteria.

      strictly do not explicitly add grading criteria into the question.

      question: {question}
      grading criteria: {criteria}

      output json format
      {{"alternative questions": ["question 1","question 2",...]}}
      ''')

      return ast.literal_eval(response)
  else:
      return {
        "alternative questions": []
      }

async def make_questions_form_jd(jd: str):
  questions = await model.generate_content(f"""
  You are a AI recrutering assistent. Given the following Job discription generate a list of questions that an interviewer should ask the candidate.
  Along with questions, provide the grading criteria for each question. ensure that the grading criteria is clear and unambiguous.
  eg. 
  question: What are the components and structure of a molecule of DNA?
  criteria: 1. described the double helix structure of DNA. 2. described the components of DNA. 3. mentioned that the base pairs bind using hydrogen bond.
  ```
  {jd}
  ```
  

  output json format
  ```json
  {{"questions": [
    {{"question": "question 1", "criteria": "criteria 1"}},
    {{"question": "question 2", "criteria": "criteria 2"}},
    ...
  ]}}
  ```
  questions and criteria should be text only.
  """,temperature=0.75)
  # Extract the JSON part from the string
  try:
    json_str = re.search(r'```(?:json\n)?(.*)\n```', questions, re.DOTALL)[1]
  except Exception as e:
    print(questions)
    raise e
  # Parse the JSON string into a Python dictionary
  data = json.loads(json_str)

  # print(data)
  return data


async def judge_interview_answer(qid, question, answer, cretria,**kargs):
  response = await model.generate_content(f"""
  you are an Interviewer ai who will help check a candidate's response. 

  for a given question, criteria and student answer evaluate a candidate's response and give a score from 1 to 5.
  Give a detailed summary of how you evaluated the candidate's answer.

  input:
  ```
  question: {question}
  criteria: {cretria}
  candidates answer: {answer}

  output format
  ```
  {{
      "score": int,
      "summary": str
  }}    
  ```
  
  """)
  try:
    json_str = re.search(r'```(?:json\n)?(.*)\n```', response, re.DOTALL)[1]
  except Exception as e:
    print(response)
    raise e
  # Parse the JSON string into a Python dictionary
  data = json.loads(json_str)
  data['qid'] = qid
  data['question'] = question
  data['answer'] = answer
  data['cretria'] = cretria
  return data
