# AWS Q Memory MCP Server (q_mem_mcp_server)

A Model Context Protocol (MCP) server that provides conversation memory and session management for Amazon Q CLI.

## 🎯 **Key Features**

- **Automatic Conversation Saving**: Real-time sync of Q CLI conversations to ChromaDB
- **Session Management**: Organize conversations by topics/sessions
- **Context Restoration**: Resume previous conversations with full context memory
- **Semantic Search**: Search through conversation history using natural language

## 🚀 **Quick Start**

### 1. MCP Configuration
Add to `~/.aws/amazonq/mcp.json`:
```json
{
  "mcpServers": {
    "q-mem": {
      "command": "uvx",
      "args": ["q_mem_mcp_server@latest"],
      "env": {
        "Q_CLI_DB_PATH": "~/Library/Application Support/amazon-q/data.sqlite3",
        "Q_MEM_VERBOSE": "true"
      },
      "disabled": false,
      "autoApprove": [
        "start_session",
        "resume_session", 
        "search_memory_by_session_id",
        "get_storage_stats",
        "list_sessions"
      ]
    }
  }
}
```

### 2. Usage Examples
```bash
# Start Q CLI
q chat

# Start a new session
start_session(description="backendDev")
# or natural language: "Start session a backendDev"

# Chat normally (automatically saved)
# ... have conversations ...

# List sessions
list_sessions()
# or natural language: "show me session list"

# Resume session (loads full context)
resume_session(session_id="backendDev")
# or natural language: "resume session a backendDev"
```

## 🛠️ **Available Commands**

| Command | Description |
|---------|-------------|
| `start_session(description)` | Start a new session |
| `list_sessions()` | List all sessions |
| `resume_session(session_id)` | Resume session with full context |
| `search_memory_by_session_id(session_id, query)` | Search previous conversations |
| `delete_session(session_id, confirm=true)` | Delete a session |
| `get_storage_stats()` | Check storage status |

## 🔧 **Technology Stack**

- **ChromaDB**: Vector database for conversation storage and search
- **SQLite WAL**: Real-time sync with Q CLI database
- **Sentence Transformers**: Semantic search embeddings
- **MCP Protocol**: Communication with Amazon Q

## 📁 **Data Storage**

- **ChromaDB**: `~/.Q_mem/chroma_db/`
- **Sync State**: `~/.Q_mem/sync_state.json`
- **Logs**: `~/.Q_mem/q_mem.log`

## 🔄 **Auto-Sync Features**

Q CLI conversations are automatically saved to ChromaDB in real-time:

- **Real-time Detection**: Checks for new conversations every 2 seconds
- **Partial Failure Handling**: Saves successful conversations even if some fail
- **Auto Recovery**: Automatically recovers from consecutive failures
- **State Restoration**: Restores sync state after restart

## 🌟 **Revolutionary Multi-Persona Workflow Example**

Experience the power of seamless context switching between different expert personas:

```bash
# === Day 1: Backend Development Session ===
q chat
> start_session(description="backendDev")
✅ Session 'backendDev' started

> "You are now a backend developer persona. Help me design a microservices architecture"
🎯 Backend Developer: I'll help you design a robust microservices architecture...

> "Store my PyPI API key: pypi-AgEI..."
✅ PyPI API key stored for future deployments

> "Design a user authentication service with JWT"
🎯 Backend Developer: Here's a comprehensive JWT authentication service design...
# ... detailed backend discussion continues ...

# === Day 2: Database Design Session ===
q chat  
> start_session(description="dba")
✅ Session 'dba' started

> "You are now a database administrator persona. Help me optimize the user service database"
🎯 Database Administrator: I'll help you optimize your database design...

> "What's the best indexing strategy for user lookups?"
🎯 Database Administrator: For optimal user lookup performance, consider these indexing strategies...
# ... detailed database discussion continues ...

# === Day 3: Seamless Context Switching ===
q chat
> list_sessions()
📋 Your sessions:
1. backendDev (15 conversations) - Backend development and API design
2. dba (8 conversations) - Database optimization and indexing

> resume_session(session_id="backendDev")
🔄 Session 'backendDev' resumed with full context
🎯 Backend Developer: Welcome back! We were discussing JWT authentication service...

> "Remember my PyPI key? I need to deploy the auth service we designed"
🎯 Backend Developer: Yes! Using your stored PyPI key: pypi-AgEI...
✅ Deploying q_auth_service v1.0.0 to PyPI...

> "Now switch to DBA context to check if our database design supports this deployment"
> resume_session(session_id="dba")
🔄 Session 'dba' resumed with full context  
🎯 Database Administrator: Checking the indexing strategy we discussed for the auth service...

> "The backend team deployed the JWT service. Does our index design handle the expected load?"
🎯 Database Administrator: Based on our previous optimization discussion, the composite index on (user_id, created_at) will handle the JWT validation queries efficiently...

# === Day 4: Cross-Session Knowledge Integration ===
> search_memory_by_session_id(session_id="backendDev", query="JWT token expiration")
🔍 Found in backendDev session:
- "JWT tokens should expire in 15 minutes for security"
- "Refresh tokens valid for 7 days"
- "Store refresh tokens in Redis for fast lookup"

> resume_session(session_id="dba")
🎯 Database Administrator: I remember we need to optimize for JWT refresh token storage...

> "Based on the backend session, we need Redis optimization for 7-day refresh tokens"
🎯 Database Administrator: Perfect! Let me design a Redis clustering strategy for high-availability refresh token storage...
```

