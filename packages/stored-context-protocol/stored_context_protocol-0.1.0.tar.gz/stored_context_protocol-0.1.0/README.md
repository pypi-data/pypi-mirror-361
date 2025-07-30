# Stored Context Protocol (SCP)

A Python library for managing and intelligently retrieving contextual information using OpenAI's function calling capabilities. SCP allows you to store multiple contexts and automatically select the most relevant ones based on user queries.

## Features

- **Context Management**: Store and manage multiple contexts from text or files (.txt, .md)
- **Intelligent Selection**: Automatically select relevant contexts using OpenAI function calling
- **Scalable**: Support for 30+ contexts with configurable limits
- **Flexible Loading**: Load contexts from files or raw text
- **Thread-Safe**: Built-in thread safety for concurrent operations
- **Persistence**: Optional context persistence to disk
- **Customizable**: Configure OpenAI settings, models, and endpoints

## Installation

```bash
pip install stored-context-protocol
```

Or install from source:

```bash
git clone https://github.com/yourusername/stored-context-protocol
cd stored-context-protocol
pip install -e .
```

## Quick Start

```python
from stored_context_protocol import StoredContextProtocol

# Initialize with API key
scp = StoredContextProtocol(
    api_key="your-openai-api-key",  # or set OPENAI_API_KEY env var
    model="gpt-4-0125-preview"       # default model
)

# Load contexts from files
scp.load_file("instructions/math_tutor.md", instructor_name="Math Tutor")
scp.load_file("instructions/code_reviewer.txt", instructor_name="Code Reviewer")

# Load context from text
scp.load_text(
    text="You are a helpful writing assistant...",
    instructor_name="Writing Assistant",
    description="Helps with writing and editing tasks"
)

# Query with automatic context selection
result = scp.query_with_context("Help me solve this calculus problem")

print(result["response"])
print(f"Selected context: {result['selected_contexts']}")
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_BASE_URL`: Custom OpenAI endpoint (optional)

### Programmatic Configuration

```python
# Initialize with custom settings
scp = StoredContextProtocol(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4-0125-preview",
    max_contexts=100  # Maximum number of contexts to store
)

# Update settings after initialization
scp.set_model("gpt-3.5-turbo")
scp.set_api_key("new-api-key")
scp.set_base_url("https://custom-endpoint.com/v1")
```

## API Reference

### StoredContextProtocol

#### `load_file(file_path, instructor_name=None, description=None)`
Load context from a file (.txt or .md).

- `file_path`: Path to the file
- `instructor_name`: Optional name (defaults to filename)
- `description`: Optional description (auto-generated if not provided)

#### `load_text(text, instructor_name, description=None)`
Load context from text.

- `text`: The context text
- `instructor_name`: Required name for the context
- `description`: Optional description

#### `query_with_context(prompt, auto_select_context=True, context_ids=None, max_contexts_to_use=1)`
Query OpenAI with context selection.

- `prompt`: User's query
- `auto_select_context`: Whether to auto-select relevant contexts
- `context_ids`: Manual list of context IDs to use
- `max_contexts_to_use`: Maximum contexts for auto-selection

Returns a dictionary with:
- `response`: The OpenAI response
- `selected_contexts`: List of selected context metadata
- `full_prompt`: The complete prompt sent to OpenAI

#### `list_contexts()`
List all available contexts with their metadata.

#### `remove_context(context_id)`
Remove a specific context by ID.

#### `clear_all_contexts()`
Remove all stored contexts.

## Advanced Usage

### Manual Context Selection

```python
# Get all available contexts
contexts = scp.list_contexts()

# Query with specific contexts
result = scp.query_with_context(
    prompt="Explain this code",
    auto_select_context=False,
    context_ids=["context_id_1", "context_id_2"]
)
```

### Context Persistence

```python
# Enable persistence
scp = StoredContextProtocol(
    api_key="your-api-key",
    persist_file="contexts.json"
)
```

### Multiple Context Selection

```python
# Select up to 3 relevant contexts
result = scp.query_with_context(
    prompt="Help me with math and coding",
    max_contexts_to_use=3
)
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.