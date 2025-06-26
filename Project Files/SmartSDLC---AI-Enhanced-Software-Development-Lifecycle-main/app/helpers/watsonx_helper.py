from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai.foundation_models.inference import ModelInference
import os
load_dotenv()

API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
URL = os.getenv("WATSONX_URL")

client = APIClient({"apikey": API_KEY, "url": URL})
client.set.default_project(PROJECT_ID)

model = ModelInference(
    model_id="ibm/granite-8b-code-instruct",
    api_client=client
)
def generate_suggestion(prompt):
    return generate_code(prompt)



def generate_code(prompt):
    try:
        response = model.generate(prompt)
        return response.get("results", [{}])[0].get("generated_text", "")
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    prompt = (
        "Write a complete Python program that reads an integer from input, "
        "computes its factorial using a recursive function, and prints the result. "
        "Include comments explaining each step."
    )
    output = generate_code(prompt)
    print("Generated Output:\n", output)
