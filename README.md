# Claude Opus 4/4.1 Chat Agent

A production-ready, modular Python CLI chat agent for both Claude Opus 4 and 4.1 models from Anthropic.

## 🚀 Features

- **Multi-model Support**: Works with both Claude Opus 4 (`claude-opus-4-20250514`) and Claude Opus 4.1 (`claude-opus-4-1-20250805`)
- **Persistent Conversations**: Automatic conversation history with incremental backups
- **File Inclusion**: Include files in messages using `{filename}` syntax with extensive format support
- **Multiple Export Formats**: Export conversations as JSON, TXT, Markdown, or HTML
- **Interactive CLI**: Rich command-line interface with colored output
- **Configuration Management**: Flexible configuration with YAML files and dataclasses
- **Logging & Statistics**: Comprehensive logging and conversation analytics
- **Streaming Support**: Real-time streaming responses from the API
- **Secure API Key Management**: Environment variables or secure file storage

## 📁 Structure

```
📁 Structure:
- main.py - CLI entry point with argument parsing
- agent.py - Core chat agent implementation  
- config.py - Configuration management with dataclasses
- utils.py - Utilities for directories, logging, backups
- export.py - Multi-format conversation export (JSON/TXT/MD/HTML)
- agents/ - Per-agent data storage (config, history, logs, exports)
```

## 🛠 Installation

1. Clone or download the files to your directory
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```
   Or the agent will prompt you to enter it and save it securely.

## 🎯 Usage Examples

### Basic Usage

```bash
# Start chat with Claude Opus 4
python main.py --agent-id my-agent --model claude-opus-4-20250514

# Start chat with Claude Opus 4.1  
python main.py --agent-id my-agent --model claude-opus-4-1-20250805

# List all agents
python main.py --list

# Show agent information
python main.py --info my-agent
```

### Configuration

```bash
# Configure agent interactively
python main.py --agent-id my-agent --config

# Override temperature
python main.py --agent-id my-agent --temperature 0.7

# Disable streaming
python main.py --agent-id my-agent --no-stream
```

### Export Conversations

```bash
# Export as HTML
python main.py --agent-id my-agent --export html

# Export as JSON
python main.py --agent-id my-agent --export json

# Export as Markdown
python main.py --agent-id my-agent --export md

# Export as plain text
python main.py --agent-id my-agent --export txt
```

## 💬 Interactive Commands

Once in chat mode, use these commands:

- `/help` - Show available commands
- `/history [n]` - Show last n messages (default 5)  
- `/search <term>` - Search conversation history
- `/stats` - Show conversation statistics
- `/config` - Show current configuration
- `/export <format>` - Export conversation (json|txt|md|html)
- `/clear` - Clear conversation history
- `/files` - List files available for inclusion
- `/info` - Show agent information
- `/quit` - Exit chat

## 📎 File Inclusion

Include file content in your messages using `{filename}` syntax:

```
Analyze this code: {main.py}
Review these configs: {config.yaml} {package.json}
```

**Supported file types:**
- Programming languages: `.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`, `.go`, `.rs`, etc.
- Configuration files: `.json`, `.yaml`, `.toml`, `.ini`, `.env`, etc.  
- Documentation: `.md`, `.txt`, `.rst`, etc.
- Web files: `.html`, `.css`, `.scss`, etc.
- And many more...

## ⚙️ Configuration Options

The agent configuration supports:

```yaml
model: claude-opus-4-20250514  # or claude-opus-4-1-20250805
temperature: 1.0               # 0.0-2.0
max_tokens: 32000             # Max response tokens
max_history_size: 1000        # Max conversation history
stream: true                  # Enable streaming responses
system_prompt: "You are Claude, an AI assistant."
top_p: 1.0                   # Nucleus sampling
frequency_penalty: 0.0       # Frequency penalty
presence_penalty: 0.0        # Presence penalty
```

## 📂 Agent Directory Structure

Each agent creates its own directory structure:

```
agents/
└── your-agent-id/
    ├── config.yaml          # Agent configuration
    ├── history.json         # Conversation history
    ├── secrets.json         # API keys (auto-added to .gitignore)
    ├── backups/            # Incremental history backups
    │   ├── history_20240101_120000.json
    │   └── ...
    ├── logs/               # Daily log files
    │   ├── 2024-01-01.log
    │   └── ...
    ├── exports/            # Conversation exports
    │   ├── conversation_20240101_120000.html
    │   └── ...
    └── uploads/            # File uploads directory
```

## 🔒 Security Features

- API keys stored in separate `secrets.json` files (auto-added to .gitignore)
- Environment variable support for API keys
- File size limits (2MB max) for inclusions
- Supported file type restrictions
- Input validation and sanitization

## 🎨 Export Formats

### HTML Export
Beautiful, responsive HTML with:
- Modern CSS styling
- Conversation statistics
- Syntax highlighting for code blocks
- Mobile-responsive design

### JSON Export
Complete data export including:
- Full conversation history
- Agent configuration
- Conversation statistics
- Timestamps and metadata

### Markdown Export
Clean Markdown format with:
- Proper heading structure
- Emoji indicators for user/assistant
- Timestamp information

### Text Export
Simple plain text format for:
- Easy reading
- Text processing
- Archive purposes

## 🔧 Advanced Features

### Search & History
- Full-text search through conversation history
- Conversation statistics and analytics
- Message preview and navigation

### Backup System
- Automatic incremental backups before changes
- Configurable backup retention (default: 10 backups)
- Safe history management

### Logging
- Daily rotating log files
- Comprehensive error logging
- Debug information for troubleshooting

### Multi-Agent Support
- Multiple agents with separate configurations
- Agent listing and management
- Per-agent statistics and exports

## 🚨 Error Handling

The agent includes robust error handling:
- API rate limiting with exponential backoff
- Network timeout handling with retries
- Graceful degradation for missing dependencies
- User-friendly error messages

## 🧪 Model Comparison

Both supported models offer:

| Feature | Claude Opus 4 | Claude Opus 4.1 |
|---------|---------------|------------------|
| Max Tokens | 32,000 | 32,000 |
| Timeout | 300s | 300s |
| Streaming | ✅ | ✅ |
| File Inclusion | ✅ | ✅ |

## 🤝 Contributing

The modular architecture makes it easy to:
- Add new export formats in `export.py`
- Add new utility functions in `utils.py`
- Extend configuration options in `config.py`
- Add new CLI commands in `main.py`

## 📄 License

This project is provided as-is for educational and development purposes.

## 🆘 Support

If you encounter issues:
1. Check the daily log files in `agents/{agent-id}/logs/`
2. Verify your API key is correctly set
3. Ensure you have the required dependencies installed
4. Check file permissions for the agents directory

---

**Happy chatting with Claude!** 🤖✨