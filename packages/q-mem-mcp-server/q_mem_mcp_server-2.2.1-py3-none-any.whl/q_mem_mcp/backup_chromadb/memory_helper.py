"""
Simple conversation recording functions
"""

from .memory_manager import MemoryManager


def record_conversation(user_message: str, ai_response: str, memory_manager: MemoryManager):
    """Record a conversation to memory"""
    try:
        memory_manager.add_conversation(user_message, ai_response)
        print(f"💾 Conversation recorded")
    except Exception as e:
        print(f"Warning: Could not record conversation: {e}")


async def start_auto_recording(memory_manager: MemoryManager):
    """Start auto recording (placeholder for compatibility)"""
    print("🎙️ Auto recording ready")


def get_auto_recorder(memory_manager: MemoryManager):
    """Get auto recorder (placeholder for compatibility)"""
    return None
