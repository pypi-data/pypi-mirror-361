"""
Conversation Management for AA Kit

Provides context managers for managing stateful conversations with agents.
Supports both synchronous and asynchronous usage patterns.
"""

import uuid
from typing import Optional, List, Dict, Any
from contextlib import contextmanager, asynccontextmanager
from datetime import datetime

from .exceptions import AAKitError


class ConversationMessage:
    """Represents a single message in a conversation."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class Conversation:
    """
    Manages a conversation session with an agent.
    
    Example:
        >>> with agent.conversation() as chat:
        ...     response = chat.send("Hello!")
        ...     response = chat.send("Tell me more")
    """
    
    def __init__(self, agent, session_id: Optional[str] = None, title: Optional[str] = None):
        self.agent = agent
        self.session_id = session_id or str(uuid.uuid4())
        self.title = title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.messages: List[ConversationMessage] = []
        self._started_at = datetime.now()
    
    def send(self, message: str) -> str:
        """Send a message and get a response (synchronous)."""
        # Get response from agent first
        response = self.agent.chat(message, session_id=self.session_id)
        
        # Only record messages if successful
        self.messages.append(ConversationMessage("user", message))
        self.messages.append(ConversationMessage("assistant", response))
        
        return response
    
    def history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self) -> None:
        """Clear conversation history."""
        self.messages.clear()
        if self.agent._memory:
            self.agent.clear_memory(session_id=self.session_id)
    
    def save(self, path: Optional[str] = None) -> str:
        """Save conversation to file."""
        import json
        
        path = path or f"conversation_{self.session_id}.json"
        
        data = {
            "session_id": self.session_id,
            "title": self.title,
            "started_at": self._started_at.isoformat(),
            "messages": self.history(),
            "agent": {
                "name": self.agent.config.name,
                "model": self.agent.config.model,
                "instruction": self.agent.config.instruction[:100] + "..."
            }
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        
        return path
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Optionally clear memory on exit (configurable)
        # exc_type, exc_val, exc_tb are required by context manager protocol
        pass


class AsyncConversation:
    """
    Async version of Conversation for async contexts.
    
    Example:
        >>> async with agent.aconversation() as chat:
        ...     response = await chat.send("Hello!")
        ...     response = await chat.send("Tell me more")
    """
    
    def __init__(self, agent, session_id: Optional[str] = None, title: Optional[str] = None):
        self.agent = agent
        self.session_id = session_id or str(uuid.uuid4())
        self.title = title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.messages: List[ConversationMessage] = []
        self._started_at = datetime.now()
    
    async def send(self, message: str) -> str:
        """Send a message and get a response (asynchronous)."""
        # Get response from agent first
        response = await self.agent.achat(message, session_id=self.session_id)
        
        # Only record messages if successful
        self.messages.append(ConversationMessage("user", message))
        self.messages.append(ConversationMessage("assistant", response))
        
        return response
    
    async def stream(self, message: str):
        """Stream a response (asynchronous)."""
        # Record user message
        self.messages.append(ConversationMessage("user", message))
        
        # Stream response from agent
        full_response = ""
        async for chunk in self.agent.astream_chat(message, session_id=self.session_id):
            full_response += chunk
            yield chunk
        
        # Record complete agent response
        self.messages.append(ConversationMessage("assistant", full_response))
    
    def history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return [msg.to_dict() for msg in self.messages]
    
    async def clear(self) -> None:
        """Clear conversation history."""
        self.messages.clear()
        if self.agent._memory:
            await self.agent.aclear_memory(session_id=self.session_id)
    
    def save(self, path: Optional[str] = None) -> str:
        """Save conversation to file."""
        import json
        
        path = path or f"conversation_{self.session_id}.json"
        
        data = {
            "session_id": self.session_id,
            "title": self.title,
            "started_at": self._started_at.isoformat(),
            "messages": self.history(),
            "agent": {
                "name": self.agent.config.name,
                "model": self.agent.config.model,
                "instruction": self.agent.config.instruction[:100] + "..."
            }
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        
        return path
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Optionally clear memory on exit (configurable)
        # exc_type, exc_val, exc_tb are required by context manager protocol
        pass


def interactive_conversation(agent, title: Optional[str] = None) -> None:
    """
    Start an interactive conversation in the terminal.
    
    Example:
        >>> agent.interactive()
        AA Kit Interactive Mode
        Type 'exit' to quit, 'clear' to clear history, 'save' to save conversation
        
        You: Hello!
        Assistant: Hello! How can I help you today?
        
        You: exit
        Goodbye!
    """
    print(f"\n🤖 AA Kit Interactive Mode - {agent.config.name}")
    print("=" * 50)
    print("Commands: 'exit' to quit, 'clear' to clear history, 'save' to save conversation")
    print("=" * 50)
    
    with agent.conversation(title=title) as chat:
        try:
            while True:
                # Get user input
                user_input = input("\n\x1b[1;34mYou:\x1b[0m ")
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n\x1b[1;32m👋 Goodbye!\x1b[0m")
                    break
                elif user_input.lower() == 'clear':
                    chat.clear()
                    print("\x1b[1;33m🧹 Conversation cleared.\x1b[0m")
                    continue
                elif user_input.lower() == 'save':
                    path = chat.save()
                    print(f"\x1b[1;32m💾 Conversation saved to: {path}\x1b[0m")
                    continue
                elif user_input.lower() == 'history':
                    print("\n\x1b[1;33m📜 Conversation History:\x1b[0m")
                    for msg in chat.messages:
                        role_color = "\x1b[1;34m" if msg.role == "user" else "\x1b[1;36m"
                        print(f"{role_color}{msg.role}:\x1b[0m {msg.content}")
                    continue
                elif not user_input.strip():
                    continue
                
                # Get and display response
                print("\n\x1b[1;36mAssistant:\x1b[0m ", end="", flush=True)
                
                # Stream response if available
                if hasattr(agent, 'stream_chat'):
                    for chunk in agent.stream_chat(user_input, session_id=chat.session_id):
                        print(chunk, end="", flush=True)
                    print()  # New line after streaming
                    
                    # Record the response for history
                    chat.messages.append(ConversationMessage("user", user_input))
                    # Note: We'd need to accumulate the streamed response for history
                else:
                    response = chat.send(user_input)
                    print(response)
                    
        except KeyboardInterrupt:
            print("\n\n\x1b[1;33m⚠️  Interrupted. Type 'exit' to quit properly.\x1b[0m")
        except Exception as e:
            print(f"\n\x1b[1;31m❌ Error: {e}\x1b[0m")