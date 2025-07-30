import json
import re
import subprocess
import shutil
from pathlib import Path
from solcx import install_solc, set_solc_version, compile_standard

def detect_pragma_version(source_code: str) -> str:
    match = re.search(r'pragma solidity\s+([^;]+);', source_code)
    if not match:
        raise RuntimeError("No pragma version found in contract.")
    return match.group(1).strip()

def normalize_version(version_str: str) -> str:
    if version_str.startswith("^"):
        return version_str[1:]
    elif ">=" in version_str:
        return version_str.split()[0].replace(">=", "")
    elif version_str.startswith("~"):
        return version_str[1:]
    return version_str


def set_global_solc_version(version: str):
    if shutil.which("solc-select") is None:
        print("[WARN] solc-select not found. Slither may use the wrong solc version.")
        return

    try:
        subprocess.run(["solc-select", "install", version], check=False)
        subprocess.run(["solc-select", "use", version], check=True)
        print(f"[INFO] solc-select set global solc version to {version}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"[ERROR] Failed to switch solc version via solc-select: {e}")

def extract_ast(sol_file_path: str) -> dict:
    sol_file_path = Path(sol_file_path).resolve()
    source = sol_file_path.read_text()

    pragma = detect_pragma_version(source)
    version = normalize_version(pragma)
    print(f"[INFO] Detected pragma: {pragma} → using solc version {version}")

    try:
        install_solc(version)
        set_solc_version(version)
    except Exception as e:
        raise RuntimeError(f"Failed to install/set solc version {version}: {e}")
    
    result = compile_standard({
        "language": "Solidity",
        "sources": {
            sol_file_path.name: {
                "content": source
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [],
                    "": ["ast"]
                }
            }
        }
    })

    try:
        ast = result["sources"][sol_file_path.name]["ast"]
        return ast
    except KeyError:
        raise RuntimeError("Failed to extract AST from compile result.")

def extract_functions(ast_node: dict) -> list:
    functions = []

    def recurse(node):
        if isinstance(node, dict):
            if node.get("nodeType") == "FunctionDefinition":
                src = node.get("src", "")
                line = int(src.split(":")[0]) if src else None

                inputs = []
                for param in node.get("parameters", {}).get("parameters", []):
                    inputs.append(param.get("typeDescriptions", {}).get("typeString", ""))

                functions.append({
                    "name": node.get("name", "(constructor or fallback)"),
                    "visibility": node.get("visibility", "default"),
                    "stateMutability": node.get("stateMutability", "nonpayable"),
                    "inputs": inputs,
                    "line": line,
                    "src": src
                })
            for child in node.values():
                recurse(child)
        elif isinstance(node, list):
            for item in node:
                recurse(item)

    recurse(ast_node)
    return functions

def extract_state_variables(ast_node: dict) -> list:
    variables = []

    def recurse(node):
        if isinstance(node, dict):
            if node.get("nodeType") == "VariableDeclaration" and node.get("stateVariable"):
                src = node.get("src", "")
                line = int(src.split(":")[0]) if src else None

                variables.append({
                    "name": node.get("name"),
                    "type": node.get("typeDescriptions", {}).get("typeString", ""),
                    "visibility": node.get("visibility", "default"),
                    "line": line,
                    "src": src
                })
            for child in node.values():
                recurse(child)
        elif isinstance(node, list):
            for item in node:
                recurse(item)

    recurse(ast_node)
    return variables
