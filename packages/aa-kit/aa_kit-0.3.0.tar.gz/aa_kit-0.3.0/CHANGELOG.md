# Changelog

All notable changes to AA Kit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-10

### Added
- **Conversation Management System**: Complete conversation support with context management
  - `agent.conversation()` - Context manager for maintaining conversation state
  - `agent.interactive()` - Interactive REPL mode for terminal conversations
  - Conversation saving/loading with JSON persistence
  - Session-based memory isolation for concurrent conversations
  - AsyncConversation class for async contexts
- **Interactive Features**:
  - Terminal-based chat interface with history
  - Commands: `help`, `history`, `save`, `clear`, `exit`
  - Colored output for better readability
- New documentation pages for conversation features
- Comprehensive test suite for conversation management

### Changed
- Enhanced chat methods to support session IDs for conversation isolation
- Improved message handling to ensure proper recording only on successful API calls

### Fixed
- Message recording now happens after successful API calls, preventing failed attempts from being stored
- Fixed pytest asyncio configuration issues

## [0.2.0] - 2025-01-10

### Added
- **Dual API Support**: Synchronous and asynchronous APIs for all major methods
  - `agent.chat()` - Synchronous chat (no async/await needed\!)
  - `agent.achat()` - Asynchronous chat
  - `agent.stream_chat()` - Synchronous streaming
  - `agent.astream_chat()` - Asynchronous streaming
  - Similar dual APIs for `add_tool`, `remove_tool`, `clear_memory`
- Comprehensive documentation for the dual API feature
- New examples demonstrating synchronous usage
- Test suite for both sync and async APIs

### Changed
- **Breaking**: Async methods now have 'a' prefix (e.g., `chat` → `achat`)
  - Migration is simple: just add 'a' prefix to async method calls
- Improved developer experience with zero-friction synchronous API
- Updated all documentation and examples to showcase sync-first approach

### Fixed
- Better error handling for synchronous method calls
- Improved initialization flow for sync usage

## [0.1.0] - 2025-01-09

### Added
- Initial release of AA Kit
- Core Agent class with MCP-native design
- Support for OpenAI and Anthropic models
- Built-in reasoning patterns (Simple, ReAct, Chain of Thought)
- Memory backends (Redis, SQLite, PostgreSQL)
- Tool system with automatic MCP conversion
- Production features (rate limiting, retries, caching)
- Comprehensive documentation and examples

[0.3.0]: https://github.com/josharsh/aa-kit/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/josharsh/aa-kit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/josharsh/aa-kit/releases/tag/v0.1.0
