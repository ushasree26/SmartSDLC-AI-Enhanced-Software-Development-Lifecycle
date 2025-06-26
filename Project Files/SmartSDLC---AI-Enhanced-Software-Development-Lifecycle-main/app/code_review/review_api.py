from transformers import pipeline

# Load Hugging Face model for code classification
review_model = pipeline("text-classification", model="microsoft/codebert-base")

def review_code(code_snippet: str):
    result = review_model(code_snippet)
    return {
        "review": result
    }