from sqlalchemy import Boolean,Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from database import engine, Base
class Questions(Base):
    
    
    
    __tablename__ = 'question'
    id = Column(Integer,primary_key=True,index=True)
    question_text = Column(String,index=True)
    
    
class Choices(Base):
    
    
     __tablename__='choices'
     
    
     id =Column(Integer,primary_key=True,index=True)
     choice_text = Column(String, index=True)
     is_correct = Column(Boolean,default=False)
     question_id = Column(Integer,ForeignKey("question.id"))