### 🚀 **Why This Is Revolutionary**

1. **Persistent Expertise**: Each session maintains specialized knowledge and context
2. **Seamless Switching**: Jump between expert personas without losing conversation flow  
3. **Cross-Session Intelligence**: Search and reference knowledge across different expert contexts
4. **Secure Credential Storage**: API keys and sensitive data persist across sessions
5. **Natural Workflow**: Mirrors real-world collaboration between different specialists

### 🎯 **Real-World Applications**

- **DevOps Teams**: Switch between developer, DBA, and infrastructure personas
- **Full-Stack Projects**: Frontend, backend, and database expert contexts
- **Learning Paths**: Separate sessions for different technologies or concepts
- **Client Projects**: Dedicated sessions per client with persistent context
- **Code Reviews**: Different perspectives from various expert personas

## 💡 **Usage Tips**

1. **Session Organization**: Separate conversations by topics, roles, or projects
2. **Semantic Search**: Use natural language rather than exact keywords
3. **Context Utilization**: Use `resume_session` for complete conversation restoration
4. **Regular Cleanup**: Delete unnecessary sessions to maintain performance
5. **Cross-Session References**: Use `search_memory_by_session_id` to find relevant information across personas

### Memory Management
```bash
# Clean up old sessions
cleanup_old_sessions(days=30, confirm=true)
# or natural language: "remove old sessions"

# Delete specific session
delete_session(session_id="session_name", confirm=true)
# or natural language: "delete session session_name"
```

## 📄 **License**

MIT License

## 🔗 **Links**

- **PyPI**: https://pypi.org/project/q_mem_mcp_server/
- **GitHub**: https://github.com/jikang-jeong/aws-q-mem-mcp-server
- **Issues**: https://github.com/jikang-jeong/aws-q-mem-mcp-server/issues

---

# AWS Q Memory MCP Server (q_mem_mcp_server) - KOR

Amazon Q CLI를 위한 대화 메모리 및 세션 관리 기능을 제공하는 Model Context Protocol (MCP) 서버입니다.

## 🎯 **주요 기능**

- **자동 대화 저장**: Q CLI 대화를 ChromaDB에 실시간 동기화
- **세션 관리**: 주제/세션별로 대화 정리
- **컨텍스트 복원**: 이전 대화의 전체 컨텍스트와 함께 재개
- **의미 검색**: 자연어를 사용한 대화 기록 검색

## 🚀 **빠른 시작**

### 1. MCP 설정
`~/.aws/amazonq/mcp.json`에 추가:
```json
{
  "mcpServers": {
    "q-mem": {
      "command": "uvx",
      "args": ["q_mem_mcp_server@latest"],
      "env": {
        "Q_CLI_DB_PATH": "~/Library/Application Support/amazon-q/data.sqlite3",
        "Q_MEM_VERBOSE": "true"
      },
      "disabled": false,
      "autoApprove": [
        "start_session",
        "resume_session", 
        "search_memory_by_session_id",
        "get_storage_stats",
        "list_sessions"
      ]
    }
  }
}
```

