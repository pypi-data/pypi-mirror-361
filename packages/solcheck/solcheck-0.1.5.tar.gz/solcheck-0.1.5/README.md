# Solcheck | Solidity Contract Audit Tools

These tools are meant for Hackaton-BI, but it can be further enhanced depends on the needs, this tools use 2 type of check semantic using SMT and Slither analyzer. Both of these tools working hand in hand to generate a report in .md format for it to be easier to check if there is any vunerbility. There is also auto fix features that I implement using OpenAI API, but you need to feed it your own api key, for now I'm using the 4.0 model, but later on I will make it customizeable to change the model version either to latest version or earlier version like 3.5, the auto fix works by fethcing the report file that already been generated from the tools

## How to use (in script)

```python
from audit_tools.cli_input import run_static_analysis
from audit_tools.cli_input import write_markdown_report
import audit_tools.auto_fix as auto_fix
import os
from dotenv import load_dotenv

load_dotenv()
auto_fix.get_openai_client(os.getenv("OPENAI_API_KEY"))
sol_file = "/contracts/SimpleEscrow.sol"
output_path = "results/reports"

functions, variables, invariant_results, slither_issues = run_static_analysis(sol_file)
write_markdown_report(sol_file, functions, variables, invariant_results, slither_issues, output_path)
```

## How to use (cli tools)

I've proided a cli tools for the github repo version if you want to tinker more with the tools

```bash
python cli_input.py 
    contracts/SimpleEscrow.sol 
    results/report.md -
    -fix y 
    --output fixed/SimpleEscrow_fixed.sol
```

I'll be adding a multiple file audit into this tools later on, so that it can detect all the sol file in a single directory and then check all of them and generate the appropriate reports and auto-fix if its enabled
