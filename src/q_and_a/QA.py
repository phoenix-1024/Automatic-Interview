import re
import ast
from ..gemini.model import model

def judge_answer(q,a,c):
  response = model.generate_content(f"""
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
  return response.text

def refine_question_wrt_criteria(question,criteria):
  response = model.generate_content(f"""
  You are a model student with best grades.
  Answer the following question. try to be consise and presise.
  question:{question}

  do not repeate the input in your response
  """
  )
  # display(Markdown(response.text))
  model_answer = response.text
  judjement = judge_answer(question,model_answer,criteria)
  # display(Markdown(judjement))


  #  The assessment model determines if the student has been unfairly penalized due to omission of requirements (or a lack of clarity) in the original question text

  response = model.generate_content(f'''
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
  # display(Markdown(response.text))
  # is_fair = re.search(r"your question is (fair|unfair)\.",response.text)
  is_fair = re.search(r"student is being (fairly|unfairly) judged\.",response.text)
  if is_fair is not None and is_fair[1].lower() == "unfairly":
      response = model.generate_content(f'''
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
      # display(Markdown(response.text))
      # print(response.text)

      return ast.literal_eval(response.text)
  else:
      return {
        "alternative questions": []
      }