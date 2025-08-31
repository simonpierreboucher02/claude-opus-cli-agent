#!/usr/bin/env python3
"""
Core chat agent implementation for Claude Opus 4/4.1

This module provides the main chat agent functionality including API communication,
message handling, conversation management, and interactive features.
"""

import json
import time
import yaml
import requests
from pathlib import Path
from typing import Generator, List, Dict, Any, Optional
from datetime import datetime
from requests.exceptions import RequestException, Timeout

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    # Fallback if colorama is not available
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""

from config import AgentConfig, get_model_config, is_supported_model, get_supported_models
from utils import (
    setup_directories, setup_logging, create_backup, get_api_key,
    process_file_inclusions, list_available_files, save_json_file, load_json_file
)
from export import ConversationExporter


class ClaudeChatAgent:
    """Claude Opus 4/4.1 chat agent with persistence and streaming support"""
    
    def __init__(self, agent_id: str, model: str = "claude-opus-4-20250514"):
        self.agent_id = agent_id
        self.base_dir = Path(f"agents/{agent_id}")
        self.api_url = "https://api.anthropic.com/v1/messages"
        
        # Validate model
        if not is_supported_model(model):
            raise ValueError(f"Unsupported model: {model}. Supported models: {list(get_supported_models().keys())}")
        
        # Setup directories
        setup_directories(self.base_dir)
        
        # Setup logging
        self.logger = setup_logging(agent_id, self.base_dir)
        
        # Load or create configuration
        self.config = self._load_config(model)
        
        # Load conversation history
        self.messages = self._load_history()
        
        # Get API key
        model_display = get_model_config(self.config.model)['name']
        self.api_key = get_api_key(self.base_dir, model_display)
        
        # Setup exporter
        self.exporter = ConversationExporter(agent_id, self.base_dir / "exports", self.config.to_dict())
        
        self.logger.info(f"Initialized Claude Chat Agent: {agent_id} with model {self.config.model}")
    
    def _load_config(self, model: str = None) -> AgentConfig:
        """Load agent configuration from config.yaml"""
        config_file = self.base_dir / "config.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    config = AgentConfig(**config_data)
                    if model and config.model != model:
                        config.model = model
                        self._save_config(config)
                    return config
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
        
        # Create new config
        config = AgentConfig(model=model or "claude-opus-4-20250514")
        self._save_config(config)
        return config
    
    def _save_config(self, config: Optional[AgentConfig] = None):
        """Save agent configuration to config.yaml"""
        if config is None:
            config = self.config
        
        config.updated_at = datetime.now().isoformat()
        config_file = self.base_dir / "config.yaml"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config.to_dict(), f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load conversation history from history.json"""
        history_file = self.base_dir / "history.json"
        
        if history_file.exists():
            try:
                return load_json_file(history_file)
            except Exception as e:
                self.logger.error(f"Error loading history: {e}")
                return []
        return []
    
    def _save_history(self):
        """Save conversation history with backup"""
        history_file = self.base_dir / "history.json"
        
        if history_file.exists():
            create_backup(history_file, self.base_dir / "backups")
        
        try:
            save_json_file(self.messages, history_file)
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        
        # Truncate if history is too long
        if len(self.messages) > self.config.max_history_size:
            removed = self.messages[:-self.config.max_history_size]
            self.messages = self.messages[-self.config.max_history_size:]
            self.logger.info(f"Truncated history: removed {len(removed)} old messages")
        
        self._save_history()
    
    def _build_api_payload(self, new_message: str, override_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build API request payload"""
        # Process file inclusions
        processed_message = process_file_inclusions(new_message, self.base_dir, self.logger)
        
        messages = []
        
        # Add conversation history
        for msg in self.messages:
            if msg["role"] in ["user", "assistant"]:
                content_blocks = []
                if isinstance(msg["content"], str):
                    content_blocks.append({"type": "text", "text": msg["content"]})
                elif isinstance(msg["content"], list):
                    content_blocks = msg["content"]
                
                messages.append({
                    "role": msg["role"],
                    "content": content_blocks
                })
        
        # Add new user message
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": processed_message}]
        })
        
        # Build payload
        config_dict = self.config.to_dict()
        if override_config:
            config_dict.update(override_config)
        
        model_config = get_model_config(self.config.model)
        max_tokens = min(config_dict["max_tokens"], model_config["max_output_tokens"])
        
        payload = {
            "model": config_dict["model"],
            "max_tokens": max_tokens,
            "temperature": config_dict["temperature"],
            "system": config_dict["system_prompt"],
            "stream": config_dict["stream"],
            "messages": messages
        }
        
        return payload
    
    def _make_api_request(self, payload: Dict[str, Any]) -> requests.Response:
        """Make API request with retries and error handling"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        model_config = get_model_config(self.config.model)
        timeout = model_config["timeout"]
        
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Making API request (attempt {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    stream=payload.get("stream", True),
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    self.logger.info("API request successful")
                    return response
                elif response.status_code == 401:
                    raise ValueError("Invalid API key")
                elif response.status_code == 403:
                    raise ValueError("API access forbidden")
                elif response.status_code == 429:
                    delay = base_delay * (2 ** attempt)
                    self.logger.warning(f"Rate limited, retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                elif response.status_code >= 500:
                    delay = base_delay * (2 ** attempt)
                    self.logger.warning(f"Server error {response.status_code}, retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    self.logger.error(f"API request failed with status {response.status_code}")
                    response.raise_for_status()
                    
            except Timeout as e:
                self.logger.warning(f"Request timed out after {timeout}s (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    raise Exception(f"Request timed out after {timeout}s") from e
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
            except RequestException as e:
                self.logger.warning(f"Request exception: {e}")
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
        
        raise Exception(f"Failed to complete API request after {max_retries} attempts")
    
    def _parse_streaming_response(self, response: requests.Response) -> Generator[str, None, None]:
        """Parse streaming response from Anthropic API"""
        accumulated_text = ""
        
        try:
            for line in response.iter_lines():
                if not line:
                    continue
                line = line.decode('utf-8').strip()
                
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    
                    try:
                        event = json.loads(data_str)
                        
                        if event.get("type") == "content_block_delta":
                            delta_text = event.get("delta", {}).get("text", "")
                            if delta_text:
                                accumulated_text += delta_text
                                yield delta_text
                        elif event.get("type") == "message_stop":
                            break
                            
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON in stream: {data_str} - {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error parsing streaming response: {e}")
        
        # Save complete assistant message
        if accumulated_text.strip():
            self.add_message("assistant", accumulated_text)
    
    def _parse_non_streaming_response(self, response: requests.Response) -> str:
        """Parse non-streaming response from Anthropic API"""
        try:
            data = response.json()
            
            content_blocks = data.get("content", [])
            if content_blocks and len(content_blocks) > 0:
                text_content = content_blocks[0].get("text", "")
                if text_content:
                    self.add_message("assistant", text_content)
                    return text_content
            
            return "No response content received"
            
        except Exception as e:
            self.logger.error(f"Error parsing non-streaming response: {e}")
            return f"Error parsing response: {e}"
    
    def call_api(self, new_message: str, override_config: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """Call Claude API with new message"""
        try:
            # Add user message to history
            self.add_message("user", new_message)
            
            # Build payload
            payload = self._build_api_payload(new_message, override_config)
            self.logger.info(f"Making API call to {self.api_url}")
            
            # Make request
            model_config = get_model_config(self.config.model)
            timeout = model_config["timeout"]
            
            print(f"{Fore.YELLOW}🤖 Using {model_config['name']} (timeout: {timeout//60}m {timeout%60}s)...{Style.RESET_ALL}")
            
            response = self._make_api_request(payload)
            
            # Parse response
            if payload.get("stream", True):
                yield from self._parse_streaming_response(response)
            else:
                result = self._parse_non_streaming_response(response)
                yield result
                
        except Exception as e:
            error_msg = f"API call failed: {e}"
            self.logger.error(error_msg)
            yield json.dumps({"error": error_msg})
    
    def clear_history(self):
        """Clear conversation history"""
        create_backup(self.base_dir / "history.json", self.base_dir / "backups")
        self.messages.clear()
        self._save_history()
        self.logger.info("Conversation history cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        if not self.messages:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "total_characters": 0,
                "average_message_length": 0,
                "first_message": None,
                "last_message": None,
                "conversation_duration": None
            }
        
        user_msgs = [m for m in self.messages if m["role"] == "user"]
        assistant_msgs = [m for m in self.messages if m["role"] == "assistant"]
        
        total_chars = sum(len(m["content"]) for m in self.messages)
        avg_length = total_chars // len(self.messages) if self.messages else 0
        
        first_time = datetime.fromisoformat(self.messages[0]["timestamp"])
        last_time = datetime.fromisoformat(self.messages[-1]["timestamp"])
        duration = last_time - first_time
        
        return {
            "total_messages": len(self.messages),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "total_characters": total_chars,
            "average_message_length": avg_length,
            "first_message": first_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_message": last_time.strftime("%Y-%m-%d %H:%M:%S"),
            "conversation_duration": str(duration).split('.')[0] if duration.total_seconds() > 0 else "0:00:00"
        }
    
    def export_conversation(self, format_type: str) -> str:
        """Export conversation in specified format"""
        statistics = self.get_statistics()
        return self.exporter.export(self.messages, format_type, statistics)
    
    def search_history(self, term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversation history for term"""
        results = []
        term_lower = term.lower()
        
        for i, msg in enumerate(self.messages):
            if term_lower in msg["content"].lower():
                results.append({
                    "index": i,
                    "message": msg,
                    "preview": msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                })
                
            if len(results) >= limit:
                break
        
        return results
    
    def list_files(self) -> List[str]:
        """List available files for inclusion"""
        return list_available_files(self.base_dir)
    
    def update_config(self, override_config: Dict[str, Any]):
        """Update configuration with validation"""
        for key, value in override_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                self.logger.warning(f"Unknown configuration key: {key}")
        
        if not self.config.validate():
            raise ValueError("Invalid configuration parameters")
        
        self.config.updated_at = datetime.now().isoformat()
        self._save_config()