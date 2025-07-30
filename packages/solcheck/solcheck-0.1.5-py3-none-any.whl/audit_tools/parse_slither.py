import subprocess
import json
from uuid import uuid4
from pathlib import Path
from audit_tools.parse_ast import detect_pragma_version, normalize_version, set_global_solc_version 

def run_slither_analysis(sol_file: str) -> list:
    output_path = f"/tmp/slither-out-{uuid4().hex}.json"
    source_code = Path(sol_file).read_text()
    pragma = detect_pragma_version(source_code)
    version = normalize_version(pragma)
    set_global_solc_version(version)

    result = subprocess.run(
        ["slither", sol_file, "--json", output_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if not Path(output_path).exists():
        print(f"[ERROR] Slither output JSON not found. STDERR:\n{result.stderr}")
        return []

    try:
        with open(output_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Reading Slither JSON failed: {e}")
        return []

    suggestions = []

    for issue in data.get("results", {}).get("detectors", []):
        name = issue.get("check", "Unknown")
        description = issue.get("description", "No description provided")
        elements = issue.get("elements", [])

        if not elements:
            suggestions.append({
                "title": name,
                "ok": False,
                "suggestion": description,
                "line": None,
                "what": None,
                "fix": f"Check `{name}` documentation for fix"
            })
            continue

        for element in elements:
            source_mapping = element.get("source_mapping", {})
            line = source_mapping.get("lines", [None])[0]
            code = element.get("name", "")

            suggestions.append({
                "title": name,
                "ok": False,
                "suggestion": description,
                "line": line,
                "what": code,
                "fix": f"Check `{name}` documentation for fix"
            })

    return suggestions
