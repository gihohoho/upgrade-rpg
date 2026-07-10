from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[3]
subprocess.run([sys.executable,str(ROOT/'tools/contracts/sync_admin_contract_registry.py'),'--check'],cwd=ROOT,check=True)
print('[OK] admin contract registry sync')
