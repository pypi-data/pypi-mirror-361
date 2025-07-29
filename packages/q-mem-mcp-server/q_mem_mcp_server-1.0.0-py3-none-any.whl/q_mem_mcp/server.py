"""
MCP Server with ChromaDB - Direct Implementation with Auto Conversation Recording
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .memory_manager import MemoryManager
from .memory_helper import get_auto_recorder, start_auto_recording
from .q_cli_sync import get_sync_daemon


# Initialize the MCP server
server = Server("conversation-memory-server")

# Global instances
memory_manager: Optional[MemoryManager] = None


def get_memory_manager(verbose: bool = False):
    """Get or create memory manager instance"""
    global memory_manager
    
    if memory_manager is None:
        try:
            memory_manager = MemoryManager(verbose=verbose)
            if verbose:
                print("✅ Memory manager initialized successfully")
        except Exception as e:
            if verbose:
                print(f"Warning: Could not initialize memory manager: {e}")
            memory_manager = MemoryManager(verbose=verbose)
    
    return memory_manager


def get_welcome_message() -> str:
    """Generate welcome message with usage instructions"""
    return """🎉 **Q Memory MCP Server Loaded Successfully!**

🚀 **Fully Automatic Conversation Memory System** - Saves everything!

## ✨ **Key Features**
• 💾 **Conversation Storage**: Save important conversations anytime
• 🧠 **Intelligent Search**: Easily find past conversations
• 🔄 **Persistent Memory**: All conversations preserved after Q CLI restart
• 📋 **Session Management**: View and continue previous sessions

## 🎯 **How to Use Q Memory**

### **🆕 Start New Session**
```
start_session(description="Your topic")
```

### **💾 Auto-Save (Core Feature!)**
```
# All conversations are automatically saved!
# Session start, resume, all interactions are automatically recorded
```

### **🔄 Continue Session After Q CLI Restart**
```
list_sessions()                    # View previous sessions
resume_session(session_id="session_name")  # Resume session
```

## 🛠️ **Available Commands**
• `start_session(description)` - Start a new session (auto-save enabled)
• `list_sessions()` - View all your sessions
• `resume_session(session_id)` - Resume session with full context loaded
• `search_memory_by_session_id(session_id, query)` - Search previous conversations (auto-triggered for memory questions)
• `get_storage_stats()` - Check current status
• `show_usage()` - Show this help again

## 💡 **Workflow Example**

**Auto-Save Conversations:**
```
# 1. Start session (automatically saved)
start_session(description="Python Learning")

# 2. Normal conversation (chat freely in Q CLI)
User: "What's the difference between lists and tuples in Python?"
AI: "Lists are mutable while tuples are immutable..."

# 3. All conversations are automatically saved!
# No separate save command needed
```

**After Q CLI Restart:**
```
list_sessions()
resume_session(session_id="Python_Learning_0708_1600")
search_memory_by_session_id(session_id="Python_Learning_0708_1600", query="lists tuples")  # Find previous conversations
```

