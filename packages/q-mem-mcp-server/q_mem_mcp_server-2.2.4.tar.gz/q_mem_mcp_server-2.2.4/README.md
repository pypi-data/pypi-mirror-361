# Q Memory MCP Server

A Model Context Protocol (MCP) server that provides conversation memory and workspace management for Amazon Q CLI using SQLite + FTS5 for fast, reliable storage and search.

## Features

- **Automatic Conversation Saving**: Real-time sync of Q CLI conversations to SQLite database
- **Workspace Management**: Organize conversations by topics/workspaces with natural language support
- **Workspace Restoration**: Resume previous conversations with full context
- **Full-Text Search**: Search through conversation history using SQLite FTS5
- **Q CLI LLM Integration**: Intelligent conversation summarization using Q CLI's built-in LLM

## Quick Start

### 1. MCP Configuration
Add to `~/.aws/amazonq/mcp.json`:

**For macOS:**
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
      "disabled": false 
    }
  }
}
```

**For Windows:**
First, find your Q CLI database path:
```cmd
where /r %USERPROFILE% data.sqlite3
```

Then use the found path in your configuration:
```json
{
  "mcpServers": {
    "q-mem": {
      "command": "uvx",
      "args": ["q_mem_mcp_server@latest"],
      "env": {
        "Q_CLI_DB_PATH": "C:\\Users\\YourUsername\\AppData\\Local\\amazon-q\\data.sqlite3",
        "Q_MEM_VERBOSE": "true"
      },
      "disabled": false 
    }
  }
}
```

### 2. Usage Examples
```bash
# Start Q CLI
q chat

# Start a new workspace
start_workspace(description="backend_development")
# OR natural language: "Start backend development workspace"

# Chat normally (automatically saved)
# ... have conversations ...

# List workspaces
list_workspaces()

# Resume workspace (loads full context)
resume_workspace(workspace_id="backend_development")
# OR natural language: "Resume backend development workspace"

# Switch to another workspace
resume_workspace(workspace_id="frontend_development")
# OR natural language: "Resume frontend development workspace"

# Search conversations
search_memory_by_workspace(workspace_id="backend_development", query="API design")
# OR natural language: "What did I say about API design?"
```

## Available Tools

| Tool | Description |
|------|-------------|
| `show_usage()` | Show usage instructions |
| `start_workspace(description)` | Start a new workspace with auto-sync |
| `list_workspaces(limit=10)` | List all workspaces (default: 10, max: 50) |
| `resume_workspace(workspace_id)` | Resume workspace with full context |
| `search_memory_by_workspace(workspace_id, query)` | Search conversations using FTS5 |
| `delete_workspace(workspace_id, confirm=true)` | Delete a workspace and all conversations |
| `cleanup_old_workspaces(days=30, confirm=true)` | Clean up workspaces older than specified days |
| `get_storage_stats()` | Get storage statistics and usage information | 

## Technology Stack

- **SQLite + FTS5**: Fast full-text search without external dependencies
- **Real-time Sync**: Monitors Q CLI database for new conversations
- **Q CLI LLM Integration**: Uses Q CLI's built-in LLM for intelligent summarization
- **MCP Protocol**: Standard communication with Amazon Q

## Data Storage

- **Database**: `~/.Q_mem/conversations.db`
- **Logs**: `~/.Q_mem/operations.log`

## Auto-Sync Features

Q CLI conversations are automatically saved to SQLite in real-time:

- **Real-time Detection**: Monitors Q CLI database for new conversations
- **Immediate Sync**: Processes new conversations as they appear
- **Background Processing**: Non-blocking synchronization
- **State Recovery**: Maintains sync state across restarts

## Workspace Management

### Creating Workspaces
```bash
# Start a new workspace
start_workspace(description="Python_learning")
# OR natural language
"Start Python learning workspace"
```

### Switching Between Workspaces
```bash
# List available workspaces (default: 10, max: 50)
list_workspaces()
list_workspaces(limit=20)

# Resume a specific workspace
resume_workspace(workspace_id="developer")
# OR natural language
"Resume developer workspace"
```

### Searching Conversations
```bash
# Search within a workspace using FTS5
search_memory_by_workspace(workspace_id="Python_learning", query="list")

# OR natural language: "Did I mention lists in the current workspace?"

# Get all conversations from a workspace
search_memory_by_workspace(workspace_id="Python_learning", query="")
```

### Maintenance
```bash
# Check storage usage and statistics
get_storage_stats()

# Clean up old workspaces (default: 30 days)
cleanup_old_workspaces(confirm=true)
cleanup_old_workspaces(days=60, confirm=true)

