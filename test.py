import requests

# URL of the FastAPI endpoint
url = "http://localhost:8000/generate-diff/"

# Example payload containing repoUrl and prompt
payload = {
    "repoUrl": "https://github.com/saarthg/PDF-Chatbot",
    "prompt": "Can you change the app.py file so that the title is something different"
}

# Send POST request to the FastAPI endpoint
response = requests.post(url, json=payload)

# Check response status code
if response.status_code == 200:
    # Print the response content
    data = response.json()
    print("Original Diff:")
    print(data["original_diff"])
    print("\nReflection Diff:")
    print(data["reflection_diff"])
else:
    print(f"Error: {response.status_code} - {response.text}")

