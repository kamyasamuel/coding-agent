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