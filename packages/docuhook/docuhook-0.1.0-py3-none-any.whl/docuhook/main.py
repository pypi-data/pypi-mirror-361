import ast
import subprocess

from ai_client import generate_docstring
from code_analyzer import DocstringFinder


def extract_docstring_content(text_block: str) -> str | None:
    """
    Finds and extracts the content from the first complete docstring.

    This function returns only the text *inside* the triple quotes,
    with leading/trailing whitespace removed.

    Args:
        text_block (str): The string containing the docstring.

    Returns:
        str: The extracted text content from the docstring.
             Returns None if a complete docstring is not found.
    """
    try:
        # Find the starting position of the first """
        start_index = text_block.find('"""')
        if start_index == -1:
            return None

        # Find the starting position of the closing """, searching *after* the opening one
        end_index = text_block.find('"""', start_index + 3)
        if end_index == -1:
            return None

        # Extract the content between the quotes
        content = text_block[start_index + 3 : end_index]

        # Return the extracted content, removing any leading/trailing whitespace (like newlines)
        return content.strip()
    except Exception:
        return None


def main() -> None:
    # Uruchom komendę gita, aby pobrać listę 'staged' plików .py
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        check=True,
    )
    staged_files = [f for f in result.stdout.splitlines() if f.endswith(".py")]
    print(staged_files)

    for file in staged_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                code_content = f.read()
        except FileNotFoundError:
            raise f"Błąd: Plik nie został znaleziony pod ścieżką: {file}"

        finder = DocstringFinder()
        tree = ast.parse(code_content)
        finder.visit(tree)

        nodes_to_document = finder.undocumented_functions

        if nodes_to_document:

            nodes_to_document.sort(key=lambda node: node.lineno, reverse=True)
            with open(file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for node in nodes_to_document:
                function_code_string = ast.unparse(node)
                docstring_text = generate_docstring(code_to_document=ast.unparse(node))

                insert_pos = node.body[0].lineno - 1
                def_line = lines[node.lineno - 1]
                indentation = " " * (len(def_line) - len(def_line.lstrip())) + "    "
                formatted_docstring = f'{indentation}"""{docstring_text.strip()}"""\n'
                lines.insert(insert_pos, formatted_docstring)

        # Zapisz całą, zmodyfikowaną treść z powrotem do pliku
        with open(file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        subprocess.run(["git", "add", file])


if __name__ == "__main__":
    main()