# Delete specific workspace
delete_workspace(workspace_id="backend_development", confirm=true)

 
# Show usage instructions
q_mem_help()
```

## Natural Language Support

The server supports natural language commands in both English and Korean:

```bash
# English
"start backend_development workspace"
"resume Python_learning workspace"
"show me all workspaces"

# Korean
"백엔드개발 워크스페이스로 시작해줘"
"Python_학습 워크스페이스로 재개해줘"
"워크스페이스 목록 보여줘"
```

## Usage Tips

1. **Workspace Organization**: Use descriptive names for workspaces to easily identify them later
2. **Search Strategy**: Use specific keywords rather than general terms for better FTS5 search results
3. **Regular Maintenance**: Periodically clean up old workspaces to maintain performance
4. **Context Restoration**: Use `resume_workspace` to restore full conversation context
5. **Natural Language**: Use natural language commands for easier interaction

## Advantages of SQLite + FTS5

- ⚡ **Instant startup** - No embedding model loading required
- 🔍 **Fast search** - Native FTS5 full-text search capabilities
- 💾 **Reliable storage** - Battle-tested SQLite database
- 🔄 **Real-time sync** - Immediate Q CLI integration
- 📊 **Simple queries** - Standard SQL operations
- 🚀 **No dependencies** - Self-contained solution

## License

MIT License

## Links

- **PyPI**: https://pypi.org/project/q_mem_mcp_server/
- **GitHub**: https://github.com/jikang-jeong/aws-q-mem-mcp-server
- **Issues**: https://github.com/jikang-jeong/aws-q-mem-mcp-server/issues

---

# Q Memory MCP Server (한국어)

Amazon Q CLI를 위한 대화 메모리 및 워크스페이스 관리 기능을 제공하는 Model Context Protocol (MCP) 서버입니다. SQLite + FTS5를 사용하여 빠르고 안정적인 저장 및 검색을 제공합니다.

## 주요 기능

- **자동 대화 저장**: Q CLI 대화를 SQLite 데이터베이스에 실시간 동기화
- **워크스페이스 관리**: 주제/워크스페이스별로 대화 정리 (자연어 지원)
- **워크스페이스 복원**: 이전 대화의 전체 컨텍스트와 함께 재개
- **전문 검색**: SQLite FTS5를 사용한 대화 기록 검색
- **Q CLI LLM 통합**: Q CLI의 내장 LLM을 사용한 지능적 대화 요약

## 빠른 시작

### 1. MCP 설정
`~/.aws/amazonq/mcp.json`에 추가:

**macOS의 경우:**
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
      "disabled": false 
    }
  }
}
```

**Windows의 경우:**
먼저 Q CLI 데이터베이스 경로를 찾으세요:
```cmd
where /r %USERPROFILE% data.sqlite3
```

찾은 경로를 설정에 사용하세요:
```json
{
  "mcpServers": {
    "q-mem": {
      "command": "uvx",
      "args": ["q_mem_mcp_server@latest"],
      "env": {
        "Q_CLI_DB_PATH": "C:\\Users\\사용자명\\AppData\\Local\\amazon-q\\data.sqlite3",
        "Q_MEM_VERBOSE": "true"
      },
      "disabled": false 
    }
  }
}
```

### 2. 사용 예시
```bash
# Q CLI 시작
q chat

# 새 워크스페이스 시작
start_workspace(description="백엔드개발")
# 또는 자연어: "백엔드개발 워크스페이스로 시작해줘"

# 일반적으로 대화 (자동 저장됨)
# ... 대화 진행 ...

# 워크스페이스 목록 보기
list_workspaces()

# 워크스페이스 재개 (전체 컨텍스트 로드)
resume_workspace(workspace_id="백엔드개발")
# 또는 자연어: "백엔드개발 워크스페이스로 재개해줘"

# 다른 워크스페이스로 전환
resume_workspace(workspace_id="프론트개발")
# 또는 자연어: "프론트개발 워크스페이스로 재개해줘"

# 대화 검색
search_memory_by_workspace(workspace_id="백엔드개발", query="API 설계")
# 또는 자연어: "API 설계에 대해서 뭐라고 말했었는가?"
```

## 사용 가능한 도구

