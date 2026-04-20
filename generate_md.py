import json
import urllib.request
import os

def generate():
    url = "http://localhost:8000/openapi.json"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching openapi.json: {e}")
        return

    md = []
    md.append("# Financial ROI Intelligence System")
    md.append("## Current Project Status & API Documentation")
    md.append("\n---\n")

    md.append("### 1. Executive Summary")
    desc = data.get("info", {}).get("description", "Financial ROI Intelligence System API")
    md.append(desc)
    md.append("\n")

    md.append("### 2. Component Architecture Overview")
    md.append("- **Backend Framework**: FastAPI (Running & Accessible)")
    md.append("- **Database Driver**: PostgreSQL with asyncpg & SQLAlchemy")
    md.append("- **Agentic Logic**: CrewAI integration fixed and operational")
    md.append("- **Endpoints**: Full API standard routes accessible via Swagger UI (`/docs`)")
    md.append("\n")

    md.append("### 3. Developed API Endpoints\n")
    
    paths = data.get("paths", {})
    if not paths:
        md.append("*No endpoints discovered or documented yet.*")
    else:
        for path, methods in paths.items():
            for method, details in methods.items():
                summary = details.get("summary", "No summary provided.")
                method_upper = method.upper()
                md.append(f"**`{method_upper}`** `{path}`")
                md.append(f"> {summary}\n")

    with open("Project_API_Status_Report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    
    print("Markdown file generated: Project_API_Status_Report.md")

if __name__ == '__main__':
    generate()
