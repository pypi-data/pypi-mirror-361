"""
Q CLI SQLite Database Sync Daemon
Monitors Q CLI's SQLite database and automatically syncs conversations to ChromaDB
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


class QCLISyncDaemon:
    """Q CLI SQLite 데이터베이스 감시 및 ChromaDB 자동 동기화"""
    
    def __init__(self, memory_manager=None):
        self.q_cli_db_path: Optional[Path] = None
        self.last_message_count = 0
        self.current_session_id = None
        self.sync_thread = None
        self.running = False
        self.memory_manager = memory_manager
        self.verbose = os.getenv('Q_MEM_VERBOSE', 'true').lower() == 'true'  # 기본값을 true로 변경
        
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
    
    def _save_sync_state(self):
        """현재 동기화 상태 저장"""
        try:
            state = {
                'session_id': self.current_session_id,
                'last_message_count': self.last_message_count,
                'timestamp': time.time(),
                'q_cli_db_path': str(self.q_cli_db_path) if self.q_cli_db_path else None,
                'retry_queue_size': len(getattr(self, 'retry_queue', []))
            }
            
            state_file = self._get_sync_state_file()
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            if self.verbose:
                print(f"💾 Sync state saved: {state}")
                
        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to save sync state: {e}")
    
    def _restore_sync_state(self):
        """저장된 동기화 상태 복원"""
        try:
            state_file = self._get_sync_state_file()
            
            if not state_file.exists():
                if self.verbose:
                    print("ℹ️ No previous sync state found")
                return False
            
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # 상태가 너무 오래된 경우 (1시간 이상) 무시
            if time.time() - state.get('timestamp', 0) > 3600:
                if self.verbose:
                    print("⚠️ Sync state too old, starting fresh")
                return False
            
            # 세션 ID가 다른 경우 무시
            if state.get('session_id') != self.current_session_id:
                if self.verbose:
                    print("ℹ️ Different session, starting fresh")
                return False
            
            # 상태 복원
            self.last_message_count = state.get('last_message_count', 0)
            
            if self.verbose:
                print(f"🔄 Sync state restored: last_count={self.last_message_count}")
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to restore sync state: {e}")
            return False
    
    def start_sync_daemon(self, session_id: str):
        """세션 시작/재개 시 데몬 시작 (상태 복구 포함)"""
        
        if not self.q_cli_db_path:
            self.q_cli_db_path = self.find_q_cli_database()
            if not self.q_cli_db_path:
                raise Exception("Q CLI database not found. Set Q_CLI_DB_PATH environment variable.")
        
        self.current_session_id = session_id
        self.running = True
        
        if self.verbose:
            print(f"🚀 Starting Q CLI sync daemon")
            print(f"📍 Database: {self.q_cli_db_path}")
            print(f"🔄 Session: {session_id}")
        
        # 상태 복구 시도
        if not self._restore_sync_state():
            # 상태 복구 실패 시 현재 메시지 수 초기화
            self._initialize_message_count()
        
        # 백그라운드 스레드 시작
        self.sync_thread = threading.Thread(
            target=self.monitor_q_cli_database, 
            daemon=True
        )
        self.sync_thread.start()
    
    def stop_sync_daemon(self):
        """동기화 데몬 중지 (상태 저장 포함)"""
        self.running = False
        
        # 현재 상태 저장
        self._save_sync_state()
        
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)
        
        if self.verbose:
            print("🛑 Q CLI sync daemon stopped")
    
    def _initialize_message_count(self):
        """현재 메시지 수 초기화"""
        try:
            current_cwd = str(Path.cwd())
            conn = sqlite3.connect(self.q_cli_db_path)
            cursor = conn.execute(
                "SELECT value FROM conversations WHERE key = ?", 
                [current_cwd]
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
    
    def _connect_with_wal(self, db_path):
        """WAL 모드로 Q CLI SQLite 데이터베이스 연결"""
        conn = sqlite3.connect(db_path)
        
        try:
            # WAL 모드 설정
            cursor = conn.execute("PRAGMA journal_mode=WAL")
            mode = cursor.fetchone()[0]
            
            # 성능 최적화 설정
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=memory")
            
            if self.verbose:
                print(f"✅ SQLite connected in {mode} mode")
                
        except sqlite3.Error as e:
            if self.verbose:
                print(f"⚠️ WAL mode setup failed: {e}, using default mode")
        
        return conn
    
    def monitor_q_cli_database(self):
        """Q CLI SQLite 실시간 감시 (WAL 모드 + 강화 로직)"""
        
        consecutive_failures = 0
        last_health_check = time.time()
        
        while self.running:
            try:
                current_cwd = str(Path.cwd())
                
                # WAL 모드로 연결
                conn = self._connect_with_wal(self.q_cli_db_path)
                cursor = conn.execute(
                    "SELECT value FROM conversations WHERE key = ?", 
                    [current_cwd]
                )
                
                result = cursor.fetchone()
                if result:
                    conversation_data = json.loads(result[0])
                    current_message_count = len(conversation_data.get('history', []))
                    
                    # 새로운 메시지 감지
                    if current_message_count > self.last_message_count:
                        new_messages = conversation_data['history'][self.last_message_count:]
                        
                        # 부분 실패 처리로 동기화
                        success_count = self._sync_with_partial_failure_handling(new_messages)
                        
                        if success_count > 0:
                            self.last_message_count = current_message_count
                            consecutive_failures = 0  # 성공 시 실패 카운터 리셋
                            
                            if self.verbose:
                                print(f"🔄 Synced {success_count}/{len(new_messages)} messages")
                
                conn.close()
                
                # 헬스체크 (5분마다)
                if time.time() - last_health_check > 300:
                    self._perform_health_check()
                    last_health_check = time.time()
                
                time.sleep(2)  # 2초마다 체크
                
            except Exception as e:
                consecutive_failures += 1
                
                if self.verbose:
                    print(f"❌ Sync daemon error (failure #{consecutive_failures}): {e}")
                
                # 연속 실패 시 자동 복구
                if consecutive_failures >= 3:
                    if self.verbose:
                        print(f"🔧 Attempting auto-recovery after {consecutive_failures} failures")
                    
                    self._attempt_auto_recovery()
                    consecutive_failures = 0
                
    def _perform_health_check(self):
        """헬스체크 수행"""
        try:
            if self.verbose:
                print("🔍 Performing health check...")
            
            # 1. Q CLI DB 접근 가능성 확인
            conn = self._connect_with_wal(self.q_cli_db_path)
            cursor = conn.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]
            conn.close()
            
            # 2. ChromaDB 접근 가능성 확인
            if self.memory_manager:
                stats = self.memory_manager.get_storage_stats()
                chromadb_conversations = stats.get('total_conversations', 0)
            else:
                chromadb_conversations = 0
            
            # 3. 동기화 상태 점검
            current_cwd = str(Path.cwd())
            conn = self._connect_with_wal(self.q_cli_db_path)
            cursor = conn.execute("SELECT value FROM conversations WHERE key = ?", [current_cwd])
            result = cursor.fetchone()
            
            if result:
                conversation_data = json.loads(result[0])
                q_cli_message_count = len(conversation_data.get('history', []))
                
                # 동기화 지연 감지 (Q CLI 메시지가 훨씬 많으면 문제)
                if q_cli_message_count > self.last_message_count + 10:
                    if self.verbose:
                        print(f"⚠️ Sync lag detected: Q CLI has {q_cli_message_count}, synced {self.last_message_count}")
                    
                    # 자동 복구 트리거
                    self._attempt_auto_recovery()
            
            conn.close()
            
            # 4. 재시도 큐 처리
            self._process_retry_queue()
            
            if self.verbose:
                print(f"✅ Health check completed - Q CLI: {total_conversations}, ChromaDB: {chromadb_conversations}")
                
        except Exception as e:
            if self.verbose:
                print(f"❌ Health check failed: {e}")
    
    def _attempt_auto_recovery(self):
        """자동 복구 시도"""
        try:
            if self.verbose:
                print("🔧 Starting auto-recovery...")
            
            # 1. 현재 상태 저장
            self._save_sync_state()
            
            # 2. 강제 동기화 수행
            current_cwd = str(Path.cwd())
            conn = self._connect_with_wal(self.q_cli_db_path)
            cursor = conn.execute("SELECT value FROM conversations WHERE key = ?", [current_cwd])
            
            result = cursor.fetchone()
            if result:
                conversation_data = json.loads(result[0])
                all_messages = conversation_data.get('history', [])
                
                # 마지막 동기화 지점부터 다시 동기화
                if self.last_message_count < len(all_messages):
                    missed_messages = all_messages[self.last_message_count:]
                    
                    if self.verbose:
                        print(f"🔄 Re-syncing {len(missed_messages)} missed messages")
                    
                    success_count = self._sync_with_partial_failure_handling(missed_messages)
                    
                    if success_count > 0:
                        self.last_message_count = len(all_messages)
                        
                        if self.verbose:
                            print(f"✅ Auto-recovery completed: {success_count} messages recovered")
            
            conn.close()
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Auto-recovery failed: {e}")
    
    def _sync_with_partial_failure_handling(self, new_messages: List) -> int:
        """부분 실패 처리로 새로운 메시지들을 ChromaDB에 저장"""
        
        # Prompt와 Response를 매칭하여 대화 쌍 생성
        conversations = self.match_prompts_and_responses(new_messages)
        
        success_count = 0
        failed_conversations = []
        
        for i, (user_msg, ai_msg) in enumerate(conversations):
            try:
                # ChromaDB에 직접 저장
                success = self.save_to_chromadb_directly(user_msg, ai_msg)
                if success:
                    success_count += 1
                else:
                    failed_conversations.append((i, user_msg, ai_msg, "Save returned False"))
                    
            except Exception as e:
                failed_conversations.append((i, user_msg, ai_msg, str(e)))
                if self.verbose:
                    print(f"❌ Failed to save conversation {i}: {e}")
        
        # 실패한 대화들을 재시도 큐에 추가
        if failed_conversations:
            self._add_to_retry_queue(failed_conversations)
            
            if self.verbose:
                print(f"⚠️ {len(failed_conversations)} conversations failed, added to retry queue")
        
        return success_count
    
    def _add_to_retry_queue(self, failed_conversations: List):
        """실패한 대화들을 재시도 큐에 추가"""
        if not hasattr(self, 'retry_queue'):
            self.retry_queue = []
        
        for failure_info in failed_conversations:
            retry_item = {
                'conversation_index': failure_info[0],
                'user_message': failure_info[1],
                'ai_response': failure_info[2],
                'error': failure_info[3],
                'retry_count': 0,
                'timestamp': time.time()
            }
            self.retry_queue.append(retry_item)
    
    def _process_retry_queue(self):
        """재시도 큐 처리"""
        if not hasattr(self, 'retry_queue') or not self.retry_queue:
            return
        
        processed_items = []
        
        for item in self.retry_queue[:]:  # 복사본으로 순회
            try:
                # 최대 3번까지 재시도
                if item['retry_count'] >= 3:
                    processed_items.append(item)
                    continue
                
                # 1분 이상 된 항목만 재시도
                if time.time() - item['timestamp'] < 60:
                    continue
                
                # 재시도 실행
                success = self.save_to_chromadb_directly(
                    item['user_message'], 
                    item['ai_response']
                )
                
                if success:
                    processed_items.append(item)
                    if self.verbose:
                        print(f"✅ Retry successful for conversation {item['conversation_index']}")
                else:
                    item['retry_count'] += 1
                    item['timestamp'] = time.time()
                    
            except Exception as e:
                item['retry_count'] += 1
                item['timestamp'] = time.time()
                item['error'] = str(e)
        
        # 처리된 항목들 제거
        for item in processed_items:
            if item in self.retry_queue:
                self.retry_queue.remove(item)
    
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
    
    def extract_message_pair(self, message_pair) -> tuple[Optional[str], Optional[str]]:
        """Q CLI 메시지 쌍에서 사용자/AI 메시지 추출"""
        
        try:
            if not isinstance(message_pair, list) or len(message_pair) != 2:
                return None, None
            
            user_part, ai_part = message_pair
            
            # 사용자 메시지 추출 (Prompt 타입)
            user_msg = None
            if isinstance(user_part, dict):
                content = user_part.get('content', {})
                if isinstance(content, dict) and 'Prompt' in content:
                    prompt_data = content['Prompt']
                    if isinstance(prompt_data, dict) and 'prompt' in prompt_data:
                        user_msg = prompt_data['prompt']
            
            # AI 메시지 추출 (Response 타입)
            ai_msg = None
            if isinstance(ai_part, dict):
                if 'Response' in ai_part:
                    response_data = ai_part['Response']
                    if isinstance(response_data, dict) and 'content' in response_data:
                        ai_msg = response_data['content']
            
            return user_msg, ai_msg
            
        except Exception as e:
            if self.verbose:
                print(f"Message extraction error: {e}")
            return None, None
    
    def save_to_chromadb_directly(self, user_message: str, ai_response: str) -> bool:
        """도구 호출 없이 직접 ChromaDB에 저장"""
        
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
        return {
            "running": self.running,
            "q_cli_db_path": str(self.q_cli_db_path) if self.q_cli_db_path else None,
            "current_session": self.current_session_id,
            "last_message_count": self.last_message_count,
            "thread_alive": self.sync_thread.is_alive() if self.sync_thread else False
        }


# 전역 데몬 인스턴스
_sync_daemon: Optional[QCLISyncDaemon] = None


def get_sync_daemon(memory_manager=None) -> QCLISyncDaemon:
    """동기화 데몬 인스턴스 반환"""
    global _sync_daemon
    
    if _sync_daemon is None:
        _sync_daemon = QCLISyncDaemon(memory_manager)
    
    return _sync_daemon
