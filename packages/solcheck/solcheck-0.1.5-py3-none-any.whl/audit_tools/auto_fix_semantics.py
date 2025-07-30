import re
from pathlib import Path

def parse_markdown_report(report_path: str) -> list:
    fixes = []
    current = {}

    with open(report_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("- **"):
            if current:
                fixes.append(current)
            current = {
                "title": re.search(r"\*\*(.*?)\*\*", line).group(1),
                "ok": "✅" in line,
                "line": None,
                "what": None,
                "fix": None,
            }
        elif line.strip().startswith("- 👮 Suggested Fix:"):
            match = re.search(r"Line (\d+), change `(.*?)` ➔ `(.*?)`", line)
            if match:
                current["line"] = int(match.group(1))
                current["what"] = match.group(2)
                current["fix"] = match.group(3)
        elif line.strip().startswith("Change `"):
            match = re.search(r"Change `(.*?)` ➔ `(.*?)`", line)
            if match:
                current["what"] = match.group(1)
                current["fix"] = match.group(2)

    if current:
        fixes.append(current)

    return [f for f in fixes if not f["ok"] and f.get("fix")]

def apply_fixes_to_contract(contract_path: str, report_path: str, output_path: str = None):
    lines = Path(contract_path).read_text().splitlines()
    fixes = parse_markdown_report(report_path)

    for fix in fixes:
        if fix["line"] is not None and 1 <= fix["line"] <= len(lines):
            idx = fix["line"] - 1
            if fix["what"] in lines[idx]:
                lines[idx] = lines[idx].replace(fix["what"], fix["fix"])
        else:
            for i in range(len(lines)):
                if fix["what"] in lines[i]:
                    lines[i] = lines[i].replace(fix["what"], fix["fix"])

    result_code = "\n".join(lines)
    output_path = output_path or contract_path.replace(".sol", "_fixed.sol")
    Path(output_path).write_text(result_code)
    print(f"✅ Auto-fixed contract written to: {output_path}")
