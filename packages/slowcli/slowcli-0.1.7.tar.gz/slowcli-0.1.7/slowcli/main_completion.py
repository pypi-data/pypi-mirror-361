#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""
Fast completion script for slowcli that avoids importing the main package
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

def is_completion_request():
    """Check if this is an argcomplete completion request"""
    return os.environ.get('_ARGCOMPLETE') == '1'

def load_snapshot(snapshot_path: str) -> Dict[str, Any]:
    """Load the CLI snapshot from JSON file"""
    try:
        with open(snapshot_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading snapshot: {e}", file=sys.stderr)
        return {}

def find_completions(snapshot: Dict[str, Any], words: List[str], prefix: str, option_being_completed: Optional[str] = None) -> List[str]:
    """Find completions based on the snapshot and current command state"""
    completions = []

    # If we're completing an option value
    if option_being_completed:
        # Find the option in the snapshot
        option = find_option_in_snapshot(snapshot, option_being_completed, words)
        if option and option.get('choices'):
            # Return choices that match the prefix
            for choice in option['choices']:
                if choice.startswith(prefix):
                    completions.append(choice)
        return completions

    # If we're completing a command or option
    current_level = snapshot
    command_path = []

    # Navigate to the current command level
    for i, word in enumerate(words[1:], 1):  # Skip the command name
        if word.startswith('-'):
            # This is an option, not a command
            break

        command_path.append(word)
        # Find the subcommand
        if 'subcommands' in current_level:
            for subcmd in current_level['subcommands']:
                if subcmd['name'] == word:
                    current_level = subcmd
                    break
            else:
                # Command not found, stop here
                break

    # Get completions for the current level
    if 'subcommands' in current_level:
        for subcmd in current_level['subcommands']:
            if subcmd['name'].startswith(prefix):
                completions.append(subcmd['name'])

    if 'options' in current_level:
        for option in current_level['options']:
            # Handle different option formats
            if 'name' in option:
                # Format: {"name": "-h", "aliases": ["--help"]}
                if option['name'].startswith(prefix):
                    completions.append(option['name'])
                if 'aliases' in option:
                    for alias in option['aliases']:
                        if alias.startswith(prefix):
                            completions.append(alias)
            elif 'short' in option or 'long' in option:
                # Format: {"short": "h", "long": "help"}
                if option.get('short') and f"-{option['short']}".startswith(prefix):
                    completions.append(f"-{option['short']}")
                if option.get('long') and f"--{option['long']}".startswith(prefix):
                    completions.append(f"--{option['long']}")

    return completions

def find_option_in_snapshot(snapshot: Dict[str, Any], option_name: str, words: List[str]) -> Optional[Dict[str, Any]]:
    """Find an option in the snapshot based on the command path"""
    current_level = snapshot
    command_path = []

    # Navigate to the current command level
    for i, word in enumerate(words[1:], 1):  # Skip the command name
        if word.startswith('-'):
            # This is an option, not a command
            break

        command_path.append(word)
        # Find the subcommand
        if 'subcommands' in current_level:
            for subcmd in current_level['subcommands']:
                if subcmd['name'] == word:
                    current_level = subcmd
                    break
            else:
                # Command not found, stop here
                break

    # Look for the option at the current level
    if 'options' in current_level:
        for option in current_level['options']:
            # Handle different option formats
            if 'name' in option:
                # Format: {"name": "-h", "aliases": ["--help"]}
                if option['name'] == option_name:
                    return option
                if 'aliases' in option and option_name in option['aliases']:
                    return option
            elif (option.get('short') and f"-{option['short']}" == option_name) or \
                 (option.get('long') and f"--{option['long']}" == option_name):
                return option

    return None

def handle_completion_fast():
    """Handle completion requests with minimal imports"""
    try:
        # Try to use snapshot first - look for it in the same directory as this script
        snapshot_path = Path(__file__).parent / "main_snapshot.json"

        if snapshot_path.exists():
            snapshot = load_snapshot(str(snapshot_path))
            if snapshot:
                # Get the current word being completed
                comp_line = os.environ.get('COMP_LINE', '')
                comp_point = int(os.environ.get('COMP_POINT', 0))
                words = comp_line.split()

                # Extract prefix and option being completed
                prefix = ''
                option_being_completed = None

                # Walk through words to find the last option and set prefix
                i = 1  # skip the command name
                while i < len(words):
                    word = words[i]
                    if word.startswith('-'):
                        if i == len(words) - 1:
                            # Cursor is after an option, completing its value
                            prefix = ''
                            option_being_completed = word
                            break
                        elif i == len(words) - 2:
                            # Cursor is after a value for an option
                            prefix = words[-1]
                            option_being_completed = word
                            break
                    i += 1
                else:
                    # Not completing an option value, use improved logic
                    if comp_line.endswith(' ') and comp_point <= len(comp_line):
                        # If the line ends with a space, we're completing after the last word
                        prefix = ''
                        # Check if the last word was an option
                        if words and words[-1].startswith('-'):
                            option_being_completed = words[-1]
                    elif len(words) > 1:
                        # Check if we're completing the last word or if there's a partial word
                        if comp_point == len(comp_line):
                            # Cursor is at the end, completing the last word
                            prefix = words[-1]
                        else:
                            # Cursor is in the middle of a word, extract the partial word
                            partial_word = comp_line[comp_point:].split()[0] if comp_line[comp_point:].strip() else ''
                            prefix = partial_word
                    else:
                        prefix = ''

                # Special case: if the last word is just '-', we're completing options
                if words and words[-1] == '-':
                    prefix = '-'
                    option_being_completed = None
                # Special case: if the last word starts with '-' but isn't complete, we're completing options
                elif words and words[-1].startswith('-') and len(words[-1]) > 1 and not comp_line.endswith(' '):
                    prefix = words[-1]
                    option_being_completed = None

                completions = find_completions(snapshot, words, prefix, option_being_completed)

                # Print completions for bash
                for completion in completions:
                    print(completion)
                return

    except Exception as e:
        print(f"Fast completion failed: {e}", file=sys.stderr)

def main():
    """Main entry point"""
    if is_completion_request():
        handle_completion_fast()
        return

    # If not a completion request, run the original slowcli main function
    from .main import main as slowcli_main
    return slowcli_main()

if __name__ == "__main__":
    main()
