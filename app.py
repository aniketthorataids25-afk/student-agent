from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List
from pathlib import Path
import importlib.util
import statistics

app = FastAPI(title="Study Companion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SubjectScores(BaseModel):
    scores: List[float] = Field(min_length=1)

class StudentData(BaseModel):
    subjects: Dict[str, SubjectScores]

def status_for(scores):
    avg = statistics.mean(scores)
    recent = scores[-1]
    if recent < 60 or (len(scores) >= 3 and recent < scores[-3] - 10):
        return "AT RISK"
    if recent < 75 or avg < 70:
        return "WATCH"
    return "ON TRACK"

def analyze(data: StudentData):
    result = {}
    for subject, payload in data.subjects.items():
        scores = payload.scores
        avg = round(statistics.mean(scores), 1)
        recent = scores[-1]
        first = scores[0]
        trend = round(recent - first, 1)
        status = status_for(scores)
        if status == "AT RISK":
            minutes = 45
            priority = 1
        elif status == "WATCH":
            minutes = 30
            priority = 2
        else:
            minutes = 15
            priority = 3
        result[subject] = {
            "scores": scores,
            "average": avg,
            "recent": recent,
            "trend": trend,
            "status": status,
            "minutes": minutes,
            "priority": priority,
        }

    plan = sorted(result.items(), key=lambda x: (x[1]["priority"], -x[1]["minutes"]))
    study_plan = [
        {"subject": subject, "minutes": info["minutes"], "reason": info["status"]}
        for subject, info in plan
    ]
    overall = round(statistics.mean([v["recent"] for v in result.values()]), 1) if result else 0
    return {"subjects": result, "study_plan": study_plan, "overall": overall}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/demo")
def demo():
    data = StudentData(subjects={
        "Mathematics": SubjectScores(scores=[82, 74, 65, 58]),
        "Physics": SubjectScores(scores=[88, 90, 87, 91]),
        "History": SubjectScores(scores=[70, 76, 72, 73]),
        "Computer Science": SubjectScores(scores=[78, 81, 84, 86]),
    })
    return analyze(data)

@app.post("/api/analyze")
def analyze_student(data: StudentData):
    return analyze(data)
