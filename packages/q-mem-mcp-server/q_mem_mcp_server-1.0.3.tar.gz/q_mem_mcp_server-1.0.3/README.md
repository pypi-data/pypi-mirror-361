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

## 💡 **Usage Tips**

1. **Session Organization**: Separate conversations by topics, roles, or projects
2. **Semantic Search**: Use natural language rather than exact keywords
3. **Context Utilization**: Use `resume_session` for complete conversation restoration
4. **Regular Cleanup**: Delete unnecessary sessions to maintain performance

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

## 💡 **사용 팁**

1. **세션 정리**: 주제, 역할, 프로젝트별로 대화 분리
2. **의미 검색**: 정확한 키워드보다 자연어 사용
3. **컨텍스트 활용**: 완전한 대화 복원을 위해 `resume_session` 사용
4. **정기 정리**: 성능 유지를 위해 불필요한 세션 삭제

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
