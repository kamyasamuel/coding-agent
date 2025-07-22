import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Optional
from pprint import PrettyPrinter
from groq import Groq, GroqError
import logging
from litellm import completion
from dotenv import load_dotenv

class CodingAgent:
    def __init__(self, base_path: str):
        """Initialize the coding agent with a base path and optional Groq API key."""
        # Load environment variables from .env file
        load_dotenv()

        self.base_path = Path(base_path)
        self.directory_tree = {}
        self.doc_summaries = {}
        self.pp = PrettyPrinter(indent=2)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        # Use provided API key or fall back to .env variable
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        if not self.groq_client.api_key:
            self.logger.warning("No Groq API key provided or found in .env file.")

        # Rich console for pretty logs
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            self.console = Console()
        except ImportError:
            self.console = None

    def read_package_docs(self, package_path: Optional[Path] = None) -> None:
        """
        Read Python package documentation and summarize key information.
        Only processes .py files and READMEs for efficiency.
        """
        package_path = package_path or self.base_path
        package_path = Path(package_path)

        if self.console:
            self.console.print(f"[bold cyan]Reading and summarizing documentation in:[/] {package_path}")

        for root, _, files in os.walk(package_path):
            for file in files:
                file_path = Path(root) / file
                if file.endswith('.py'):
                    if self.console:
                        self.console.print(f"[green]Summarizing Python file:[/] {file_path}")
                    self._summarize_python_file(file_path)
                elif file.lower() in ('readme.md', 'readme.rst', 'readme.txt'):
                    if self.console:
                        self.console.print(f"[yellow]Summarizing README:[/] {file_path}")
                    self._summarize_readme(file_path)

    def _summarize_python_file(self, file_path: Path) -> None:
        """Extract and summarize docstrings from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source)

            summary = {
                'module': file_path.stem,
                'docstring': ast.get_docstring(tree) or "No module docstring",
                'functions': [],
                'classes': []
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    doc = ast.get_docstring(node) or "No docstring"
                    summary['functions'].append({
                        'name': node.name,
                        'docstring': doc.split('\n')[0]
                    })
                elif isinstance(node, ast.ClassDef):
                    doc = ast.get_docstring(node) or "No docstring"
                    summary['classes'].append({
                        'name': node.name,
                        'docstring': doc.split('\n')[0]
                    })

            self.doc_summaries[str(file_path)] = summary
        except (SyntaxError, UnicodeDecodeError) as e:
            self.doc_summaries[str(file_path)] = {'error': f'Failed to parse: {e}'}

    def _summarize_readme(self, file_path: Path) -> None:
        """Summarize README content (first few lines for brevity)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()[:5]
            summary = {
                'file': file_path.name,
                'summary': ''.join(content).strip()[:200] + '...'
            }
            self.doc_summaries[str(file_path)] = summary
        except Exception as e:
            self.doc_summaries[str(file_path)] = {'error': f'Failed to read: {e}'}

    def generate_directory_tree(self, base_path: Optional[Path] = None) -> Dict:
        """
        Generate a directory tree for the given path and store it.
        Returns the tree as a dictionary.
        """
        base_path = base_path or self.base_path
        base_path = Path(base_path)
        if self.console:
            self.console.print(f"[bold cyan]Generating directory tree for:[/] {base_path}")
        self.directory_tree = self._build_tree(base_path)
        if self.console:
            self.console.print(f"[green]Directory tree generated.[/]")
        return self.directory_tree

    def _build_tree(self, path: Path) -> Dict:
        """Recursively build a directory tree."""
        tree = {'name': path.name, 'type': 'dir', 'children': []}
        try:
            for item in path.iterdir():
                if item.is_dir():
                    tree['children'].append(self._build_tree(item))
                else:
                    tree['children'].append({'name': item.name, 'type': 'file'})
        except PermissionError:
            tree['error'] = 'Permission denied'
        return tree

    def pretty_print_tree(self, output_file: Optional[str] = None) -> None:
        """Pretty print the directory tree to console or a file."""
        if not self.directory_tree:
            self.logger.warning("Directory tree is empty. Run generate_directory_tree first.")
            return

        if self.console:
            self.console.print("[bold cyan]Pretty printing directory tree...[/]")
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                print(self.pp.pformat(self.directory_tree), file=f)
            if self.console:
                self.console.print(f"[green]Directory tree saved to:[/] {output_file}")
        else:
            self.pp.pprint(self.directory_tree)

    def pretty_print_summaries(self, output_file: Optional[str] = None) -> None:
        """Pretty print the documentation summaries to console or a file."""
        if not self.doc_summaries:
            self.logger.warning("Documentation summaries are empty. Run read_package_docs first.")
            return

        if self.console:
            self.console.print("[bold cyan]Pretty printing documentation summaries...[/]")
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                print(self.pp.pformat(self.doc_summaries), file=f)
            if self.console:
                self.console.print(f"[green]Documentation summaries saved to:[/] {output_file}")
        else:
            self.pp.pprint(self.doc_summaries)

    def save_summaries(self, output_path: str) -> None:
        """Save documentation summaries to a JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.doc_summaries, f, indent=2)
        if self.console:
            self.console.print(f"[green]Summaries saved to:[/] {output_path}")

    def generate_code_with_groq(self, prompt: str) -> str:
        """
        Generate code using the Groq API based on a user prompt.
        Returns the generated code as a string.
        """
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",  # Example model, adjust as needed
                messages=[
                    {"role": "system", "content": "You are a Python code generator. Provide clean, well-documented ready to run Python code without further debugging."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except GroqError as e:
            self.logger.error(f"Groq API error: {e}")
            return f"# Error: Failed to generate code: {e}"

    def create_project_directory(self, project_path: str, structure: Dict, use_groq: bool = False) -> None:
        """
        Create a project directory based on the provided structure.
        Optionally use Groq API to generate file content.
        """
        path_obj = Path(project_path)
        if self.console:
            self.console.print(f"[bold cyan]Creating project directory at:[/] {project_path}")
        path_obj.mkdir(exist_ok=True)
        self._create_directory_structure(path_obj, structure, use_groq)
        if self.console:
            self.console.print(f"[green]Project directory created at:[/] {project_path}")

    def _create_directory_structure(self, base_path: Path, structure: Dict, use_groq: bool) -> None:
        """Recursively create directories and files from the structure."""
        for item in structure.get('children', []):
            item_path = base_path / item['name']
            if item['type'] == 'dir':
                if self.console:
                    self.console.print(f"[cyan]Creating directory:[/] {item_path}")
                item_path.mkdir(exist_ok=True)
                self._create_directory_structure(item_path, item, use_groq)
            elif item['type'] == 'file':
                content = item.get('content', '')
                if use_groq and not content:  # Generate content with Groq if not provided
                    prompt = f"Generate a Python file named {item['name']} for a {structure['name']} project."
                    if self.console:
                        self.console.print(f"[yellow]Generating content for file:[/] {item_path}")
                    content = self.generate_code_with_groq(prompt)
                with open(item_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                if self.console:
                    self.console.print(f"[green]Created file:[/] {item_path}")

    def design_project_template(self, project_type: str = 'basic', use_groq: bool = True, prompt: str = '') -> Dict:
        """
        Design a project directory structure based on a template type.
        If use_groq is True, use the LLM to generate a detailed project template from a prompt.
        Otherwise, use a static template.
        """
        logging.info(prompt)
        if use_groq:
            if not prompt:
                prompt = (
                    f"Design a detailed Python project directory structure for a '{project_type}' project. "
                    "Return the structure as a JSON object with keys: 'name' (project root), 'children' (list of files and folders), "
                    "where each child is a dict with 'name', 'type' ('file' or 'dir'), and for directories, a 'children' list. "
                    "For files, optionally include a 'content' key with a short code or description. "
                    "Example: {\"name\": \"project\", \"children\": [{\"name\": \"src\", ...}]}"
                )
            if self.console:
                self.console.print(f"[bold cyan]Requesting LLM to design a project template for type:[/] {project_type}")
            try:
                response = self.generate_code_with_groq(prompt)
                print(response)
                import json as _json
                # Try to extract the first JSON object from the response
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = response[start:end]
                    if self.console:
                        self.console.print("[green]LLM project template received and parsed.[/]")
                    return _json.loads(json_str)
                # fallback: try to parse the whole response
                if self.console:
                    self.console.print("[yellow]Trying to parse full LLM response as JSON...[/]")
                return _json.loads(response)
            except Exception as e:
                if self.console:
                    self.console.print(f"[red]Failed to parse LLM project template: {e}[/]")
                self.logger.error(f"Failed to parse LLM project template: {e}")
                # fallback to static template
        templates = {
            'basic': {
                'name': 'project',
                'children': [
                    {'name': 'src', 'type': 'dir', 'children': [
                        {'name': '__init__.py', 'type': 'file', 'content': '# Package init'},
                        {'name': 'main.py', 'type': 'file', 'content': 'def main():\n    pass\n\nif __name__ == "__main__":\n    main()'}
                    ]},
                    {'name': 'tests', 'type': 'dir', 'children': [
                        {'name': '__init__.py', 'type': 'file', 'content': ''},
                        {'name': 'test_main.py', 'type': 'file', 'content': 'import pytest\n'}
                    ]},
                    {'name': 'README.md', 'type': 'file', 'content': '# Project\nA basic Python project.'},
                    {'name': 'requirements.txt', 'type': 'file', 'content': ''}
                ]
            }
        }
        return templates.get(project_type, templates['basic'])

