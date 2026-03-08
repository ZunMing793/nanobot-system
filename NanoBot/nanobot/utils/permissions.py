"""Permission management for multi-bot system."""

from pathlib import Path
from typing import Optional


class PermissionManager:
    """
    Permission manager for multi-bot system.
    
    Rules:
    - shared/ → All bots can read and write
    - botX/ → Only the corresponding bot can write, all bots can read
    - Management actions (restart, etc.) → Only bot1_core can execute
    """
    
    SHARED_AREAS = ["shared"]
    BOT_FOLDERS = ["bot1_core", "bot2_health", "bot3_finance", "bot4_emotion", "bot5_media"]
    MANAGEMENT_ACTIONS = [
        "manage_bot",
        "restart_bot", 
        "start_bot",
        "stop_bot",
        "get_bot_logs",
        "list_bots",
        "restart_all_bots",
        "stop_all_bots",
    ]
    
    def __init__(self, bot_id: str, root_path: Path):
        """
        Initialize permission manager.
        
        Args:
            bot_id: Bot identifier (e.g., "bot1_core", "bot2_health")
            root_path: Root path of NanoBot_System
        """
        self.bot_id = bot_id
        self.root_path = root_path.resolve()
    
    def _get_relative_path(self, path: Path) -> Optional[Path]:
        """Get path relative to root, or None if outside."""
        try:
            return path.resolve().relative_to(self.root_path)
        except ValueError:
            return None
    
    def can_read(self, path: Path) -> bool:
        """
        Check if bot can read the path.
        
        All areas are readable by all bots.
        """
        rel_path = self._get_relative_path(path)
        if rel_path is None:
            return False
        return True
    
    def can_write(self, path: Path) -> bool:
        """
        Check if bot can write to the path.
        
        Rules:
        - shared/ → All bots can write
        - botX/ → Only the corresponding bot can write
        """
        rel_path = self._get_relative_path(path)
        if rel_path is None:
            return False
        
        parts = rel_path.parts
        
        if not parts:
            return False
        
        first_dir = parts[0]
        
        if first_dir in self.SHARED_AREAS:
            return True
        
        if first_dir in self.BOT_FOLDERS:
            return first_dir == self.bot_id
        
        return False
    
    def can_execute(self, action: str) -> bool:
        """
        Check if bot can execute a management action.
        
        Only bot1_core can execute management actions.
        """
        if action in self.MANAGEMENT_ACTIONS:
            return self.bot_id == "bot1_core"
        return True
    
    def get_allowed_bot_folders(self) -> list[str]:
        """Get list of bot folders this bot can write to."""
        if self.bot_id in self.BOT_FOLDERS:
            return [self.bot_id]
        return []
    
    def get_shared_areas(self) -> list[str]:
        """Get list of shared areas."""
        return self.SHARED_AREAS.copy()
    
    def is_leader(self) -> bool:
        """Check if this bot is the leader (bot1_core)."""
        return self.bot_id == "bot1_core"
    
    def validate_path(self, path: Path, require_write: bool = False) -> tuple[bool, str]:
        """
        Validate access to a path.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if require_write:
            if not self.can_write(path):
                return False, f"Bot {self.bot_id} does not have write permission for {path}"
        else:
            if not self.can_read(path):
                return False, f"Bot {self.bot_id} does not have read permission for {path}"
        
        return True, ""
    
    def get_other_bot_paths(self) -> dict[str, Path]:
        """Get paths to other bots' directories (read-only access)."""
        paths = {}
        for bot_folder in self.BOT_FOLDERS:
            if bot_folder != self.bot_id:
                bot_path = self.root_path / bot_folder
                if bot_path.exists():
                    paths[bot_folder] = bot_path
        return paths
    
    def get_shared_path(self) -> Path:
        """Get the shared directory path."""
        return self.root_path / "shared"
    
    def get_bot_memory_path(self, bot_id: Optional[str] = None) -> Path:
        """
        Get memory path for a bot.
        
        Args:
            bot_id: Bot ID, defaults to current bot
        """
        target_bot = bot_id or self.bot_id
        return self.root_path / target_bot / "memory"
    
    def get_shared_memory_path(self) -> Path:
        """Get shared memory path."""
        return self.root_path / "shared" / "memory"


class PermissionError(Exception):
    """Permission denied error."""
    
    def __init__(self, bot_id: str, action: str, path: Optional[Path] = None):
        self.bot_id = bot_id
        self.action = action
        self.path = path
        message = f"Permission denied: Bot '{bot_id}' cannot {action}"
        if path:
            message += f" on '{path}'"
        super().__init__(message)
