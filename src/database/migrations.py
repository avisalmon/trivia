import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Migration:
    def __init__(self, version: int, description: str):
        self.version = version
        self.description = description
        self.applied_at = None
    
    def up(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply migration forward"""
        raise NotImplementedError
    
    def down(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback migration"""
        raise NotImplementedError

class AddPlayerStatsV1(Migration):
    def __init__(self):
        super().__init__(1, "Add player statistics")
    
    def up(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add stats field to players"""
        for username, player in data.get("players", {}).items():
            if "stats" not in player:
                player["stats"] = {
                    "correct_answers": 0,
                    "wrong_answers": 0,
                    "fast_correct_answers": 0,
                    "hints_used": 0,
                    "categories_played": []
                }
        return data
    
    def down(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove stats field from players"""
        for username, player in data.get("players", {}).items():
            player.pop("stats", None)
        return data

class AddAchievementsV2(Migration):
    def __init__(self):
        super().__init__(2, "Add achievements system")
    
    def up(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add achievements field to players"""
        for username, player in data.get("players", {}).items():
            if "achievements" not in player:
                player["achievements"] = []
        return data
    
    def down(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove achievements field from players"""
        for username, player in data.get("players", {}).items():
            player.pop("achievements", None)
        return data

class DatabaseMigrator:
    def __init__(self, db_file: str = "database.json"):
        self.db_file = db_file
        self.migrations: List[Migration] = [
            AddPlayerStatsV1(),
            AddAchievementsV2()
        ]
        self.version_file = "db_version.json"
    
    def get_current_version(self) -> int:
        """Get the current database version"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    version_data = json.load(f)
                    return version_data.get("version", 0)
            return 0
        except Exception as e:
            logger.error(f"Error reading version file: {e}")
            return 0
    
    def save_version(self, version: int):
        """Save the current database version"""
        try:
            version_data = {
                "version": version,
                "updated_at": datetime.now().isoformat()
            }
            with open(self.version_file, 'w') as f:
                json.dump(version_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving version file: {e}")
    
    def migrate(self, target_version: int = None) -> bool:
        """Run database migrations"""
        try:
            # Load current database
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"players": {}, "used_questions": []}
            
            current_version = self.get_current_version()
            if target_version is None:
                target_version = len(self.migrations)
            
            logger.info(f"Current database version: {current_version}")
            logger.info(f"Target database version: {target_version}")
            
            # Apply migrations
            if current_version < target_version:
                for migration in self.migrations[current_version:target_version]:
                    logger.info(f"Applying migration {migration.version}: {migration.description}")
                    data = migration.up(data)
                    migration.applied_at = datetime.now().isoformat()
            elif current_version > target_version:
                for migration in reversed(self.migrations[target_version:current_version]):
                    logger.info(f"Rolling back migration {migration.version}: {migration.description}")
                    data = migration.down(data)
            
            # Save updated database
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Update version
            self.save_version(target_version)
            logger.info("Migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            return False
    
    def backup_database(self) -> bool:
        """Create a backup of the current database"""
        try:
            if os.path.exists(self.db_file):
                backup_file = f"{self.db_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                with open(self.db_file, 'r') as src, open(backup_file, 'w') as dst:
                    data = json.load(src)
                    json.dump(data, dst, indent=2)
                logger.info(f"Database backup created: {backup_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return False 