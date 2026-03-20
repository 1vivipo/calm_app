"""
平静AI Agent - 会话管理
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
from collections import OrderedDict
from backend.models import Session, Message, MessageType
from config.config import Config
from loguru import logger


class SessionManager:
    """会话管理器"""
    
    def __init__(self, max_sessions: int = 1000):
        """
        初始化会话管理器
        
        Args:
            max_sessions: 最大会话数量
        """
        self.sessions: OrderedDict[str, Session] = OrderedDict()
        self.max_sessions = max_sessions
        self.session_timeout = Config.SESSION_TIMEOUT
        logger.info(f"会话管理器初始化完成，最大会话数: {max_sessions}")
    
    def create_session(self, session_id: Optional[str] = None) -> Session:
        """
        创建新会话
        
        Args:
            session_id: 可选的会话ID，不提供则自动生成
            
        Returns:
            新创建的会话
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session = Session(
            session_id=session_id,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 如果达到最大会话数，删除最旧的会话
        if len(self.sessions) >= self.max_sessions:
            oldest_id = next(iter(self.sessions))
            del self.sessions[oldest_id]
            logger.info(f"删除最旧会话: {oldest_id}")
        
        self.sessions[session_id] = session
        logger.info(f"创建新会话: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        获取会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话对象，不存在则返回None
        """
        session = self.sessions.get(session_id)
        if session:
            # 检查会话是否超时
            if datetime.now() - session.updated_at > timedelta(seconds=self.session_timeout):
                logger.info(f"会话超时: {session_id}")
                del self.sessions[session_id]
                return None
            # 更新访问时间
            session.updated_at = datetime.now()
        return session
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        message_type: MessageType = MessageType.TEXT,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        添加消息到会话
        
        Args:
            session_id: 会话ID
            role: 角色 (user/assistant/system)
            content: 消息内容
            message_type: 消息类型
            metadata: 元数据
            
        Returns:
            是否成功
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"会话不存在: {session_id}")
            return False
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            message_type=message_type,
            metadata=metadata
        )
        
        session.messages.append(message)
        session.updated_at = datetime.now()
        
        # 限制历史消息数量
        if len(session.messages) > Config.MAX_HISTORY:
            session.messages = session.messages[-Config.MAX_HISTORY:]
            logger.info(f"会话 {session_id} 消息数量达到上限，保留最近 {Config.MAX_HISTORY} 条")
        
        return True
    
    def get_messages(self, session_id: str) -> List[Message]:
        """
        获取会话的所有消息
        
        Args:
            session_id: 会话ID
            
        Returns:
            消息列表
        """
        session = self.get_session(session_id)
        if not session:
            return []
        return session.messages.copy()
    
    def clear_session(self, session_id: str) -> bool:
        """
        清空会话历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.messages.clear()
        session.updated_at = datetime.now()
        logger.info(f"清空会话历史: {session_id}")
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"删除会话: {session_id}")
            return True
        return False
    
    def get_active_sessions_count(self) -> int:
        """获取活跃会话数量"""
        return len(self.sessions)
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期会话
        
        Returns:
            清理的会话数量
        """
        expired_count = 0
        expired_ids = []
        
        for session_id, session in self.sessions.items():
            if datetime.now() - session.updated_at > timedelta(seconds=self.session_timeout):
                expired_ids.append(session_id)
        
        for session_id in expired_ids:
            del self.sessions[session_id]
            expired_count += 1
        
        if expired_count > 0:
            logger.info(f"清理了 {expired_count} 个过期会话")
        
        return expired_count


# 全局会话管理器实例
session_manager = SessionManager()
