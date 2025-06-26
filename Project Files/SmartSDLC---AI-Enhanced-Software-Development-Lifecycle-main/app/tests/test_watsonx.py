from helpers.watsonx_helper import generate_suggestion

prompt = "Write a Python program that prints 'Hello, World!'"

output = generate_suggestion(prompt)

print("Generated Output:\n", output)
