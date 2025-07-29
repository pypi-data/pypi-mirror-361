"""
Entrypoint generator for FastEntry

This module handles automatic generation of lightweight completion entrypoints
and snapshots for existing CLI applications.
"""

import sys
import ast
import json
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any, Tuple



class EntrypointGenerator:
    """
    Generates lightweight completion entrypoints for CLI applications
    """

    def __init__(self, cli_file: str, output_file: Optional[str] = None,
                 snapshot_path: Optional[str] = None):
        """
        Initialize the generator

        Args:
            cli_file: Path to the original CLI file
            output_file: Optional output path for the entrypoint
            snapshot_path: Optional path for the snapshot file
        """
        self.cli_file = Path(cli_file)
        self.output_file = Path(output_file) if output_file else self._get_default_output_path()
        self.snapshot_path = Path(snapshot_path) if snapshot_path else self._get_default_snapshot_path()

    def _get_default_output_path(self) -> Path:
        """Get default output path for the entrypoint"""
        return self.cli_file.parent / f"{self.cli_file.stem}_completion.py"

    def _get_default_snapshot_path(self) -> Path:
        """Get default snapshot path"""
        return self.cli_file.parent / f"{self.cli_file.stem}_snapshot.json"

    def generate(self) -> str:
        """
        Generate the lightweight entrypoint

        Returns:
            Path to the generated entrypoint file
        """
        # First, generate the snapshot
        self._generate_snapshot()

        # Then generate the entrypoint
        self._generate_entrypoint()

        return str(self.output_file)

    def _generate_snapshot(self):
        """Generate snapshot from the CLI file"""
        try:
            generate_snapshot_for_file(str(self.cli_file), str(self.snapshot_path))
        except Exception as e:
            print(f"Warning: Could not generate snapshot: {e}", file=sys.stderr)
            # Continue without snapshot - will fall back to regular argcomplete

    def _generate_entrypoint(self):
        """Generate the lightweight entrypoint file"""
        # Analyze the CLI file to extract module and function names
        module_name, main_function = self._extract_cli_info()

        # Generate the entrypoint code
        entrypoint_code = self._generate_entrypoint_code(module_name, main_function)

        # Write the entrypoint file
        with open(self.output_file, 'w') as f:
            f.write(entrypoint_code)

        # Make it executable
        self.output_file.chmod(0o755)

    def _extract_cli_info(self) -> Tuple[str, str]:
        """
        Extract module name and main function from CLI file

        Returns:
            Tuple of (module_name, main_function)
        """
        try:
            # Read the CLI file
            with open(self.cli_file, 'r') as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content)

            # Look for main function
            main_function = "main"
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name == "main":
                        main_function = "main"
                        break
                    elif node.name == "__main__":
                        main_function = "__main__"
                        break

            # Get module name - improved to handle package structure
            cli_path = Path(self.cli_file).resolve()

            # Try to determine the package structure
            # Look for __init__.py files to determine package hierarchy
            current_dir = cli_path.parent
            package_parts = []

            # Walk up the directory tree to find the package root
            while current_dir != current_dir.parent:
                if (current_dir / "__init__.py").exists():
                    package_parts.append(current_dir.name)
                    current_dir = current_dir.parent
                else:
                    break

            # Reverse to get the correct order
            package_parts.reverse()

            # Add the module name
            module_name = cli_path.stem
            if package_parts:
                module_name = ".".join(package_parts) + "." + module_name

            return module_name, main_function

        except Exception as e:
            print(f"Warning: Could not analyze CLI file: {e}", file=sys.stderr)
            # Fallback to common patterns
            return self.cli_file.stem, "main"

    def _generate_entrypoint_code(self, module_name: str, main_function: str) -> str:
        """
        Generate the entrypoint code

        Args:
            module_name: Name of the module to import
            main_function: Name of the main function

        Returns:
            Generated entrypoint code
        """
        # Get relative import path - simplified approach
        import_path = module_name

        entrypoint_code = f'''#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
"""
Lightweight completion entrypoint for {self.cli_file.name}
Generated by FastEntry - DO NOT EDIT MANUALLY
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

def is_completion_request():
    """Check if this is an argcomplete completion request"""
    return os.environ.get('_ARGCOMPLETE') == '1'

def load_snapshot(snapshot_path: str) -> Dict[str, Any]:
    """Load the CLI snapshot from JSON file"""
    try:
        with open(snapshot_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading snapshot: {{e}}", file=sys.stderr)
        return {{}}

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
                # Format: {{"name": "-h", "aliases": ["--help"]}}
                if option['name'].startswith(prefix):
                    completions.append(option['name'])
                if 'aliases' in option:
                    for alias in option['aliases']:
                        if alias.startswith(prefix):
                            completions.append(alias)

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
                # Format: {{"name": "-h", "aliases": ["--help"]}}
                if option['name'] == option_name:
                    return option
                if 'aliases' in option and option_name in option['aliases']:
                    return option

    return None

def handle_completion_fast():
    """Handle completion requests with minimal imports"""
    try:
        # Try to use snapshot first - look for it in the same directory as this script
        snapshot_path = Path(__file__).parent / "{self.snapshot_path.name}"

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

                # If we got completions from snapshot, use them
                if completions:
                    for completion in completions:
                        print(completion)
                    return

                # If no completions from snapshot, fall back to argcomplete
                # This handles dynamic completions like file paths
                handle_completion_fallback()
                return

    except Exception as e:
        print(f"Fast completion failed: {{e}}", file=sys.stderr)

    # If anything fails, fall back to argcomplete
    handle_completion_fallback()

def handle_completion_fallback():
    """Fall back to the original argcomplete behavior for dynamic completions"""
    try:
        # Import the original main function and let argcomplete handle it
        import {import_path}
        {import_path}.{main_function}()

    except Exception as e:
        print(f"Fallback completion failed: {{e}}", file=sys.stderr)

def main():
    """Main entry point"""
    if is_completion_request():
        handle_completion_fast()
        return

    # If not a completion request, run the original CLI
    import {import_path}
    {import_path}.{main_function}()

if __name__ == "__main__":
    main()
'''
        return entrypoint_code