### 2. 사용 예시
```bash
# Q CLI 시작
q chat

# 새 세션 시작
start_session(description="백엔드개발")
# 또는 자연어: "백엔드개발 세션 시작해줘"

# 일반적으로 대화 (자동 저장됨)
# ... 대화 진행 ...

# 세션 목록 보기
list_sessions()
# 또는 자연어: "세션 목록 보여줘"

# 세션 재개 (전체 컨텍스트 로드)
resume_session(session_id="백엔드개발")
# 또는 자연어: "백엔드개발 세션으로 재개해줘"
```

## 🛠️ **사용 가능한 명령어**

| 명령어 | 설명 |
|---------|-------------|
| `start_session(description)` | 새 세션 시작 |
| `list_sessions()` | 모든 세션 목록 보기 |
| `resume_session(session_id)` | 전체 컨텍스트와 함께 세션 재개 |
| `search_memory_by_session_id(session_id, query)` | 이전 대화 검색 |
| `delete_session(session_id, confirm=true)` | 세션 삭제 |
| `get_storage_stats()` | 저장소 상태 확인 |

## 🔧 **기술 스택**

- **ChromaDB**: 대화 저장 및 검색을 위한 벡터 데이터베이스
- **SQLite WAL**: Q CLI 데이터베이스와 실시간 동기화
- **Sentence Transformers**: 의미 검색 임베딩
- **MCP Protocol**: Amazon Q와의 통신

## 📁 **데이터 저장**

- **ChromaDB**: `~/.Q_mem/chroma_db/`
- **동기화 상태**: `~/.Q_mem/sync_state.json`
- **로그**: `~/.Q_mem/q_mem.log`

## 🔄 **자동 동기화 기능**

Q CLI 대화가 ChromaDB에 실시간으로 자동 저장됩니다:

- **실시간 감지**: 2초마다 새로운 대화 확인
- **부분 실패 처리**: 일부 실패해도 성공한 대화는 저장
- **자동 복구**: 연속 실패 시 자동 복구
- **상태 복원**: 재시작 후 동기화 상태 복원

## 🌟 **혁신적인 멀티 페르소나 워크플로우 예시**

서로 다른 전문가 페르소나 간의 매끄러운 컨텍스트 전환의 힘을 경험해보세요:

