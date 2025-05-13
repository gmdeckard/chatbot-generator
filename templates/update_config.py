#!/usr/bin/env python3
"""
Utility script for updating the LLM configuration of a generated chatbot.
This allows users to modify the system prompt and LLM parameters after deployment.
"""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load the current configuration from file.
    
    Args:
        config_path: Path to the config file
        
    Returns:
        Dictionary containing the configuration
    """
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: Config file contains invalid JSON")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        sys.exit(1)


def save_config(config_path: Path, config: Dict[str, Any]) -> None:
    """
    Save the configuration to file.
    
    Args:
        config_path: Path to the config file
        config: Configuration dictionary to save
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_path}")
    except Exception as e:
        print(f"Error saving config: {str(e)}")
        sys.exit(1)


def update_system_prompt(config: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """
    Update the system prompt in the configuration.
    
    Args:
        config: Current configuration
        prompt: New system prompt
        
    Returns:
        Updated configuration
    """
    config['system_prompt'] = prompt
    return config


def update_parameters(config: Dict[str, Any], param_updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update parameters in the configuration.
    
    Args:
        config: Current configuration
        param_updates: Dictionary of parameter updates
        
    Returns:
        Updated configuration
    """
    for key, value in param_updates.items():
        config['parameters'][key] = value
    return config


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Update LLM configuration for a generated chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update system prompt from a file
  python update_config.py --prompt-file new_prompt.txt
  
  # Update system prompt directly
  python update_config.py --prompt "You are a helpful assistant specialized in biology."
  
  # Update temperature parameter
  python update_config.py --param temperature=0.8
  
  # Update multiple parameters
  python update_config.py --param temperature=0.7 --param max_tokens=2048
"""
    )
    
    parser.add_argument(
        "--config-path",
        type=str,
        default="src/config/llm_config.json",
        help="Path to the LLM config file (default: src/config/llm_config.json)"
    )
    
    prompt_group = parser.add_mutually_exclusive_group()
    prompt_group.add_argument(
        "--prompt",
        type=str,
        help="New system prompt text"
    )
    prompt_group.add_argument(
        "--prompt-file",
        type=str,
        help="File containing new system prompt"
    )
    
    parser.add_argument(
        "--param",
        action="append",
        metavar="KEY=VALUE",
        help="Update a parameter (format: key=value). Can be used multiple times."
    )
    
    args = parser.parse_args()
    
    # Convert config path to absolute path if needed
    config_path = Path(args.config_path)
    if not config_path.is_absolute():
        config_path = Path.cwd() / args.config_path
    
    # Load current config
    config = load_config(config_path)
    
    # Update system prompt if requested
    if args.prompt:
        config = update_system_prompt(config, args.prompt)
        print("System prompt updated")
    elif args.prompt_file:
        prompt_file = Path(args.prompt_file)
        if not prompt_file.exists():
            print(f"Error: Prompt file not found at {prompt_file}")
            sys.exit(1)
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                new_prompt = f.read().strip()
            config = update_system_prompt(config, new_prompt)
            print("System prompt updated from file")
        except Exception as e:
            print(f"Error reading prompt file: {str(e)}")
            sys.exit(1)
    
    # Update parameters if requested
    if args.param:
        param_updates = {}
        for param in args.param:
            if '=' not in param:
                print(f"Error: Parameter '{param}' is not in format 'key=value'")
                sys.exit(1)
            
            key, value = param.split('=', 1)
            
            # Convert value to appropriate type
            try:
                # Try to convert to number if possible
                if value.lower() == 'true':
                    typed_value = True
                elif value.lower() == 'false':
                    typed_value = False
                elif '.' in value:
                    typed_value = float(value)
                else:
                    typed_value = int(value)
            except ValueError:
                # Keep as string if conversion fails
                typed_value = value
            
            param_updates[key] = typed_value
        
        config = update_parameters(config, param_updates)
        print(f"Parameters updated: {', '.join(param_updates.keys())}")
    
    # Save updated config
    save_config(config_path, config)
    
    print("\nTo apply these changes, restart your chatbot with:")
    print("docker-compose down")
    print("docker-compose up -d")


if __name__ == "__main__":
    main()
