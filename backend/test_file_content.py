
import requests

url = "http://127.0.0.1:5000/api/file-content"

payload = {
    "owner": "pallets",
    "repo": "flask",
    "file_path": "src/flask/__init__.py"
}

response = requests.post(url, json=payload, timeout=30)

print("Status Code:", response.status_code)

data = response.json()

if response.ok:
    print("Repository:", data["repository"])
    print("File:", data["file_path"])
    print("\nFirst 500 characters of source code:\n")
    print(data["content"][:500])
else:
    print("Error:", data.get("error"))