"""
Memory Manager using ChromaDB + HuggingFace for Amazon Q CLI
ChromaDB-only implementation - no fallback storage
"""

import json
import re
import os
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

import chromadb
from sentence_transformers import SentenceTransformer


class MemoryManager:
    """ChromaDB-only Memory Manager optimized for Amazon Q CLI"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, verbose: bool = False):
        """Initialize memory manager with ChromaDB implementation"""
        self.current_workspace: Optional[str] = None
        self.verbose = verbose
        
        # 로그 설정
        self._setup_logging()
        
        # ChromaDB 클라이언트 초기화 (단순화)
        self.db_path = os.path.expanduser("~/.Q_mem/chroma_db")
        os.makedirs(self.db_path, exist_ok=True)
        
        # 단일 ChromaDB 클라이언트 사용 (스레드 안전성 제거)
        self.chroma_client = chromadb.PersistentClient(path=self.db_path)
        
        # 임베딩 모델 초기화 (차원: 384)
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.embedding_dimension = 384
        
        # 컬렉션 초기화 (단순화)
        self.conversations_collection = self._get_or_create_conversations_collection()
        self.workspaces_collection = self._get_or_create_workspaces_collection()
        
        self._log("ChromaDB initialized successfully (simplified)")

    def _get_or_create_conversations_collection(self):
        """대화 컬렉션 생성/조회 (단순화)"""
        return self.chroma_client.get_or_create_collection(
            name="mcp_conversations",
            metadata={
                "description": "Amazon Q CLI conversations",
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": self.embedding_dimension,
                "hnsw:space": "cosine",
                "hnsw:M": 16,
                "hnsw:construction_ef": 200,
                "hnsw:search_ef": 50,
            }
        )
    
    def _get_or_create_workspaces_collection(self):
        """워크스페이스 컬렉션 생성/조회 (단순화)"""
        return self.chroma_client.get_or_create_collection(
            name="mcp_workspaces",
            metadata={
                "description": "Amazon Q CLI workspaces",
                "hnsw:space": "cosine",
                "hnsw:M": 16,
                "hnsw:construction_ef": 200,
                "hnsw:search_ef": 50,
            }
        )

    def _setup_logging(self):
        """로그 파일 설정"""
        log_dir = os.path.expanduser("~/.Q_mem")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "operations.log")
        
        # 로거 설정
        self.logger = logging.getLogger('q_mem_mcp')
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
        """로그 기록 (파일 + verbose 모드시 콘솔)"""
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        
        if self.verbose:
            print(f"[{level}] {message}")
    
    def _get_operation_stats(self) -> Dict[str, Any]:
        """현재 작업의 통계 정보 반환"""
        return {
            "current_workspace": self.current_workspace,
            "timestamp": datetime.now().isoformat(),
            "storage_type": "chromadb"
        }

    
    def find_or_create_workspace(self, description: str) -> Tuple[str, bool]:
        """Find existing workspace by description or create new one"""
        # Use description as workspace_id (sanitized)
        import re
        workspace_id = re.sub(r'[^\w\-_]', '_', description)[:50]  # 안전한 ID로 변환
        
        print(f"🔍 Looking for workspace: {workspace_id}")
        
        # Check existing workspaces
        existing_workspaces = self.list_all_workspaces()
        print(f"📋 Found {len(existing_workspaces)} existing workspaces")
        
        for workspace in existing_workspaces:
            if workspace.get('workspace_id') == workspace_id:
                print(f"✅ Found existing workspace: {workspace_id}")
                return workspace_id, False
        
        # Create new workspace
        print(f"🆕 Creating new workspace: {workspace_id}")
        workspace_data = {
            "workspace_id": workspace_id,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            # Save workspace to ChromaDB (단순화)
            workspace_embedding = self.embedder.encode(f"Workspace: {description}")
            workspace_doc_id = f"workspace_{workspace_id}_{datetime.now().timestamp()}"
            
            self.workspaces_collection.add(
                ids=[workspace_doc_id],
                embeddings=[workspace_embedding.tolist()],
                documents=[f"Workspace: {description}"],
                metadatas=[{
                    "type": "workspace_metadata",
                    "workspace_id": workspace_data["workspace_id"],
                    "description": workspace_data["description"],
                    "created_at": workspace_data["created_at"]
                }]
            )
            print(f"✅ Workspace '{workspace_id}' saved to ChromaDB with ID: {workspace_doc_id}")
            
            # Verify save
            verification = self.workspaces_collection.get(
                where={"workspace_id": workspace_id}
            )
            print(f"🔍 Verification: Found {len(verification['ids']) if verification['ids'] else 0} records for workspace")
            
        except Exception as e:
            print(f"❌ Failed to save workspace to ChromaDB: {e}")
            raise e
        
        self.current_workspace = workspace_id
        
        return workspace_id, True  # New workspace created
    
    def start_workspace(self, description: str) -> Dict[str, Any]:
        """Start a new workspace with truthfulness context"""
        workspace_id, is_new = self.find_or_create_workspace(description)
        self.current_workspace = workspace_id
        
        # 컨텍스트 변경 기록
        context_data = {
            "type": "workspace_start",
            "workspace": workspace_id,
            "timestamp": datetime.now().isoformat(),
            "is_new_workspace": is_new
        }
        
        context_text = f"Workspace started: {workspace_id}"
        context_embedding = self.embedder.encode(context_text)
        self.conversations_collection.add(
            ids=[f"workspace_start_{workspace_id}_{datetime.now().timestamp()}"],
            embeddings=[context_embedding.tolist()],
            documents=[context_text],
            metadatas=[context_data]
        )
        
        # 진실성 강조 컨텍스트를 워크스페이스 시작 시 주입
        try:
            truthfulness_context = self._get_truthfulness_context()
            self.add_conversation(
                user_message="[SYSTEM] Workspace started - Loading truthfulness guidelines",
                ai_response=truthfulness_context
            )
            print("✅ Truthfulness context loaded for this workspace")
        except Exception as e:
            print(f"Warning: Could not load truthfulness context: {e}")
        
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
            print("✅ Truthfulness context reloaded")
            return True
        except Exception as e:
            print(f"Warning: Could not reload truthfulness context: {e}")
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
        """Add conversation to ChromaDB"""
        workspace_id = self.get_current_workspace_id()
        if not workspace_id:
            raise ValueError("Workspace not set. Please start a workspace first.")
        
        try:
            enhanced_metadata = self._analyze_conversation_content(user_message, ai_response)
            
            conversation_text = f"User: {user_message}\nAI: {ai_response}"
            conversation_id = f"conv_{workspace_id}_{datetime.now().timestamp()}"
            
            # 메타데이터 길이 제한 (ChromaDB 제한 고려)
            user_msg_truncated = user_message[:1000] if len(user_message) > 1000 else user_message
            ai_msg_truncated = ai_response[:1000] if len(ai_response) > 1000 else ai_response
            
            # 메타데이터 준비
            files_mentioned = enhanced_metadata.get("files_mentioned", [])
            detected_tasks = enhanced_metadata.get("detected_tasks", [])
            
            metadata = {
                "type": "conversation",
                "workspace": workspace_id,
                "timestamp": datetime.now().isoformat(),
                "user_message": user_msg_truncated,
                "ai_response": ai_msg_truncated,
                "user_message_length": len(user_message),
                "ai_response_length": len(ai_response),
                "total_length": len(user_message) + len(ai_response),
                "importance_score": enhanced_metadata.get("importance_score", 0),
                "code_blocks_count": enhanced_metadata.get("code_blocks_count", 0),
                "files_mentioned_count": len(files_mentioned),
                "detected_tasks_count": len(detected_tasks),
                "analysis_method": enhanced_metadata.get("analysis_method", "basic")
            }
            
            # 파일과 작업 정보를 문자열로 저장
            if files_mentioned:
                metadata["files_mentioned_str"] = "|".join(files_mentioned[:5])
            if detected_tasks:
                metadata["detected_tasks_str"] = "|".join(detected_tasks[:5])
            
            # ChromaDB에 저장 (단순화)
            conversation_embedding = self.embedder.encode(conversation_text)
            self.conversations_collection.add(
                ids=[conversation_id],
                embeddings=[conversation_embedding.tolist()],
                documents=[conversation_text],
                metadatas=[metadata]
            )
            
            # 로깅
            self._log(f"Conversation stored: {len(user_message)}+{len(ai_response)} chars, importance={metadata['importance_score']}")
            
            return True
            
        except Exception as e:
            self._log(f"Failed to store conversation: {str(e)}", "ERROR")
            return False
    
    def _analyze_conversation_content(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """임베딩 기반 의미론적 대화 분석"""
        try:
            # 작업 유형별 임베딩 정의
            task_embeddings = {
                'file_operation': self.embedder.encode("read file open document save write"),
                'code_analysis': self.embedder.encode("analyze review examine code function class"),
                'modification': self.embedder.encode("modify change update improve fix edit"),
                'creation': self.embedder.encode("create generate make build implement develop"),
                'testing': self.embedder.encode("test run execute check verify debug"),
                'explanation': self.embedder.encode("explain describe how what why tutorial"),
                'problem_solving': self.embedder.encode("error problem issue bug solve fix")
            }
            
            # 대화 내용 임베딩
            conversation_text = f"{user_message} {ai_response}"
            conversation_embedding = self.embedder.encode(conversation_text)
            
            # 유사도 계산 및 작업 유형 감지
            detected_tasks = []
            task_scores = {}
            
            for task_type, task_embedding in task_embeddings.items():
                # 코사인 유사도 계산 (간단한 내적 사용)
                similarity = float(conversation_embedding.dot(task_embedding) / 
                                 (conversation_embedding.dot(conversation_embedding)**0.5 * 
                                  task_embedding.dot(task_embedding)**0.5))
                
                if similarity > 0.3:  # 임계값
                    detected_tasks.append(task_type)
                    task_scores[task_type] = round(similarity, 3)
            
            # 파일 언급 감지 (정규식 보조)
            file_patterns = [r'\.[a-zA-Z]{2,4}(?:\s|$)', r'/[\w/]+', r'[\w]+\.[\w]+']
            files_mentioned = []
            for pattern in file_patterns:
                matches = re.findall(pattern, conversation_text)
                files_mentioned.extend(matches)
            
            # 코드 블록 감지
            code_blocks = len(re.findall(r'```', ai_response))
            
            # 중요도 점수 계산
            importance_score = len(detected_tasks) * 2 + len(files_mentioned) + code_blocks
            
            analysis = {
                "detected_tasks": detected_tasks,
                "task_confidence": task_scores,
                "files_mentioned": list(set(files_mentioned)) if files_mentioned else [],
                "code_blocks_count": code_blocks,
                "importance_score": importance_score,
                "user_message_length": len(user_message),
                "ai_response_length": len(ai_response),
                "total_length": len(user_message) + len(ai_response),
                "analysis_method": "embedding_based"
            }
            
            return analysis
            
        except Exception as e:
            self._log(f"Warning: Embedding analysis failed: {str(e)}", "WARNING")
            # Fallback to basic analysis
            return {
                "user_message_length": len(user_message),
                "ai_response_length": len(ai_response),
                "total_length": len(user_message) + len(ai_response),
                "analysis_method": "fallback"
            }
    
    def search_memory_by_workspace_id(self, workspace_id: str, query: str = "", limit: int = 3) -> Dict[str, Any]:
        """Search conversation memory by workspace ID using ChromaDB"""
        self._log(f"Searching memory for workspace '{workspace_id}': '{query}' (limit: {limit})")
        
        if query.strip():
            # 의미적 검색 (쿼리가 있는 경우) - 단순화
            query_embedding = self.embedder.encode(query)
            try:
                results = self.conversations_collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=limit,
                    where={"$and": [{"workspace": workspace_id}, {"type": "conversation"}]}
                )
                
            except Exception as e:
                self._log(f"ChromaDB query error: {str(e)}", "ERROR")
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
            
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    
                    if (metadata.get('type') == 'conversation' and 
                        metadata.get('workspace') == workspace_id):
                        
                        search_results.append({
                            "memory": doc,
                            "metadata": metadata,
                            "score": results['distances'][0][i] if results['distances'] and results['distances'][0] else 0,
                            "user_message": metadata.get('user_message', ''),
                            "ai_response": metadata.get('ai_response', ''),
                            "timestamp": metadata.get('timestamp', '')
                        })
            
            # 결과 제한
            search_results = search_results[:limit]
            
        else:
            # 전체 대화 가져오기 (쿼리가 없는 경우) - 단순화
            try:
                results = self.conversations_collection.get(
                    where={"$and": [{"workspace": workspace_id}, {"type": "conversation"}]}
                )
                
            except Exception as e:
                self._log(f"ChromaDB get error: {str(e)}", "ERROR")
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
            
            search_results = []
            if results['documents'] and results['metadatas']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if i < len(results['metadatas']) else {}
                    
                    if (metadata.get('type') == 'conversation' and 
                        metadata.get('workspace') == workspace_id):
                        
                        search_results.append({
                            "memory": doc,
                            "metadata": metadata,
                            "score": 0,  # 전체 조회시 점수 없음
                            "user_message": metadata.get('user_message', ''),
                            "ai_response": metadata.get('ai_response', ''),
                            "timestamp": metadata.get('timestamp', '')
                        })
            
            # 시간순 정렬 (query가 없을 때는 limit 적용하지 않음)
            def safe_timestamp_sort(item):
                timestamp = item.get('timestamp', '')
                if not timestamp:
                    return '1970-01-01T00:00:00'
                return timestamp
            
            search_results.sort(key=safe_timestamp_sort, reverse=True)
        
        self._log(f"Search completed: {len(search_results)} results found")
        
        return {
            "results": search_results,
            "stats": {
                "query": query,
                "total_found": len(search_results),
                "workspace": workspace_id,
                "limit": limit,
                "search_type": "semantic" if query.strip() else "all"
            }
        }
    
    def list_all_workspaces(self) -> List[Dict[str, Any]]:
        """List all available workspaces with detailed information"""
        workspaces = []
        
        try:
            self._log("Querying ChromaDB for all workspaces")
            
            # ChromaDB에서 모든 워크스페이스 가져오기 (단순화)
            results = self.workspaces_collection.get()
            
            if results['metadatas']:
                for metadata in results['metadatas']:
                    if metadata and metadata.get('type') == 'workspace_metadata':
                        workspace_id = metadata.get('workspace_id', '')
                        if workspace_id:
                            conversation_count = self._get_conversation_count_for_workspace(workspace_id)
                            
                            workspace_info = {
                                "workspace_id": workspace_id,
                                "description": metadata.get('description', ''),
                                "created_at": metadata.get('created_at', ''),
                                "conversation_count": conversation_count
                            }
                            workspaces.append(workspace_info)
                
                self._log(f"Found {len(workspaces)} valid workspaces")
            else:
                self._log("No workspace metadata found in ChromaDB", "WARNING")
            
        except Exception as e:
            self._log(f"Error querying workspaces from ChromaDB: {str(e)}", "ERROR")
        
        return workspaces
    
    def _get_conversation_count_for_workspace(self, workspace_id: str) -> int:
        """Get conversation count for a workspace from ChromaDB"""
        try:
            results = self.conversations_collection.get(
                where={"$and": [{"workspace": workspace_id}, {"type": "conversation"}]}
            )
            
            count = len(results['ids']) if results['ids'] else 0
            return count
            
        except Exception as e:
            self._log(f"Error counting conversations for workspace {workspace_id}: {str(e)}", "ERROR")
            return 0
    
    def resume_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Resume an existing workspace with full conversation history loaded"""
        self._log(f"Resuming workspace with full context: {workspace_id}")
        
        # 워크스페이스 존재 확인
        workspaces = self.list_all_workspaces()
        target_workspace = None
        
        for workspace in workspaces:
            if workspace.get('workspace_id') == workspace_id:
                target_workspace = workspace
                break
        
        if not target_workspace:
            error_msg = f"Workspace '{workspace_id}' not found"
            self._log(error_msg, "ERROR")
            raise ValueError(error_msg)
        
        # 워크스페이스 재개
        self.current_workspace = workspace_id
        
        # 전체 대화 히스토리 로드
        history_result = self.get_workspace_conversations(workspace_id)
        full_history = history_result.get('conversations', [])
        
        # LLM context용 대화 문자열 생성
        context_messages = []
        for conv in full_history:
            user_msg = conv.get('user_message', '')
            ai_msg = conv.get('ai_response', '')
            if user_msg and ai_msg:
                context_messages.append(f"User: {user_msg}")
                context_messages.append(f"Assistant: {ai_msg}")
        
        context_length = sum(len(msg) for msg in context_messages)
        
        result = {
            "workspace_id": workspace_id,
            "description": target_workspace.get('description', ''),
            "created_at": target_workspace.get('created_at', ''),
            "conversation_count": len(full_history),
            "full_history": full_history,
            "context_messages": context_messages,
            "context_length": context_length,
            "estimated_tokens": context_length // 4,
            "is_resumed": True
        }
        
        self._log(f"Workspace resumed with full context: {workspace_id} ({len(full_history)} conversations, {context_length} chars)")
        return result
    
    def get_workspace_conversations(self, workspace_id: str) -> Dict[str, Any]:
        """Get all conversations from a workspace (simplified)"""
        self._log(f"Loading conversations for workspace: {workspace_id}")
        
        # ChromaDB에서 해당 워크스페이스의 모든 대화 가져오기 (단순화)
        results = self.conversations_collection.get(
            where={"$and": [{"workspace": workspace_id}, {"type": "conversation"}]}
        )
        
        conversations = []
        if results['documents'] and results['metadatas']:
            for i, doc in enumerate(results['documents']):
                metadata = results['metadatas'][i] if i < len(results['metadatas']) else {}
                
                if (metadata.get('type') == 'conversation' and 
                    metadata.get('workspace') == workspace_id):
                    conversations.append({
                        "content": doc,
                        "timestamp": metadata.get('timestamp', ''),
                        "user_message": metadata.get('user_message', ''),
                        "ai_response": metadata.get('ai_response', ''),
                        "importance_score": metadata.get('importance_score', 0),
                        "document": doc
                    })
        
        # 시간순 정렬
        def safe_timestamp_sort(conv):
            timestamp = conv.get('timestamp', '')
            if not timestamp:
                return '1970-01-01T00:00:00'
            return timestamp
        
        conversations.sort(key=safe_timestamp_sort)
        
        result = {
            "conversations": conversations,
            "stats": {
                "total_conversations": len(conversations),
                "workspace_id": workspace_id,
                "context_length": sum(len(c.get('user_message', '') + c.get('ai_response', '')) for c in conversations)
            }
        }
        
        self._log(f"Loaded {len(conversations)} conversations from workspace: {workspace_id}")
        return result
    
    def _safe_extract_string(self, metadata: Dict, key: str, default: str = "") -> str:
        """메타데이터에서 안전하게 문자열 추출"""
        try:
            value = metadata.get(key, default)
            if value is None:
                return default
            if isinstance(value, str):
                return value
            # 문자열이 아닌 경우 변환 시도
            return str(value)
        except Exception:
            return default
    
    def _safe_calculate_context_length(self, conversations: List[Dict]) -> int:
        """안전하게 컨텍스트 길이 계산"""
        try:
            total_length = 0
            for conv in conversations:
                user_msg = conv.get('user_message', '')
                ai_msg = conv.get('ai_response', '')
                
                if isinstance(user_msg, str):
                    total_length += len(user_msg)
                if isinstance(ai_msg, str):
                    total_length += len(ai_msg)
            
            return total_length
        except Exception as e:
            self._log(f"Error calculating context length: {str(e)}", "WARNING")
            return 0
    
    def _generate_workspace_summary(self, conversations: List[Dict]) -> Dict[str, Any]:
        """대화 목록에서 요약 정보 생성 (오류 처리 강화)"""
        file_mentions = []
        code_mentions = []
        task_mentions = []
        processing_errors = []
        
        for i, conv in enumerate(conversations):
            try:
                # 안전한 메시지 추출
                user_msg = self._safe_extract_string(conv, 'user_message', '')
                ai_msg = self._safe_extract_string(conv, 'ai_response', '')
                
                if not user_msg and not ai_msg:
                    continue
                
                # 파일 경로 추출 (안전한 정규식 처리)
                try:
                    import re
                    file_patterns = [
                        r'/[^\s]+\.(py|js|json|md|txt|yml|yaml|sql)',
                        r'[^\s]+\.(py|js|json|md|txt|yml|yaml|sql)'
                    ]
                    for pattern in file_patterns:
                        try:
                            matches = re.findall(pattern, user_msg + ' ' + ai_msg)
                            file_mentions.extend(matches)
                        except re.error as e:
                            processing_errors.append(f"Regex error in conversation {i}: {str(e)}")
                except Exception as e:
                    processing_errors.append(f"File pattern matching error in conversation {i}: {str(e)}")
                
                # 코드 블록 감지 (안전한 문자열 검사)
                try:
                    if ('```' in user_msg) or ('```' in ai_msg):
                        code_mentions.append(f"Code: {user_msg[:50]}...")
                except Exception as e:
                    processing_errors.append(f"Code detection error in conversation {i}: {str(e)}")
                
                # 작업/요청 감지 (안전한 키워드 검사)
                try:
                    task_keywords = ['읽어', '분석', '개선', '수정', '생성', '만들어', '구현', '테스트', '조회', '확인']
                    if any(keyword in user_msg for keyword in task_keywords):
                        task_mentions.append(user_msg[:100])
                except Exception as e:
                    processing_errors.append(f"Task detection error in conversation {i}: {str(e)}")
                    
            except Exception as e:
                processing_errors.append(f"General processing error in conversation {i}: {str(e)}")
                continue
        
        # 컨텍스트 요약 구성 (안전한 처리)
        summary_parts = []
        
        try:
            if file_mentions:
                # 안전한 파일 목록 처리
                unique_files = []
                for f in file_mentions:
                    try:
                        file_name = f[0] if isinstance(f, tuple) else f
                        if isinstance(file_name, str) and file_name not in unique_files:
                            unique_files.append(file_name)
                    except Exception:
                        continue
                
                if unique_files:
                    summary_parts.append(f"📁 Files: {', '.join(unique_files[:5])}")
            
            if task_mentions:
                # 안전한 작업 목록 처리
                safe_tasks = []
                for task in task_mentions[-3:]:
                    if isinstance(task, str):
                        safe_tasks.append(task)
                
                if safe_tasks:
                    summary_parts.append(f"🎯 Tasks: {'; '.join(safe_tasks)}")
            
            if code_mentions:
                summary_parts.append(f"💻 Code discussions: {len(code_mentions)}")
            
            # 최근 대화 요약 (안전한 처리)
            recent_convs = conversations[-3:] if len(conversations) >= 3 else conversations
            if recent_convs:
                summary_parts.append("💬 Recent:")
                for conv in recent_convs:
                    try:
                        user_msg = self._safe_extract_string(conv, 'user_message', '')
                        if user_msg and len(user_msg) > 0:
                            safe_msg = user_msg[:80] if len(user_msg) > 80 else user_msg
                            summary_parts.append(f"   U: {safe_msg}...")
                    except Exception:
                        continue
            
        except Exception as e:
            processing_errors.append(f"Summary construction error: {str(e)}")
            summary_parts = ["Summary generation partially failed"]
        
        # 최종 요약 생성
        summary = "\n".join(summary_parts) if summary_parts else "Workspace context available"
        
        # 통계 생성 (안전한 처리)
        try:
            unique_files_count = len(set([
                f[0] if isinstance(f, tuple) else f 
                for f in file_mentions 
                if isinstance(f, (str, tuple))
            ]))
        except Exception:
            unique_files_count = 0
        
        result = {
            "summary": summary,
            "summary_stats": {
                "conversations_analyzed": len(conversations),
                "files_found": unique_files_count,
                "tasks_found": len(task_mentions),
                "code_blocks": len(code_mentions),
                "processing_errors": len(processing_errors)
            }
        }
        
        # 처리 오류가 있으면 포함
        if processing_errors:
            self._log(f"Summary generation errors: {len(processing_errors)} errors", "WARNING")
            result["processing_errors"] = processing_errors[:5]  # 최대 5개만 포함
        
        return result
    
    def delete_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Delete workspace and all related data"""
        print(f"🗑️ Deleting workspace: {workspace_id}")
        
        deleted_items = {
            "workspace_metadata": False,
            "conversations": 0,
            "context_data": 0
        }
        
        # 1. 워크스페이스 메타데이터 삭제 (단순화)
        workspace_results = self.workspaces_collection.get(
            where={"workspace_id": workspace_id}
        )
        
        if workspace_results['ids']:
            self.workspaces_collection.delete(ids=workspace_results['ids'])
            deleted_items["workspace_metadata"] = True
            print(f"✅ Workspace metadata deleted")
        
        # 2. 해당 워크스페이스의 모든 대화 삭제 (단순화)
        conv_results = self.conversations_collection.get(
            where={"workspace": workspace_id}
        )
        
        if conv_results['ids']:
            self.conversations_collection.delete(ids=conv_results['ids'])
            deleted_items["conversations"] = len(conv_results['ids'])
            print(f"✅ {len(conv_results['ids'])} conversations deleted")
        
        # 현재 워크스페이스가 삭제된 워크스페이스이면 초기화
        if self.current_workspace == workspace_id:
            self.current_workspace = None
        
        print(f"🗑️ Workspace '{workspace_id}' completely deleted")
        return deleted_items
    
    def cleanup_old_workspaces(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old workspaces"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cleanup_stats = {
            "workspaces_deleted": 0,
            "conversations_deleted": 0,
            "cutoff_date": cutoff_date.isoformat()
        }
        
        workspaces = self.list_all_workspaces()
        
        for workspace in workspaces:
            try:
                created_at = workspace.get('created_at', '')
                if created_at:
                    workspace_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    
                    if workspace_date < cutoff_date:
                        workspace_id = workspace.get('workspace_id')
                        deleted_items = self.delete_workspace(workspace_id)
                        
                        cleanup_stats["workspaces_deleted"] += 1
                        cleanup_stats["conversations_deleted"] += deleted_items.get("conversations", 0)
                        
                        print(f"🧹 Cleaned up old workspace: {workspace_id}")
                        
            except Exception as e:
                print(f"Warning: Could not process workspace for cleanup: {e}")
        
        print(f"🧹 Cleanup complete: {cleanup_stats['workspaces_deleted']} workspaces, {cleanup_stats['conversations_deleted']} conversations")
        return cleanup_stats
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Return storage statistics information (optimized for reliability)"""
        stats = {
            "total_workspaces": 0,
            "total_conversations": 0,
            "storage_type": "chromadb",
            "current_workspace": self.current_workspace,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dimension": self.embedding_dimension
        }
        
        try:
            # 간단한 카운트만 수행 (복잡한 연산 피함) - 단순화
            workspaces_result = self.workspaces_collection.get()
            stats["total_workspaces"] = len(workspaces_result.get('ids', []))
            
            # 대화 수는 직접 카운트 (list_all_workspaces 호출 피함) - 단순화
            conversations_result = self.conversations_collection.get()
            stats["total_conversations"] = len(conversations_result.get('ids', []))
            
        except Exception as e:
            self._log(f"Error getting basic stats: {e}", "WARNING")
            # 에러 발생 시 기본값 유지
        
        # 저장소 크기 정보 (가능한 경우)
        try:
            import os
            storage_dir = os.path.expanduser("~/.Q_mem")
            if os.path.exists(storage_dir):
                total_size = 0
                for root, dirs, files in os.walk(storage_dir):
                    for file in files:
                        try:
                            total_size += os.path.getsize(os.path.join(root, file))
                        except (OSError, IOError):
                            continue  # 파일 접근 실패 시 무시
                stats["storage_size_mb"] = round(total_size / (1024 * 1024), 2)
        except Exception as e:
            self._log(f"Error calculating storage size: {e}", "WARNING")
            stats["storage_size_mb"] = "unknown"
        
        return stats
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get current context information"""
        return {
            "workspace_id": self.get_current_workspace_id(),
            "is_active": self.get_current_workspace_id() is not None,
            "storage_type": "chromadb"
        }
