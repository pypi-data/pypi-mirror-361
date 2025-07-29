import sys
from requests import get

"""
PyPI Package Info Fetcher

This script fetches metadata about a Python package from the Python Package Index (PyPI) given the package name 
as a command-line argument. It prints key details like author email, classifiers, URLs, version, license, 
download links, and the last serial number. 

You can optionally add the `--json` flag to print the complete raw JSON response from the PyPI API.

Usage:
    python main.py <package_name> [--json]

Arguments:
    <package_name>  Required. The name of the PyPI package to query.
    --json          Optional. If present, prints the full JSON response instead of the parsed fields.

Examples:
    python main.py requests
    python main.py django --json

Exits with status code 1 if the package name is missing or if the PyPI API request fails.
"""

# Step 1: Get a package name
def main():
    """
    Main function to handle command-line arguments, fetch package data from PyPI, and display results.

    Steps:
    1. Parse command-line arguments to get the package name.
    2. Send a GET request to the PyPI API endpoint for the package JSON data.
    3. If the request fails, exit with an error message.
    4. If the ` -- JSON ` flag is present in arguments, print a raw JSON response and exit.
    5. Otherwise, extract and print relevant metadata fields:
        - author_email
        - classifiers
        - package_url
        - project_url
        - version
        - license
        - download_url (list of tuples with URL and filename)
        - last_serial

    Prints usage errors and exits with status 1 if required arguments are missing or invalid.
    """

    if len(sys.argv) > 1:
        name = sys.argv[1]
        print(f"{name}!")
    else:
        print("Please provide a package name as an argument.")
        sys.exit(1)

    # Step 2: Fetch data from PyPI
    response = get(f"https://pypi.org/pypi/{name}/json")


    if response.status_code != 200:
        print(f"Error: Unable to fetch data for {name}. Status code: {response.status_code}")
        sys.exit(1)


    data = response.json()

    if "--json" in sys.argv:
        print(data)
        sys.exit(0)
    # Step 3: Extract relevant fields
    info = data.get('info', {})
    last_serial = data.get('last_serial', 'N/A')
    urls = data.get('urls', [])

    author_email = info.get('author_email', 'N/A')
    classifiers = info.get('classifiers', [])
    package_url = info.get('package_url', 'N/A')
    project_url = info.get('project_url', 'N/A')
    version = info.get('version', 'N/A')
    license_ = info.get('license', 'N/A')

    # Step 4: Extract download URLs
    download_url = [(url['url'], url['filename']) for url in urls] if urls else []

    # Step 5: Print the output
    print(
        f"author_email: {author_email}",
        f"classifiers: {classifiers}",
        f"package_url: {package_url}",
        f"project_url: {project_url}",
        f"version: {version}",
        f"license: {license_}",
        f"download_url: {download_url}",
        f"last_serial: {last_serial}",
        sep="\n"
    )
    sys.exit(0)

if __name__ == "__main__":
    main()
# This script fetches package information from PyPI and prints relevant details.