import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pprint import PrettyPrinter
from groq import Groq, GroqError
import logging
import re
from litellm import completion
from dotenv import load_dotenv

class CodingAgent:
    def __init__(self, base_path: str, provider: str = 'groq'):
        """Initialize the coding agent with a base path."""
        load_dotenv()
        self.base_path = Path(base_path)
        self.pp = PrettyPrinter(indent=2)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.provider = provider
        self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        if not self.groq_client.api_key:
            self.logger.warning("No Groq API key provided or found in .env file.")
        try:
            from rich.console import Console
            self.console = Console()
        except ImportError:
            self.console = None

    def generate_code(self, prompt: str, system_prompt: str) -> str:
        """Generate code using the specified provider."""
        if self.provider == 'groq':
            return self.generate_code_with_groq(prompt, system_prompt)
        else:
            return self.generate_code_with_litellm(prompt, system_prompt)

    def generate_code_with_litellm(self, prompt: str, system_prompt: str) -> str:
        """Generate code using LiteLLM with a dynamic system prompt."""
        try:
            model_name = ""
            if self.provider == "gemini":   model_name = "gemini/gemini-2.5-pro"
            if self.provider == "groq": model_name = "groq/llama3-70b-8192"
            if self.provider == "openai":   model_name = "openai/gpt-4o-mini"
            else:   model_name = "ollama/granite3.3:2b"
            response = completion(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"LiteLLM API error: {e}")
            return f"# Error: Failed to generate code: {e}"

    def generate_code_with_groq(self, prompt: str, system_prompt: str) -> str:
        """Generate code using Groq API with a dynamic system prompt."""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()
        except GroqError as e:
            self.logger.error(f"Groq API error: {e}")
            return f"# Error: Failed to generate code: {e}"
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return f"# Error: An unexpected error occurred: {e}"

    def plan_project(self, prompt: str) -> Optional[Dict]:
        """Agent: Plan Project. Creates a comprehensive blueprint for the project."""
        if self.console:
            self.console.print("[bold cyan]Agent: Project Planner running...[/]")
        
        system_prompt = (
            "You are a master software architect. Based on the user's request, create a comprehensive project blueprint. "
            "The blueprint must be a single, clean JSON object, without any surrounding text or markdown. "
            "It must contain two keys: 'readme_content' and 'project_structure'. "
            "The 'readme_content' value must be a single string with properly escaped newlines () to be valid JSON. "
            "The 'project_structure' value should be a JSON object representing the file and directory structure, with instructional comments in each file."
        )
        
        response_str = self.generate_code(prompt, system_prompt)
        
        try:
            # Enhanced JSON extraction
            json_str = None
            json_match = re.search(r'```json\s*([\s\S]+?)\s*```', response_str)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                start = response_str.find('{')
                end = response_str.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = response_str[start:end].strip()

            if not json_str:
                 raise json.JSONDecodeError("No JSON object found in LLM response", response_str, 0)
            
            if self.console:
                self.console.print("[green]Project blueprint generated successfully.[/]")
            return json.loads(json_str)

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse project blueprint: {e} Response was: {response_str}")
            return None

    def verify_project_plan(self, plan: Dict, original_prompt: str) -> Tuple[bool, str]:
        """Agent: Verify Project Plan. Reviews the blueprint for quality and alignment."""
        if self.console:
            self.console.print("[bold cyan]Agent: Project Verifier running...[/]")

        system_prompt = (
            "You are a meticulous project manager. Your task is to review the provided project blueprint. "
            "Assess if the plan is logical, complete, and accurately reflects the user's initial request. "
            "Respond with only 'APPROVED' if the plan is good, or 'REJECTED:' followed by your specific feedback for improvement."
        )
        
        prompt = (f"Original User Request: '{original_prompt}' Generated Blueprint: {json.dumps(plan, indent=2)}")

        response = self.generate_code(prompt, system_prompt)
        
        if response.startswith("APPROVED"):
            if self.console:
                self.console.print("[green]Verification result: Plan APPROVED.[/]")
            return True, ""
        elif response.startswith("REJECTED:"):
            feedback = response.replace("REJECTED:", "").strip()
            if self.console:
                self.console.print(f"[yellow]Verification result: Plan REJECTED. Feedback: {feedback}[/]")
            return False, feedback
        else:
            if self.console:
                self.console.print("[red]Verifier gave an invalid response. Assuming rejection.[/]")
            return False, "The verifier provided an invalid response. Please try again."

    def create_project_directory(self, project_path: str, structure: Dict) -> None:
        """Agent: Create Project Directory. Creates the folder structure and placeholder files."""
        path_obj = Path(project_path)
        if self.console:
            self.console.print(f"[bold cyan]Agent: Directory Creator running at:[/][dim] {path_obj}[/]")
        path_obj.mkdir(exist_ok=True, parents=True)
        # Create README.md from the plan
        readme_content = structure.get('readme_content', '# Project Generated by AI.')
        with open(path_obj / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        if self.console:
            self.console.print(f"[green]Created file:[/] {path_obj / 'README.md'}")
        # Create the rest of the structure
        project_structure = structure.get('project_structure', {})
        if project_structure:
            self._create_directory_structure(path_obj, self._transform_structure(project_structure))

    def _create_directory_structure(self, base_path: Path, children: List[Dict]) -> None:
        """Recursively create directories and files."""
        for item in children:
            item_path = base_path / item['name']
            if item['type'] == 'dir':
                item_path.mkdir(exist_ok=True)
                self._create_directory_structure(item_path, item.get('children', []))
            elif item['type'] == 'file':
                with open(item_path, 'w', encoding='utf-8') as f:
                    f.write(item.get('content', ''))
                if self.console:
                    self.console.print(f"[cyan]Created file:[/][dim] {item_path}[/]")
                self._create_directory_structure(item_path, item.get('children', []))
            elif item_path.is_file():
                with open(item_path, 'w', encoding='utf-8') as f:
                    f.write(item.get('content', ''))
                if self.console:
                    self.console.print(f"[green]Created file:[/][dim] {item_path}[/]")

    def _transform_structure(self, structure: Dict) -> List[Dict]:
        """Transforms the dictionary-based structure into a list-based one for recursion."""
        transformed_list = []
        for name, content in structure.items():
            if isinstance(content, dict):
                transformed_list.append({
                    'name': name,
                    'type': 'dir',
                    'children': self._transform_structure(content)
                })
            else:
                transformed_list.append({
                    'name': name,
                    'type': 'file',
                    'content': content
                })
        return transformed_list

    def generate_file_content_from_instructions(self, project_path: str) -> None:
        """Agent: Generate File Content. Populates files based on instructional comments."""
        if self.console:
            self.console.print(f"[bold cyan]Agent: Content Generator running for project at:[/][dim] {project_path}[/]")
        
        system_prompt = (
            "You are a sophisticated AI file processor. Based on the instructional comments provided, generate the full, complete content for the file. "
            "Return only the raw code or text for the file, without any surrounding text, explanations, or markdown."
        )

        for root, _, files in os.walk(project_path):
            for file in files:
                # Skip README, as it's already generated
                if file.lower() == 'readme.md':
                    continue
                file_path = Path(root) / file
                with open(file_path, 'r+', encoding='utf-8') as f:
                    instructions = f.read()
                    if instructions.strip().startswith('#'):
                        if self.console:
                            self.console.print(f"[yellow]Generating content for:[/][dim] {file_path}[/]")
                        
                        generated_content = self.generate_code(instructions, system_prompt)
                        f.seek(0)
                        f.write(generated_content)
                        f.truncate()
                        if self.console:
                            self.console.print(f"[green]Successfully updated:[/][dim] {file_path}[/]")

    def refine_python_code(self, project_path: str) -> None:
        """Agent: Refine and Debug Code. Cleans, refactors, and debugs Python files."""
        system_prompt = (
            "You are a sophisticated AI file processor. Based on the instructional comments provided, generate the full, complete content for the file. "
            "Return only the raw code or text for the file, without any surrounding text, explanations, or markdown."
        )
        for root, _, files in os.walk(project_path):
            for file in files:
                # Skip README, as it's already generated
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    with open(file_path, 'r+', encoding='utf-8') as f:
                        original_code = f.read()

                        if not original_code.strip(): # Skip empty files
                            if self.console:
                                self.console.print(f"[dim]Skipping empty file:[/][dim] {file_path}[/]")
                                continue
                            
                        if self.console:
                            self.console.print(f"[yellow]Refining code in:[/][dim] {file_path}[/]")
                        
                        refined_code = self.generate_code(original_code, system_prompt)
                        
                        f.seek(0)
                        f.write(refined_code)
                        f.truncate()
                        if self.console:
                            self.console.print(f"[green]Successfully updated:[/] {file_path}")