# DocuHook 🤖

> [!NOTE]
> DocuHook is a pre-commit hook that automatically generates docstrings for your Python code using AI.

## Key Features

*   **Automatic Docstring Generation:** Forget about writing docstrings manually. DocuHook does it for you with every commit.
*   **Seamless Git Integration:** Works in the background as a pre-commit hook without changing your natural workflow.
*   **Support for Fast AI Models:** Configured to work with the fastest models (e.g., Groq, Claude Haiku) to avoid slowing down your work.
*   **Smart Code Analysis:** Uses the `ast` module to precisely find functions that require documentation.

## Installation

To get started, install the package using `pip`:

```bash
pip install docuhook
```

## Usage

To enable DocuHook in your project, follow these 3 simple steps:

### 1. Configure pre-commit

In your `.pre-commit-config.yaml` file, add the following entry:

```yaml
repos:
  - repo: https://github.com/bartoszborowski/docuhook
    rev: v0.1.0
    hooks:
      - id: docuhook
```

### 2. Install the hook

Run the following command to have `pre-commit` activate the hook in your repository:

```bash
pre-commit install
```

### 3. Set the API Key

DocuHook needs an API key to communicate with the language model. Set it as an environment variable. For example, for Groq:

```bash
export GROQ_API_KEY="sk-..."
```

Done! From now on, with every `git commit`, DocuHook will automatically analyze your code and add any missing docstrings.

## Configuration

To use a different language model, you need to update the API endpoint and the request payload in the `docuhook/ai_client.py` file.

Specifically, you will need to modify the `API_URL` variable and the `payload` dictionary inside the `generate_docstring` function.

Here is the relevant code snippet from `docuhook/ai_client.py`:

```python
# docuhook/ai_client.py

import os
import requests

# Ensure you have the correct environment variable for your API key
API_KEY = os.getenv("YOUR_API_KEY") 

# 1. Change this URL to your provider's API endpoint
API_URL = "https://api.groq.com/openai/v1/chat/completions"


def generate_docstring(code_to_document: str) -> str:
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    prompt_instruction = """
    Your sole task is to process the Python code below.
1. Generate a complete, Google-style docstring for the provided function.
2. Return only the new docstring as raw text
3. Don't include anything like: Here is the Google-style docstring for the provided function
"""
    # 2. Adjust the payload to match the new API's requirements
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert in writing clean Python code. Your task is to generate documentation in the Google Style Docstrings format. Documentation has to be written in English",
            },
            {
                "role": "user",
                "content": f"{prompt_instruction}:\n\n```python\n{code_to_document}\n```",
            },
        ],
        "temperature": 0.1,
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"API Error: {response.status_code} - {response.text}"
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.