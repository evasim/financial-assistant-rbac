from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_checked

app = FastAPI()

class Question(BaseModel):
    question: str
    role: str

# to show that server is alive 
@app.get("/")
def home():
    return{"message": "Financial assistant is running"}

# users ask a question then it grabs from multi agent  
@app.post("/ask")
def ask(q: Question):
    answer = run_checked(q.question, q.role)
    return {"answer": answer}
