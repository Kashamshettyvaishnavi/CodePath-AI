import requests

url = "http://127.0.0.1:5000/api/analyze-file"

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

    print("\nImports:")
    for item in data["imports"][:10]:
        print(item)

    print("\nFunctions:")
    for function in data["functions"][:10]:
        print(function)

    print("\nClasses:")
    for cls in data["classes"][:10]:
        print(cls)
else:
    print("Error:", data.get("error"))