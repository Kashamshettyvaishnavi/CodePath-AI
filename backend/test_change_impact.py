
import requests

API_URL = "http://127.0.0.1:5000/api/change-impact"

payload = {
    "owner": "pallets",
    "repo": "flask",
    "changed_file": "src/flask/ctx.py",
}

try:
    response = requests.post(
        API_URL,
        json=payload,
        timeout=120,
    )

    print("Status Code:", response.status_code)
    result = response.json()

    if response.ok:
        print("Repository:", result["repository"])
        print("Changed File:", result["changed_file"])
        print("Files Analyzed:", result["files_analyzed"])
        print("Direct Dependents:")

        for file_path in result["direct_dependents"]:
            print(" -", file_path)

        print("\nIndirect Dependents:")

        for file_path in result["indirect_dependents"]:
            print(" -", file_path)

        print("\nTotal Affected:", result["total_affected"])
    else:
        print("Error:", result)

except requests.RequestException as error:
    print("Request failed:", error)
