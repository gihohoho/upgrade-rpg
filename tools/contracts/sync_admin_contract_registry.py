from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend/app/services/admin_service_split_contract.py"
FRONTEND = ROOT / "src/api/admin-page-readonly.js"
REGISTRY = ROOT / "docs/contracts/admin-contract-registry.json"


def load_backend_contract() -> dict:
    tree = ast.parse(BACKEND.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "ADMIN_SERVICE_SPLIT_CONTRACT":
            return ast.literal_eval(node.value)
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ADMIN_SERVICE_SPLIT_CONTRACT" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("ADMIN_SERVICE_SPLIT_CONTRACT not found")


def js_array(values: list[str], indent: str = "    ") -> str:
    return "[\n" + "\n".join(f'{indent}  {json.dumps(v, ensure_ascii=False)},' for v in values) + f"\n{indent}]"


def replace_array(source: str, key: str, values: list[str]) -> str:
    pattern = re.compile(rf"({re.escape(key)}:\s*)\[(.*?)\](,\s*\n\s*[A-Za-z])", re.S)
    match = pattern.search(source)
    if not match:
        raise RuntimeError(f"frontend array not found: {key}")
    replacement = match.group(1) + js_array(values) + match.group(3)
    return source[:match.start()] + replacement + source[match.end():]


def main(*, check: bool = False) -> None:
    contract = load_backend_contract()
    registry = {
        "version": contract.get("version"),
        "splitStatus": contract.get("splitStatus"),
        "extractedFiles": contract.get("extractedFiles", []),
        "routeContract": contract.get("routeContract", []),
    }
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    source = FRONTEND.read_text(encoding="utf-8")
    source = replace_array(source, "extractedFiles", registry["extractedFiles"])
    source = replace_array(source, "routeContract", registry["routeContract"])
    current = FRONTEND.read_text(encoding="utf-8")
    if check:
        if source != current:
            raise SystemExit("admin contract registry is out of sync; run sync_admin_contract_registry.py")
    else:
        FRONTEND.write_text(source, encoding="utf-8")
    print(f"synced {len(registry['extractedFiles'])} files and {len(registry['routeContract'])} route contracts")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    main(check=args.check)
