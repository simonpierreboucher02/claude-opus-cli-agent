#!/usr/bin/env python3
"""
Configuration management for Claude Opus 4/4.1 Chat Agent

This module provides configuration management using dataclasses for both
Claude Opus 4 and 4.1 models with comprehensive validation and defaults.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class AgentConfig:
    """Configuration parameters for Claude Opus 4/4.1 chat agent"""
    model: str = "claude-opus-4-20250514"  # Default to Opus 4
    temperature: float = 1.0
    max_tokens: Optional[int] = 32000
    max_history_size: int = 1000
    stream: bool = True
    system_prompt: Optional[str] = "You are Claude, an AI assistant."
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        """Set timestamps after initialization"""
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        self.updated_at = now

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Create configuration from dictionary"""
        return cls(**data)

    def validate(self) -> bool:
        """Validate configuration parameters"""
        if not (0.0 <= self.temperature <= 2.0):
            return False
        if not (0.0 <= self.top_p <= 1.0):
            return False
        if not (0.0 <= self.frequency_penalty <= 2.0):
            return False
        if not (0.0 <= self.presence_penalty <= 2.0):
            return False
        if self.max_tokens and self.max_tokens <= 0:
            return False
        if self.max_history_size <= 0:
            return False
        return True


# Supported models configuration
SUPPORTED_MODELS = {
    "claude-opus-4-20250514": {
        "name": "Claude Opus 4",
        "description": "Claude Opus 4 model from Anthropic",
        "timeout": 300,
        "max_output_tokens": 32000
    },
    "claude-opus-4-1-20250805": {
        "name": "Claude Opus 4.1", 
        "description": "Claude Opus 4.1 model from Anthropic",
        "timeout": 300,
        "max_output_tokens": 32000
    }
}

# Supported file extensions for file inclusion
SUPPORTED_EXTENSIONS = {
    # Programming languages
    '.py', '.r', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cc', '.cxx',
    '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
    '.clj', '.hs', '.ml', '.fs', '.vb', '.pl', '.pm', '.sh', '.bash', '.zsh', '.fish',
    '.ps1', '.bat', '.cmd', '.sql', '.html', '.htm', '.css', '.scss', '.sass', '.less',
    '.xml', '.xsl', '.xslt', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.properties', '.env', '.dockerfile', '.docker', '.makefile', '.cmake', '.gradle',
    '.sbt', '.pom', '.lock', '.mod', '.sum',

    # Data and markup
    '.md', '.markdown', '.rst', '.tex', '.latex', '.csv', '.tsv', '.jsonl', '.ndjson',
    '.xml', '.svg', '.rss', '.atom', '.plist',

    # Configuration and infrastructure
    '.tf', '.tfvars', '.hcl', '.nomad', '.consul', '.vault', '.k8s', '.kubectl',
    '.helm', '.kustomize', '.ansible', '.inventory', '.playbook',

    # Documentation and text
    '.txt', '.log', '.out', '.err', '.trace', '.debug', '.info', '.warn', '.error',
    '.readme', '.license', '.changelog', '.authors', '.contributors', '.todo',

    # Notebooks and scripts
    '.ipynb', '.rmd', '.qmd', '.jl', '.m', '.octave', '.R', '.Rmd',

    # Web and API
    '.graphql', '.gql', '.rest', '.http', '.api', '.postman', '.insomnia',

    # Other useful formats
    '.editorconfig', '.gitignore', '.gitattributes', '.dockerignore', '.eslintrc',
    '.prettierrc', '.babelrc', '.webpack', '.rollup', '.vite', '.parcel'
}


def get_model_config(model: str) -> Dict[str, Any]:
    """Get configuration for a specific model"""
    return SUPPORTED_MODELS.get(model, SUPPORTED_MODELS["claude-opus-4-20250514"])


def is_supported_model(model: str) -> bool:
    """Check if model is supported"""
    return model in SUPPORTED_MODELS


def get_supported_models() -> Dict[str, Dict[str, Any]]:
    """Get all supported models"""
    return SUPPORTED_MODELS.copy()