"""Shared memory writer with section-based locking."""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger


class SharedMemoryWriter:
    """
    Shared memory writer with section-based access control.
    
    Each bot can only write to its designated section in shared memory files.
    Uses asyncio locks to prevent concurrent writes to the same section.
    """
    
    SECTIONS = {
        "bot1_core": "基本信息",
        "bot2_health": "健康档案",
        "bot3_finance": "财务状况",
        "bot4_emotion": "心理状态",
        "bot5_media": "自媒体运营",
    }
    
    SECTION_MARKERS = {
        "基本信息": ("## 基本信息", "## 健康档案"),
        "健康档案": ("## 健康档案", "## 财务状况"),
        "财务状况": ("## 财务状况", "## 心理状态"),
        "心理状态": ("## 心理状态", "## 自媒体运营"),
        "自媒体运营": ("## 自媒体运营", "## 更新日志"),
    }
    
    def __init__(self, shared_memory_path: Path):
        self.shared_memory_path = shared_memory_path
        self.user_profile_path = shared_memory_path / "USER_PROFILE.md"
        self.shared_knowledge_path = shared_memory_path / "SHARED_KNOWLEDGE.md"
        self._locks: dict[str, asyncio.Lock] = {}
    
    def _get_lock(self, section: str) -> asyncio.Lock:
        """Get or create a lock for a section."""
        if section not in self._locks:
            self._locks[section] = asyncio.Lock()
        return self._locks[section]
    
    def _get_section_name(self, bot_id: str) -> Optional[str]:
        """Get the section name for a bot."""
        return self.SECTIONS.get(bot_id)
    
    def can_write_section(self, bot_id: str, section: str) -> bool:
        """Check if a bot can write to a section."""
        return self.SECTIONS.get(bot_id) == section
    
    async def read_section(self, bot_id: str) -> str:
        """Read the section content for a bot."""
        section_name = self._get_section_name(bot_id)
        if not section_name:
            return ""
        
        if not self.user_profile_path.exists():
            return ""
        
        content = self.user_profile_path.read_text(encoding="utf-8")
        return self._extract_section(content, section_name)
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a section from the content."""
        markers = self.SECTION_MARKERS.get(section_name)
        if not markers:
            return ""
        
        start_marker, end_marker = markers
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return ""
        
        end_idx = content.find(end_marker)
        if end_idx == -1:
            end_idx = len(content)
        
        return content[start_idx:end_idx].strip()
    
    async def update_section(self, bot_id: str, new_content: str) -> bool:
        """
        Update the section for a bot.
        
        Args:
            bot_id: Bot identifier
            new_content: New section content (including the section header)
        
        Returns:
            True if successful, False otherwise
        """
        section_name = self._get_section_name(bot_id)
        if not section_name:
            logger.error(f"Unknown bot_id: {bot_id}")
            return False
        
        lock = self._get_lock(section_name)
        
        async with lock:
            try:
                if not self.user_profile_path.exists():
                    logger.error(f"User profile not found: {self.user_profile_path}")
                    return False
                
                content = self.user_profile_path.read_text(encoding="utf-8")
                updated = self._replace_section(content, section_name, new_content)
                
                if updated == content:
                    logger.warning(f"Section not found or unchanged: {section_name}")
                    return False
                
                self.user_profile_path.write_text(updated, encoding="utf-8")
                logger.info(f"Updated section '{section_name}' for {bot_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to update section: {e}")
                return False
    
    def _replace_section(self, content: str, section_name: str, new_content: str) -> str:
        """Replace a section in the content."""
        markers = self.SECTION_MARKERS.get(section_name)
        if not markers:
            return content
        
        start_marker, end_marker = markers
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return content
        
        end_idx = content.find(end_marker)
        if end_idx == -1:
            end_idx = len(content)
        
        return content[:start_idx] + new_content + "\n\n" + content[end_idx:]
    
    async def append_to_update_log(self, bot_id: str, update_description: str) -> bool:
        """Append an entry to the update log."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            bot_name = bot_id.replace("_", " ").title()
            
            log_entry = f"| {timestamp} | {bot_name} | {update_description} |\n"
            
            content = ""
            if self.user_profile_path.exists():
                content = self.user_profile_path.read_text(encoding="utf-8")
            
            log_marker = "## 更新日志"
            log_idx = content.find(log_marker)
            
            if log_idx == -1:
                return False
            
            header_end = content.find("\n|", log_idx)
            if header_end == -1:
                header_end = content.find("\n\n", log_idx)
            
            if header_end == -1:
                return False
            
            new_content = content[:header_end + 1] + log_entry + content[header_end + 1:]
            self.user_profile_path.write_text(new_content, encoding="utf-8")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to append to update log: {e}")
            return False
    
    async def read_shared_knowledge(self) -> str:
        """Read the shared knowledge file."""
        if not self.shared_knowledge_path.exists():
            return ""
        return self.shared_knowledge_path.read_text(encoding="utf-8")
    
    async def update_shared_knowledge(self, bot_id: str, section: str, content: str) -> bool:
        """Update a section in shared knowledge."""
        lock = self._get_lock("shared_knowledge")
        
        async with lock:
            try:
                if not self.shared_knowledge_path.exists():
                    return False
                
                file_content = self.shared_knowledge_path.read_text(encoding="utf-8")
                section_marker = f"## {section}"
                
                section_idx = file_content.find(section_marker)
                if section_idx == -1:
                    return False
                
                next_section_idx = file_content.find("\n## ", section_idx + 1)
                if next_section_idx == -1:
                    next_section_idx = len(file_content)
                
                new_file_content = (
                    file_content[:section_idx] 
                    + content 
                    + "\n" 
                    + file_content[next_section_idx:]
                )
                
                self.shared_knowledge_path.write_text(new_file_content, encoding="utf-8")
                logger.info(f"Updated shared knowledge section '{section}' by {bot_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to update shared knowledge: {e}")
                return False
