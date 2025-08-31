#!/usr/bin/env python3
"""
Multi-format conversation export for Claude Opus 4/4.1 Chat Agent

This module provides conversation export functionality in JSON, TXT, MD, and HTML formats
with proper formatting and styling for each format.
"""

import json
import html
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from config import get_model_config


class ConversationExporter:
    """Handle conversation export in multiple formats"""
    
    def __init__(self, agent_id: str, export_dir: Path, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.export_dir = export_dir
        self.config = config
        self.model_config = get_model_config(config.get('model', 'claude-opus-4-20250514'))
        
    def export(self, messages: List[Dict[str, Any]], format_type: str, statistics: Dict[str, Any]) -> str:
        """Export conversation in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "json":
            return self._export_json(messages, timestamp, statistics)
        elif format_type == "txt":
            return self._export_txt(messages, timestamp)
        elif format_type == "md":
            return self._export_markdown(messages, timestamp)
        elif format_type == "html":
            return self._export_html(messages, timestamp, statistics)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _export_json(self, messages: List[Dict[str, Any]], timestamp: str, statistics: Dict[str, Any]) -> str:
        """Export as JSON format"""
        filename = f"conversation_{timestamp}.json"
        filepath = self.export_dir / filename
        
        export_data = {
            "agent_id": self.agent_id,
            "exported_at": datetime.now().isoformat(),
            "config": self.config,
            "messages": messages,
            "statistics": statistics
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def _export_txt(self, messages: List[Dict[str, Any]], timestamp: str) -> str:
        """Export as plain text format"""
        filename = f"conversation_{timestamp}.txt"
        filepath = self.export_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Anthropic {self.model_config['name']} Chat Agent Conversation Export\n")
            f.write(f"Agent ID: {self.agent_id}\n")
            f.write(f"Model: {self.config.get('model', 'Unknown')}\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            for msg in messages:
                timestamp_str = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp_str}] {msg['role'].upper()}:\n")
                f.write(f"{msg['content']}\n\n")
        
        return str(filepath)
    
    def _export_markdown(self, messages: List[Dict[str, Any]], timestamp: str) -> str:
        """Export as Markdown format"""
        filename = f"conversation_{timestamp}.md"
        filepath = self.export_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Anthropic {self.model_config['name']} Chat Agent Conversation\n\n")
            f.write(f"**Agent ID:** {self.agent_id}  \n")
            f.write(f"**Model:** {self.config.get('model', 'Unknown')}  \n")
            f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n\n")
            
            for msg in messages:
                timestamp_str = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                role_emoji = "🧑" if msg["role"] == "user" else "🤖"
                f.write(f"## {role_emoji} {msg['role'].title()} - {timestamp_str}\n\n")
                f.write(f"{msg['content']}\n\n")
        
        return str(filepath)
    
    def _export_html(self, messages: List[Dict[str, Any]], timestamp: str, statistics: Dict[str, Any]) -> str:
        """Export as HTML format with styling"""
        filename = f"conversation_{timestamp}.html"
        filepath = self.export_dir / filename
        
        html_content = self._generate_html_content(messages, statistics)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def _generate_html_content(self, messages: List[Dict[str, Any]], statistics: Dict[str, Any]) -> str:
        """Generate complete HTML content with styling"""
        model_display = self.model_config['name']
        
        # HTML template with modern styling
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anthropic {model_display} Conversation - {self.agent_id}</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --secondary-color: #f1f5f9;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
            --user-bg: #3b82f6;
            --assistant-bg: #10b981;
            --code-bg: #f8fafc;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 1rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            overflow: hidden;
        }}

        .header {{
            background: var(--primary-color);
            color: white;
            padding: 2rem;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}

        .header-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
            font-size: 0.9rem;
        }}

        .stats {{
            background: var(--secondary-color);
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-color);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }}

        .stat-item {{
            text-align: center;
            padding: 1rem;
            background: white;
            border-radius: 0.5rem;
            box-shadow: var(--shadow);
        }}

        .stat-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary-color);
        }}

        .stat-label {{
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 0.25rem;
        }}

        .messages {{
            padding: 2rem;
            max-height: 70vh;
            overflow-y: auto;
        }}

        .message {{
            margin-bottom: 2rem;
            display: flex;
            align-items: flex-start;
            gap: 1rem;
        }}

        .message.user {{
            flex-direction: row-reverse;
        }}

        .message-avatar {{
            width: 3rem;
            height: 3rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            font-weight: bold;
            color: white;
            flex-shrink: 0;
        }}

        .message.user .message-avatar {{
            background: var(--user-bg);
        }}

        .message.assistant .message-avatar {{
            background: var(--assistant-bg);
        }}

        .message-content {{
            flex: 1;
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: var(--shadow);
        }}

        .message.user .message-content {{
            background: #eff6ff;
            border-color: var(--user-bg);
        }}

        .message.assistant .message-content {{
            background: #f0fdf4;
            border-color: var(--assistant-bg);
        }}

        .message-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
        }}

        .message-role {{
            font-weight: 600;
            text-transform: capitalize;
        }}

        .message-time {{
            font-size: 0.8rem;
            color: #64748b;
        }}

        .message-text {{
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .code-block {{
            background: var(--code-bg);
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9rem;
        }}

        .footer {{
            background: var(--secondary-color);
            padding: 1rem 2rem;
            text-align: center;
            font-size: 0.8rem;
            color: #64748b;
            border-top: 1px solid var(--border-color);
        }}

        @media (max-width: 768px) {{
            body {{ padding: 1rem; }}
            .header {{ padding: 1.5rem; }}
            .header h1 {{ font-size: 1.5rem; }}
            .header-info {{ grid-template-columns: 1fr; }}
            .messages {{ padding: 1rem; }}
            .message-content {{ padding: 1rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Anthropic {model_display} Chat Agent</h1>
            <p>Conversation Export</p>
            <div class="header-info">
                <div><strong>Agent ID:</strong> {self.agent_id}</div>
                <div><strong>Model:</strong> {self.config.get('model', 'Unknown')}</div>
                <div><strong>Exported:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div><strong>Temperature:</strong> {self.config.get('temperature', 1.0)}</div>
            </div>
        </div>

        <div class="stats">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value">{statistics.get('total_messages', 0)}</div>
                    <div class="stat-label">Total Messages</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{statistics.get('user_messages', 0)}</div>
                    <div class="stat-label">User Messages</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{statistics.get('assistant_messages', 0)}</div>
                    <div class="stat-label">Assistant Messages</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{statistics.get('total_characters', 0):,}</div>
                    <div class="stat-label">Total Characters</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{statistics.get('average_message_length', 0):,}</div>
                    <div class="stat-label">Avg Message Length</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{statistics.get('conversation_duration', 'N/A')}</div>
                    <div class="stat-label">Duration</div>
                </div>
            </div>
        </div>

        <div class="messages">"""

        # Generate messages
        for msg in messages:
            timestamp_str = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            role = msg["role"]
            content = msg["content"]
            
            # Escape HTML content
            content_escaped = html.escape(content)
            
            # Handle code blocks
            if '```' in content_escaped:
                parts = content_escaped.split('```')
                formatted_content = ""
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Code block
                        formatted_content += f'<div class="code-block">{part}</div>'
                    else:  # Regular text
                        formatted_content += part
                content_escaped = formatted_content
            
            avatar_text = "U" if role == "user" else "AI"
            
            html_template += f"""
            <div class="message {role}">
                <div class="message-avatar">{avatar_text}</div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="message-role">{role}</span>
                        <span class="message-time">{timestamp_str}</span>
                    </div>
                    <div class="message-text">{content_escaped}</div>
                </div>
            </div>"""

        # Close HTML structure
        html_template += f"""
        </div>

        <div class="footer">
            Generated by Anthropic {model_display} Chat Agent • Agent ID: {self.agent_id} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""

        return html_template