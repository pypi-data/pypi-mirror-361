from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import os
import re

client = None

def get_openai_client(api_key: str = None) -> OpenAI:
    global client
    if client is None:
        client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    return client    

def build_fix_prompt(solidity_file_path: str, markdown_report_path: str) -> str:
    source_code = Path(solidity_file_path).read_text()
    report_md = Path(markdown_report_path).read_text()

    prompt = f"""
You are a Solidity security assistant. You will receive a Solidity smart contract and an audit report in Markdown format.

Your task is to automatically apply the suggested fixes in the report to the Solidity contract.
- Do not change anything that is not mentioned in the report.
- Do not rename variables or functions unless explicitly asked.
- Preserve formatting, comments, and SPDX license header.

❗ Do not add explanations, comments, or modify logic unless directly specified in the report.
❗ Return **only** the updated Solidity code, no markdown, no bullet points, no commentary.

## Solidity Contract
```solidity
{source_code}
```

## Audit Report (Markdown)
{report_md}

Return ONLY the corrected Solidity code.
"""
    return prompt

def strip_solidity_fence(text: str) -> str:
    return re.sub(r"```solidity\n(.*?)```", r"\1", text, flags=re.DOTALL)

def generate_fixed_contract(solidity_file_path: str, markdown_report_path: str, output_path: str = None) -> None:
    client = get_openai_client()
    prompt = build_fix_prompt(solidity_file_path, markdown_report_path)
    
    fixed_code = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=5000,
        temperature=0.2 
    ).choices[0].message.content.strip()

    fixed_code = strip_solidity_fence(fixed_code)

    output_file = output_path or solidity_file_path.replace(".sol", "_fixed.sol")
    Path(output_file).write_text(fixed_code)
    print(f"✅ Auto-fixed contract written to: {output_file}")