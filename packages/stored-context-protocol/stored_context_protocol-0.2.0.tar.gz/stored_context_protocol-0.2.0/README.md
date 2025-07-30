# Stored Context Protocol (SCP)

A powerful Python library for managing and intelligently selecting contextual information based on instructor names. This library enables you to load multiple context files (instructors) and automatically select the most relevant one based on your queries using OpenAI's function calling capabilities.

## 🌟 Features

- **Smart Context Selection**: Automatically selects the most relevant instructor/context based on your query
- **Multiple File Formats**: Support for `.txt` and `.md` files
- **Flexible Loading**: Load contexts from files, directories, or plain text
- **OpenAI Integration**: Built-in integration with OpenAI API for intelligent context selection
- **Async Support**: Both synchronous and asynchronous methods available
- **Environment Configuration**: Easy configuration through environment variables
- **Type Safety**: Full type hints for better IDE support
- **Error Handling**: Comprehensive error handling with custom exceptions

## 📦 Installation

### From Source

```bash
git clone https://github.com/QuitCool/stored-context-protocol.git
cd stored-context-protocol
pip install -e .
```

### Using pip

```bash
pip install stored-context-protocol
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Simple Example

Here's a complete example from `simple_example.py`:

```python
from openai import OpenAI
from stored_context_protocol import ContextManager

# Initialize
manager = ContextManager()
client = OpenAI()

# Load context from file
manager.load_file("contexts/python_expert.txt")  # Uses filename as instructor name 
manager.load_file("contexts/web_dev_coach.txt", instructor_name="Use it for web development queries") # Using instructor name

# Ask question
question = "What are Python decorators?"

# Get context-aware response
selection = manager.select_context(question)
prompt = manager.build_prompt_with_context(question, selection['instructor_name'])

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[{"role": "user", "content": prompt}]
)

print(f"Answer: {response.choices[0].message.content}")
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Required
OPENAI_API_KEY=your-api-key-here

# Optional
OPENAI_BASE_URL=https://api.openai.com/v1  # Custom base URL for OpenAI-compatible APIs
OPENAI_MODEL=gpt-4.1           # Default model for context selection
```

### Programmatic Configuration

You can also configure the library programmatically:

```python
from stored_context_protocol import ContextManager

manager = ContextManager(
    openai_api_key="your-api-key",
    openai_base_url="https://api.openai.com/v1",
    openai_model="gpt-4.1"
)
```

## 📖 Detailed Usage

### Loading Contexts

#### From Files

```python
# Load with automatic instructor name (uses filename)
manager.load_file("contexts/python_expert.txt")

# Load with custom instructor name
manager.load_file("contexts/data.txt", instructor_name="Data Science Expert")

# Load with description
manager.load_file(
    "contexts/ml_instructor.md",
    instructor_name="ML Instructor",
    description="Expert in machine learning and neural networks"
)
```

#### From Text

```python
context_text = """
You are a Python expert with deep knowledge of the language...
"""

manager.load_text(
    text=context_text,
    instructor_name="Python Expert",
    description="Expert in Python programming"
)
```

#### From Directory

```python
# Load all .txt and .md files from a directory
contexts = manager.load_directory("contexts/")

# With custom instructor mapping
mapping = {
    "py_expert.txt": "Python Expert",
    "js_expert.txt": "JavaScript Expert"
}
contexts = manager.load_directory("contexts/", instructor_mapping=mapping)
```

### Selecting Contexts

#### Synchronous Selection

```python
# Select the most relevant context
selection = manager.select_context("How do I use async/await in Python?")

print(f"Selected: {selection['instructor_name']}")
print(f"Description: {selection['description']}")
print(f"Context ID: {selection['context_id']}")
```

#### Asynchronous Selection

```python
import asyncio

async def get_context():
    selection = await manager.select_context_async("Explain REST APIs")
    return selection

# Run async function
selection = asyncio.run(get_context())
```

### Building Prompts

```python
# Get the selected context
selection = manager.select_context("What is machine learning?")

# Build a complete prompt with context
full_prompt = manager.build_prompt_with_context(
    prompt="What is machine learning?",
    instructor_name=selection['instructor_name']
)

