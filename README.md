pip install groq python-dotenv rich
groq-inference-project/
groq = GroqInference(model="llama3-70b-8192", temperature=0.5, max_tokens=200)

# Groq API Streaming Inference

Interact with the Groq API using Python, featuring real-time streaming responses and rich, colored console output. Environment variables are securely loaded from a `.env` file.

## Features
- **Streaming Inference**: Real-time response streaming from Groq API.
- **Rich Console Output**: User prompts in blue, responses in green, errors in red.
- **Environment Variables**: Secure API key management via `.env`.
- **Configurable**: Easily set model, temperature, and max tokens.

## Requirements
- Python 3.8+
- Groq API Key ([Get one from xAI](https://x.ai/api))
- Dependencies:
  - `groq`
  - `python-dotenv`
  - `rich`

## Installation
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file** in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key
   ```
   Add `.env` to `.gitignore` to keep your API key safe.

## Project Structure
```
groq-inference-project/
├── .env            # Environment variables (not committed)
├── .gitignore      # Git ignore file
├── app-bup.py      # Main script with GroqInference class
├── README.md       # This file
├── requirements.txt
├── venv/           # Virtual environment
└── __pycache__/
```

## Usage
Run the script:
```bash
python app-bup.py
```

Example code:
```python
from app-bup import GroqInference

# Initialize the GroqInference class
groq = GroqInference(model="llama3-70b-8192", temperature=0.5, max_tokens=200)

# Run inference with a sample prompt
prompt = "Explain the meaning of life in a concise way."
groq.run(prompt, system_prompt="You are a philosopher AI with concise answers.")
```

### Expected Output
- User prompt displayed in a blue panel
- Streaming response printed in real-time (white text)
- Final response shown in a green panel with Markdown formatting

#### Example
```
┌───────────────────────────────┐
│         User Prompt           │
│ Explain the meaning of life   │
│      in a concise way.        │
└───────────────────────────────┘
[Streaming response...]
┌───────────────────────────────┐
│        Groq Response          │
│ The meaning of life is to     │
│ find purpose through          │
│ relationships, growth, and    │
│ contributing to the universe. │
└───────────────────────────────┘
```

## Configuration
- **Environment Variable**: `GROQ_API_KEY` (required, set in `.env`)
- **Class Parameters**:
  - `model`: Groq model to use (default: `llama3-70b-8192`)
  - `temperature`: Controls randomness (default: `0.7`, range: `0.0–2.0`)
  - `max_tokens`: Maximum response tokens (default: `500`)

## Troubleshooting
- **GROQ_API_KEY not found**: Ensure `.env` exists and contains a valid key.
- **Streaming issues**: Update `groq` package (`pip install --upgrade groq`). Check model availability.
- **No output**: Verify API key and internet connection.
- **Formatting issues**: Ensure `rich` is installed and your terminal supports colors.

## Notes
- **Security**: Never commit `.env` to version control.
- **Streaming Limitation**: Groq API streaming does not support tool calling or structured response formats.
- **Extending**: Modify `app-bup.py` to add custom prompts, system messages, or features.

## Contributing
Contributions are welcome! Please submit issues or pull requests. Update the README for any changes.

## License
MIT License. See LICENSE for details.

## Workflow for a 3-Agent System

Here's a breakdown of a coherent workflow for a coding agent that manages three primary agents, including system and user prompts for each.

**Agent 1: Project Structure and Directory Generating Agent**

This agent is responsible for creating the foundational structure of a new project. It generates directories and placeholder script files. Crucially, it embeds instructions within these placeholder files, guiding a language model on the specific content to be generated for each file.

**System Prompt:**

"You are an expert software architect and project planner. Your task is to generate a complete and logical directory structure for a new software project based on the user's description. You will create all necessary folders and files, including placeholders for source code, tests, documentation, and configuration. For each generated file, you will write a clear and concise set of instructions, embedded as comments, that will guide another AI in generating the full content of that file. The instructions should specify the file's purpose, key functionalities, required imports, and any other relevant details to ensure the generated code is accurate and complete."

**User Prompt:**

"Generate the project structure for a Python-based web application using the Flask framework. The application should include a single endpoint that returns a 'Hello, World!' message. The project should have a standard layout with separate directories for the application, static assets, and templates. Include a `requirements.txt` file, a basic README, and a test file for the main application logic."

**Agent 2: File Content Generation Agent**

This agent iterates through the project directory, reads the instructions from the placeholder files, and uses them as prompts for a language model to generate the actual file content. Once the content is generated, the agent overwrites the placeholder file with the new, AI-generated content.

**System Prompt:**

"You are a sophisticated AI file processor. Your task is to scan a directory for files containing instructional comments. For each file you find, you will:
1.  Read the instructional comments within the file.
2.  Use these instructions as a prompt to a large language model to generate the full, complete content for that file.
3.  Once the content is generated, you will replace the original file's content (including the instructional comments) with the newly generated content.
4.  Ensure that the new content is written cleanly and without any additional boilerplate or introductory text."

**User Prompt:**

"Process the project directory located at `./new-flask-app`. Scan all files for instructional comments, use them to generate the corresponding file content, and update the files in place."

**Agent 3: Code Refinement and Debugging Agent**

The final agent in the workflow is responsible for ensuring the quality of the generated code. It searches for all Python files (`.py`), reads their content, and passes it to a language model with instructions to clean, refactor, and debug the code. The goal is to produce code that is not only functional but also well-structured, readable, and ready to run without errors.

**System Prompt:**

"You are an expert Python programmer and code reviewer with a keen eye for detail. You will be given the content of a Python file. Your task is to analyze the code and perform the following actions:
1.  **Clean the code:** Format the code according to PEP 8 standards, ensuring consistent indentation, line spacing, and naming conventions.
2.  **Refactor for clarity and efficiency:** Improve the code's structure, remove redundancies, and optimize for performance where possible.
3.  **Identify and fix bugs:** Scrutinize the code for any potential errors, logical flaws, or edge cases that might cause issues. Correct these issues to ensure the code is robust and reliable.
4.  **Add documentation:** Add or improve docstrings and comments to explain the purpose of functions, classes, and complex code blocks.
5.  **Return only the cleaned, refactored, and debugged code.** Do not include any explanations or apologies in your response, only the final, production-ready code."

**User Prompt:**

"Please review and refine the following Python code to ensure it is clean, efficient, and free of errors. The code is located at `./new-flask-app/app/main.py`."

This 3-agent workflow provides a structured and automated approach to software development, from initial project setup to final code refinement. Each agent has a distinct role, ensuring a clear separation of concerns and a more manageable and scalable process.
