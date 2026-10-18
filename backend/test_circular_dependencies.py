
import requests

API_URL = "http://127.0.0.1:5000/api/circular-dependencies"

payload = {
    "owner": "pallets",
    "repo": "flask"
}

try:
    response = requests.post(API_URL, json=payload, timeout=120)

    print("Status Code:", response.status_code)

    result = response.json()

    if response.ok:
        print("Repository:", result["repository"])
        print("Files Analyzed:", result["files_analyzed"])
        print("Cycles Found:", result["cycles_found"])

        print("Circular Dependency Groups:", result["groups_found"])

        print("\nDependency Groups:")

        for index, group in enumerate(
            result["circular_dependency_groups"], start=1
        ):
            print(f"\nGroup {index}:")
            for file_path in group:
                print(f"  - {file_path}")

        if result["circular_dependencies"]:
            print(f"\nShowing {len(result['circular_dependencies'])} ""bounded cycle examples.")
        else:
            print("\nNo circular dependencies detected in the analyzed graph.")
    else:
        print("\nNo cycle examples found.")

except requests.RequestException as error:
    print("Request failed:", error)
