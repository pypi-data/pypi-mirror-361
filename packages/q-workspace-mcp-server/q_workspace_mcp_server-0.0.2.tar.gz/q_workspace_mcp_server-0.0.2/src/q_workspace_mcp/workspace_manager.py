"""
Workspace Manager using SQLite + FTS5 for Amazon Q CLI
Simple, fast, and reliable implementation
"""

import json
import logging
import os
import re
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple


class WorkspaceManager:
    """SQLite + FTS5 기반 워크스페이스 매니저 - 단순하고 빠른 구현"""

    def __init__(self, config: Optional[Dict[str, Any]] = None, verbose: bool = False):
        """Initialize workspace manager with SQLite implementation"""
        self.current_workspace: Optional[str] = None
        self.verbose = verbose

        # 로그 설정
        self._setup_logging()

        # SQLite 데이터베이스 초기화
        self.db_path = os.path.expanduser("~/.Q_workspace/conversations.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # 데이터베이스 초기화
        self._init_database()

        self._log("SQLite Workspace Manager initialized successfully")

    def _setup_logging(self):
        """로그 파일 설정"""
        log_dir = os.path.expanduser("~/.Q_workspace")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, "operations.log")

        # 로거 설정
        self.logger = logging.getLogger('q_workspace_sqlite')
        self.logger.setLevel(logging.INFO)

        # 기존 핸들러 제거
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # 파일 핸들러 추가
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _log(self, message: str):
        """로그 메시지 기록"""
        if self.verbose:
            print(f"[Q-Workspace] {message}")
        self.logger.info(message)

    def _init_database(self):
        """SQLite 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 워크스페이스 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS workspaces (
            workspace_id TEXT PRIMARY KEY,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_used_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 대화 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id TEXT,
            user_message TEXT,
            ai_response TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workspace_id) REFERENCES workspaces (workspace_id)
        )
        ''')

        # FTS5 가상 테이블 (전문 검색용)
        cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS conversations_fts USING fts5(
            user_message, 
            ai_response, 
            workspace_id,
            content='conversations',
            content_rowid='id'
        )
        ''')

        # 트리거 생성 (자동 FTS 인덱싱)
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS conversations_ai AFTER INSERT ON conversations
        BEGIN
            INSERT INTO conversations_fts(rowid, user_message, ai_response, workspace_id)
            VALUES (new.id, new.user_message, new.ai_response, new.workspace_id);
        END
        ''')

        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS conversations_ad AFTER DELETE ON conversations
        BEGIN
            INSERT INTO conversations_fts(conversations_fts, rowid, user_message, ai_response, workspace_id)
            VALUES ('delete', old.id, old.user_message, old.ai_response, old.workspace_id);
        END
        ''')

        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS conversations_au AFTER UPDATE ON conversations
        BEGIN
            INSERT INTO conversations_fts(conversations_fts, rowid, user_message, ai_response, workspace_id)
            VALUES ('delete', old.id, old.user_message, old.ai_response, old.workspace_id);
            INSERT INTO conversations_fts(rowid, user_message, ai_response, workspace_id)
            VALUES (new.id, new.user_message, new.ai_response, new.workspace_id);
        END
        ''')

        conn.commit()
        conn.close()

    def start_workspace(self, description: str) -> Dict[str, Any]:
        """새 워크스페이스 시작 또는 기존 워크스페이스 재개"""
        # 워크스페이스 ID 생성 (설명에서 공백을 언더스코어로 변환)
        workspace_id = description.strip().lower().replace(" ", "_")
        
        # 특수문자 제거 및 ID 정리
        workspace_id = re.sub(r'[^\w]', '', workspace_id)
        
        # 빈 ID 방지
        if not workspace_id:
            workspace_id = "general"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 워크스페이스 존재 여부 확인
        cursor.execute("SELECT workspace_id FROM workspaces WHERE workspace_id = ?", (workspace_id,))
        existing_workspace = cursor.fetchone()

        is_new_workspace = False

        if not existing_workspace:
            # 새 워크스페이스 생성
            cursor.execute(
                "INSERT INTO workspaces (workspace_id, description) VALUES (?, ?)",
                (workspace_id, description)
            )
            is_new_workspace = True
            self._log(f"New workspace created: {workspace_id}")
        else:
            # 기존 워크스페이스 업데이트
            cursor.execute(
                "UPDATE workspaces SET last_used_at = CURRENT_TIMESTAMP WHERE workspace_id = ?",
                (workspace_id,)
            )
            self._log(f"Existing workspace resumed: {workspace_id}")

        conn.commit()
        conn.close()

        # 현재 워크스페이스 설정
        self.current_workspace = workspace_id

        # 진실성 컨텍스트 로드
        truthfulness_context_loaded = self.reload_truthfulness_context()

        return {
            "workspace_id": workspace_id,
            "description": description,
            "is_new_workspace": is_new_workspace,
            "truthfulness_context_loaded": truthfulness_context_loaded
        }

    def add_conversation(self, user_message: str, ai_response: str) -> bool:
        """대화 추가"""
        if not self.current_workspace:
            self._log("Warning: No active workspace, conversation not saved")
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO conversations (workspace_id, user_message, ai_response) VALUES (?, ?, ?)",
                (self.current_workspace, user_message, ai_response)
            )
            conn.commit()
            self._log(f"Conversation added to workspace: {self.current_workspace}")
            return True
        except Exception as e:
            self._log(f"Error adding conversation: {e}")
            return False
        finally:
            conn.close()

    def get_workspace_conversations(self, workspace_id: str) -> Dict[str, Any]:
        """워크스페이스의 모든 대화 가져오기"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 워크스페이스 존재 여부 확인
        cursor.execute("SELECT description FROM workspaces WHERE workspace_id = ?", (workspace_id,))
        workspace = cursor.fetchone()

        if not workspace:
            conn.close()
            raise ValueError(f"Workspace '{workspace_id}' not found")

        description = workspace[0]

        # 대화 가져오기
        cursor.execute(
            "SELECT user_message, ai_response, timestamp FROM conversations WHERE workspace_id = ? ORDER BY timestamp",
            (workspace_id,)
        )
        conversations_data = cursor.fetchall()

        # 대화 수 가져오기
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE workspace_id = ?", (workspace_id,))
        conversation_count = cursor.fetchone()[0]

        conn.close()

        # 결과 포맷팅
        conversations = []
        for user_message, ai_response, timestamp in conversations_data:
            conversations.append({
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": timestamp
            })

        return {
            "workspace_id": workspace_id,
            "description": description,
            "conversation_count": conversation_count,
            "conversations": conversations
        }

    def resume_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """기존 워크스페이스를 전체 대화 기록과 함께 재개"""
        self._log(f"Resuming workspace: {workspace_id}")
        
        # 워크스페이스 대화 가져오기
        workspace_data = self.get_workspace_conversations(workspace_id)
        
        # 현재 워크스페이스 설정
        self.current_workspace = workspace_id
        
        # 워크스페이스 마지막 사용 시간 업데이트
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE workspaces SET last_used_at = CURRENT_TIMESTAMP WHERE workspace_id = ?",
            (workspace_id,)
        )
        conn.commit()
        conn.close()
        
        # 대화 컨텍스트 길이 추정
        context_length = sum(len(conv.get("user_message", "")) + len(conv.get("ai_response", "")) 
                            for conv in workspace_data.get("conversations", []))
        
        # 토큰 수 추정 (문자 수 / 4)
        estimated_tokens = context_length // 4
        
        return {
            "workspace_id": workspace_id,
            "description": workspace_data.get("description", ""),
            "conversation_count": workspace_data.get("conversation_count", 0),
            "context_length": context_length,
            "estimated_tokens": estimated_tokens,
            "full_history": workspace_data.get("conversations", [])
        }

    def list_all_workspaces(self) -> List[Dict[str, Any]]:
        """모든 워크스페이스 목록 가져오기"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 워크스페이스 목록 가져오기 (대화 수 포함)
        cursor.execute("""
            SELECT w.workspace_id, w.description, w.created_at, w.last_used_at, COUNT(c.id) as conversation_count
            FROM workspaces w
            LEFT JOIN conversations c ON w.workspace_id = c.workspace_id
            GROUP BY w.workspace_id
            ORDER BY w.last_used_at DESC
        """)
        
        workspaces_data = cursor.fetchall()
        conn.close()

        # 결과 포맷팅
        workspaces = []
        for workspace_id, description, created_at, last_used_at, conversation_count in workspaces_data:
            workspaces.append({
                "workspace_id": workspace_id,
                "description": description,
                "created_at": created_at,
                "last_used_at": last_used_at,
                "conversation_count": conversation_count
            })

        return workspaces

    def search_memory_by_workspace_id(self, workspace_id: str, query: str = "", limit: int = 10) -> Dict[str, Any]:
        """워크스페이스 내에서 대화 검색"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 워크스페이스 존재 여부 확인
        cursor.execute("SELECT workspace_id FROM workspaces WHERE workspace_id = ?", (workspace_id,))
        if not cursor.fetchone():
            conn.close()
            raise ValueError(f"Workspace '{workspace_id}' not found")

        results = []
        search_type = "all"

        if query:
            # FTS5 검색 수행
            cursor.execute("""
                SELECT c.user_message, c.ai_response, c.timestamp
                FROM conversations_fts fts
                JOIN conversations c ON fts.rowid = c.id
                WHERE fts.workspace_id = ? AND (fts.user_message MATCH ? OR fts.ai_response MATCH ?)
                ORDER BY c.timestamp DESC
                LIMIT ?
            """, (workspace_id, query, query, limit))
            search_type = "fts5"
        else:
            # 모든 대화 가져오기
            cursor.execute("""
                SELECT user_message, ai_response, timestamp
                FROM conversations
                WHERE workspace_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (workspace_id, limit))
            search_type = "all"

        conversations_data = cursor.fetchall()
        conn.close()

        # 결과 포맷팅
        for user_message, ai_response, timestamp in conversations_data:
            results.append({
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": timestamp
            })

        return {
            "results": results,
            "stats": {
                "search_type": search_type,
                "query": query,
                "workspace_id": workspace_id,
                "result_count": len(results)
            }
        }

    def delete_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """워크스페이스와 모든 대화 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 워크스페이스 존재 여부 확인
        cursor.execute("SELECT workspace_id FROM workspaces WHERE workspace_id = ?", (workspace_id,))
        if not cursor.fetchone():
            conn.close()
            raise ValueError(f"Workspace '{workspace_id}' not found")

        # 대화 수 확인
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE workspace_id = ?", (workspace_id,))
        conversation_count = cursor.fetchone()[0]

        # 대화 삭제
        cursor.execute("DELETE FROM conversations WHERE workspace_id = ?", (workspace_id,))
        
        # 워크스페이스 삭제
        cursor.execute("DELETE FROM workspaces WHERE workspace_id = ?", (workspace_id,))
        
        conn.commit()
        conn.close()

        # 현재 워크스페이스가 삭제된 경우 초기화
        if self.current_workspace == workspace_id:
            self.current_workspace = None

        self._log(f"Deleted workspace: {workspace_id} with {conversation_count} conversations")

        return {
            "workspace_id": workspace_id,
            "conversations": conversation_count,
            "workspace_metadata": True
        }

    def cleanup_old_workspaces(self, days: int = 30) -> Dict[str, Any]:
        """지정된 일수보다 오래된 워크스페이스 정리"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 기준 날짜 계산
        cutoff_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 오래된 워크스페이스 찾기
        cursor.execute(f"""
            SELECT workspace_id FROM workspaces 
            WHERE datetime(last_used_at) < datetime('now', '-{days} days')
        """)
        
        old_workspaces = [row[0] for row in cursor.fetchall()]
        
        # 삭제 통계
        workspaces_deleted = 0
        conversations_deleted = 0
        
        # 각 워크스페이스 삭제
        for workspace_id in old_workspaces:
            # 대화 수 확인
            cursor.execute("SELECT COUNT(*) FROM conversations WHERE workspace_id = ?", (workspace_id,))
            conversation_count = cursor.fetchone()[0]
            
            # 대화 삭제
            cursor.execute("DELETE FROM conversations WHERE workspace_id = ?", (workspace_id,))
            
            # 워크스페이스 삭제
            cursor.execute("DELETE FROM workspaces WHERE workspace_id = ?", (workspace_id,))
            
            workspaces_deleted += 1
            conversations_deleted += conversation_count
            
            # 현재 워크스페이스가 삭제된 경우 초기화
            if self.current_workspace == workspace_id:
                self.current_workspace = None
        
        conn.commit()
        conn.close()
        
        self._log(f"Cleaned up {workspaces_deleted} old workspaces with {conversations_deleted} conversations")
        
        return {
            "cutoff_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "days": days,
            "workspaces_deleted": workspaces_deleted,
            "conversations_deleted": conversations_deleted
        }

    def get_storage_stats(self) -> Dict[str, Any]:
        """저장소 통계 및 사용 정보 가져오기"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 워크스페이스 수
        cursor.execute("SELECT COUNT(*) FROM workspaces")
        total_workspaces = cursor.fetchone()[0]
        
        # 대화 수
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]
        
        conn.close()
        
        # 데이터베이스 파일 크기
        try:
            storage_size_bytes = os.path.getsize(self.db_path)
            storage_size_mb = round(storage_size_bytes / (1024 * 1024), 2)
        except:
            storage_size_mb = "unknown"
        
        return {
            "storage_type": "SQLite + FTS5",
            "total_workspaces": total_workspaces,
            "total_conversations": total_conversations,
            "storage_size_mb": storage_size_mb,
            "database_path": self.db_path,
            "current_workspace": self.current_workspace
        }

    def reload_truthfulness_context(self) -> bool:
        """진실성 컨텍스트 재로드"""
        if not self.current_workspace:
            return False
            
        # 시스템 메시지 추가
        system_message = "[SYSTEM] Workspace resumed - Reloading truthfulness guidelines"
        
        truthfulness_guidelines = """🎯 **CORE PRINCIPLES FOR THIS WORKSPACE:**

**ABSOLUTE TRUTHFULNESS REQUIRED:**
• Only provide information you are certain about
• If you don't know something, clearly state "I don't know" or "I'm not certain"
• Never guess, estimate, or make assumptions when asked for specific facts
• Distinguish clearly between what you know vs. what you think might be true

**WHEN UNCERTAIN:**
• Say "I don't have enough information to answer that accurately"
• Suggest where the user might find reliable information
• Offer to help with related topics you do know about

**AVOID:**
• "I think...", "It might be...", "Probably..." for factual questions
• Making up details to fill gaps in knowledge
• Presenting speculation as fact

**REMEMBER:** It's better to admit ignorance than to provide potentially incorrect information. Your credibility depends on accuracy, not having all the answers."""
        
        # 대화에 추가
        self.add_conversation(system_message, truthfulness_guidelines)
        
        return True
