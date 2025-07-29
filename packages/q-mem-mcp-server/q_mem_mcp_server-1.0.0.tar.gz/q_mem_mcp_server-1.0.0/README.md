# Q Memory MCP Server

A Model Context Protocol (MCP) server that provides conversation memory and session management for Amazon Q CLI.

## 🎯 **Key Features**

- **Automatic Conversation Saving**: Real-time sync of Q CLI conversations to ChromaDB
- **Session Management**: Organize conversations by topics/sessions
- **Context Restoration**: Resume previous conversations with full context memory
- **Semantic Search**: Search through conversation history using natural language

## 🚀 **Quick Start**

### 1. Installation
```bash
cd /path/to/q-mem-mcp-server
pip install -e .
```

### 2. MCP Configuration
Add to `~/.config/q/mcp_config.json`:
```json
{
  "mcpServers": {
    "q-mem": {
      "command": "python",
      "args": ["-m", "q_mem_mcp.server"],
      "env": {}
    }
  }
}
```

### 3. Usage
```bash
# Start Q CLI
q chat

# Start a new session
start_session(description="Python Learning")

# Chat normally (automatically saved)
# ... have conversations ...

# List sessions
list_sessions()

# Resume session (loads full context)
resume_session(session_id="Python_Learning_0709_1234")
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

1. **Session Organization**: Separate conversations by topics
2. **Semantic Search**: Use natural language rather than exact keywords
3. **Context Utilization**: Use `resume_session` for complete conversation restoration
4. **Regular Cleanup**: Delete unnecessary sessions with `delete_session`

## 🐛 **Troubleshooting**

### Q CLI Sync Issues
```bash
# Set environment variable
export Q_CLI_DB_PATH="/path/to/q/cli/database"

# Or check auto-detection
get_storage_stats()
```

### ChromaDB Errors
```bash
# Recreate database
rm -rf ~/.Q_mem/chroma_db/
# Run start_session again
```

### Memory Issues
```bash
# Clean up old sessions
cleanup_old_sessions(days=30, confirm=true)
```

## 📄 **License**

MIT License
