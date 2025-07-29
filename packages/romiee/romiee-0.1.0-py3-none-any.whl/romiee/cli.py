import os

def run():
    print("📦 Welcome to romiee setup!")
    project_name = input("🔹 Project name (default: my_scraper): ") or "my_scraper"
    url = input("🔹 URL to scrape (default: https://example.com): ") or "https://example.com"

    os.makedirs(project_name, exist_ok=True)

    with open(f"{project_name}/main.py", "w") as f:
        f.write(f"""from romiee import fetch_html, extract_title

html = fetch_html("{url}")
print("Title:", extract_title(html))
""")
    print(f"\n✅ Project folder '{project_name}' created successfully!")
