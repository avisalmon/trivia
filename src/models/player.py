from dataclasses import dataclass
from typing import List, Dict, Union, Set
from datetime import datetime


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    unlocked_at: datetime = None


@dataclass
class Player:
    username: str
    level: int = 1
    experience: int = 0
    points: int = 0
    streak: int = 0
    achievements: List[Achievement] = None
    question_history: List[str] = None  # List of question IDs
    stats: Dict[str, Union[int, Set[str]]] = None
    
    def __post_init__(self):
        self.achievements = self.achievements or []
        self.question_history = self.question_history or []
        self.stats = self.stats or {
            "correct_answers": 0,
            "wrong_answers": 0,
            "hints_used": 0,
            "challenges_completed": 0,
            "categories_played": set()
        }
        # Ensure categories_played is a set
        if "categories_played" in self.stats and not isinstance(self.stats["categories_played"], set):
            self.stats["categories_played"] = set(self.stats["categories_played"])
    
    def add_points(self, points: int, streak_multiplier: bool = True) -> int:
        multiplier = min(2.0, 1 + (self.streak * 0.1)) if streak_multiplier else 1
        earned_points = int(points * multiplier)
        self.points += earned_points
        return earned_points
    
    def update_streak(self, correct: bool):
        if correct:
            self.streak += 1
        else:
            self.streak = 0
    
    def to_dict(self) -> dict:
        """Convert player data to a JSON-serializable dictionary"""
        return {
            "username": self.username,
            "level": self.level,
            "experience": self.experience,
            "points": self.points,
            "streak": self.streak,
            "achievements": [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "unlocked_at": a.unlocked_at.isoformat() if a.unlocked_at else None
                }
                for a in self.achievements
            ],
            "question_history": self.question_history,
            "stats": {
                k: list(v) if isinstance(v, set) else v
                for k, v in self.stats.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Create a Player instance from a dictionary"""
        # Convert achievement dictionaries to Achievement objects
        achievements = []
        for ach_data in data.get("achievements", []):
            achievement = Achievement(
                id=ach_data["id"],
                name=ach_data["name"],
                description=ach_data["description"]
            )
            if ach_data.get("unlocked_at"):
                achievement.unlocked_at = datetime.fromisoformat(ach_data["unlocked_at"])
            achievements.append(achievement)
        
        # Convert categories list back to a set
        stats = data.get("stats", {}).copy()
        if "categories_played" in stats and isinstance(stats["categories_played"], list):
            stats["categories_played"] = set(stats["categories_played"])
        
        return cls(
            username=data["username"],
            level=data["level"],
            experience=data["experience"],
            points=data["points"],
            streak=data["streak"],
            achievements=achievements,
            question_history=data["question_history"],
            stats=stats
        ) 