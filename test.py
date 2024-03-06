import requests

# URL of the FastAPI endpoint
url = "http://localhost:8000/generate-diff/"

# Example payload containing repoUrl and prompt
payload = {
    "repoUrl": "https://github.com/jayhack/llm.sh",
    "prompt": "Also it might be great if the script detects which OS or shell I'm using and try to use the appropriate command e.g. dir instead of ls because I don't want to be adding windows after every prompt."
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