💾 **All conversations are automatically saved!** 🚀
🔄 **All conversations persist even after Q CLI restart!** ✨"""


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MCP tools"""
    return [
        Tool(
            name="show_usage",
            description="📖 Show simple usage instructions",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_sessions",
            description="📋 List all previous sessions (for resuming after Q CLI restart)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of sessions to show (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                }
            }
        ),
        Tool(
            name="resume_session",
            description="🔄 Resume a previous session by session ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to resume (from list_sessions)"
                    }
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="start_session",
            description="🚀 Start a new conversation session (ALL interactions will be auto-saved)",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "What you want to work on (e.g., 'Python 학습', 'React 개발', '코드 리뷰')"
                    }
                },
                "required": ["description"]
            }
        ),
        Tool(
            name="search_memory_by_session_id",
            description="Find all conversations by session ID or search for specific topics/content from previous conversations. Use when user asks 'do you remember?', 'what did I say about', 'we talked about', 'previously', 'earlier', 'before', 'what did I mention', 'find that conversation', 'search for', 'what was that about', 'recall', 'look up' etc. Can search current session or other sessions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Required. Session ID to search in (use current active session ID for current session search)"
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional. Content or topic to search for (e.g., 'Python lists', 'headphone recommendation', 'coding problem'). Empty string returns all conversations from the session",
                        "default": ""
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of search results (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="delete_session",
            description="🗑️ Delete a session and all its conversations",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation flag (must be true to delete)",
                        "default": False
                    }
                },
                "required": ["session_id", "confirm"]
            }
        ),
        Tool(
            name="cleanup_old_sessions",
            description="🧹 Clean up sessions older than specified days",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Delete sessions older than this many days",
                        "default": 30,
                        "minimum": 1
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation flag (must be true to delete)",
                        "default": False
                    }
                },
                "required": ["confirm"]
            }
        ),
        Tool(
            name="get_storage_stats",
            description="📊 Get storage statistics and usage information",
            inputSchema={"type": "object", "properties": {}}
        ),

    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls and save ALL interactions"""
    
    mm = get_memory_manager()

    try:
        if name == "show_usage":
            welcome_msg = get_welcome_message()
            print(welcome_msg)
            response_text = ""  # Empty response
        
        elif name == "list_sessions":
            limit = arguments.get("limit", 10)
            sessions = mm.list_all_sessions()
            
            if sessions:
                response_text = f"📋 **Your previous sessions ({len(sessions)} found):**\n\n"
                
                # 최신순으로 정렬
                sessions_sorted = sorted(sessions, key=lambda x: x.get('created_at', ''), reverse=True)
                
                for i, session in enumerate(sessions_sorted[:limit], 1):
                    session_id = session.get('session_id', 'Unknown')
                    description = session.get('description', 'No description')
                    created_at = session.get('created_at', 'Unknown time')
                    conversation_count = session.get('conversation_count', 0)
                    
                    # 날짜 포맷팅
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        formatted_date = created_at
                    
                    response_text += f"**{i}. {session_id}**\n"
                    response_text += f"   📝 Description: {description}\n"
                    response_text += f"   📅 Created: {formatted_date}\n"
                    response_text += f"   💬 Conversations: {conversation_count}\n\n"
                
                response_text += f"💡 **To resume a session:**\n"
                response_text += f"`resume_session(session_id=\"session_name\")`\n\n"
                response_text += f"🔍 **To see conversation history:**\n"
                response_text += f"`search_memory(query=\"your search term\")`"
                
                # 콘솔에도 출력
                print(response_text.replace("**", "").replace("`", ""))
            else:
                response_text = f"📋 **No previous sessions found**\n\n"
                response_text += f"💡 **Start your first session:**\n"
                response_text += f"`start_session(description=\"your topic\")`"
                
                print(response_text.replace("**", "").replace("`", ""))
        
        elif name == "resume_session":
            session_id = arguments["session_id"]
            
            # 세션 존재 확인
            sessions = mm.list_all_sessions()
            target_session = None
            
            for session in sessions:
                if session.get('session_id') == session_id:
                    target_session = session
                    break
            
            if not target_session:
                response_text = f"❌ **Session not found: '{session_id}'**\n\n"
                response_text += "📋 **Available sessions:**\n"
                response_text += "`list_sessions()` to see all sessions"
                
                print(f"❌ Session not found: '{session_id}'")
                print("📋 Available sessions: list_sessions() to see all sessions")
            else:
                # 🔥 핵심: current_session을 먼저 설정
                mm.current_session = session_id
                
                # 세션 재개 (전체 컨텍스트 로드)
                try:
                    resume_result = mm.resume_session(session_id)
                    full_history = resume_result.get('full_history', [])
                    context_length = resume_result.get('context_length', 0)
                    estimated_tokens = resume_result.get('estimated_tokens', 0)
                    
                    # Q CLI 동기화 데몬 시작
                    try:
                        sync_daemon = get_sync_daemon(mm)
                        sync_daemon.start_sync_daemon(session_id)
                        auto_sync_status = "✅ Auto-Sync Enabled"
                    except Exception as e:
                        auto_sync_status = f"❌ Auto-Sync Failed: {e}"
                    
                    # 진실성 컨텍스트 다시 로드
                    truthfulness_reloaded = mm.reload_truthfulness_context()
                    
                    # MCP 응답 생성 (Q가 읽을 컨텍스트)
                    response_text = f"🔄 **Session '{session_id}' resumed with full context**\n\n"
                    
                    # 세션 정보
                    response_text += f"📋 **Session**: {session_id}\n"
                    response_text += f"📝 **Description**: {resume_result.get('description', '')}\n"
                    response_text += f"💬 **Total Conversations**: {len(full_history)}\n"
                    response_text += f"📏 **Context Length**: {context_length:,} characters (~{estimated_tokens:,} tokens)\n"
                    if truthfulness_reloaded:
                        response_text += f"🎯 **Truthfulness Guidelines**: ✅ Reloaded for accuracy\n"
                    response_text += f"💾 **Auto-Save**: {auto_sync_status}\n\n"
                    
                    # 이전 대화 컨텍스트 제공
                    if full_history:
                        response_text += "🧠 **Previous Conversation History:**\n\n"
                        
                        for i, conv in enumerate(full_history, 1):
                            user_msg = conv.get('user_message', '')
                            ai_msg = conv.get('ai_response', '')
                            timestamp = conv.get('timestamp', '')
                            
                            if user_msg and ai_msg:
                                # 타임스탬프 포맷팅
                                time_str = ""
                                if timestamp:
                                    try:
                                        from datetime import datetime
                                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                        time_str = f" ({dt.strftime('%m-%d %H:%M')})"
                                    except:
                                        pass
                                
                                response_text += f"**{i}.{time_str}**\n"
                                response_text += f"**User**: {user_msg}\n"
                                response_text += f"**Assistant**: {ai_msg}\n\n"
                        
                        response_text += f"---\n\n"
                        response_text += f"✅ **All {len(full_history)} previous conversations have been loaded into context.**\n"
                        response_text += f"💡 **I now remember everything we discussed in this session and can continue where we left off.**"
                    else:
                        response_text += "ℹ️ **No previous conversations found in this session.**\n"
                        response_text += "🚀 **Ready to start fresh!**"
                    
                    # 콘솔 출력 (간단한 버전)
                    print(f"🔄 Session '{session_id}' resumed!")
                    print(f"📊 Loaded {len(full_history)} conversations ({context_length:,} chars)")
                    print(f"💾 Auto-Save: {auto_sync_status}")
                    if truthfulness_reloaded:
                        print(f"🎯 Truthfulness Guidelines: ✅ Reloaded")
                    print("🚀 Ready to continue with full context!")
                    
                except Exception as e:
                    response_text = f"❌ **Error resuming session:** {str(e)}"
                    print(f"❌ Error resuming session: {e}")
        
        elif name == "delete_session":
            session_id = arguments["session_id"]
            confirm = arguments.get("confirm", False)
            
            if not confirm:
                response_text = f"⚠️ **Deletion requires confirmation**\n\n"
                response_text += f"To delete session '{session_id}' and ALL its conversations:\n"
                response_text += f"`delete_session(session_id=\"{session_id}\", confirm=true)`\n\n"
                response_text += "❌ **This action cannot be undone!**"
            else:
                try:
                    deleted_items = mm.delete_session(session_id)
                    
                    response_text = f"🗑️ **Session deleted successfully!**\n\n"
                    response_text += f"📋 **Deleted Session**: {session_id}\n"
                    response_text += f"💬 **Conversations Deleted**: {deleted_items.get('conversations', 0)}\n"
                    response_text += f"📊 **Metadata Deleted**: {'✅' if deleted_items.get('session_metadata') else '❌'}\n\n"
                    response_text += "✅ **All data has been permanently removed.**"
                    
                except Exception as e:
                    response_text = f"❌ **Error deleting session:** {str(e)}"
        
        elif name == "cleanup_old_sessions":
            days = arguments.get("days", 30)
            confirm = arguments.get("confirm", False)
            
            if not confirm:
                response_text = f"⚠️ **Cleanup requires confirmation**\n\n"
                response_text += f"This will delete ALL sessions older than {days} days.\n"
                response_text += f"`cleanup_old_sessions(days={days}, confirm=true)`\n\n"
                response_text += "❌ **This action cannot be undone!**"
            else:
                try:
                    cleanup_stats = mm.cleanup_old_sessions(days)
                    
                    response_text = f"🧹 **Cleanup completed!**\n\n"
                    response_text += f"📅 **Cutoff Date**: {cleanup_stats.get('cutoff_date', '')[:10]}\n"
                    response_text += f"🗑️ **Sessions Deleted**: {cleanup_stats.get('sessions_deleted', 0)}\n"
                    response_text += f"💬 **Conversations Deleted**: {cleanup_stats.get('conversations_deleted', 0)}\n\n"
                    
                    if cleanup_stats.get('sessions_deleted', 0) > 0:
                        response_text += "✅ **Old sessions have been cleaned up.**"
                    else:
                        response_text += "ℹ️ **No old sessions found to clean up.**"
                        
                except Exception as e:
                    response_text = f"❌ **Error during cleanup:** {str(e)}"
        

        elif name == "get_storage_stats":
            try:
                stats = mm.get_storage_stats()
                
                # MCP 응답 생성
                response_text = f"📊 **Storage Statistics**\n\n"
                response_text += f"🗄️ **Storage Type**: {stats.get('storage_type', 'unknown')}\n"
                response_text += f"📋 **Total Sessions**: {stats.get('total_sessions', 0)}\n"
                response_text += f"💬 **Total Conversations**: {stats.get('total_conversations', 0)}\n"
                response_text += f"💾 **Storage Size**: {stats.get('storage_size_mb', 'unknown')} MB\n"
                
                if stats.get('current_session'):
                    response_text += f"🔄 **Current Session**: {stats.get('current_session')}\n"
                
                response_text += f"\n💡 **Management commands:**\n"
                response_text += f"• `cleanup_old_sessions(days=30, confirm=true)` - Clean old data\n"
                response_text += f"• `delete_session(session_id=\"name\", confirm=true)` - Delete specific session\n"
                
                # 콘솔에도 출력
                print(response_text.replace("**", "").replace("`", ""))
                
            except Exception as e:
                error_msg = f"❌ Error getting storage stats: {str(e)}"
                print(error_msg)
                response_text = error_msg
        
        elif name == "start_session":
            description = arguments["description"]
            
            result = mm.start_session(description)
            
            status_emoji = "🆕" if result["is_new_session"] else "🔄"
            
            # Q CLI 동기화 데몬 시작
            try:
                sync_daemon = get_sync_daemon(mm)
                sync_daemon.start_sync_daemon(result["session_id"])
                auto_sync_status = "✅ Q CLI Auto-Sync Enabled"
            except Exception as e:
                auto_sync_status = f"❌ Auto-Sync Failed: {e}"
            
            # 콘솔에 직접 출력
            print(f"{status_emoji} Session ready!")
            print(f"📋 Topic: {description}")
            print(f"💾 Auto-Save: {auto_sync_status}")
            print(f"🔄 Persistent: Session survives Q CLI restarts")
            
            # 진실성 컨텍스트 로드 알림
            if result.get("truthfulness_context_loaded"):
                print(f"🎯 Truthfulness Guidelines: ✅ Loaded for accurate responses")
            
            print(f"🚀 Perfect! Everything is ready!")
            print(f"   • Every conversation will be automatically synced from Q CLI")
            print(f"   • AI will prioritize accuracy over speculation")
            print(f"   • Use list_sessions() after restart to resume")
            print(f"   • Just chat normally - everything is saved!")
            print(f"💬 Start chatting - all conversations are automatically saved!")
            
            response_text = ""  # Empty response
        
        elif name == "search_memory_by_session_id":
            session_id = arguments["session_id"]
            query = arguments.get("query", "")
            limit = arguments.get("limit", 10)
            
            result = mm.search_memory_by_session_id(session_id, query, limit)
            
            # 결과에서 실제 검색 결과 리스트 추출
            results = result.get("results", []) if isinstance(result, dict) else []
            stats = result.get("stats", {})
            
            if results:
                search_type = "semantic search" if query.strip() else "all conversations"
                response_text = f"🔍 **Found {len(results)} results from session '{session_id}' ({search_type})**\n\n"
                
                if query.strip():
                    response_text += f"**Query**: {query}\n\n"
                
                for i, result_item in enumerate(results, 1):
                    user_msg = result_item.get('user_message', 'N/A')
                    ai_msg = result_item.get('ai_response', 'N/A')
                    timestamp = result_item.get('timestamp', 'N/A')
                    
                    # 메시지 길이 제한
                    if len(user_msg) > 100:
                        user_msg = user_msg[:100] + "..."
                    if len(ai_msg) > 150:
                        ai_msg = ai_msg[:150] + "..."
                    
                    response_text += f"**{i}. Conversation** ({timestamp[:16] if timestamp != 'N/A' else 'No timestamp'})\n"
                    response_text += f"   👤 **User**: {user_msg}\n"
                    response_text += f"   🤖 **AI**: {ai_msg}\n\n"
                
                response_text += f"📊 **Search Stats**: {stats.get('search_type', 'unknown')} search in session '{session_id}'"
                
                # 콘솔에도 출력
                print(response_text.replace("**", ""))
            else:
                if query.strip():
                    response_text = f"🔍 **No results found for '{query}' in session '{session_id}'**\n\n"
                else:
                    response_text = f"🔍 **No conversations found in session '{session_id}'**\n\n"
                
                if result.get("error"):
                    response_text += f"❌ **Error**: {result['error']}"
                else:
                    response_text += "💡 **Tip**: Try a different search term or check if the session ID is correct."
                
                print(response_text.replace("**", ""))
        
        elif name == "get_daemon_status":
            force_sync = arguments.get("force_sync", False)
            
            try:
                # Daemon 상태 확인
                sync_daemon = get_sync_daemon(mm)
                daemon_status = sync_daemon.get_status()
                
                response_text = f"🔄 **Q CLI Sync Daemon Status**\n\n"
                response_text += f"🟢 **Running**: {'Yes' if daemon_status.get('running') else 'No'}\n"
                response_text += f"📍 **Q CLI DB**: {daemon_status.get('q_cli_db_path', 'Not found')}\n"
                response_text += f"📋 **Current Session**: {daemon_status.get('current_session', 'None')}\n"
                response_text += f"📊 **Last Message Count**: {daemon_status.get('last_message_count', 0)}\n"
                response_text += f"🧵 **Thread Alive**: {'Yes' if daemon_status.get('thread_alive') else 'No'}\n\n"
                
                if force_sync:
                    response_text += f"🔄 **Force Sync Requested**\n\n"
                    
                    # 강제 동기화 실행
                    import sqlite3
                    import json
                    from pathlib import Path
                    
                    if sync_daemon.q_cli_db_path:
                        current_cwd = str(Path.cwd())
                        conn = sqlite3.connect(sync_daemon.q_cli_db_path)
                        cursor = conn.execute(
                            "SELECT value FROM conversations WHERE key = ?", 
                            [current_cwd]
                        )
                        
                        result = cursor.fetchone()
                        if result:
                            conversation_data = json.loads(result[0])
                            all_messages = conversation_data.get('history', [])
                            
                            # 모든 메시지 파싱
                            conversations = sync_daemon.match_prompts_and_responses(all_messages)
                            
                            # ChromaDB에 저장
                            saved_count = 0
                            for user_msg, ai_msg in conversations:
                                try:
                                    success = mm.add_conversation(user_msg, ai_msg)
                                    if success:
                                        saved_count += 1
                                except Exception as e:
                                    print(f"Error saving conversation: {e}")
                            
                            response_text += f"✅ **Sync Complete**\n"
                            response_text += f"   📊 Total Q CLI messages: {len(all_messages)}\n"
                            response_text += f"   💬 Parsed conversation pairs: {len(conversations)}\n"
                            response_text += f"   ✅ Successfully saved: {saved_count}\n"
                            response_text += f"   ❌ Failed to save: {len(conversations) - saved_count}\n"
                        else:
                            response_text += f"❌ **No Q CLI data found for current directory**\n"
                        
                        conn.close()
                    else:
                        response_text += f"❌ **Q CLI database not accessible**\n"
                
                response_text += f"\n💡 **Tips:**\n"
                response_text += f"• Use `force_sync=true` to manually sync all conversations\n"
                response_text += f"• Daemon should auto-sync new conversations every 2 seconds\n"
                response_text += f"• Check Q CLI database path if sync is not working"
                
                # 콘솔에도 출력
                print(response_text.replace("**", ""))
                
            except Exception as e:
                error_msg = f"❌ Error checking daemon status: {str(e)}"
                print(error_msg)
                response_text = error_msg
        
        elif name == "get_recent_conversations":
            limit = arguments.get("limit", 10)
            result = mm.get_recent_conversations(limit)
            
            # 결과에서 실제 대화 리스트 추출
            conversations = result.get("conversations", []) if isinstance(result, dict) else []
            
            if conversations:
                response_text = f"💬 **Your recent {len(conversations)} conversations:**\n\n"
                for i, conv in enumerate(conversations, 1):
                    memory_text = conv.get('memory', 'N/A')
                    if len(memory_text) > 120:
                        memory_text = memory_text[:120] + "..."
                    response_text += f"{i}. {memory_text}\n\n"
                
                response_text += "💾 This request was also saved to your memory!"
                
                # 콘솔에도 출력
                print(response_text.replace("**", ""))
            else:
                response_text = "💬 **No conversations yet.**\n\n"
                response_text += "💾 But this request was just saved! Keep using tools and you'll see them accumulate."
                
                print(response_text.replace("**", ""))
        
        else:
            print(f"❌ Unknown command: {name}")
            print()
            print(f"💡 Available commands: show_usage() to see all options")
            response_text = ""
        
        return [TextContent(type="text", text=response_text)]
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()
        print(f"💡 Help: Use show_usage() for guidance")
        error_response = ""
        
        return [TextContent(type="text", text=error_response)]


async def main():
    """Main entry point for the MCP server"""
    print("🚀 Starting Q_mem-MCP-Server with direct ChromaDB implementation...")
    print("💾 Every single interaction will be automatically saved")
    print("🔄 Data persists across Q CLI restarts")
    print("🎯 Truthfulness guidelines loaded for accurate responses")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
