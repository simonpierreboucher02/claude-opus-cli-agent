#!/usr/bin/env python3
"""
Main CLI entry point for Claude Opus 4/4.1 Chat Agent

This is the main command-line interface for the refactored Claude chat agent,
supporting both Claude Opus 4 and 4.1 models with comprehensive features.

Usage Examples:
    python main.py --agent-id my-agent --model claude-opus-4-20250514
    python main.py --agent-id my-agent --model claude-opus-4-1-20250805 
    python main.py --list
    python main.py --agent-id my-agent --export html
"""

import sys
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""

from agent import ClaudeChatAgent
from config import AgentConfig, get_supported_models, get_model_config


def list_agents() -> List[Dict[str, Any]]:
    """List all available agents"""
    agents_dir = Path("agents")
    agents = []
    
    if not agents_dir.exists():
        return agents
    
    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir():
            config_file = agent_dir / "config.yaml"
            history_file = agent_dir / "history.json"
            
            agent_info = {
                "id": agent_dir.name,
                "path": str(agent_dir),
                "exists": True
            }
            
            if config_file.exists():
                try:
                    with open(config_file) as f:
                        config = yaml.safe_load(f)
                        agent_info["model"] = config.get("model", "claude-opus-4-20250514")
                        agent_info["created_at"] = config.get("created_at")
                        agent_info["updated_at"] = config.get("updated_at")
                except:
                    pass
            
            if history_file.exists():
                try:
                    import json
                    with open(history_file) as f:
                        history = json.load(f)
                        agent_info["message_count"] = len(history)
                        agent_info["history_size"] = history_file.stat().st_size
                except:
                    agent_info["message_count"] = 0
                    agent_info["history_size"] = 0
            else:
                agent_info["message_count"] = 0
                agent_info["history_size"] = 0
            
            agents.append(agent_info)
    
    return sorted(agents, key=lambda x: x.get("updated_at", ""))


