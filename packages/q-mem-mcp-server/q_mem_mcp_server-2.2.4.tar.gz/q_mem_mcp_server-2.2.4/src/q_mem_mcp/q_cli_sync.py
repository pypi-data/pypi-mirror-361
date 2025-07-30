"""
Q CLI SQLite Database Real-time Sync - Immediate Synchronization
워크스페이스 시작/재개 시 즉시 Q CLI DB를 조회하여 실시간 동기화
"""

import json
import os
import sqlite3
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, List


class QCLISync:
    """Q CLI SQLite 실시간 동기화 - 타이머 없이 즉시 처리"""
    
    def __init__(self, memory_manager=None):
        self.q_cli_db_path: Optional[Path] = None
        self.last_sync_timestamp = None
        self.current_workspace_id = None
        self.memory_manager = memory_manager
        self.verbose = os.getenv('Q_MEM_VERBOSE', 'true').lower() == 'true'
        self.sync_lock = threading.Lock()
        
        # Q CLI DB 경로 찾기
        self.q_cli_db_path = self.find_q_cli_database()
        
        if self.verbose and self.q_cli_db_path:
            print(f"✅ Q CLI DB found: {self.q_cli_db_path}")
        elif self.verbose:
            print("⚠️ Q CLI DB not found - sync will be disabled")
    
    def find_q_cli_database(self) -> Optional[Path]:
        """Q CLI SQLite 데이터베이스 경로 탐지"""
        
        # 1순위: 환경변수
        env_path = os.getenv('Q_CLI_DB_PATH')
        if env_path:
            path = Path(env_path).expanduser()
            if path.exists():
                return path
        
        # 2순위: 기본 경로
        primary_path = Path.home() / "Library/Application Support/amazon-q/data.sqlite3"
        if primary_path.exists():
            return primary_path
        
        # 3순위: 실행 중인 프로세스에서 탐지
        try:
            result = subprocess.run(['lsof', '-c', 'q'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'data.sqlite3' in line:
                    path_str = line.split()[-1]
                    path = Path(path_str)
                    if path.exists():
                        return path
        except Exception:
            pass
        
        return None
    
    def start_immediate_sync(self, workspace_id: str):
        """워크스페이스 시작 시 즉시 동기화 시작"""
        if not self.q_cli_db_path:
            if self.verbose:
                print("❌ Q CLI database not found - sync disabled")
            return
        
        self.current_workspace_id = workspace_id
        
        if self.verbose:
            print(f"🚀 Starting immediate Q CLI sync")
            print(f"📍 Database: {self.q_cli_db_path}")
            print(f"🔄 Workspace: {workspace_id}")
        
        # 즉시 첫 번째 동기화 실행
        self.sync_now()
        
        # 백그라운드에서 주기적 체크 시작 (가벼운 체크)
        self._start_background_monitor()
    
    def sync_now(self):
        """즉시 동기화 실행"""
        if not self.sync_lock.acquire(blocking=False):
            if self.verbose:
                print("⚠️ Sync already in progress")
            return
        
        try:
            self._perform_immediate_sync()
        except Exception as e:
            if self.verbose:
                print(f"❌ Sync error: {e}")
        finally:
            self.sync_lock.release()
    
    def _perform_immediate_sync(self):
        """실제 동기화 작업 수행"""
        if not self.q_cli_db_path or not self.current_workspace_id:
            return
        
        try:
            workspace_key = str(Path.cwd())
            
            # Q CLI DB 연결
            conn = sqlite3.connect(self.q_cli_db_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            
            cursor = conn.execute(
                "SELECT value FROM conversations WHERE key = ?", 
                [workspace_key]
            )
            
            result = cursor.fetchone()
            if not result:
                conn.close()
                return
            
            conversation_data = json.loads(result[0])
            messages = conversation_data.get('history', [])
            
            # 새로운 메시지만 처리 (타임스탬프 기반)
            new_messages = self._filter_new_messages(messages)
            
            if new_messages:
                success_count = self._process_new_messages(new_messages)
                
                if self.verbose and success_count > 0:
                    print(f"🔄 Synced {success_count} new conversations")
            
            conn.close()
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Sync operation failed: {e}")
    
    def _filter_new_messages(self, messages: List) -> List:
        """새로운 메시지만 필터링 (타임스탬프 기반)"""
        if not self.last_sync_timestamp:
            # 첫 동기화: 최근 10개 메시지만 처리
            self.last_sync_timestamp = time.time()
            return messages[-10:] if len(messages) > 10 else messages
        
        # 마지막 동기화 이후 메시지만 처리
        new_messages = []
        current_time = time.time()
        
        # 간단한 휴리스틱: 메시지 순서 기반으로 새 메시지 감지
        # (Q CLI는 메시지를 순차적으로 추가하므로)
        if hasattr(self, '_last_message_count'):
            if len(messages) > self._last_message_count:
                new_messages = messages[self._last_message_count:]
        else:
            # 첫 실행시 최근 5개만
            new_messages = messages[-5:] if len(messages) > 5 else messages
        
        self._last_message_count = len(messages)
        self.last_sync_timestamp = current_time
        
        return new_messages
    
    def _process_new_messages(self, new_messages: List) -> int:
        """새로운 메시지들을 처리하여 SQLite에 저장"""
        conversations = self._match_prompts_and_responses(new_messages)
        
        success_count = 0
        for user_msg, ai_msg in conversations:
            try:
                if self.memory_manager:
                    success = self.memory_manager.add_conversation(user_msg, ai_msg)
                    if success:
                        success_count += 1
                        
            except Exception as e:
                if self.verbose:
                    print(f"❌ Failed to save conversation: {e}")
        
        return success_count
    
    def _match_prompts_and_responses(self, messages: List) -> List[tuple[str, str]]:
        """Prompt와 Response를 매칭하여 대화 쌍 생성 - ToolUseResults 구조도 지원"""
        conversations = []
        
        for message in messages:
            if not isinstance(message, list) or len(message) != 2:
                continue
                
            user_part, ai_part = message
            
            # 사용자 메시지 추출
            user_msg = None
            if (isinstance(user_part, dict) and 
                'content' in user_part and 
                isinstance(user_part['content'], dict)):
                
                # 기존 Prompt 구조 처리
                if 'Prompt' in user_part['content']:
                    prompt_data = user_part['content']['Prompt']
                    if isinstance(prompt_data, dict) and 'prompt' in prompt_data:
                        user_msg = prompt_data['prompt']
                
                # ToolUseResults 구조 처리 (도구 사용 대화)
                elif 'ToolUseResults' in user_part['content']:
                    tool_results = user_part['content']['ToolUseResults']
                    if isinstance(tool_results, dict):
                        # tool_use_result에서 원본 사용자 질문 추출 시도
                        if 'tool_use_result' in tool_results:
                            # 이전 메시지에서 사용자 질문을 찾거나 도구 사용 컨텍스트 활용
                            user_msg = self._extract_user_message_from_tool_context(user_part, message)
            
            # AI 응답 추출 - Response와 ToolUse 구조 모두 지원
            ai_msg = None
            if isinstance(ai_part, dict):
                # 기존 Response 구조
                if 'Response' in ai_part:
                    response_data = ai_part['Response']
                    if isinstance(response_data, dict) and 'content' in response_data:
                        ai_msg = response_data['content']
                # ToolUse 구조 (도구 사용 응답)
                elif 'ToolUse' in ai_part:
                    tool_use_data = ai_part['ToolUse']
                    if isinstance(tool_use_data, dict) and 'content' in tool_use_data:
                        ai_msg = tool_use_data['content']
            
            # 둘 다 있으면 대화 쌍으로 저장
            if user_msg and ai_msg:
                conversations.append((user_msg, ai_msg))
                
                if self.verbose:
                    print(f"💬 New conversation: {user_msg[:50]}... → {ai_msg[:50]}...")
        
        return conversations
    
    def _extract_user_message_from_tool_context(self, user_part: dict, message: list) -> str:
        """ToolUseResults에서 원본 사용자 질문 추출"""
        try:
            # 1. additional_context에서 사용자 질문 추출 시도
            if 'additional_context' in user_part:
                context = user_part['additional_context']
                if isinstance(context, str):
                    # USER MESSAGE BEGIN/END 패턴 찾기
                    patterns = [
                        ('--- USER MESSAGE BEGIN ---', '--- USER MESSAGE END ---'),
                        ('USER MESSAGE BEGIN', 'USER MESSAGE END'),
                        ('User:', '\n'),  # 간단한 User: 패턴
                    ]
                    
                    for start_marker, end_marker in patterns:
                        start_idx = context.find(start_marker)
                        if start_idx != -1:
                            start_idx += len(start_marker)
                            end_idx = context.find(end_marker, start_idx)
                            if end_idx != -1:
                                user_msg = context[start_idx:end_idx].strip()
                                if user_msg and len(user_msg) > 0:
                                    return user_msg
            
            # 2. env_context에서 현재 작업 디렉토리 기반 추정
            if 'env_context' in user_part:
                env_context = user_part['env_context']
                if isinstance(env_context, dict) and 'env_state' in env_context:
                    cwd = env_context['env_state'].get('current_working_directory', '')
                    if cwd:
                        return f"[작업 디렉토리: {cwd}에서의 도구 사용 대화]"
            
            # 3. tool_use_results 내용 기반 추정 (복수형 키 지원)
            tool_results = user_part.get('content', {}).get('ToolUseResults', {})
            if isinstance(tool_results, dict):
                # tool_use_results (복수형) 우선 확인
                if 'tool_use_results' in tool_results:
                    results_content = str(tool_results['tool_use_results'])
                    # 도구 사용 결과에서 힌트 추출
                    if 'fs_read' in results_content:
                        return "[파일 읽기 요청]"
                    elif 'execute_bash' in results_content:
                        return "[명령어 실행 요청]"
                    elif 'search' in results_content:
                        return "[검색 요청]"
                    elif 'sqlite3' in results_content or 'database' in results_content:
                        return "[데이터베이스 조회 요청]"
                    else:
                        return f"[도구 사용 대화]: {results_content}"
                # tool_use_result (단수형) 백업 지원
                elif 'tool_use_result' in tool_results:
                    result_content = str(tool_results['tool_use_result'])
                    if 'fs_read' in result_content:
                        return "[파일 읽기 요청]"
                    elif 'execute_bash' in result_content:
                        return "[명령어 실행 요청]"
                    elif 'search' in result_content:
                        return "[검색 요청]"
                    else:
                        return f"[도구 사용 대화]: {result_content}"
            
            # 4. 기본값
            return "[도구 사용 대화 - 사용자 질문 추출 실패]"
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Failed to extract user message from tool context: {e}")
            return "[도구 사용 대화 - 파싱 오류]"
    
    def _start_background_monitor(self):
        """백그라운드 모니터링 시작 (10초 간격)"""
        def monitor():
            while self.current_workspace_id:
                try:
                    time.sleep(10)  # 10초마다 체크
                    if self.current_workspace_id:  # 여전히 활성 상태인지 확인
                        self.sync_now()
                except Exception as e:
                    if self.verbose:
                        print(f"Background monitor error: {e}")
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
        if self.verbose:
            print("🔍 Background monitor started (10s interval)")
    
    def stop_sync(self):
        """동기화 중지"""
        self.current_workspace_id = None
        if self.verbose:
            print("🛑 Q CLI sync stopped")

    def get_status(self) -> Dict[str, Any]:
        """동기화 상태 반환"""
        return {
            "running": self.current_workspace_id is not None,
            "q_cli_db_path": str(self.q_cli_db_path) if self.q_cli_db_path else None,
            "current_workspace": self.current_workspace_id,
            "last_sync_timestamp": self.last_sync_timestamp,
            "sync_type": "immediate_realtime",
            "database_accessible": self.q_cli_db_path is not None and self.q_cli_db_path.exists()
        }


# 전역 동기화 인스턴스
_sync_instance: Optional[QCLISync] = None


def get_sync_instance(memory_manager=None) -> QCLISync:
    """동기화 인스턴스 반환"""
    global _sync_instance
    
    if _sync_instance is None:
        _sync_instance = QCLISync(memory_manager)
    
    return _sync_instance


def start_immediate_sync(workspace_id: str, memory_manager=None):
    """워크스페이스 시작 시 즉시 동기화 시작"""
    sync_instance = get_sync_instance(memory_manager)
    sync_instance.start_immediate_sync(workspace_id)


def stop_sync():
    """동기화 중지"""
    global _sync_instance
    if _sync_instance:
        _sync_instance.stop_sync()

def get_sync_status() -> Dict[str, Any]:
    """동기화 상태 조회"""
    global _sync_instance
    if _sync_instance:
        return _sync_instance.get_status()
    return {"running": False, "sync_type": "not_initialized"}
