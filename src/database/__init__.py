"""
Database package initialization.
"""

import json
import os
import logging
from typing import List, Optional, Dict
from ..models.player import Player, Achievement
from ..models.question import Question
from datetime import datetime
from .migrations import DatabaseMigrator

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, filename: str = "database.json"):
        self.filename = filename
        self.migrator = DatabaseMigrator(filename)
        self.data = self._load_data()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database with migrations"""
        try:
            # Create backup before migration
            self.migrator.backup_database()
            
            # Run migrations
            if not self.migrator.migrate():
                logger.error("Database migration failed")
                self._handle_migration_failure()
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            self._handle_migration_failure()
    
    def _handle_migration_failure(self):
        """Handle database migration failure"""
        # Try to restore from backup
        backups = [f for f in os.listdir('.') if f.startswith(self.filename) and f.endswith('.bak')]
        if backups:
            latest_backup = max(backups)
            logger.info(f"Attempting to restore from backup: {latest_backup}")
            try:
                with open(latest_backup, 'r') as f:
                    self.data = json.load(f)
                logger.info("Database restored from backup")
            except Exception as e:
                logger.error(f"Error restoring from backup: {e}")
                self._create_empty_database()
        else:
            logger.warning("No backup found, creating empty database")
            self._create_empty_database()
    
    def _create_empty_database(self):
        """Create a new empty database"""
        self.data = {
            "players": {},
            "used_questions": set(),
            "created_at": datetime.now().isoformat()
        }
        self._save_data()
    
    def _load_data(self) -> dict:
        """Load data from database file with error handling"""
        try:
            if not os.path.exists(self.filename):
                return self._create_empty_database()
            
            with open(self.filename, "r") as f:
                data = json.load(f)
                # Convert used_questions to set for better performance
                data["used_questions"] = set(data.get("used_questions", []))
                return data
                
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding database file: {e}")
            return self._handle_corrupt_database()
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return self._create_empty_database()
    
    def _handle_corrupt_database(self) -> dict:
        """Handle corrupted database file"""
        # Try to restore from backup
        backups = [f for f in os.listdir('.') if f.startswith(self.filename) and f.endswith('.bak')]
        if backups:
            latest_backup = max(backups)
            logger.info(f"Attempting to restore from backup: {latest_backup}")
            try:
                with open(latest_backup, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error restoring from backup: {e}")
        
        return self._create_empty_database()
    
    def _save_data(self):
        """Save data to database file with backup"""
        try:
            # Create backup before saving
            if os.path.exists(self.filename):
                backup_file = f"{self.filename}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                with open(self.filename, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            
            # Convert set to list for JSON serialization
            data = self.data.copy()
            data["used_questions"] = list(self.data["used_questions"])
            data["last_updated"] = datetime.now().isoformat()
            
            # Save to temporary file first
            temp_file = f"{self.filename}.tmp"
            with open(temp_file, "w") as f:
                json.dump(data, f, indent=2)
            
            # Rename temporary file to actual file
            os.replace(temp_file, self.filename)
            
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise
    
    def save_player(self, player: Player):
        """Save player data with error handling"""
        try:
            self.data["players"][player.username] = player.to_dict()
            self._save_data()
            logger.info(f"Player {player.username} saved successfully")
        except Exception as e:
            logger.error(f"Error saving player {player.username}: {e}")
            raise
    
    def get_player(self, username: str) -> Optional[Player]:
        """Get player data with error handling"""
        try:
            if username not in self.data["players"]:
                return None
            
            player_data = self.data["players"][username]
            return Player.from_dict(player_data)
            
        except Exception as e:
            logger.error(f"Error retrieving player {username}: {e}")
            return None
    
    def add_used_question(self, question_hash: str):
        """Add used question with error handling"""
        try:
            self.data["used_questions"].add(question_hash)
            self._save_data()
        except Exception as e:
            logger.error(f"Error adding used question: {e}")
    
    def is_question_used(self, question_hash: str) -> bool:
        """Check if question is used with error handling"""
        try:
            return question_hash in self.data["used_questions"]
        except Exception as e:
            logger.error(f"Error checking used question: {e}")
            return False
    
    def clear_used_questions(self):
        """Clear used questions with error handling"""
        try:
            self.data["used_questions"] = set()
            self._save_data()
            logger.info("Used questions cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing used questions: {e}")
    
    def get_all_players(self) -> List[Player]:
        """Get all players with error handling"""
        try:
            return [Player.from_dict(data) for data in self.data["players"].values()]
        except Exception as e:
            logger.error(f"Error retrieving all players: {e}")
            return []
    
    def delete_player(self, username: str) -> bool:
        """Delete player with error handling"""
        try:
            if username in self.data["players"]:
                del self.data["players"][username]
                self._save_data()
                logger.info(f"Player {username} deleted successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting player {username}: {e}")
            return False 