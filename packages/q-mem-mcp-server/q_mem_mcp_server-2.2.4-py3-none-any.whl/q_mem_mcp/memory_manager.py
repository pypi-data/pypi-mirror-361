"""
Memory Manager using SQLite + FTS5 for Amazon Q CLI
Simple, fast, and reliable implementation
"""

import json
import logging
import os
import re
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple


class MemoryManager:
    """SQLite + FTS5 기반 메모리 매니저 - 단순하고 빠른 구현"""

    def __init__(self, config: Optional[Dict[str, Any]] = None, verbose: bool = False):
        """Initialize memory manager with SQLite implementation"""
        self.current_workspace: Optional[str] = None
        self.verbose = verbose

        # 로그 설정
        self._setup_logging()

        # SQLite 데이터베이스 초기화
        self.db_path = os.path.expanduser("~/.Q_mem/conversations.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # 데이터베이스 초기화
        self._init_database()

        self._log("SQLite Memory Manager initialized successfully")

    def _setup_logging(self):
        """로그 파일 설정"""
        log_dir = os.path.expanduser("~/.Q_mem")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, "operations.log")

        # 로거 설정
        self.logger = logging.getLogger('q_mem_sqlite')
        self.logger.setLevel(logging.INFO)

        # 기존 핸들러 제거
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # 파일 핸들러 추가
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # 포맷터 설정
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def _log(self, message: str, level: str = "INFO"):
        """로그 기록"""
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)

        if self.verbose:
            print(f"[{level}] {message}")

    def _init_database(self):
        """SQLite 데이터베이스 및 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 워크스페이스 테이블
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS workspaces
                       (
                           workspace_id
                           TEXT
                           PRIMARY
                           KEY,
                           description
                           TEXT
                           NOT
                           NULL,
                           created_at
                           TEXT
                           NOT
                           NULL,
                           updated_at
                           TEXT
                           NOT
                           NULL
                       )
                       ''')

        # 대화 테이블
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS conversations
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           workspace_id
                           TEXT
                           NOT
                           NULL,
                           user_message
                           TEXT
                           NOT
                           NULL,
                           ai_response
                           TEXT
                           NOT
                           NULL,
                           timestamp
                           TEXT
                           NOT
                           NULL,
                           importance_score
                           INTEGER
                           DEFAULT
                           0,
                           metadata
                           TEXT,
                           FOREIGN
                           KEY
                       (
                           workspace_id
                       ) REFERENCES workspaces
                       (
                           workspace_id
                       )
                           )
                       ''')

        # FTS5 전문 검색 테이블
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS conversations_fts USING fts5(
                user_message,
                ai_response,
                workspace_id UNINDEXED,
                timestamp UNINDEXED,
                content='conversations',
                content_rowid='id'
            )
        ''')

        # 인덱스 생성
        cursor.execute('''
                       CREATE INDEX IF NOT EXISTS idx_conversations_workspace
                           ON conversations(workspace_id)
                       ''')

        cursor.execute('''
                       CREATE INDEX IF NOT EXISTS idx_conversations_timestamp
                           ON conversations(timestamp)
                       ''')

        # FTS5 트리거 설정 (자동 동기화)
        cursor.execute('''
                       CREATE TRIGGER IF NOT EXISTS conversations_ai AFTER INSERT ON conversations
                       BEGIN
                INSERT INTO conversations_fts(rowid, user_message, ai_response, workspace_id, timestamp)
                VALUES (new.id, new.user_message, new.ai_response, new.workspace_id, new.timestamp);
                       END
                       ''')

        cursor.execute('''
                       CREATE TRIGGER IF NOT EXISTS conversations_ad AFTER
                       DELETE
                       ON conversations BEGIN
                INSERT INTO conversations_fts(conversations_fts, rowid, user_message, ai_response, workspace_id, timestamp)
                VALUES('delete', old.id, old.user_message, old.ai_response, old.workspace_id, old.timestamp);
                       END
                       ''')

        cursor.execute('''
                       CREATE TRIGGER IF NOT EXISTS conversations_au AFTER
                       UPDATE ON conversations BEGIN
                       INSERT
                       INTO conversations_fts(conversations_fts, rowid, user_message, ai_response, workspace_id,
                                              timestamp)
                       VALUES ('delete', old.id, old.user_message, old.ai_response, old.workspace_id, old.timestamp);
                       INSERT INTO conversations_fts(rowid, user_message, ai_response, workspace_id, timestamp)
                       VALUES (new.id, new.user_message, new.ai_response, new.workspace_id, new.timestamp);
                       END
                       ''')

        conn.commit()
        conn.close()

        self._log("Database initialized with FTS5 support")

    def find_or_create_workspace(self, description: str) -> Tuple[str, bool]:
        """Find existing workspace by description or create new one"""
        # Use description as workspace_id (sanitized)
        workspace_id = re.sub(r'[^\w\-_]', '_', description)[:50]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check existing workspace
        cursor.execute(
            "SELECT workspace_id FROM workspaces WHERE workspace_id = ?",
            (workspace_id,)
        )

        if cursor.fetchone():
            conn.close()
            self._log(f"Found existing workspace: {workspace_id}")
            return workspace_id, False

        # Create new workspace
        now = datetime.now().isoformat()
        cursor.execute('''
                       INSERT INTO workspaces (workspace_id, description, created_at, updated_at)
                       VALUES (?, ?, ?, ?)
                       ''', (workspace_id, description, now, now))

        conn.commit()
        conn.close()

        self._log(f"Created new workspace: {workspace_id}")
        return workspace_id, True

    def start_workspace(self, description: str) -> Dict[str, Any]:
        """Start a new workspace with truthfulness context"""
        workspace_id, is_new = self.find_or_create_workspace(description)
        self.current_workspace = workspace_id

        # 진실성 강조 컨텍스트를 워크스페이스 시작 시 주입
        try:
            truthfulness_context = self._get_truthfulness_context()
            self.add_conversation(
                user_message="[SYSTEM] Workspace started - Loading truthfulness guidelines",
                ai_response=truthfulness_context
            )
            self._log("Truthfulness context loaded for workspace")
        except Exception as e:
            self._log(f"Warning: Could not load truthfulness context: {e}", "WARNING")

        return {
            "workspace_id": workspace_id,
            "is_new_workspace": is_new,
            "description": description,
            "truthfulness_context_loaded": True
        }

    def reload_truthfulness_context(self) -> bool:
        """Reload truthfulness context to current workspace"""
        if not self.current_workspace:
            return False

        try:
            truthfulness_context = self._get_truthfulness_context()
            self.add_conversation(
                user_message="[SYSTEM] Workspace resumed - Reloading truthfulness guidelines",
                ai_response=truthfulness_context
            )
            self._log("Truthfulness context reloaded")
            return True
        except Exception as e:
            self._log(f"Warning: Could not reload truthfulness context: {e}", "WARNING")
            return False

    def _get_truthfulness_context(self) -> str:
        """진실성 강조 컨텍스트 생성"""
        return """🎯 **CORE PRINCIPLES FOR THIS WORKSPACE:**

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

    def get_current_workspace_id(self) -> Optional[str]:
        """Get current workspace identifier"""
        return self.current_workspace

    def add_conversation(self, user_message: str, ai_response: str) -> bool:
        """Add conversation to SQLite database"""
        workspace_id = self.get_current_workspace_id()
        if not workspace_id:
            raise ValueError("Workspace not set. Please start a workspace first.")

        try:
            # 메타데이터 분석
            metadata = self._analyze_conversation_content(user_message, ai_response)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 대화 저장
            cursor.execute('''
                           INSERT INTO conversations
                           (workspace_id, user_message, ai_response, timestamp, importance_score, metadata)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''', (
                               workspace_id,
                               user_message,
                               ai_response,
                               datetime.now().isoformat(),
                               metadata.get("importance_score", 0),
                               json.dumps(metadata)
                           ))

            conn.commit()
            conn.close()

            self._log(f"Conversation stored: {len(user_message)}+{len(ai_response)} chars")
            return True

        except Exception as e:
            self._log(f"Failed to store conversation: {str(e)}", "ERROR")
            return False

    def _analyze_conversation_content(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """대화 내용 분석"""
        try:
            # 파일 언급 감지
            file_patterns = [r'\.[a-zA-Z]{2,4}(?:\s|$)', r'/[\w/]+', r'[\w]+\.[\w]+']
            files_mentioned = []
            conversation_text = f"{user_message} {ai_response}"

            for pattern in file_patterns:
                matches = re.findall(pattern, conversation_text)
                files_mentioned.extend(matches)

            # 코드 블록 감지
            code_blocks = len(re.findall(r'```', ai_response))

            # 작업 유형 감지
            task_keywords = {
                'file_operation': ['읽어', 'read', 'open', 'save', 'write'],
                'code_analysis': ['분석', 'analyze', 'review', 'examine'],
                'modification': ['수정', 'modify', 'change', 'update', 'fix'],
                'creation': ['생성', 'create', 'make', 'build', 'implement'],
                'testing': ['테스트', 'test', 'run', 'execute', 'debug'],
                'explanation': ['설명', 'explain', 'describe', 'how', 'what'],
                'problem_solving': ['문제', 'error', 'issue', 'bug', 'solve']
            }

            detected_tasks = []
            for task_type, keywords in task_keywords.items():
                if any(keyword in conversation_text.lower() for keyword in keywords):
                    detected_tasks.append(task_type)

            # 중요도 점수 계산
            importance_score = len(detected_tasks) * 2 + len(files_mentioned) + code_blocks

            return {
                "detected_tasks": detected_tasks,
                "files_mentioned": list(set(files_mentioned)) if files_mentioned else [],
                "code_blocks_count": code_blocks,
                "importance_score": importance_score,
                "user_message_length": len(user_message),
                "ai_response_length": len(ai_response),
                "total_length": len(user_message) + len(ai_response)
            }

        except Exception as e:
            self._log(f"Warning: Content analysis failed: {str(e)}", "WARNING")
            return {
                "user_message_length": len(user_message),
                "ai_response_length": len(ai_response),
                "total_length": len(user_message) + len(ai_response)
            }

    def search_memory_by_workspace_id(self, workspace_id: str, query: str = "", limit: int = 10) -> Dict[str, Any]:
        """Search conversation memory by workspace ID using SQLite + FTS5"""
        self._log(f"Searching memory for workspace '{workspace_id}': '{query}' (limit: {limit})")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if query.strip():
                # FTS5 전문 검색
                cursor.execute('''
                               SELECT c.id,
                                      c.user_message,
                                      c.ai_response,
                                      c.timestamp,
                                      c.importance_score,
                                      c.metadata,
                                      rank
                               FROM conversations_fts
                                        JOIN conversations c ON conversations_fts.rowid = c.id
                               WHERE conversations_fts MATCH ?
                                 AND c.workspace_id = ?
                               ORDER BY rank LIMIT ?
                               ''', (query, workspace_id, limit))

                search_type = "fts_search"
            else:
                # 전체 대화 조회
                cursor.execute('''
                               SELECT id, user_message, ai_response, timestamp, importance_score, metadata, 0 as rank
                               FROM conversations
                               WHERE workspace_id = ?
                               ORDER BY timestamp DESC
                                   LIMIT ?
                               ''', (workspace_id, limit))

                search_type = "all_conversations"

            results = cursor.fetchall()

            search_results = []
            for row in results:
                try:
                    metadata = json.loads(row[5]) if row[5] else {}
                except:
                    metadata = {}

                search_results.append({
                    "id": row[0],
                    "user_message": row[1],
                    "ai_response": row[2],
                    "timestamp": row[3],
                    "importance_score": row[4],
                    "metadata": metadata,
                    "rank": row[6] if len(row) > 6 else 0
                })

            conn.close()

            self._log(f"Search completed: {len(search_results)} results found")

            return {
                "results": search_results,
                "stats": {
                    "query": query,
                    "total_found": len(search_results),
                    "workspace": workspace_id,
                    "limit": limit,
                    "search_type": search_type
                }
            }

        except Exception as e:
            conn.close()
            self._log(f"Search error: {str(e)}", "ERROR")
            return {
                "results": [],
                "stats": {
                    "query": query,
                    "total_found": 0,
                    "workspace": workspace_id,
                    "limit": limit,
                    "search_type": "error",
                    "error": str(e)
                }
            }

    def list_all_workspaces(self) -> List[Dict[str, Any]]:
        """List all available workspaces with detailed information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                           SELECT w.workspace_id,
                                  w.description,
                                  w.created_at,
                                  w.updated_at,
                                  COUNT(c.id) as conversation_count
                           FROM workspaces w
                                    LEFT JOIN conversations c ON w.workspace_id = c.workspace_id
                           GROUP BY w.workspace_id, w.description, w.created_at, w.updated_at
                           ORDER BY w.updated_at DESC
                           ''')

            results = cursor.fetchall()
            workspaces = []

            for row in results:
                workspaces.append({
                    "workspace_id": row[0],
                    "description": row[1],
                    "created_at": row[2],
                    "updated_at": row[3],
                    "conversation_count": row[4]
                })

            conn.close()
            self._log(f"Found {len(workspaces)} workspaces")
            return workspaces

        except Exception as e:
            conn.close()
            self._log(f"Error listing workspaces: {str(e)}", "ERROR")
            return []

    def resume_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Resume an existing workspace with full conversation history loaded"""
        self._log(f"Resuming workspace: {workspace_id}")

        # 워크스페이스 존재 확인
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT workspace_id, description, created_at FROM workspaces WHERE workspace_id = ?",
            (workspace_id,)
        )

        workspace_info = cursor.fetchone()
        if not workspace_info:
            conn.close()
            error_msg = f"Workspace '{workspace_id}' not found"
            self._log(error_msg, "ERROR")
            raise ValueError(error_msg)

        # 워크스페이스 재개
        self.current_workspace = workspace_id

        # 전체 대화 히스토리 로드
        cursor.execute('''
                       SELECT user_message, ai_response, timestamp, importance_score, metadata
                       FROM conversations
                       WHERE workspace_id = ?
                       ORDER BY timestamp ASC
                       ''', (workspace_id,))

        conversations = []
        context_messages = []

        for row in cursor.fetchall():
            try:
                metadata = json.loads(row[4]) if row[4] else {}
            except:
                metadata = {}

            conv = {
                "user_message": row[0],
                "ai_response": row[1],
                "timestamp": row[2],
                "importance_score": row[3],
                "metadata": metadata
            }
            conversations.append(conv)

            # LLM context용 대화 문자열 생성
            context_messages.append(f"User: {row[0]}")
            context_messages.append(f"Assistant: {row[1]}")

        conn.close()

        context_length = sum(len(msg) for msg in context_messages)

        result = {
            "workspace_id": workspace_id,
            "description": workspace_info[1],
            "created_at": workspace_info[2],
            "conversation_count": len(conversations),
            "full_history": conversations,
            "context_messages": context_messages,
            "context_length": context_length,
            "estimated_tokens": context_length // 4,
            "is_resumed": True
        }

        self._log(f"Workspace resumed: {workspace_id} ({len(conversations)} conversations, {context_length} chars)")
        return result

    def get_workspace_conversations(self, workspace_id: str) -> Dict[str, Any]:
        """Get all conversations from a workspace"""
        self._log(f"Loading conversations for workspace: {workspace_id}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                           SELECT user_message, ai_response, timestamp, importance_score, metadata
                           FROM conversations
                           WHERE workspace_id = ?
                           ORDER BY timestamp ASC
                           ''', (workspace_id,))

            conversations = []
            for row in cursor.fetchall():
                try:
                    metadata = json.loads(row[4]) if row[4] else {}
                except:
                    metadata = {}

                conversations.append({
                    "user_message": row[0],
                    "ai_response": row[1],
                    "timestamp": row[2],
                    "importance_score": row[3],
                    "metadata": metadata,
                    "content": f"User: {row[0]}\nAI: {row[1]}"
                })

            conn.close()

            result = {
                "conversations": conversations,
                "stats": {
                    "total_conversations": len(conversations),
                    "workspace_id": workspace_id,
                    "context_length": sum(len(c["user_message"]) + len(c["ai_response"]) for c in conversations)
                }
            }

            self._log(f"Loaded {len(conversations)} conversations from workspace: {workspace_id}")
            return result

        except Exception as e:
            conn.close()
            self._log(f"Error loading conversations: {str(e)}", "ERROR")
            return {
                "conversations": [],
                "stats": {
                    "total_conversations": 0,
                    "workspace_id": workspace_id,
                    "context_length": 0,
                    "error": str(e)
                }
            }

    def delete_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Delete workspace and all related data"""
        self._log(f"Deleting workspace: {workspace_id}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 대화 수 확인
            cursor.execute(
                "SELECT COUNT(*) FROM conversations WHERE workspace_id = ?",
                (workspace_id,)
            )
            conversation_count = cursor.fetchone()[0]

            # 대화 삭제
            cursor.execute(
                "DELETE FROM conversations WHERE workspace_id = ?",
                (workspace_id,)
            )

            # 워크스페이스 삭제
            cursor.execute(
                "DELETE FROM workspaces WHERE workspace_id = ?",
                (workspace_id,)
            )

            conn.commit()
            conn.close()

            # 현재 워크스페이스가 삭제된 워크스페이스이면 초기화
            if self.current_workspace == workspace_id:
                self.current_workspace = None

            deleted_items = {
                "workspace_metadata": True,
                "conversations": conversation_count,
                "context_data": 0
            }

            self._log(f"Workspace '{workspace_id}' deleted: {conversation_count} conversations")
            return deleted_items

        except Exception as e:
            conn.close()
            self._log(f"Error deleting workspace: {str(e)}", "ERROR")
            return {
                "workspace_metadata": False,
                "conversations": 0,
                "context_data": 0,
                "error": str(e)
            }

    def cleanup_old_workspaces(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old workspaces"""
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 오래된 워크스페이스 찾기
            cursor.execute(
                "SELECT workspace_id FROM workspaces WHERE created_at < ?",
                (cutoff_iso,)
            )

            old_workspaces = [row[0] for row in cursor.fetchall()]

            cleanup_stats = {
                "workspaces_deleted": 0,
                "conversations_deleted": 0,
                "cutoff_date": cutoff_iso
            }

            for workspace_id in old_workspaces:
                deleted_items = self.delete_workspace(workspace_id)
                cleanup_stats["workspaces_deleted"] += 1
                cleanup_stats["conversations_deleted"] += deleted_items.get("conversations", 0)

            conn.close()

            self._log(f"Cleanup complete: {cleanup_stats['workspaces_deleted']} workspaces")
            return cleanup_stats

        except Exception as e:
            conn.close()
            self._log(f"Error during cleanup: {str(e)}", "ERROR")
            return {
                "workspaces_deleted": 0,
                "conversations_deleted": 0,
                "cutoff_date": cutoff_iso,
                "error": str(e)
            }

    def get_storage_stats(self) -> Dict[str, Any]:
        """Return storage statistics information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 워크스페이스 수
            cursor.execute("SELECT COUNT(*) FROM workspaces")
            total_workspaces = cursor.fetchone()[0]

            # 대화 수
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]

            conn.close()

            # 파일 크기
            try:
                file_size = os.path.getsize(self.db_path)
                storage_size_mb = round(file_size / (1024 * 1024), 2)
            except:
                storage_size_mb = "unknown"

            return {
                "total_workspaces": total_workspaces,
                "total_conversations": total_conversations,
                "storage_type": "sqlite_fts5",
                "current_workspace": self.current_workspace,
                "storage_size_mb": storage_size_mb,
                "database_path": self.db_path
            }

        except Exception as e:
            conn.close()
            self._log(f"Error getting storage stats: {str(e)}", "ERROR")
            return {
                "total_workspaces": 0,
                "total_conversations": 0,
                "storage_type": "sqlite_fts5",
                "current_workspace": self.current_workspace,
                "error": str(e)
            }

    def get_context_info(self) -> Dict[str, Any]:
        """Get current context information"""
        return {
            "workspace_id": self.get_current_workspace_id(),
            "is_active": self.get_current_workspace_id() is not None,
            "storage_type": "sqlite_fts5"
        }