```bash
# === 1일차: 백엔드 개발 세션 ===
q chat
> start_session(description="백엔드개발")
✅ '백엔드개발' 세션이 시작되었습니다

> "너는 이제부터 백엔드 개발자 페르소나야. 마이크로서비스 아키텍처 설계를 도와줘"
🎯 백엔드 개발자: 견고한 마이크로서비스 아키텍처 설계를 도와드리겠습니다...

> "PyPI API 키 저장해줘: pypi-AgEI..."
✅ 향후 배포를 위해 PyPI API 키가 저장되었습니다

> "JWT를 사용한 사용자 인증 서비스 설계해줘"
🎯 백엔드 개발자: 포괄적인 JWT 인증 서비스 설계를 제시하겠습니다...
# ... 상세한 백엔드 논의 계속 ...

# === 2일차: 데이터베이스 설계 세션 ===
q chat  
> start_session(description="DBA")
✅ 'DBA' 세션이 시작되었습니다

> "너는 이제부터 데이터베이스 관리자 페르소나야. 사용자 서비스 데이터베이스 최적화를 도와줘"
🎯 데이터베이스 관리자: 데이터베이스 설계 최적화를 도와드리겠습니다...

> "사용자 조회를 위한 최적의 인덱싱 전략은 뭐야?"
🎯 데이터베이스 관리자: 최적의 사용자 조회 성능을 위해 다음 인덱싱 전략을 고려하세요...
# ... 상세한 데이터베이스 논의 계속 ...

# === 3일차: 매끄러운 컨텍스트 전환 ===
q chat
> list_sessions()
📋 세션 목록:
1. 백엔드개발 (15개 대화) - 백엔드 개발 및 API 설계
2. DBA (8개 대화) - 데이터베이스 최적화 및 인덱싱

> resume_session(session_id="백엔드개발")
🔄 '백엔드개발' 세션이 전체 컨텍스트와 함께 재개되었습니다
🎯 백엔드 개발자: 다시 오셨군요! JWT 인증 서비스에 대해 논의하고 있었죠...

> "내 PyPI 키 기억하지? 우리가 설계한 인증 서비스를 배포해야 해"
🎯 백엔드 개발자: 네! 저장된 PyPI 키를 사용합니다: pypi-AgEI...
✅ q_auth_service v1.0.0을 PyPI에 배포 중...

> "이제 DBA 컨텍스트로 전환해서 우리 데이터베이스 설계가 이 배포를 지원하는지 확인해줘"
> resume_session(session_id="DBA")
🔄 'DBA' 세션이 전체 컨텍스트와 함께 재개되었습니다
🎯 데이터베이스 관리자: 인증 서비스를 위해 논의했던 인덱싱 전략을 확인하겠습니다...

> "백엔드 팀이 JWT 서비스를 배포했어. 우리 인덱스 설계가 예상 부하를 처리할 수 있을까?"
🎯 데이터베이스 관리자: 이전 최적화 논의를 바탕으로, (user_id, created_at) 복합 인덱스가 JWT 검증 쿼리를 효율적으로 처리할 것입니다...

# === 4일차: 세션 간 지식 통합 ===
> search_memory_by_session_id(session_id="백엔드개발", query="JWT 토큰 만료")
🔍 '백엔드개발' 세션에서 발견:
- "보안을 위해 JWT 토큰은 15분 후 만료되어야 함"
- "리프레시 토큰은 7일간 유효"
- "빠른 조회를 위해 리프레시 토큰을 Redis에 저장"

> resume_session(session_id="DBA")
🎯 데이터베이스 관리자: JWT 리프레시 토큰 저장을 위한 최적화가 필요하다고 기억합니다...

> "백엔드 세션 기반으로, 7일간 유효한 리프레시 토큰을 위한 Redis 최적화가 필요해"
🎯 데이터베이스 관리자: 완벽합니다! 고가용성 리프레시 토큰 저장을 위한 Redis 클러스터링 전략을 설계하겠습니다...
```

### 🚀 **왜 이것이 혁신적인가**

1. **지속적인 전문성**: 각 세션이 전문 지식과 컨텍스트를 유지
2. **매끄러운 전환**: 대화 흐름을 잃지 않고 전문가 페르소나 간 이동
3. **세션 간 지능**: 서로 다른 전문가 컨텍스트 간 지식 검색 및 참조
4. **보안 자격증명 저장**: API 키와 민감한 데이터가 세션 간 지속
5. **자연스러운 워크플로우**: 실제 다양한 전문가 간 협업을 반영

### 🎯 **실제 활용 사례**

- **DevOps 팀**: 개발자, DBA, 인프라 페르소나 간 전환
- **풀스택 프로젝트**: 프론트엔드, 백엔드, 데이터베이스 전문가 컨텍스트
- **학습 경로**: 다양한 기술이나 개념별 별도 세션
- **클라이언트 프로젝트**: 클라이언트별 전용 세션과 지속적인 컨텍스트
- **코드 리뷰**: 다양한 전문가 페르소나의 서로 다른 관점

## 💡 **사용 팁**

1. **세션 정리**: 주제, 역할, 프로젝트별로 대화 분리
2. **의미 검색**: 정확한 키워드보다 자연어 사용
3. **컨텍스트 활용**: 완전한 대화 복원을 위해 `resume_session` 사용
4. **정기 정리**: 성능 유지를 위해 불필요한 세션 삭제
5. **세션 간 참조**: `search_memory_by_session_id`를 사용해 페르소나 간 관련 정보 찾기

### 메모리 관리
```bash
# 오래된 세션 정리
cleanup_old_sessions(days=30, confirm=true)
# 또는 자연어: "오래된 세션 삭제해줘"

# 특정 세션 삭제
delete_session(session_id="세션이름", confirm=true)
# 또는 자연어: "세션이름 세션 삭제해줘"
```

## 📄 **라이선스**

MIT License

## 🔗 **링크**

- **PyPI**: https://pypi.org/project/q_mem_mcp_server/
- **GitHub**: https://github.com/jikang-jeong/aws-q-mem-mcp-server
- **Issues**: https://github.com/jikang-jeong/aws-q-mem-mcp-server/issues
