import ast
import os
import sys
import json
import re
from openai import OpenAI
from forgen.tool.node import InputPhase, OutputPhase
from forgen.tool.gen.phase import GenerativePhase
from forgen.tool.gen.tool import GenerativeTool

DOCSTRING_SYSTEM_PROMPT = """You are a helpful Python assistant that generates clean, concise docstrings for functions and methods.

You must return ONLY a valid JSON object with the following structure:
{
    "docstring": "The docstring content here",
    "function_signature": "The function signature (def function_name(args):)"
}

Do NOT include any markdown formatting, code blocks, or additional text outside the JSON response."""

DOCSTRING_USER_PROMPT_TEMPLATE = """
Generate or improve the docstring for the following Python function following Google style docstring format.

Function code:
{code_snippet}

Requirements:
- Return ONLY valid JSON with "docstring" and "function_signature" fields
- The docstring should be clean and properly formatted
- Do NOT include triple quotes in the docstring field
- Do NOT include any markdown formatting or code blocks
- Follow Google style docstring conventions
- Include Args, Returns, and Raises sections as appropriate

Example JSON format:
{{"docstring": "Brief description.\\n\\nArgs:\\n    param1 (type): Description.\\n\\nReturns:\\n    type: Description.", "function_signature": "def example_function(param1):"}}
"""


def clean_json_response(response_text):
    """Clean and extract JSON from LLM response."""
    # Remove markdown code blocks if present
    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*$', '', response_text)

    # Remove any leading/trailing whitespace
    response_text = response_text.strip()

    # Try to find JSON object in the response
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(0)

    return response_text


def build_docstring_tool(openai_key=None):
    def structured_prompt_fn(input_data):
        return DOCSTRING_USER_PROMPT_TEMPLATE.format(**input_data)

    def generation_function(input_data, openai_client=None):
        from forgen.llm.openai_interface.interface import get_chat_completions_response

        user_prompt = structured_prompt_fn(input_data)

        result = get_chat_completions_response(
            message_history=[],
            system_content=DOCSTRING_SYSTEM_PROMPT,
            user_content=user_prompt,
            ai_client=OpenAI(api_key=openai_key) if isinstance(openai_key, str) else openai_client,
            json_response=True  # ✅ Enable JSON mode
        )

        # Clean and parse JSON response
        try:

            # Extract docstring and ensure it's properly formatted
            docstring = result.get("docstring", "").strip()
            function_signature = result.get("function_signature", "").strip()

            # Ensure docstring doesn't have triple quotes
            docstring = docstring.replace('"""', '').replace("'''", '')

            return {"docstring": docstring, "function_signature": function_signature}

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {result}")
            # Fallback to empty docstring
            return {"docstring": "", "function_signature": ""}

    input_schema = {"code_snippet": str}
    output_schema = {"docstring": str, "function_signature": str}

    input_phase = InputPhase(
        input_schema=input_schema,
        output_schema=input_schema,
        code=lambda input_data: input_data  # ✅ Returns dict
    )

    generative_phase = GenerativePhase(
        generative_function=generation_function,
        input_schema=input_schema,
        output_schema=output_schema
    )

    output_phase = OutputPhase(
        input_schema=output_schema,
        output_schema=output_schema,
        code=lambda output_data: output_data  # ✅ Returns dict
    )

    return GenerativeTool(
        input_phase=input_phase,
        generative_phase=generative_phase,
        output_phase=output_phase,
        input_schema=input_schema,
        output_schema=output_schema,
        name="FunctionDocstringGenerator",
        description="Generates or cleans docstrings for Python functions."
    )


def extract_function_code(node, source_lines):
    """Extract function code as string from AST node with better accuracy."""
    try:
        # Get the line range for the function
        start_line = node.lineno - 1  # Convert to 0-based indexing
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1

        # Extract the actual source code
        if end_line <= len(source_lines):
            function_lines = source_lines[start_line:end_line]
            return '\n'.join(function_lines)
        else:
            # Fallback to reconstructed version
            return reconstruct_function_signature(node)
    except:
        return reconstruct_function_signature(node)