def generate_snapshot_for_file(cli_file: str, output_path: Optional[str] = None) -> str:
    """
    Generate a snapshot for a CLI file

    Args:
        cli_file: Path to the CLI file
        output_path: Optional output path for the snapshot

    Returns:
        Path to the generated snapshot file
    """
    if output_path is None:
        output_path = str(Path(cli_file).with_suffix('.json'))

    try:
        # Import the CLI module - improved to handle package structures
        cli_path = Path(cli_file).resolve()
        cli_dir = cli_path.parent
        cli_name = cli_path.stem

        # Try to determine the package structure and add the right path to sys.path
        # Look for __init__.py files to determine package hierarchy
        current_dir = cli_dir
        package_parts = []

        # Walk up the directory tree to find the package root
        while current_dir != current_dir.parent:
            if (current_dir / "__init__.py").exists():
                package_parts.append(current_dir.name)
                current_dir = current_dir.parent
            else:
                break

        # Add the package root to sys.path
        package_root = current_dir
        if str(package_root) not in sys.path:
            sys.path.insert(0, str(package_root))

        # Build the module name for import
        package_parts.reverse()
        if package_parts:
            module_name = ".".join(package_parts) + "." + cli_name
        else:
            module_name = cli_name

        # Try to import the module using the package name
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            # Fallback to direct file import if package import fails
            print(f"Package import failed ({e}), trying direct import...")
            spec = importlib.util.spec_from_file_location(module_name, cli_file)
            if spec is None:
                raise ImportError(f"Could not create spec for {cli_file}")
            module = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                raise ImportError(f"Could not get loader for {cli_file}")
            spec.loader.exec_module(module)

        # Look for parser or main function
        parser = None

        # Try to find parser
        if hasattr(module, 'parser'):
            parser = module.parser
        elif hasattr(module, 'create_parser'):
            try:
                parser = module.create_parser()
                print(f"Found create_parser() function in {cli_file}")
            except Exception as e:
                print(f"Error calling create_parser(): {e}")
                parser = None
        elif hasattr(module, 'main'):
            # Try to extract parser from main function
            # This is a simplified approach
            print(f"Warning: Could not find parser in {cli_file}")
            print("You may need to manually create a parser and call generate_snapshot()")
            return output_path
        else:
            print(f"Error: Could not find parser in {cli_file}")
            return output_path

        if parser is None:
            print(f"Error: Could not create parser from {cli_file}")
            return output_path

        # Generate snapshot using the recursive function
        from .core import _extract_parser_structure_recursive
        snapshot = _extract_parser_structure_recursive(parser)

        with open(output_path, 'w') as f:
            json.dump(snapshot, f, indent=2)

        print(f"Successfully generated snapshot for {cli_file}")

    except Exception as e:
        print(f"Error generating snapshot for {cli_file}: {e}")
        # Create a minimal snapshot
        minimal_snapshot = {
            "description": f"Generated snapshot for {cli_file}",
            "options": [],
            "positionals": [],
            "subcommands": []
        }

        with open(output_path, 'w') as f:
            json.dump(minimal_snapshot, f, indent=2)

    return output_path


def analyze_cli_file(cli_file: str) -> Dict[str, Any]:
    """
    Analyze a CLI file to extract information

    Args:
        cli_file: Path to the CLI file

    Returns:
        Dictionary with analysis results
    """
    try:
        with open(cli_file, 'r') as f:
            content = f.read()

        tree = ast.parse(content)

        analysis = {
            'imports': [],
            'functions': [],
            'classes': [],
            'has_main': False,
            'has_argparse': False,
            'has_argcomplete': False
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    analysis['imports'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    analysis['imports'].append(f"{module}.{alias.name}")
            elif isinstance(node, ast.FunctionDef):
                analysis['functions'].append(node.name)
                if node.name == 'main':
                    analysis['has_main'] = True
            elif isinstance(node, ast.ClassDef):
                analysis['classes'].append(node.name)

        # Check for specific imports
        analysis['has_argparse'] = any('argparse' in imp for imp in analysis['imports'])
        analysis['has_argcomplete'] = any('argcomplete' in imp for imp in analysis['imports'])

        return analysis

    except Exception as e:
        print(f"Error analyzing {cli_file}: {e}")
        return {
            'imports': [],
            'functions': [],
            'classes': [],
            'has_main': False,
            'has_argparse': False,
            'has_argcomplete': False
        }
