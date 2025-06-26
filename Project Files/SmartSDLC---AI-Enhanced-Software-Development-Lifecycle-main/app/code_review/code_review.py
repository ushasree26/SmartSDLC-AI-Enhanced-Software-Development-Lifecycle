# code_review.py

from transformers import pipeline
from datetime import datetime
import os

# Load the pre-trained classification model
try:
    review_pipeline = pipeline("text-classification", model="sshleifer/distilbart-cnn-12-6")
except Exception as e:
    print(f"Failed to load model: {e}")
    review_pipeline = None

def analyze_code(file_path):
    issues = []

    if review_pipeline is None:
        return [{"error": "Model loading failed. Please check the model name or your internet connection."}]

    if not os.path.exists(file_path):
        return [{"error": "File not found!"}]

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if not line.strip():
            continue  # skip empty lines

        try:
            result = review_pipeline(line[:512])  # truncate to avoid model overload

            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                label = result[0].get('label', 'Unknown')
                score = result[0].get('score', 0.0)
            else:
                label = "Unclassified"
                score = 0.0

        except Exception as e:
            issues.append({
                "line": i + 1,
                "code": line.strip(),
                "label": "Error",
                "confidence": 0.0,
                "severity": "High",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "error": str(e)
            })
            continue

        # Determine severity
        if score > 0.85:
            severity = "High"
        elif score > 0.6:
            severity = "Medium"
        else:
            severity = "Low"

        issues.append({
            "line": i + 1,
            "code": line.strip(),
            "label": label,
            "confidence": round(score, 2),
            "severity": severity,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return issues