def reconstruct_function_signature(node):
    """Reconstruct function signature from AST node."""
    lines = []

    # Function signature
    if isinstance(node, ast.AsyncFunctionDef):
        lines.append(f"async def {node.name}(")
    else:
        lines.append(f"def {node.name}(")

    # Arguments
    args = []
    for arg in node.args.args:
        args.append(arg.arg)
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")

    lines[0] += ", ".join(args) + "):"

    # Body (simplified - just get first few lines or existing docstring)
    if node.body:
        first_stmt = node.body[0]
        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, (ast.Str, ast.Constant)):
            # Has existing docstring
            if isinstance(first_stmt.value, ast.Str):
                existing_docstring = first_stmt.value.s
            else:
                existing_docstring = first_stmt.value.value
            lines.append(f'    """{existing_docstring}"""')
        else:
            lines.append("    pass")
    else:
        lines.append("    pass")

    return "\n".join(lines)


def create_function_with_docstring(function_signature, docstring):
    """Create a properly formatted function with docstring."""
    if not docstring.strip():
        return function_signature

    # Split signature and add docstring
    lines = function_signature.split('\n')
    signature_line = lines[0]

    # Create the function with proper docstring formatting
    result_lines = [signature_line]
    result_lines.append(f'    """')

    # Add docstring content with proper indentation
    for line in docstring.split('\n'):
        if line.strip():
            result_lines.append(f'    {line}')
        else:
            result_lines.append('')

    result_lines.append(f'    """')
    result_lines.append('    pass')

    return '\n'.join(result_lines)


def update_function_in_source(source_code, original_func_code, updated_func_code):
    """Replace function in source code with improved matching."""
    # Try exact match first
    if original_func_code.strip() in source_code:
        return source_code.replace(original_func_code.strip(), updated_func_code.strip())

    # Try to match just the function signature for partial replacement
    original_lines = original_func_code.split('\n')
    if original_lines:
        signature_line = original_lines[0].strip()
        # Find the signature in source and replace the whole function
        # This is a simplified approach - in production you'd want more robust AST manipulation
        return source_code.replace(original_func_code.strip(), updated_func_code.strip())

    return source_code


def run_docstring_generator(directory: str, openai_key=None):
    """Generate or clean docstrings for all Python functions in directory."""
    tool = build_docstring_tool(openai_key)
    updated_files = []

    for root, dirs, files in os.walk(directory):
        dirs[:] = [
            d for d in dirs
            if not d.startswith('.')
               and d not in {'__pycache__', 'venv', '.venv', 'dist', 'build'}
        ]

        # Only process directories with __init__.py (Python packages)
        if '__init__.py' not in files:
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        original_code = f.read()

                    # Parse the AST
                    try:
                        parsed = ast.parse(original_code)
                    except SyntaxError as e:
                        print(f"Syntax error in {file_path}: {e}")
                        continue

                    modified = False
                    updated_code = original_code
                    source_lines = original_code.split('\n')

                    # Find all function definitions
                    for node in ast.walk(parsed):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            # Extract function code
                            func_code = extract_function_code(node, source_lines)

                            print(f"  Processing function: {node.name}")

                            # Generate improved docstring
                            result = tool.execute({"code_snippet": func_code})
                            docstring = result.get("docstring", "").strip()
                            function_signature = result.get("function_signature", "").strip()

                            if docstring:
                                # Create the updated function with proper docstring
                                updated_snippet = create_function_with_docstring(
                                    function_signature or func_code.split('\n')[0] + ':',
                                    docstring
                                )

                                if updated_snippet and updated_snippet.strip() != func_code.strip():
                                    updated_code = update_function_in_source(
                                        updated_code, func_code, updated_snippet
                                    )
                                    modified = True
                                    print(f"    Added/updated docstring for {node.name}")

                    # Write back if modified
                    if modified:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(updated_code)
                        updated_files.append(file_path)
                        print(f"  Updated: {file_path}")

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    return updated_files