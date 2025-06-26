from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai.foundation_models.inference import ModelInference

creds = {
    "apikey": "G4dKXBbv5Af6M9TChbIWOUnpexu2-LcGdo1vSK__QRhh",
    "url": "https://au-syd.ml.cloud.ibm.com"
}

client = APIClient(creds)
client.set.default_project("42f3c966-581c-474a-8846-c542e1545dcb")

model = ModelInference(
    model_id="ibm/granite-13b-instruct-v2",
    api_client=client
)

response = model.generate(prompt="Write a short Java program to print Hello World.")
print(response)
# print(response['results'][0]['generated_text'])
