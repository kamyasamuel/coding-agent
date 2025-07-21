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

    def read_package_docs(self, package_path: Optional[Path] = None) -> None:
        """
        Read Python package documentation and summarize key information.
        Only processes .py files and READMEs for efficiency.
        """
        package_path = package_path or self.base_path
        package_path = Path(package_path)

        for root, _, files in os.walk(package_path):
            for file in files:
                file_path = Path(root) / file
                if file.endswith('.py'):
                    self._summarize_python_file(file_path)
                elif file.lower() in ('readme.md', 'readme.rst', 'readme.txt'):
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
        self.directory_tree = self._build_tree(base_path)
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

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                print(self.pp.pformat(self.directory_tree), file=f)
        else:
            self.pp.pprint(self.directory_tree)

    def pretty_print_summaries(self, output_file: Optional[str] = None) -> None:
        """Pretty print the documentation summaries to console or a file."""
        if not self.doc_summaries:
            self.logger.warning("Documentation summaries are empty. Run read_package_docs first.")
            return

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                print(self.pp.pformat(self.doc_summaries), file=f)
        else:
            self.pp.pprint(self.doc_summaries)

    def save_summaries(self, output_path: str) -> None:
        """Save documentation summaries to a JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.doc_summaries, f, indent=2)

    def generate_code_with_groq(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate code using the Groq API based on a user prompt.
        Returns the generated code as a string.
        """
        try:
            response = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",  # Example model, adjust as needed
                messages=[
                    {"role": "system", "content": "You are a Python code generator. Provide clean, well-documented Python code."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
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
        path_obj.mkdir(exist_ok=True)
        self._create_directory_structure(path_obj, structure, use_groq)

    def _create_directory_structure(self, base_path: Path, structure: Dict, use_groq: bool) -> None:
        """Recursively create directories and files from the structure."""
        for item in structure.get('children', []):
            item_path = base_path / item['name']
            if item['type'] == 'dir':
                item_path.mkdir(exist_ok=True)
                self._create_directory_structure(item_path, item, use_groq)
            elif item['type'] == 'file':
                content = item.get('content', '')
                if use_groq and not content:  # Generate content with Groq if not provided
                    prompt = f"Generate a Python file named {item['name']} for a {structure['name']} project."
                    content = self.generate_code_with_groq(prompt)
                with open(item_path, 'w', encoding='utf-8') as f:
                    f.write(content)

    def design_project_template(self, project_type: str = 'basic', use_groq: bool = False) -> Dict:
        """
        Design a project directory structure based on a template type.
        Optionally use Groq to generate file content.
        """
        templates = {
            'basic': {
                'name': 'project',
                'children': [
                    {'name': 'src', 'type': 'dir', 'children': [
                        {'name': '__init__.py', 'type': 'file', 'content': '# Package init'},
                        {'name': 'main.py', 'type': 'file', 'content': '' if use_groq else 'def main():\n    pass\n\nif __name__ == "__main__":\n    main()'}
                    ]},
                    {'name': 'tests', 'type': 'dir', 'children': [
                        {'name': '__init__.py', 'type': 'file', 'content': ''},
                        {'name': 'test_main.py', 'type': 'file', 'content': '' if use_groq else 'import pytest\n'}
                    ]},
                    {'name': 'README.md', 'type': 'file', 'content': '# Project\nA basic Python project.'},
                    {'name': 'requirements.txt', 'type': 'file', 'content': ''}
                ]
            }
        }
        return templates.get(project_type, templates['basic'])
