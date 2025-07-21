import os
from dotenv import load_dotenv
from groq import Groq
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
import asyncio

class GroqInference:
    """A class to handle Groq API inference with streaming and colored output."""

    def __init__(self, model="llama3-70b-8192", temperature=0.7, max_tokens=500):
        """Initialize the Groq client with environment variables and model settings."""
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")

        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.console = Console()  # Initialize rich console for pretty printing

    def _format_message(self, content, role="assistant"):
        """Format a message with rich styling based on role."""
        if role == "user":
            return Panel(
                Text(content, style="bold cyan"),
                title="User Prompt",
                border_style="blue",
                expand=False
            )
        return Panel(
            Markdown(content),
            title="Grok Response",
            border_style="green",
            expand=False
        )

    async def stream_inference(self, prompt, system_prompt="You are a helpful AI assistant."):
        """Run streaming inference with the Groq API and print responses in real-time."""
        try:
            # Print user prompt
            self.console.print(self._format_message(prompt, role="user"))

            # Initialize streaming chat completion
            stream = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )

            # Stream and print responses with rich formatting
            response_content = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    response_content += content
                    #self.console.print(Text(content, style="white"), end="", soft_wrap=True)

            # Print complete response in a formatted panel
            self.console.print("\n")  # New line after streaming
            self.console.print(self._format_message(response_content))

        except Exception as e:
            self.console.print(
                Panel(
                    Text(f"Error during inference: {str(e)}", style="bold red"),
                    title="Error",
                    border_style="red"
                )
            )

    def run(self, prompt, system_prompt="You are a helpful AI assistant."):
        """Synchronous wrapper to run the async stream_inference method."""
        asyncio.run(self.stream_inference(prompt, system_prompt))

# Example usage
if __name__ == "__main__":
    # Initialize the GroqInference class
    groq = GroqInference(model="llama3-70b-8192", temperature=0.5, max_tokens=200)

    # Run inference with a sample prompt
    prompt = "Explain the meaning of life in a concise way."
    groq.run(prompt, system_prompt="You are a philosopher AI with concise answers.")