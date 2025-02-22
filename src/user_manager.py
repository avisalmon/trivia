import os
import json
import logging
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Dict
from .models.player import Player

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, users_file: str = "users.json"):
        self.users_file = users_file
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load users from file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            return {
                "users": {},
                "created_at": datetime.now().isoformat(),
                "version": 1
            }
        except Exception as e:
            logger.error(f"Error loading users: {e}")
            return {
                "users": {},
                "created_at": datetime.now().isoformat(),
                "version": 1
            }
    
    def _save_users(self):
        """Save users to file"""
        try:
            # Create backup
            if os.path.exists(self.users_file):
                backup_file = f"{self.users_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                with open(self.users_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            
            # Save to temporary file first
            temp_file = f"{self.users_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            
            # Rename temporary file to actual file
            os.replace(temp_file, self.users_file)
            
        except Exception as e:
            logger.error(f"Error saving users: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Create hash
        hasher = hashlib.sha256()
        hasher.update(salt.encode())
        hasher.update(password.encode())
        password_hash = hasher.hexdigest()
        
        return password_hash, salt
    
    def create_user(self, username: str, password: str, email: str) -> bool:
        """Create a new user"""
        try:
            if username in self.users["users"]:
                logger.warning(f"User {username} already exists")
                return False
            
            # Hash password
            password_hash, salt = self._hash_password(password)
            
            # Create user
            self.users["users"][username] = {
                "username": username,
                "password_hash": password_hash,
                "salt": salt,
                "email": email,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "login_count": 0,
                "is_active": True
            }
            
            self._save_users()
            logger.info(f"User {username} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate a user"""
        try:
            if username not in self.users["users"]:
                logger.warning(f"User {username} not found")
                return False
            
            user = self.users["users"][username]
            if not user["is_active"]:
                logger.warning(f"User {username} is not active")
                return False
            
            # Check password
            password_hash, _ = self._hash_password(password, user["salt"])
            if password_hash != user["password_hash"]:
                logger.warning(f"Invalid password for user {username}")
                return False
            
            # Update login info
            user["last_login"] = datetime.now().isoformat()
            user["login_count"] += 1
            self._save_users()
            
            logger.info(f"User {username} authenticated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return False
    
    def update_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Update user password"""
        try:
            if not self.authenticate(username, old_password):
                return False
            
            # Hash new password
            password_hash, salt = self._hash_password(new_password)
            
            # Update password
            self.users["users"][username]["password_hash"] = password_hash
            self.users["users"][username]["salt"] = salt
            self._save_users()
            
            logger.info(f"Password updated for user {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating password for user {username}: {e}")
            return False
    
    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user"""
        try:
            if username not in self.users["users"]:
                return False
            
            self.users["users"][username]["is_active"] = False
            self._save_users()
            
            logger.info(f"User {username} deactivated")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating user {username}: {e}")
            return False
    
    def activate_user(self, username: str) -> bool:
        """Activate a user"""
        try:
            if username not in self.users["users"]:
                return False
            
            self.users["users"][username]["is_active"] = True
            self._save_users()
            
            logger.info(f"User {username} activated")
            return True
            
        except Exception as e:
            logger.error(f"Error activating user {username}: {e}")
            return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        try:
            if username not in self.users["users"]:
                return None
            
            user = self.users["users"][username].copy()
            # Remove sensitive information
            user.pop("password_hash", None)
            user.pop("salt", None)
            return user
            
        except Exception as e:
            logger.error(f"Error getting info for user {username}: {e}")
            return None
    
    def get_active_users(self) -> List[str]:
        """Get list of active users"""
        try:
            return [
                username for username, user in self.users["users"].items()
                if user["is_active"]
            ]
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    def cleanup_inactive_users(self, days: int = 365) -> int:
        """Remove users inactive for specified number of days"""
        try:
            now = datetime.now()
            removed = 0
            
            for username, user in list(self.users["users"].items()):
                if not user["is_active"]:
                    last_login = datetime.fromisoformat(user["last_login"]) if user["last_login"] else None
                    if last_login is None or (now - last_login).days > days:
                        del self.users["users"][username]
                        removed += 1
            
            if removed > 0:
                self._save_users()
                logger.info(f"Removed {removed} inactive users")
            
            return removed
            
        except Exception as e:
            logger.error(f"Error cleaning up inactive users: {e}")
            return 0 