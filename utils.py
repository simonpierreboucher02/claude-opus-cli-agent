#!/usr/bin/env python3
"""
Utilities for Claude Opus 4/4.1 Chat Agent

This module provides utilities for directory management, logging setup,
backup management, and file operations.
"""

import os
import json
import shutil
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import SUPPORTED_EXTENSIONS


def setup_directories(base_dir: Path) -> None:
    """Create necessary directory structure for agent"""
    directories = [
        base_dir,
        base_dir / "backups",
        base_dir / "logs", 
        base_dir / "exports",
        base_dir / "uploads"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def setup_logging(agent_id: str, base_dir: Path) -> logging.Logger:
    """Setup logging for agent with file and console handlers"""
    log_file = base_dir / "logs" / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    
    logger = logging.getLogger(f"ClaudeAgent_{agent_id}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler (warnings and above only)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.WARNING)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def create_backup(history_file: Path, backup_dir: Path, max_backups: int = 10) -> None:
    """Create incremental backup of history file"""
    if not history_file.exists():
        return
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"history_{timestamp}.json"
    
    try:
        shutil.copy2(history_file, backup_file)
        
        # Keep only the most recent backups
        backups = sorted(backup_dir.glob("history_*.json"))
        while len(backups) > max_backups:
            oldest = backups.pop(0)
            oldest.unlink()
            
    except Exception as e:
        # Log error but don't fail
        print(f"Warning: Could not create backup: {e}")


def get_api_key(base_dir: Path, model_name: str) -> str:
    """Get API key from environment or secrets file, prompt if needed"""
    # Try environment variable first
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        return api_key
    
    # Try secrets file
    secrets_file = base_dir / "secrets.json"
    if secrets_file.exists():
        try:
            with open(secrets_file, 'r') as f:
                secrets = json.load(f)
                api_key = secrets.get('keys', {}).get('default')
                if api_key:
                    return api_key
        except Exception as e:
            print(f"Warning: Could not read secrets file: {e}")
    
    # Prompt user for API key
    print(f"API key not found for {model_name}.")
    print("You can set ANTHROPIC_API_KEY environment variable or enter it now.")
    
    api_key = input(f"Enter API key for {model_name}: ").strip()
    if not api_key:
        raise ValueError("API key is required")
    
    # Save to secrets file
    secrets = {
        "provider": "anthropic",
        "keys": {
            "default": api_key
        }
    }
    
    try:
        with open(secrets_file, 'w') as f:
            json.dump(secrets, f, indent=2)
        
        # Add to .gitignore
        gitignore_file = Path('.gitignore')
        gitignore_content = ""
        if gitignore_file.exists():
            gitignore_content = gitignore_file.read_text()
        
        if 'secrets.json' not in gitignore_content:
            with open(gitignore_file, 'a') as f:
                f.write('\n# API Keys\n**/secrets.json\nsecrets.json\n')
        
        masked_key = f"{api_key[:4]}...{api_key[-2:]}" if len(api_key) > 6 else "***"
        print(f"API key saved ({masked_key})")
        
    except Exception as e:
        print(f"Warning: Could not save API key to file: {e}")
    
    return api_key


def is_supported_file(file_path: Path) -> bool:
    """Check if file extension is supported for inclusion"""
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS


def process_file_inclusions(content: str, base_dir: Path, logger: logging.Logger) -> str:
    """Replace {filename} patterns with file content"""
    def replace_file(match):
        filename = match.group(1).strip()
        
        search_paths = [
            Path('.'),
            Path('src'),
            Path('lib'),
            Path('scripts'),
            Path('data'),
            Path('documents'),
            Path('files'),
            Path('config'),
            Path('configs'),
            base_dir / 'uploads'
        ]
        
        for search_path in search_paths:
            file_path = search_path / filename
            if file_path.exists() and file_path.is_file():
                if not is_supported_file(file_path):
                    logger.warning(f"Unsupported file type: {filename}")
                    return f"[WARNING: Unsupported file type {filename}]"
                
                try:
                    # Check file size (max 2MB)
                    max_size = 2 * 1024 * 1024
                    if file_path.stat().st_size > max_size:
                        logger.error(f"File {filename} too large (>2MB)")
                        return f"[ERROR: File {filename} too large (max 2MB)]"
                    
                    # Try UTF-8 first, fallback to latin-1
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                    except UnicodeDecodeError:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            file_content = f.read()
                    
                    # Add file info header
                    file_info = get_file_header(filename, file_path.suffix)
                    full_content = file_info + file_content
                    
                    logger.info(f"Included file: {filename} ({len(file_content)} chars, {file_path.suffix})")
                    return full_content
                    
                except Exception as e:
                    logger.error(f"Error reading file {filename}: {e}")
                    return f"[ERROR: Could not read {filename}: {e}]"
        
        logger.warning(f"File not found: {filename}")
        return f"[ERROR: File {filename} not found]"
    
    return re.sub(r'\{([^}]+)\}', replace_file, content)


def get_file_header(filename: str, suffix: str) -> str:
    """Get appropriate file header comment based on file type"""
    suffix_lower = suffix.lower()
    
    if suffix_lower in ['.py', '.r']:
        return f"# File: {filename} ({suffix})\n"
    elif suffix_lower in ['.html', '.xml']:
        return f"<!-- File: {filename} ({suffix}) -->\n"
    elif suffix_lower in ['.css', '.scss', '.sass']:
        return f"/* File: {filename} ({suffix}) */\n"
    elif suffix_lower in ['.sql']:
        return f"-- File: {filename} ({suffix})\n"
    else:
        return f"// File: {filename} ({suffix})\n"


def list_available_files(base_dir: Path) -> List[str]:
    """List all available files for inclusion"""
    files = []
    search_paths = [
        Path('.'),
        Path('src'),
        Path('lib'),
        Path('scripts'),
        Path('data'),
        Path('documents'),
        Path('files'),
        Path('config'),
        Path('configs'),
        base_dir / 'uploads'
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            for file_path in search_path.rglob("*"):
                if (file_path.is_file() and 
                    not file_path.name.startswith('.') and 
                    is_supported_file(file_path)):
                    
                    size = file_path.stat().st_size
                    size_str = f"{size:,} bytes" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
                    files.append(f"{file_path} ({size_str}) [{file_path.suffix}]")
    
    return sorted(files)


def save_json_file(data: Any, file_path: Path) -> None:
    """Save data to JSON file with proper encoding"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json_file(file_path: Path) -> Any:
    """Load data from JSON file with proper encoding"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"