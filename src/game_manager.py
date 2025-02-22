from .models.player import Player
from .question_generator import QuestionGenerator
from .database import Database
from .game.achievements_manager import AchievementsManager
import asyncio
import logging

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self):
        self.db = Database()
        self.question_generator = QuestionGenerator()
        self.achievements_manager = AchievementsManager()
        self.player = None
        self.current_question = None
        self.performance_window = []  # Track recent performance
        self.max_performance_window = 10  # Number of questions to consider
        self.used_questions = set()  # Track used questions to prevent repeats
        
    async def cleanup(self):
        """Cleanup resources before shutdown"""
        try:
            # Save current player state
            if self.player:
                self.db.save_player(self.player)
            
            # Clear any pending questions
            self.current_question = None
            self.performance_window.clear()
            self.used_questions.clear()
            
            logger.info("Game manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during game manager cleanup: {e}")
    
    def start_game(self, username: str):
        self.player = self.db.get_player(username)
        if not self.player:
            self.player = Player(username=username)
            self.db.save_player(self.player)
        # Initialize player stats if not present
        if not hasattr(self.player, 'stats'):
            self.player.stats = {
                "correct_answers": 0,
                "wrong_answers": 0,
                "fast_correct_answers": 0,
                "hints_used": 0,
                "categories_played": set()
            }
        # Start continuous pre-fetching in background
        difficulty = self.calculate_difficulty()
        self.question_generator.start_background_prefetch(difficulty)
        logger.info("Started continuous question pre-fetching")
    
    async def get_next_question(self):
        difficulty = self.calculate_difficulty()
        question, explanation = await self.question_generator.get_next_question(difficulty)
        self.current_question = question
        return question, explanation
    
    def calculate_difficulty(self) -> int:
        # Start with base difficulty from player level
        base_difficulty = min(10, max(1, self.player.level))
        
        # Adjust based on recent performance
        if len(self.performance_window) > 0:
            # Calculate success rate from recent questions
            correct_count = sum(1 for result in self.performance_window if result['correct'])
            success_rate = correct_count / len(self.performance_window)
            
            # Calculate average speed bonus
            avg_time_bonus = sum(result['time_bonus'] for result in self.performance_window) / len(self.performance_window)
            
            # Adjust difficulty based on performance
            if success_rate > 0.8 and avg_time_bonus > 10:
                # Player is doing very well with fast answers
                base_difficulty = min(10, base_difficulty + 2)
            elif success_rate > 0.7:
                # Player is doing well
                base_difficulty = min(10, base_difficulty + 1)
            elif success_rate < 0.4:
                # Player is struggling
                base_difficulty = max(1, base_difficulty - 1)
        
        return base_difficulty
    
    def handle_correct_answer(self, time_bonus: int = 0) -> int:
        # Calculate points with time bonus and streak multiplier
        base_points = self.current_question.points
        time_points = time_bonus * 2  # 2 points per second remaining
        total_points = base_points + time_points
        
        # Apply streak multiplier (10% bonus per streak, up to 100%)
        earned_points = self.player.add_points(total_points)
        
        # Update player stats
        self.player.stats["correct_answers"] += 1
        if time_bonus > 10:
            self.player.stats["fast_correct_answers"] = (
                self.player.stats.get("fast_correct_answers", 0) + 1
            )
        
        self.player.update_streak(True)
        
        # Update performance window
        self.performance_window.append({
            'correct': True,
            'time_bonus': time_bonus,
            'difficulty': self.current_question.difficulty
        })
        if len(self.performance_window) > self.max_performance_window:
            self.performance_window.pop(0)
        
        # Level up every 500 points
        if self.player.points >= (self.player.level * 500):
            self.player.level += 1
        
        # Save progress
        self.db.save_player(self.player)
        
        return earned_points
    
    def handle_wrong_answer(self):
        self.player.stats["wrong_answers"] += 1
        self.player.update_streak(False)
        
        # Update performance window
        self.performance_window.append({
            'correct': False,
            'time_bonus': 0,
            'difficulty': self.current_question.difficulty
        })
        if len(self.performance_window) > self.max_performance_window:
            self.performance_window.pop(0)
        
        # Add question to history
        self.player.question_history.append(self.current_question.id)
        
        self.db.save_player(self.player)
    
    def get_hint(self, question) -> str:
        """Generate a hint for the current question"""
        correct_answer = question.correct_answer.lower()
        
        # Create a masked version of the answer
        if len(correct_answer) <= 4:
            # For short answers, show only the first letter
            hint = correct_answer[0] + "*" * (len(correct_answer) - 1)
        else:
            # For longer answers, show first and last letters
            hint = correct_answer[0] + "*" * (len(correct_answer) - 2) + correct_answer[-1]
        
        return f"The answer starts with '{correct_answer[0]}' and has {len(correct_answer)} letters"
    
    def check_achievements(self, time_remaining: float = None) -> list:
        """Check and award any new achievements"""
        return self.achievements_manager.check_achievements(
            self.player,
            time_remaining
        ) 