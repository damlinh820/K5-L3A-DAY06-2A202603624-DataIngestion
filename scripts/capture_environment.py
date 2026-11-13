"""Record installed runtime versions and a complete pip dependency lock."""
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    freeze = subprocess.run([sys.executable, '-m', 'pip', 'freeze'],
                            capture_output=True, text=True, check=True).stdout
    (ROOT / 'requirements.lock.txt').write_text(freeze, encoding='utf-8')
    report = {'python': sys.version, 'platform': platform.platform(),
              'packages': {name: importlib.metadata.version(name) for name in
                           ['pdfplumber', 'pdfminer.six', 'chromadb', 'tiktoken', 'httpx', 'python-dotenv']}}
    (ROOT / 'results/environment.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
