"""
Q CLI SQLite Database Sync Daemon - Simplified Timer-based Implementation
Monitors Q CLI's SQLite database and automatically syncs conversations to ChromaDB using periodic timers
"""

import json
import os
import sqlite3
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Global timer instance
_sync_timer: Optional[threading.Timer] = None
_sync_lock = threading.Lock()  # Prevent concurrent sync operations
_embedding_model = None  # Global embedding model cache


class QCLISyncDaemon:
    """Q CLI SQLite 데이터베이스 감시 및 ChromaDB 자동 동기화 - 단순화된 타이머 기반"""
    
    def __init__(self, memory_manager=None):
        self.q_cli_db_path: Optional[Path] = None
        self.last_message_count = 0
        self.current_workspace_id = None
        self.memory_manager = memory_manager
        self.verbose = os.getenv('Q_MEM_VERBOSE', 'true').lower() == 'true'
        
        # 전역 임베딩 모델 초기화
        global _embedding_model
        if _embedding_model is None and memory_manager:
            try:
                from sentence_transformers import SentenceTransformer
                _embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                if self.verbose:
                    print("✅ Global embedding model initialized")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Failed to initialize embedding model: {e}")
        
    def find_q_cli_database(self) -> Optional[Path]:
        """Q CLI SQLite 데이터베이스 경로 탐지 (우선순위 적용)"""
        
        # 1순위: 환경변수에서 지정된 경로
        env_path = os.getenv('Q_CLI_DB_PATH')
        if env_path:
            path = Path(env_path).expanduser()
            if path.exists():
                if self.verbose:
                    print(f"✅ Using Q CLI DB from env: {path}")
                return path
            else:
                if self.verbose:
                    print(f"⚠️ Env path not found: {path}, falling back to auto-detection")
        
        # 2순위: 기본 경로
        primary_path = Path.home() / "Library/Application Support/amazon-q/data.sqlite3"
        if primary_path.exists():
            if self.verbose:
                print(f"✅ Using default Q CLI DB: {primary_path}")
            return primary_path
        
        # 3순위: 실행 중인 프로세스에서 탐지
        process_path = self.find_from_running_process()
        if process_path:
            if self.verbose:
                print(f"✅ Found Q CLI DB from process: {process_path}")
            return process_path
        
        if self.verbose:
            print("❌ Q CLI database not found in any location")
        return None
    
    def find_from_running_process(self) -> Optional[Path]:
        """실행 중인 Q CLI 프로세스에서 SQLite 파일 찾기"""
        try:
            result = subprocess.run(['lsof', '-c', 'q'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'data.sqlite3' in line:
                    path_str = line.split()[-1]
                    return Path(path_str)
        except Exception as e:
            if self.verbose:
                print(f"Process detection failed: {e}")
        return None
    
    def _get_sync_state_file(self):
        """동기화 상태 파일 경로 반환"""
        storage_dir = Path.home() / ".Q_mem"
        storage_dir.mkdir(exist_ok=True)
        return storage_dir / "sync_state.json"
    
    def _load_sync_state(self):
        """저장된 동기화 상태 로드"""
        try:
            state_file = self._get_sync_state_file()
            if not state_file.exists():
                return False
            
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # 상태가 너무 오래된 경우 (1시간 이상) 무시
            if time.time() - state.get('timestamp', 0) > 3600:
                if self.verbose:
                    print("⚠️ Sync state too old, starting fresh")
                return False
            
            # 워크스페이스 ID가 다른 경우 무시
            if state.get('workspace_id') != self.current_workspace_id:
                if self.verbose:
                    print("ℹ️ Different workspace, starting fresh")
                return False
            
            # 상태 복원
            self.last_message_count = state.get('last_message_count', 0)
            
            if self.verbose:
                print(f"🔄 Sync state loaded: last_count={self.last_message_count}")
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to load sync state: {e}")
            return False
    
    def _save_sync_state(self):
        """현재 동기화 상태 저장 (단순화)"""
        try:
            state = {
                'workspace_id': self.current_workspace_id,
                'last_message_count': self.last_message_count,
                'timestamp': time.time()
            }
            
            state_file = self._get_sync_state_file()
            with open(state_file, 'w') as f:
                json.dump(state, f)
                
        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to save sync state: {e}")
    
    def start_sync_daemon(self, workspace_id: str):
        """워크스페이스 시작/재개 시 타이머 기반 동기화 시작"""
        global _sync_timer
        
        # 기존 타이머 정리
        if _sync_timer:
            _sync_timer.cancel()
            if self.verbose:
                print("🛑 Previous sync timer cancelled")
        
        if not self.q_cli_db_path:
            self.q_cli_db_path = self.find_q_cli_database()
            if not self.q_cli_db_path:
                raise Exception("Q CLI database not found. Set Q_CLI_DB_PATH environment variable.")
        
        self.current_workspace_id = workspace_id
        
        if self.verbose:
            print(f"🚀 Starting Q CLI sync daemon (Timer-based)")
            print(f"📍 Database: {self.q_cli_db_path}")
            print(f"🔄 Workspace: {workspace_id}")
            print(f"⏰ Interval: 10 seconds")
        
        # 상태 로드
        if not self._load_sync_state():
            self._initialize_message_count()
        
        # 첫 번째 동기화 즉시 실행
        self._sync_once_and_schedule_next()
    
    def stop_sync_daemon(self):
        """동기화 데몬 중지"""
        global _sync_timer
        
        if _sync_timer:
            _sync_timer.cancel()
            _sync_timer = None
        
        # 현재 상태 저장
        self._save_sync_state()
        
        if self.verbose:
            print("🛑 Q CLI sync daemon stopped")
    
    def _initialize_message_count(self):
        """현재 메시지 수 초기화"""
        try:
            workspace_key = str(Path.cwd())
            conn = sqlite3.connect(self.q_cli_db_path)
            cursor = conn.execute(
                "SELECT value FROM conversations WHERE key = ?", 
                [workspace_key]
            )
            
            result = cursor.fetchone()
            if result:
                conversation_data = json.loads(result[0])
                self.last_message_count = len(conversation_data.get('history', []))
            else:
                self.last_message_count = 0
            
            conn.close()
            
            if self.verbose:
                print(f"📊 Initial message count: {self.last_message_count}")
                
        except Exception as e:
            if self.verbose:
                print(f"Failed to initialize message count: {e}")
            self.last_message_count = 0
    
    def _sync_once_and_schedule_next(self):
        """한 번 동기화 실행 후 다음 타이머 예약"""
        global _sync_timer
        
        # 동시 실행 방지
        if not _sync_lock.acquire(blocking=False):
            if self.verbose:
                print("⚠️ Sync already in progress, skipping this cycle")
            # 다음 타이머 예약
            _sync_timer = threading.Timer(10.0, self._sync_once_and_schedule_next)
            _sync_timer.start()
            return
        
        try:
            # 실제 동기화 작업 수행
            self._perform_sync()
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Sync error: {e}")
        finally:
            _sync_lock.release()
            
            # 다음 10초 후 타이머 예약
            _sync_timer = threading.Timer(10.0, self._sync_once_and_schedule_next)
            _sync_timer.start()
    
    def _perform_sync(self):
        """실제 동기화 작업 수행 (단순화된 버전)"""
        try:
            workspace_key = str(Path.cwd())
            
            # Q CLI DB 연결 (새로 생성)
            conn = sqlite3.connect(self.q_cli_db_path)
            
            # WAL 모드 설정
            try:
                cursor = conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA cache_size=10000")
            except sqlite3.Error:
                pass  # WAL 모드 실패해도 계속 진행
            
            cursor = conn.execute(
                "SELECT value FROM conversations WHERE key = ?", 
                [workspace_key]
            )
            
            result = cursor.fetchone()
            if result:
                conversation_data = json.loads(result[0])
                current_message_count = len(conversation_data.get('history', []))
                
                # 새로운 메시지 감지
                if current_message_count > self.last_message_count:
                    new_messages = conversation_data['history'][self.last_message_count:]
                    
                    # 새 메시지들 처리
                    success_count = self._process_new_messages(new_messages)
                    
                    if success_count > 0:
                        self.last_message_count = current_message_count
                        self._save_sync_state()  # 상태 저장
                        
                        if self.verbose:
                            print(f"🔄 Synced {success_count}/{len(new_messages)} messages")
            
            conn.close()
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Sync operation failed: {e}")
    
    def _process_new_messages(self, new_messages: List) -> int:
        """새로운 메시지들을 처리하여 ChromaDB에 저장"""
        # 메시지 파싱 (기존 로직 재사용)
        conversations = self.match_prompts_and_responses(new_messages)
        
        success_count = 0
        for user_msg, ai_msg in conversations:
            try:
                # ChromaDB에 직접 저장 (새 연결 사용)
                success = self.save_to_chromadb_directly(user_msg, ai_msg)
                if success:
                    success_count += 1
                    
            except Exception as e:
                if self.verbose:
                    print(f"❌ Failed to save conversation: {e}")
        
        return success_count
    
    def match_prompts_and_responses(self, messages: List) -> List[tuple[str, str]]:
        """Prompt와 Response를 매칭하여 대화 쌍 생성 - 실제 Q CLI 구조에 맞게 수정"""
        conversations = []
        
        for message in messages:
            if not isinstance(message, list) or len(message) != 2:
                continue
                
            user_part, ai_part = message
            
            # 사용자 메시지 추출 (Prompt)
            user_msg = None
            if (isinstance(user_part, dict) and 
                'content' in user_part and 
                isinstance(user_part['content'], dict) and 
                'Prompt' in user_part['content']):
                
                prompt_data = user_part['content']['Prompt']
                if isinstance(prompt_data, dict) and 'prompt' in prompt_data:
                    user_msg = prompt_data['prompt']
            
            # AI 응답 추출 (Response)
            ai_msg = None
            if (isinstance(ai_part, dict) and 'Response' in ai_part):
                response_data = ai_part['Response']
                if isinstance(response_data, dict) and 'content' in response_data:
                    ai_msg = response_data['content']
            
            # 둘 다 있으면 대화 쌍으로 저장
            if user_msg and ai_msg:
                conversations.append((user_msg, ai_msg))
                
                if self.verbose:
                    print(f"💬 Matched conversation: {user_msg[:50]}... → {ai_msg[:50]}...")
        
        return conversations
    
    def save_to_chromadb_directly(self, user_message: str, ai_response: str) -> bool:
        """도구 호출 없이 직접 ChromaDB에 저장 (새 연결 사용)"""
        
        if not self.memory_manager:
            return False
        
        try:
            # memory_manager의 add_conversation 메서드 사용
            success = self.memory_manager.add_conversation(user_message, ai_response)
            
            if success and self.verbose:
                print(f"💾 Auto-saved conversation via Q CLI sync")
            elif not success and self.verbose:
                print(f"❌ Failed to auto-save conversation")
            
            return success
                
        except Exception as e:
            if self.verbose:
                print(f"ChromaDB save error: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """동기화 데몬 상태 반환"""
        global _sync_timer
        
        return {
            "running": _sync_timer is not None,
            "q_cli_db_path": str(self.q_cli_db_path) if self.q_cli_db_path else None,
            "current_workspace": self.current_workspace_id,
            "last_message_count": self.last_message_count,
            "timer_active": _sync_timer is not None and _sync_timer.is_alive() if _sync_timer else False,
            "sync_type": "timer_based"
        }


# 전역 데몬 인스턴스
_sync_daemon: Optional[QCLISyncDaemon] = None


def get_sync_daemon(memory_manager=None) -> QCLISyncDaemon:
    """동기화 데몬 인스턴스 반환"""
    global _sync_daemon
    
    if _sync_daemon is None:
        _sync_daemon = QCLISyncDaemon(memory_manager)
    
    return _sync_daemon
