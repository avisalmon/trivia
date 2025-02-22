from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class Question:
    id: str
    text: str
    correct_answer: str
    options: List[str]
    category: str
    difficulty: int  # 1-10
    points: int
    created_at: datetime = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "correct_answer": self.correct_answer,
            "options": self.options,
            "category": self.category,
            "difficulty": self.difficulty,
            "points": self.points,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data) 