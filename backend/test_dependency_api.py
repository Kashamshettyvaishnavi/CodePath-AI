
import requests

url = "http://127.0.0.1:5000/api/dependency-graph"

payload = {
    "owner": "pallets",
    "repo": "flask"
}

response = requests.post(url, json=payload, timeout=120)

print("Status Code:", response.status_code)

data = response.json()

if response.ok:
    print("Repository:", data["repository"])
    print("Files analyzed:", data["files_analyzed"])
    print("Dependencies found:", data["dependencies_found"])

    print("\nFirst 10 nodes:")
    for node in data["nodes"][:10]:
        print(node)
    print("\nAll analyzed file paths:")
    for node in data["nodes"]:
        print(node["id"])

    print("\nAll detected edges:")
    print(data["edges"])
    print("\nFirst 10 edges:")
    for edge in data["edges"][:10]:
        print(edge)
else:
    print("Error:", data.get("error"))
