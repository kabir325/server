#!/usr/bin/env python3
"""
Chat Manager - Manages chat sessions and history with persistent storage
"""

import logging
import uuid
import time
import json
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ChatManager:
    """Chat session manager with JSON file persistence"""
    
    def __init__(self, storage_file: str = "chat_history.json"):
        self.storage_file = storage_file
        self.sessions = {}  # session_id -> session data
        self._load_from_file()
        logger.info(f"✅ Chat Manager initialized (storage: {storage_file})")
    
    def _load_from_file(self):
        """Load chat history from JSON file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
                logger.info(f"📂 Loaded {len(self.sessions)} chat sessions from {self.storage_file}")
            except Exception as e:
                logger.error(f"❌ Failed to load chat history: {e}")
                self.sessions = {}
        else:
            logger.info("📂 No existing chat history found, starting fresh")
    
    def _save_to_file(self):
        """Save chat history to JSON file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Failed to save chat history: {e}")
    
    def create_session(self, title: str = "New Chat") -> str:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'session_id': session_id,
            'title': title,
            'messages': [],
            'created_at': int(time.time()),
            'updated_at': int(time.time())
        }
        self._save_to_file()
        logger.info(f"Created chat session: {title} ({session_id})")
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, images: List = None) -> bool:
        """Add a message to a session"""
        if session_id not in self.sessions:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        message = {
            'message_id': str(uuid.uuid4()),
            'session_id': session_id,
            'role': role,
            'content': content,
            'timestamp': int(time.time()),
            'images': images or []
        }
        
        self.sessions[session_id]['messages'].append(message)
        self.sessions[session_id]['updated_at'] = int(time.time())
        self._save_to_file()
        
        return True
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self, limit: int = 50) -> List[Dict]:
        """Get all sessions"""
        sessions = []
        for session in self.sessions.values():
            session_copy = session.copy()
            session_copy['message_count'] = len(session['messages'])
            # Don't include full messages in list view
            session_copy.pop('messages', None)
            sessions.append(session_copy)
        sessions.sort(key=lambda x: x['updated_at'], reverse=True)
        return sessions[:limit]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_to_file()
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    def update_session_title(self, session_id: str, title: str) -> bool:
        """Update session title"""
        if session_id in self.sessions:
            self.sessions[session_id]['title'] = title
            self.sessions[session_id]['updated_at'] = int(time.time())
            self._save_to_file()
            return True
        return False
    
    def get_conversation_context(self, session_id: str, max_messages: int = 5) -> str:
        """Get conversation context for a session"""
        session = self.get_session(session_id)
        if not session or not session['messages']:
            return ""
        
        messages = session['messages'][-max_messages:]
        
        context = "Previous conversation:\n\n"
        for msg in messages:
            role = msg['role'].capitalize()
            content = msg['content']
            context += f"{role}: {content}\n\n"
        
        return context
    
    def get_stats(self) -> Dict:
        """Get chat statistics"""
        total_messages = sum(len(s['messages']) for s in self.sessions.values())
        return {
            'total_sessions': len(self.sessions),
            'total_messages': total_messages
        }