# Use with OpenAI
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": full_prompt}]
)
```

### Managing Contexts

```python
# Get all loaded instructors
instructors = manager.get_all_instructors()
for instructor in instructors:
    print(f"- {instructor['instructor_name']}: {instructor['description']}")

# Get context count
count = manager.get_context_count()
print(f"Loaded {count} contexts")

# Remove a specific context
manager.remove_context("Python Expert")

# Clear all contexts
manager.clear_contexts()

# Export contexts to JSON
manager.export_contexts("contexts_backup.json")
```

## 🏗️ Advanced Usage

### Custom OpenAI Integration

```python
from stored_context_protocol import ContextManager
from openai import OpenAI

class SmartAssistant:
    def __init__(self):
        self.manager = ContextManager()
        self.client = OpenAI()
        
    def load_experts(self):
        self.manager.load_directory("experts/")
        
    def answer(self, question: str) -> str:
        # Select context
        selection = self.manager.select_context(question)
        
        # Build prompt
        prompt = self.manager.build_prompt_with_context(
            question, 
            selection['instructor_name']
        )
        
        # Get response
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are the {selection['instructor_name']}"},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

# Usage
assistant = SmartAssistant()
assistant.load_experts()
answer = assistant.answer("How do I optimize database queries?")
```

### Error Handling

```python
from stored_context_protocol import (
    ContextManager,
    ContextNotFoundError,
    InvalidFileFormatError,
    OpenAIError
)

try:
    manager = ContextManager()
    
    # Handle file loading errors
    try:
        manager.load_file("contexts/expert.pdf")  # Wrong format
    except InvalidFileFormatError as e:
        print(f"Invalid file format: {e}")
    
    # Handle context selection errors
    try:
        selection = manager.select_context("Question")
    except ContextNotFoundError as e:
        print(f"No contexts loaded: {e}")
    except OpenAIError as e:
        print(f"OpenAI API error: {e}")
        
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 📚 API Reference

### ContextManager

The main class for managing contexts.

#### Methods

- `__init__(openai_api_key=None, openai_base_url=None, openai_model=None)`: Initialize the manager
- `load_file(file_path, instructor_name=None, description=None)`: Load context from file
- `load_text(text, instructor_name, description=None)`: Load context from text
- `load_directory(directory_path, instructor_mapping=None)`: Load all contexts from directory
- `select_context(prompt)`: Select the most relevant context (synchronous)
- `select_context_async(prompt)`: Select the most relevant context (asynchronous)
- `build_prompt_with_context(prompt, instructor_name)`: Build complete prompt with context
- `get_all_instructors()`: Get list of all loaded instructors
- `get_context_count()`: Get number of loaded contexts
- `remove_context(instructor_name)`: Remove specific context
- `clear_contexts()`: Remove all contexts
- `export_contexts(output_path)`: Export contexts to JSON file

### Context

Represents a single context/instructor.

#### Properties

- `id`: Unique identifier
- `content`: The context text
- `instructor_name`: Name of the instructor
- `description`: Optional description
- `file_path`: Source file path (if loaded from file)
- `created_at`: Creation timestamp

### Exceptions

- `StoredContextProtocolError`: Base exception for all library errors
- `ContextNotFoundError`: Raised when requested context is not found
- `InvalidFileFormatError`: Raised when file format is not supported
- `OpenAIError`: Raised when OpenAI API calls fail

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=stored_context_protocol

# Run specific test file
pytest tests/test_context_manager.py
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repo
git clone https://github.com/QuitCool/stored-context-protocol.git
cd stored-context-protocol

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run code formatting
black stored_context_protocol

# Run linting
flake8 stored_context_protocol
```

## 📋 Requirements

- Python 3.7+
- openai >= 1.0.0
- python-dotenv >= 0.19.0

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with the OpenAI API
- Inspired by the need for intelligent context management in AI applications
- Thanks to all contributors and users of this library

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/QuitCool/stored-context-protocol/issues)
- **Discussions**: [GitHub Discussions](https://github.com/QuitCool/stored-context-protocol/discussions)
- **Email**: scp@olives.chat

---

Made with ❤️ by the Stored Context Protocol team