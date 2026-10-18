
import requests

url = "http://127.0.0.1:5000/api/repository-summary"

payload = {
    "owner": "pallets",
    "repo": "flask"
}

try:
    response = requests.post(url, json=payload, timeout=180)

    print("Status Code:", response.status_code)

    result = response.json()

    if response.ok:
        print("\nRepository:", result["repository"])
        print("\nOverview:", result["overview"])
        print("\nStatistics:", result["statistics"])
        print("\nDetected libraries:", result["detected_libraries"])
        print("\nImport Categories:")

        for category, modules in result.get("import_categories", {}).items():
            print(f"\n{category.replace('_', ' ').title()}:")

            for module in modules[:10]:
                print(f"  {module['name']}: {module['count']}")
        print("\nMain file candidates:", result["main_file_candidates"])
        print("\nFolders:", result["folders"][:5])
        print("\nFirst file summary:")
        if result["file_summaries"]:
            print(result["file_summaries"][0])
    else:
        print("Error:", result)

except requests.RequestException as error:
    print("Request failed:", error)