| 도구 | 설명 |
|------|-------------|
| `show_usage()` | 사용법 안내 표시 |
| `start_workspace(description)` | 자동 동기화와 함께 새 워크스페이스 시작 |
| `list_workspaces(limit=10)` | 모든 워크스페이스 목록 (기본: 10개, 최대: 50개) |
| `resume_workspace(workspace_id)` | 전체 컨텍스트와 함께 워크스페이스 재개 |
| `search_memory_by_workspace(workspace_id, query)` | FTS5를 사용한 대화 검색 |
| `delete_workspace(workspace_id, confirm=true)` | 워크스페이스와 모든 대화 삭제 |
| `cleanup_old_workspaces(days=30, confirm=true)` | 지정된 일수보다 오래된 워크스페이스 정리 |
| `get_storage_stats()` | 저장소 통계 및 사용량 정보 조회 |

## 기술 스택

- **SQLite + FTS5**: 외부 의존성 없는 빠른 전문 검색
- **실시간 동기화**: Q CLI 데이터베이스의 새 대화 모니터링
- **Q CLI LLM 통합**: Q CLI의 내장 LLM을 사용한 지능적 요약
- **MCP 프로토콜**: Amazon Q와의 표준 통신

## 데이터 저장

- **데이터베이스**: `~/.Q_mem/conversations.db`
- **로그**: `~/.Q_mem/operations.log`

## 자동 동기화 기능

Q CLI 대화가 SQLite에 실시간으로 자동 저장됩니다:

- **실시간 감지**: Q CLI 데이터베이스의 새 대화 모니터링
- **즉시 동기화**: 새 대화가 나타나면 즉시 처리
- **백그라운드 처리**: 논블로킹 동기화
- **상태 복구**: 재시작 후에도 동기화 상태 유지

## 워크스페이스 관리

### 워크스페이스 생성
```bash
# 새 워크스페이스 시작
start_workspace(description="Python_학습")
# 또는 자연어
"Python_학습 워크스페이스로 시작해줘"
```

### 워크스페이스 간 전환
```bash
# 사용 가능한 워크스페이스 목록 (기본: 10개, 최대: 50개)
list_workspaces()
list_workspaces(limit=20)

# 특정 워크스페이스 재개
resume_workspace(workspace_id="개발자")
# 또는 자연어
"개발자 워크스페이스로 재개해"
```

### 대화 검색
```bash
# FTS5를 사용한 워크스페이스 내 검색
search_memory_by_workspace(workspace_id="Python_학습", query="리스트")

# 또는 자연어: "현재 워크스페이스에서 내가 리스트를 말한적이 있었는가?"

# 워크스페이스의 모든 대화 조회
search_memory_by_workspace(workspace_id="Python_학습", query="")
```

### 유지보수
```bash
# 저장소 사용량 및 통계 확인
get_storage_stats()

# 오래된 워크스페이스 정리 (기본: 30일)
cleanup_old_workspaces(confirm=true)
cleanup_old_workspaces(days=60, confirm=true)

# 특정 워크스페이스 삭제
delete_workspace(workspace_id="백엔드개발", confirm=true)


# 사용법 안내 표시
q_mem_help()
```

## 자연어 지원

서버는 영어와 한국어 자연어 명령을 모두 지원합니다:

```bash
# 영어
"start backend_development workspace"
"resume Python_learning workspace"
"show me all workspaces"

# 한국어
"백엔드개발 워크스페이스로 시작해줘"
"Python_학습 워크스페이스로 재개해줘"
"워크스페이스 목록 보여줘"
```

## 사용 팁

1. **워크스페이스 정리**: 나중에 쉽게 식별할 수 있도록 워크스페이스에 설명적인 이름 사용
2. **검색 전략**: 더 나은 FTS5 검색 결과를 위해 일반적인 용어보다 구체적인 키워드 사용
3. **정기 유지보수**: 성능 유지를 위해 주기적으로 오래된 워크스페이스 정리
4. **컨텍스트 복원**: 전체 대화 컨텍스트 복원을 위해 `resume_workspace` 사용
5. **자연어**: 더 쉬운 상호작용을 위해 자연어 명령 사용

## SQLite + FTS5의 장점

- ⚡ **즉시 시작** - 임베딩 모델 로딩 불필요
- 🔍 **빠른 검색** - 네이티브 FTS5 전문 검색 기능
- 💾 **안정적인 저장** - 검증된 SQLite 데이터베이스
- 🔄 **실시간 동기화** - 즉시 Q CLI 통합
- 📊 **간단한 쿼리** - 표준 SQL 작업
- 🚀 **의존성 없음** - 자체 완결형 솔루션

## 라이선스

MIT License

## 링크

- **PyPI**: https://pypi.org/project/q_mem_mcp_server/
- **GitHub**: https://github.com/jikang-jeong/aws-q-mem-mcp-server
- **Issues**: https://github.com/jikang-jeong/aws-q-mem-mcp-server/issues
