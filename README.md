# FastAPI Questions Project

This repo contains a small FastAPI app that stores Questions and Choices using SQLAlchemy with a PostgreSQL (or SQLite) backend.

---

## Files included

* `README.md` (this document)
* `requirements.txt`
* `.env.example`
* `.gitignore`
* `database.py` (example)
* `models.py` (example)
* `main.py` (example)

---

## Project structure

```
fastapi_questions/
├─ main.py
├─ models.py
├─ database.py
├─ requirements.txt
├─ README.md
├─ .env.example
└─ .gitignore
```

---

## README.md (user-facing)

# Questions API (FastAPI + SQLAlchemy)

A minimal example FastAPI application that demonstrates how to store `Question` entities and related `Choices` using SQLAlchemy with a foreign key relationship.

### Features

* Create a question with multiple choices
* Read a question and its choices
* Works with PostgreSQL (production) or SQLite (for quick testing)

### Prerequisites

* Python 3.10+
* PostgreSQL (optional) or SQLite

### Setup (Postgres)

1. Create a Python virtualenv and activate it:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
.venv\Scripts\activate     # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update the `DATABASE_URL`:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/dbname
```

4. Start the app:

```bash
uvicorn main:app --reload
```

5. Open docs:

* Swagger UI: `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`

### Setup (SQLite quick test)

If you want to test quickly without Postgres, change the `DATABASE_URL` to:

```
DATABASE_URL=sqlite:///./test.db
```

and, in `database.py`, when using SQLite include `connect_args={"check_same_thread": False}` in `create_engine(...)`.

### API Examples

**Create a question**

```bash
curl -X POST "http://127.0.0.1:8000/questions/" \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is the capital of France?",
    "choices": [
      {"choice_text": "Paris", "is_correct": true},
      {"choice_text": "Berlin", "is_correct": false}
    ]
  }'
```

**Get a question**

```bash
curl "http://127.0.0.1:8000/questions/1"
```

---

## requirements.txt

```
fastapi==0.95.2
uvicorn[standard]==0.23.0
SQLAlchemy==2.0.20
psycopg2-binary==2.9.8
pydantic==1.10.11
```

> If you choose SQLite for local testing you can skip `psycopg2-binary`.

---

## .env.example

```
# Example Database URL for Postgres
DATABASE_URL=postgresql://postgres:password@localhost:5432/priya
```

---

## .gitignore

```
__pycache__/
*.pyc
.env
.venv/
venv/
*.db
```

---

## Example `database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# If using SQLite in local dev, add connect_args
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

---

## Example `models.py`

```python
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Questions(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True, nullable=False)

    choices = relationship("Choices", back_populates="question", cascade="all, delete-orphan")


class Choices(Base):
    __tablename__ = "choices"

    id = Column(Integer, primary_key=True, index=True)
    choice_text = Column(String, index=True, nullable=False)
    is_correct = Column(Boolean, default=False)

    question_id = Column(Integer, ForeignKey("question.id"))
    question = relationship("Questions", back_populates="choices")
```

---

## Example `main.py`

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Questions API")


class ChoiceCreate(BaseModel):
    choice_text: str
    is_correct: bool


class QuestionCreate(BaseModel):
    question_text: str
    choices: List[ChoiceCreate]


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/questions/", status_code=201)
def create_questions(question: QuestionCreate, db: Session = Depends(get_db)):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    db_choices = []
    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id,
        )
        db_choices.append(db_choice)

    db.add_all(db_choices)
    db.commit()
    for c in db_choices:
        db.refresh(c)

    return {
        "question": {"id": db_question.id, "question_text": db_question.question_text},
        "choices": [
            {"id": c.id, "choice_text": c.choice_text, "is_correct": c.is_correct}
            for c in db_choices
        ],
    }


@app.get("/questions/{question_id}")
def read_question(question_id: int, db: Session = Depends(get_db)):
    q = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return {
        "id": q.id,
        "question_text": q.question_text,
        "choices": [
            {"id": c.id, "choice_text": c.choice_text, "is_correct": c.is_correct}
            for c in q.choices
        ],
    }
```

---

## Notes & troubleshooting

* Avoid naming files `sqlalchemy.py`, `fastapi.py`, or `database.py` in ways that shadow libraries.
* If you use Postgres, install `psycopg2-binary` and ensure DB service is running.
* For development, SQLite is easiest to try.
* Use migrations (Alembic) when your schema evolves.

---

## License

MIT
