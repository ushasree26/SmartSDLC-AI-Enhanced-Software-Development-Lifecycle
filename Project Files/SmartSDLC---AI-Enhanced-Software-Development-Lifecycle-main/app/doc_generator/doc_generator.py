# doc_generator.py

import ast
from datetime import datetime
from transformers import pipeline

# Load Hugging Face summarization pipeline (once)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


def summarize_code(code_snippet):
    try:
        input_len = len(code_snippet.split())  # count words
        # Set max_length smaller than input length to avoid warnings
        max_len = min(50, max(10, input_len // 2))
        result = summarizer(code_snippet[:1024], max_length=max_len, min_length=10, do_sample=False)
        return result[0]['summary_text']
    except Exception as e:
        return f"Summary error: {str(e)}"


def generate_doc(file_path):
    docs = []

    try:
        with open(file_path, "r") as f:
            source = f.read()

        tree = ast.parse(source)
        lines = source.splitlines()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # Extract code lines for this block
                start_line = node.lineno - 1
                end_line = getattr(node, 'end_lineno', start_line + 10)
                code_snippet = "\n".join(lines[start_line:end_line])

                summary = summarize_code(code_snippet)

                docs.append({
                    "type": "Function" if isinstance(node, ast.FunctionDef) else "Class",
                    "name": node.name,
                    "line": node.lineno,
                    "summary": summary,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

    except Exception as e:
        docs.append({
            "type": "Error",
            "name": "N/A",
            "line": 0,
            "summary": f"Error: {str(e)}",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return docs