def show_agent_info(agent_id: str):
    """Show detailed agent information"""
    agent_dir = Path(f"agents/{agent_id}")
    
    if not agent_dir.exists():
        print(f"{Fore.RED}Agent '{agent_id}' not found{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"Agent Information: {Fore.YELLOW}{agent_id}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    # Configuration
    config_file = agent_dir / "config.yaml"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            model = config.get('model', 'claude-opus-4-20250514')
            model_config = get_model_config(model)
            model_display = model_config.get('name', model)
            
            print(f"\n{Fore.GREEN}Configuration:")
            print(f"{Fore.WHITE}  Model: {model} ({model_display})")
            print(f"  Temperature: {config.get('temperature', 1.0)}")
            print(f"  Max Tokens: {config.get('max_tokens', 32000)}")
            print(f"  Streaming: {config.get('stream', True)}")
            print(f"  Created: {config.get('created_at', 'Unknown')}")
            print(f"  Updated: {config.get('updated_at', 'Unknown')}")
            
        except Exception as e:
            print(f"{Fore.RED}Error loading config: {e}")
    
    # History
    history_file = agent_dir / "history.json"
    if history_file.exists():
        try:
            import json
            with open(history_file) as f:
                history = json.load(f)
            
            user_msgs = len([m for m in history if m.get("role") == "user"])
            assistant_msgs = len([m for m in history if m.get("role") == "assistant"])
            total_chars = sum(len(m.get("content", "")) for m in history)
            
            print(f"\n{Fore.GREEN}Conversation History:")
            print(f"{Fore.WHITE}  Total Messages: {len(history)}")
            print(f"  User Messages: {user_msgs}")
            print(f"  Assistant Messages: {assistant_msgs}")
            print(f"  Total Characters: {total_chars:,}")
            print(f"  File Size: {history_file.stat().st_size:,} bytes")
            
            if history:
                first_msg = datetime.fromisoformat(history[0]["timestamp"])
                last_msg = datetime.fromisoformat(history[-1]["timestamp"])
                print(f"  First Message: {first_msg.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Last Message: {last_msg.strftime('%Y-%m-%d %H:%M:%S')}")
                
        except Exception as e:
            print(f"{Fore.RED}Error loading history: {e}")
    else:
        print(f"\n{Fore.YELLOW}No conversation history found{Style.RESET_ALL}")
    
    # Directory structure
    print(f"\n{Fore.GREEN}Directory Structure:")
    for item in sorted(agent_dir.rglob("*")):
        if item.is_file():
            size = item.stat().st_size
            size_str = f"{size:,}" if size < 1024 else f"{size/1024:.1f}K"
            rel_path = item.relative_to(agent_dir)
            print(f"{Fore.WHITE}  {rel_path} ({size_str} bytes)")


def create_agent_config_interactive() -> AgentConfig:
    """Create agent configuration interactively"""
    print(f"\n{Fore.CYAN}Agent Configuration Setup{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Press Enter to use default values{Style.RESET_ALL}\n")
    
    # Model selection
    supported_models = get_supported_models()
    print(f"{Fore.GREEN}Available Models:")
    for i, (model_id, model_info) in enumerate(supported_models.items(), 1):
        print(f"{Fore.WHITE}  {i}. {model_info['name']} ({model_id})")
    
    model_choice = input(f"\nSelect model (1-{len(supported_models)}) [1]: ").strip()
    if model_choice and model_choice.isdigit():
        model_index = int(model_choice) - 1
        if 0 <= model_index < len(supported_models):
            selected_model = list(supported_models.keys())[model_index]
        else:
            selected_model = "claude-opus-4-20250514"
    else:
        selected_model = "claude-opus-4-20250514"
    
    config = AgentConfig(model=selected_model)
    
    # Temperature
    temp_input = input(f"Temperature (0.0-2.0) [{config.temperature}]: ").strip()
    if temp_input:
        try:
            temp = float(temp_input)
            if 0.0 <= temp <= 2.0:
                config.temperature = temp
            else:
                print(f"{Fore.RED}Invalid temperature, using default{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid temperature, using default{Style.RESET_ALL}")
    
    # System prompt
    system_prompt = input(f"System prompt [{config.system_prompt}]: ").strip()
    if system_prompt:
        config.system_prompt = system_prompt
    
    # Max tokens
    tokens_input = input(f"Max tokens [{config.max_tokens}]: ").strip()
    if tokens_input:
        try:
            tokens = int(tokens_input)
            if tokens > 0:
                config.max_tokens = tokens
        except ValueError:
            print(f"{Fore.RED}Invalid token count, using default{Style.RESET_ALL}")
    
    # Streaming
    stream_input = input(f"Enable streaming (y/n) [{'y' if config.stream else 'n'}]: ").strip().lower()
    if stream_input in ['n', 'no', 'false']:
        config.stream = False
    elif stream_input in ['y', 'yes', 'true']:
        config.stream = True
    
    return config


def interactive_chat(agent: ClaudeChatAgent):
    """Start interactive chat session"""
    model_config = get_model_config(agent.config.model)
    model_display = model_config['name']
    
    print(f"\n{Fore.GREEN}Starting interactive chat with {model_display}")
    print(f"Agent: {Fore.YELLOW}{agent.agent_id}")
    print(f"{Fore.GREEN}Type '/help' for commands, '/quit' to exit{Style.RESET_ALL}\n")
    
    while True:
        try:
            user_input = input(f"{Fore.CYAN}You: {Style.RESET_ALL}").strip()
            
            if not user_input:
                continue
            
            if user_input.startswith('/'):
                command_parts = user_input[1:].split()
                command = command_parts[0].lower()
                
                if command == 'help':
                    print(f"\n{Fore.YELLOW}Available Commands:")
                    print(f"{Fore.WHITE}/help - Show this help message")
                    print(f"/history [n] - Show last n messages (default 5)")
                    print(f"/search <term> - Search conversation history")
                    print(f"/stats - Show conversation statistics")
                    print(f"/config - Show current configuration")
                    print(f"/export <json|txt|md|html> - Export conversation")
                    print(f"/clear - Clear conversation history")
                    print(f"/files - List available files for inclusion")
                    print(f"/info - Show agent information")
                    print(f"/quit - Exit chat{Style.RESET_ALL}\n")
                    print(f"{Fore.CYAN}File Inclusion: Use {{filename}} to include file content")
                    print(f"Supported: Programming files (.py, .js, etc.), configs, docs{Style.RESET_ALL}\n")
                    continue
                
                elif command == 'history':
                    limit = 5
                    if len(command_parts) > 1:
                        try:
                            limit = int(command_parts[1])
                        except ValueError:
                            print(f"{Fore.RED}Invalid number{Style.RESET_ALL}")
                            continue
                    
                    recent_messages = agent.messages[-limit:]
                    if not recent_messages:
                        print(f"{Fore.YELLOW}No messages in history{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.YELLOW}Last {len(recent_messages)} messages:")
                        for msg in recent_messages:
                            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
                            role_color = Fore.CYAN if msg["role"] == "user" else Fore.GREEN
                            content_preview = msg['content'][:100] + '...' if len(msg['content']) > 100 else msg['content']
                            print(f"{Fore.WHITE}[{timestamp}] {role_color}{msg['role']}: {content_preview}")
                    print()
                
                elif command == 'search':
                    if len(command_parts) < 2:
                        print(f"{Fore.RED}Usage: /search <term>{Style.RESET_ALL}")
                        continue
                    
                    search_term = ' '.join(command_parts[1:])
                    results = agent.search_history(search_term)
                    
                    if not results:
                        print(f"{Fore.YELLOW}No matches found for '{search_term}'{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.YELLOW}Found {len(results)} matches for '{search_term}':")
                        for result in results:
                            msg = result["message"]
                            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
                            role_color = Fore.CYAN if msg["role"] == "user" else Fore.GREEN
                            print(f"{Fore.WHITE}[{timestamp}] {role_color}{msg['role']}: {result['preview']}")
                    print()
                
                elif command == 'stats':
                    stats = agent.get_statistics()
                    print(f"\n{Fore.YELLOW}Conversation Statistics:")
                    print(f"{Fore.WHITE}Model: {agent.config.model} ({model_display})")
                    print(f"Total Messages: {stats['total_messages']}")
                    print(f"User Messages: {stats['user_messages']}")
                    print(f"Assistant Messages: {stats['assistant_messages']}")
                    print(f"Total Characters: {stats['total_characters']:,}")
                    print(f"Average Message Length: {stats['average_message_length']:,}")
                    if stats['first_message']:
                        print(f"First Message: {stats['first_message']}")
                        print(f"Last Message: {stats['last_message']}")
                        print(f"Duration: {stats['conversation_duration']}")
                    print()
                
                elif command == 'config':
                    print(f"\n{Fore.YELLOW}Current Configuration:")
                    config_dict = agent.config.to_dict()
                    for key, value in config_dict.items():
                        if key not in ['created_at', 'updated_at']:
                            if key == 'model':
                                model_name = get_model_config(str(value)).get('name', value)
                                print(f"{Fore.WHITE}{key}: {value} ({model_name})")
                            else:
                                print(f"{Fore.WHITE}{key}: {value}")
                    print()
                
                elif command == 'export':
                    if len(command_parts) < 2:
                        print(f"{Fore.RED}Usage: /export <json|txt|md|html>{Style.RESET_ALL}")
                        continue
                    
                    format_type = command_parts[1].lower()
                    if format_type not in ['json', 'txt', 'md', 'html']:
                        print(f"{Fore.RED}Invalid format. Use: json, txt, md, or html{Style.RESET_ALL}")
                        continue
                    
                    try:
                        filepath = agent.export_conversation(format_type)
                        print(f"{Fore.GREEN}Exported to: {filepath}{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}Export failed: {e}{Style.RESET_ALL}")
                
                elif command == 'clear':
                    confirm = input(f"{Fore.YELLOW}Clear conversation history? (y/N): {Style.RESET_ALL}").strip().lower()
                    if confirm in ['y', 'yes']:
                        agent.clear_history()
                        print(f"{Fore.GREEN}Conversation history cleared{Style.RESET_ALL}")
                
                elif command == 'files':
                    files = agent.list_files()
                    if not files:
                        print(f"{Fore.YELLOW}No supported files found for inclusion{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.YELLOW}Available Files for Inclusion:")
                        for file_info in files[:20]:
                            print(f"{Fore.WHITE}{file_info}")
                        if len(files) > 20:
                            print(f"{Fore.YELLOW}... and {len(files) - 20} more files")
                        print(f"{Fore.CYAN}Use {{filename}} in your message to include file content{Style.RESET_ALL}\n")
                
                elif command == 'info':
                    show_agent_info(agent.agent_id)
                
                elif command in ['quit', 'exit', 'q']:
                    print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                    break
                
                else:
                    print(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Type '/help' for available commands{Style.RESET_ALL}")
                
                continue
            
            # Regular message - send to API
            print(f"\n{Fore.GREEN}Assistant: {Style.RESET_ALL}", end="", flush=True)
            
            for chunk in agent.call_api(user_input):
                if isinstance(chunk, str):
                    print(chunk, end="", flush=True)
            
            print("\n")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Use '/quit' to exit properly{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Claude Opus 4/4.1 Chat Agent - Advanced AI Chat Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --agent-id my-agent --model claude-opus-4-20250514
  %(prog)s --agent-id my-agent --model claude-opus-4-1-20250805
  %(prog)s --list
  %(prog)s --agent-id my-agent --export html
  %(prog)s --agent-id my-agent --config
        """
    )
    
    parser.add_argument("--agent-id", help="Agent ID for chat session")
    parser.add_argument("--model", choices=list(get_supported_models().keys()), 
                       help="Model to use (default: claude-opus-4-20250514)")
    parser.add_argument("--list", action="store_true", help="List all available agents")
    parser.add_argument("--info", metavar="ID", help="Show detailed info for an agent")
    parser.add_argument("--config", action="store_true", help="Configure agent interactively")
    parser.add_argument("--temperature", type=float, help="Override temperature (0.0-2.0)")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming")
    parser.add_argument("--export", choices=["json", "txt", "md", "html"], 
                       help="Export conversation in specified format")
    
    args = parser.parse_args()
    
    # Handle list command
    if args.list:
        agents = list_agents()
        if not agents:
            print(f"{Fore.YELLOW}No agents found{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Available Agents:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'ID':<25} {'Model':<35} {'Messages':<10} {'Last Updated':<20}")
        print("-" * 90)
        
        for agent in agents:
            updated = agent.get("updated_at", "Unknown")
            if updated != "Unknown":
                try:
                    updated = datetime.fromisoformat(updated).strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            model = agent.get('model', 'claude-opus-4-20250514')
            model_display = get_model_config(model).get('name', model)
            print(f"{agent['id']:<25} {model_display:<35} {agent.get('message_count', 0):<10} {updated:<20}")
        
        return
    
    # Handle info command
    if args.info:
        show_agent_info(args.info)
        return
    
    # Require agent ID for other operations
    if not args.agent_id:
        parser.print_help()
        print(f"\n{Fore.RED}Error: --agent-id is required{Style.RESET_ALL}")
        return
    
    try:
        # Create agent
        model = args.model or "claude-opus-4-20250514"
        agent = ClaudeChatAgent(args.agent_id, model)
        
        # Handle config command
        if args.config:
            new_config = create_agent_config_interactive()
            agent.config = new_config
            agent._save_config()
            print(f"{Fore.GREEN}Configuration saved{Style.RESET_ALL}")
            return
        
        # Handle export command
        if args.export:
            filepath = agent.export_conversation(args.export)
            print(f"{Fore.GREEN}Exported to: {filepath}{Style.RESET_ALL}")
            return
        
        # Apply command-line overrides
        overrides = {}
        if args.temperature is not None:
            overrides["temperature"] = args.temperature
        if args.no_stream:
            overrides["stream"] = False
        
        if overrides:
            agent.update_config(overrides)
        
        # Start interactive chat
        interactive_chat(agent)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()