import joblib
import re
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

# Try loading model and vectorizer if they exist
model_path = "models/bug_model.pkl"
vectorizer_path = "models/tfidf_vectorizer.pkl"

model, vectorizer = None, None
if os.path.exists(model_path) and os.path.exists(vectorizer_path):
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

def clean_code(code):
    return re.sub(r'\s+', ' ', code.strip())

def predict_bug(code_snippet):
    try:
        code = clean_code(code_snippet)

        if model and vectorizer:
            vector = vectorizer.transform([code])
            prediction = model.predict(vector)[0]
            prob = model.predict_proba(vector)[0]

            return {
                "is_buggy": bool(prediction),
                "probability": round(float(max(prob)), 2),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "suggestion": "Consider refactoring or reviewing logic." if prediction else "Looks clean."
            }
        else:
            # Fallback: Rule-based detection
            buggy_patterns = [r"\b01\b", r"==\s*None", r"==\s*True"]
            is_buggy = any(re.search(pat, code) for pat in buggy_patterns)

            return {
                "is_buggy": is_buggy,
                "probability": 0.91 if is_buggy else 0.03,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "suggestion": "Avoid using 01 or poor comparisons." if is_buggy else "Looks clean."
            }

    except Exception as e:
        return {"error": str(e)}
