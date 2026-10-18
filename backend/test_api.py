import requests

url = "http://127.0.0.1:5000/api/analyze"

payload = {
    "repo_url": "https://github.com/pallets/flask"
}

response = requests.post(url, json=payload, timeout=30)

print("Status Code:", response.status_code)

data = response.json()

if response.ok:
    print("Repository:", data["repository"])
    print("Python files found:", data["python_files_found"])

    print("\nFirst 10 Python files:")

    for file in data["python_files"][:10]:
        print(f"- {file['path']} ({file['size']} bytes)")
else:
    print("Error:", data.get("error"))