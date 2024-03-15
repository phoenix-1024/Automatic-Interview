from google import generativeai as genai
from dotenv import load_dotenv
import os
'''
given a jobdiscription we will make questions.
and evaluate a candidates response to those questions
'''

load_dotenv()

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

model = genai.GenerativeModel('gemini-pro')

# res = model.generate_content("Hi, how are you?")

# print(res.text)

def make_questions(jd: str):
    res = model.generate_content(f"""
    You are a AI recrutering assistent. Given the following Job discription generate a list of questions that an interviewer should ask the candidate.
    ```
    {jd}
    ```
    

    output format
    ```
    {{
        "1" : " question 1 "
        "2" : " question 2 "
        "3" : " question 3 "
        ...
    }}
    ```
    """)
    print(res.text)

if __name__=="__main__":
    with open("jd.txt",'r') as f:
        jd = f.read()

    make_questions(jd)

