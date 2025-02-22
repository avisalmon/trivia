from typing import List
from datetime import datetime
from src.models.player import Achievement, Player
from src.question_generator import QuestionGenerator


class AchievementsManager:
    def __init__(self):
        self.question_generator = QuestionGenerator()
        self.achievements = {
            "first_correct": Achievement(
                id="first_correct",
                name="First Steps",
                description="Answer your first question correctly"
            ),
            "perfect_streak_5": Achievement(
                id="perfect_streak_5",
                name="Hot Streak",
                description="Get 5 correct answers in a row"
            ),
            "perfect_streak_10": Achievement(
                id="perfect_streak_10",
                name="Unstoppable",
                description="Get 10 correct answers in a row"
            ),
            "points_100": Achievement(
                id="points_100",
                name="Point Collector",
                description="Earn 100 points"
            ),
            "points_500": Achievement(
                id="points_500",
                name="Point Master",
                description="Earn 500 points"
            ),
            "points_1000": Achievement(
                id="points_1000",
                name="Point Champion",
                description="Earn 1000 points"
            ),
            "level_5": Achievement(
                id="level_5",
                name="Rising Star",
                description="Reach level 5"
            ),
            "level_10": Achievement(
                id="level_10",
                name="Knowledge Master",
                description="Reach level 10"
            ),
            "all_categories": Achievement(
                id="all_categories",
                name="Jack of All Trades",
                description="Answer questions from all categories"
            ),
            "speed_demon": Achievement(
                id="speed_demon",
                name="Speed Demon",
                description="Answer 5 questions correctly with more than 10 seconds remaining"
            )
        }
    
    def check_achievements(self, player: Player, time_remaining: float = None) -> List[Achievement]:
        """Check and award new achievements based on player's current state"""
        new_achievements = []
        
        # Get existing achievement IDs
        unlocked_ids = {a.id for a in player.achievements}
        
        # Initialize stats if not present
        if not hasattr(player, 'stats'):
            player.stats = {
                "correct_answers": 0,
                "wrong_answers": 0,
                "fast_correct_answers": 0,
                "hints_used": 0,
                "categories_played": set()
            }
        
        # Check each achievement condition
        if player.stats["correct_answers"] >= 1:
            new_achievements.extend(self._award_if_not_unlocked(
                player, "first_correct", unlocked_ids))
        
        if player.streak >= 5:
            new_achievements.extend(self._award_if_not_unlocked(
                player, "perfect_streak_5", unlocked_ids))
        
        if player.streak >= 10:
            new_achievements.extend(self._award_if_not_unlocked(
                player, "perfect_streak_10", unlocked_ids))
        
        if player.points >= 100:
            new_achievements.extend(self._award_if_not_unlocked(
                player, "points_100", unlocked_ids))
        
        if player.points >= 500:
            new_achievements.extend(self._award_if_not_unlocked(
                player, "points_500", unlocked_ids))
        
        if player.points >= 1000:
            new_achievements.extend(self._award_if_not_unlocked(
                player, "points_1000", unlocked_ids))
        
        if player.level >= 5:
            new_achievements.extend(self._award_if_not_unlocked(
                player, "level_5", unlocked_ids))
        
        if player.level >= 10:
            new_achievements.extend(self._award_if_not_unlocked(
                player, "level_10", unlocked_ids))
        
        # Check categories achievement
        if len(player.stats.get("categories_played", set())) >= len(self.question_generator.categories):
            new_achievements.extend(self._award_if_not_unlocked(
                player, "all_categories", unlocked_ids))
        
        # Speed demon achievement
        if player.stats.get("fast_correct_answers", 0) >= 5:
            new_achievements.extend(self._award_if_not_unlocked(
                player, "speed_demon", unlocked_ids))
        
        return new_achievements
    
    def _award_if_not_unlocked(
        self, player: Player, achievement_id: str, unlocked_ids: set
    ) -> List[Achievement]:
        """Award an achievement if it hasn't been unlocked yet"""
        if achievement_id not in unlocked_ids and achievement_id in self.achievements:
            achievement = self.achievements[achievement_id]
            achievement.unlocked_at = datetime.now()
            if not hasattr(player, 'achievements'):
                player.achievements = []
            player.achievements.append(achievement)
            return [achievement]
        return []
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get all possible achievements"""
        return list(self.achievements.values())
    
    def get_locked_achievements(self, player: Player) -> List[Achievement]:
        """Get achievements that haven't been unlocked yet"""
        unlocked_ids = {a.id for a in player.achievements}
        return [
            achievement for achievement in self.achievements.values()
            if achievement.id not in unlocked_ids
        ] 