from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel
from typing import List, Optional,Annotated
import models

from database import engine,sessionlocal
from sqlalchemy.orm import session
app = FastAPI
models.Base.metabase.create_all(bind=engine)



class choiceBase(BaseModel):
      choice_text:str
      is_correct:bool
      
      
class QuestionBase(BaseModel):
    question_text:str
    choices: List[choiceBase]
    
def get_db():
    db = sessionlocal()
    try:
         yield db
    finally:
        db.close()
        
        
        
db_dependency = Annotated[session,Depends(get_db)]

@app.post("/questions/")
async def create_questions(question:QuestionBase, db: db_dependency):
   db_question = models.Questions(question_text=question.question_text)
   db.add(db_question)
   db.commit()
   db.refresh(db_question)
   for choice in question.choices:
        db_choice = models.Choices(choice_text=choice.choice_text,is_correct=choice.is_correct,question_id=db_question.id)
        db.add(db_choice)
