import os
import sys

import requests

API_KEY = os.getenv("GROQ_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"


def generate_docstring(code_to_document: str) -> str:
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    prompt_instruction = """
    Your sole task is to process the Python code below.
1. Generate a complete, Google-style docstring for the provided function.
2. Return only the new docstring as raw text
3. Don't include anything like: Here is the Google-style docstring for the provided function
"""

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
        "temperature": 0.1,  # Niska temperatura dla zadań związanych z kodem
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Błąd API: {response.status_code} - {response.text}"


# if __name__ == "__main__":
#     if not API_KEY:
#         print("Error: Set the GROQ_API_KEY environment variable with your API key.")
#         sys.exit(1)

#     # if len(sys.argv) < 2:
#     #     print("Usage: python script_name.py <path_to_script_file>")
#     #     sys.exit(1)

#     # file_path = sys.argv[1]

#     function_string = """
# def get_ai_suggestion(file_path, prompt_instruction):

#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             code_content = f.read()
#     except FileNotFoundError:
#         return f"Błąd: Plik nie został znaleziony pod ścieżką: {file_path}"

#     headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

#     payload = {
#         "model": "llama3-8b-8192",
#         "messages": [
#             {
#                 "role": "system",
#                 "content": "Jesteś światowej klasy ekspertem od programowania w Pythonie. Twoim zadaniem jest pomagać deweloperom, analizując ich kod i dostarczając konkretnych, wysokiej jakości odpowiedzi.",
#             },
#             {
#                 "role": "user",
#                 "content": f"{prompt_instruction}:\n\n```python\n{code_content}\n```",
#             },
#         ],
#         "temperature": 0.1,  # Niska temperatura dla zadań związanych z kodem
#     }

#     response = requests.post(API_URL, headers=headers, json=payload)

#     if response.status_code == 200:
#         return response.json()["choices"][0]["message"]["content"]
#     else:
#         return f"Błąd API: {response.status_code} - {response.text}"

# """

#     output = generate_docstring(function_string)
#     print(output)
