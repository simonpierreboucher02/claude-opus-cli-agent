# 🎼 Claude Opus 4 / 4.1 CLI Chat Agent  

**👨‍💻 Author: Simon-Pierre Boucher**  

<div align="center">  

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)  
![Anthropic](https://img.shields.io/badge/Anthropic-API-green?logo=anthropic&logoColor=white)  
![License](https://img.shields.io/badge/License-MIT-yellow)  
![Version](https://img.shields.io/badge/Version-1.0.0-purple)  

**A production-ready, modular Python CLI agent for Claude Opus 4 and 4.1 models**  
*Supports both `claude-opus-4-20250514` and `claude-opus-4-1-20250805` with advanced configuration and exports*  

[✨ Features](#-features) • [⚙️ Installation](#-installation) • [🚀 Usage Examples](#-usage-examples) • [💬 Commands](#-interactive-commands) • [📎 File Inclusion](#-file-inclusion) • [⚙️ Configuration](#-configuration-options) • [📂 Agent Structure](#-agent-directory-structure) • [🎨 Export Formats](#-export-formats) • [🔧 Advanced Features](#-advanced-features) • [🚨 Error Handling](#-error-handling) • [🧪 Model Comparison](#-model-comparison) • [🤝 Contributing](#-contributing) • [📄 License](#-license)  

</div>  

---

## ✨ Features  

- 🔹 **Multi-model Support**: Claude Opus 4 & 4.1  
- 💬 **Persistent Conversations**: Automatic history & backups  
- 📁 **File Inclusion**: `{filename}` syntax with many formats  
- 📤 **Export Formats**: JSON, TXT, Markdown, HTML  
- 🎨 **Interactive CLI**: Colored output & user-friendly commands  
- ⚙️ **Configuration Management** with YAML + dataclasses  
- 📊 **Logging & Statistics** with conversation analytics  
- 🌊 **Streaming Support**: Real-time responses  
- 🔑 **Secure API Key Handling**  

---

## ⚙️ Installation  

Clone the repository:  
```bash
git clone https://github.com/simonpierreboucher02/claude-opus-cli-agent.git
cd claude-opus-cli-agent
```

Create and activate a virtual environment (recommended):  
```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:  
```bash
pip install -r requirements.txt
```

Set your Anthropic API key:  
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```  

Or the system will prompt you to enter and save it securely.  

---

## 🚀 Usage Examples  

### Start a chat with Claude Opus 4  
```bash
python main.py --agent-id my-agent --model claude-opus-4-20250514
```  

### Start a chat with Claude Opus 4.1  
```bash
python main.py --agent-id my-agent --model claude-opus-4-1-20250805
```  

### List agents & show info  
```bash
python main.py --list
python main.py --info my-agent
```  

### Configure agent  
```bash
python main.py --agent-id my-agent --config
python main.py --agent-id my-agent --temperature 0.7 --no-stream
```  

### Export conversations  
```bash
python main.py --agent-id my-agent --export html
python main.py --agent-id my-agent --export json
python main.py --agent-id my-agent --export md
python main.py --agent-id my-agent --export txt
```  

---

## 💬 Interactive Commands  

- `/help` → Show help  
- `/history [n]` → Last n messages  
- `/search <term>` → Search history  
- `/stats` → Conversation statistics  
- `/config` → Show config  
- `/export <format>` → Export (json/txt/md/html)  
- `/clear` → Clear history  
- `/files` → List files  
- `/info` → Show agent info  
- `/quit` → Exit chat  

---

## 📎 File Inclusion  

```
Analyze this code: {main.py}  
Review configs: {config.yaml} {package.json}  
```  

Supported: `.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`, `.go`, `.rs`, `.html`, `.css`, `.json`, `.yaml`, `.md`, `.txt`, etc.  

---

## ⚙️ Configuration Options  

Configurable via YAML or CLI overrides:  

```yaml
model: claude-opus-4-20250514
temperature: 1.0
max_tokens: 32000
max_history_size: 1000
stream: true
system_prompt: "You are Claude, an AI assistant."
top_p: 1.0
frequency_penalty: 0.0
presence_penalty: 0.0
```  

---

## 📂 Agent Directory Structure  

```
agents/
└── my-agent/
    ├── config.yaml
    ├── history.json
    ├── secrets.json
    ├── backups/
    ├── logs/
    ├── exports/
    └── uploads/
```  

---

## 🎨 Export Formats  

- **HTML** → Responsive, styled, with code highlighting  
- **JSON** → Full metadata + config  
- **Markdown** → Clean GitHub format  
- **TXT** → Plain text  

---

## 🔧 Advanced Features  

- 🔍 Full-text search in history  
- 💾 Incremental backups with retention  
- 📊 Statistics & analytics  
- 📝 Rotating logs  
- 🧑‍🤝‍🧑 Multi-agent support  

---

## 🚨 Error Handling  

- ⏱️ Rate limit backoff  
- 🌐 Network retries  
- ❌ Graceful dependency fallback  
- 🙌 User-friendly errors  

---

## 🧪 Model Comparison  

| Feature | Claude Opus 4 | Claude Opus 4.1 |
|---------|---------------|-----------------|
| Max Tokens | 32,000 | 32,000 |
| Timeout | 300s | 300s |
| Streaming | ✅ | ✅ |
| File Inclusion | ✅ | ✅ |  

---

## 🤝 Contributing  

Easy to extend:  
- Add exports in `export.py`  
- Utilities in `utils.py`  
- Config in `config.py`  
- Commands in `main.py`  

---

## 📄 License  

MIT License — professional & educational use.  

---

**2025-08-29**  
*Université Laval*  
