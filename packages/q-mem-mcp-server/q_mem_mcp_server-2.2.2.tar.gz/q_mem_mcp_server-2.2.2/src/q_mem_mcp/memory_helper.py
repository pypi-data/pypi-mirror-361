"""
Memory Helper for SQLite-based Q Memory MCP Server
Simple helper functions for memory management
"""

from typing import Optional, Dict, Any


def get_auto_recorder():
    """Get auto recorder instance (placeholder for compatibility)"""
    return None


def start_auto_recording(workspace_id: str):
    """Start auto recording (placeholder for compatibility)"""
    pass


def get_memory_context() -> Dict[str, Any]:
    """Get current memory context"""
    return {
        "storage_type": "sqlite_fts5",
        "auto_recording": True,
        "search_engine": "fts5"
    }
