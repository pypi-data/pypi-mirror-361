# Q Memory MCP Server (q_mem_mcp_server)

A Model Context Protocol (MCP) server that provides conversation memory and session management for Amazon Q CLI.

## 🎯 **Key Features**

- **Automatic Conversation Saving**: Real-time sync of Q CLI conversations to ChromaDB
- **Session Management**: Organize conversations by topics/sessions
- **Context Restoration**: Resume previous conversations with full context memory
- **Semantic Search**: Search through conversation history using natural language

## 🚀 **Quick Start (PyPI Installation)**

### 1. MCP Configuration
Add to `~/.aws/amazonq/mcp.json`:
```json
{
  "mcpServers": {
    "q-mem": {
      "command": "uvx",
      "args": ["q_mem_mcp_server@latest"],
      "env": {
        "Q_CLI_DB_PATH": "/Users/YOUR_USERNAME/Library/Application Support/amazon-q/data.sqlite3",
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

### 2. Usage
```bash
# Start Q CLI
q chat

# Start a new session
start_session(description="backendDev")
or 
Start session a backendDev  
# Chat normally (automatically saved)
# ... have conversations ...

# List sessions
list_sessions()
or 
show me session list 
# Resume session (loads full context)
resume_session(session_id="backendDev")
or 
resume session a backendDev
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

1. **Session Organization**: Separate conversations by Topics or Role or Anything 
2. **Semantic Search**: Use natural language rather than exact keywords
3. **Context Utilization**: Use `resume_session` for complete conversation restoration and anytime you can switch session with conversation restoration.
4. **Regular Cleanup**: Delete unnecessary sessions with `delete_session` or `delete all session` or `delete specific id session`
 

### Memory Issues
```bash
# Clean up old sessions
cleanup_old_sessions(days=30, confirm=true)
or 
remove old session 
```

## 📦 **Installation Methods**

###  PyPI  
```json
{
  "mcpServers": {
    "q-mem": {
      "command": "uvx",
      "args": ["q_mem_mcp_server@latest"],
      "env": {
        "Q_CLI_DB_PATH": "~/Library/Application Support/amazon-q/data.sqlite3",
        "Q_MEM_VERBOSE": "true"
      }
    }
  }
}
```

  

## 📄 **License**

MIT License

## 🔗 **Links**

- **PyPI**: https://pypi.org/project/q_mem_mcp_server/
- **GitHub**: https://github.com/jikang-jeong/aws-q-mem-mcp-server
- **Issues**: https://github.com/jikang-jeong/aws-q-mem-mcp-server/issues
