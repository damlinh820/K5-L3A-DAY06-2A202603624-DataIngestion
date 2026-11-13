"""Read-only submission checks; report paths/counts, never credential values."""
import ast
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.extract import validate_lock


def main():
    validate_lock()
    results = ROOT / 'results'
    errors = []
    raw = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT)
    candidates = sorted(set(p.decode('utf-8') for p in raw.split(b'\0') if p))
    patterns = [rb'sk-or-v1-[A-Za-z0-9_-]{20,}', rb'sk-proj-[A-Za-z0-9_-]{20,}',
                rb'gh[pousr]_[A-Za-z0-9]{25,}', rb'github_pat_[A-Za-z0-9_]{25,}']
    syntax_count = 0
    for relative in candidates:
        path = ROOT / relative
        if not path.is_file():
            continue
        data = path.read_bytes()
        if path.name == '.env' or (path.name.startswith('.env.') and path.name != '.env.example'):
            errors.append({'path': relative, 'issue': 'environment secret file in candidate set'})
        if any(re.search(pattern, data) for pattern in patterns):
            errors.append({'path': relative, 'issue': 'credential-shaped text; value withheld'})
        if path.suffix == '.py':
            try:
                ast.parse(data.decode('utf-8-sig'), filename=relative)
                syntax_count += 1
            except (UnicodeError, SyntaxError):
                errors.append({'path': relative, 'issue': 'Python syntax or encoding error'})
        if len(data) > 50_000_000:
            errors.append({'path': relative, 'issue': 'oversized publication candidate'})

    selection = json.loads((results / 'dev_selection.json').read_text(encoding='utf-8'))
    for relative, expected in selection['code_snapshot'].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            errors.append({'path': relative, 'issue': 'evaluation code changed after dev selection'})
    method = json.loads((results / 'audit_method.json').read_text(encoding='utf-8'))
    for name, expected in method['labelled_sheet_sha256'].items():
        if hashlib.sha256((results / name).read_bytes()).hexdigest() != expected:
            errors.append({'path': 'results/' + name, 'issue': 'audit labels changed since method record'})
    status = json.loads((results / 'audit_status.json').read_text(encoding='utf-8'))
    if status['status'] != 'complete' or status['pending_fields']:
        errors.append({'issue': 'audit labels incomplete or invalid'})
    for relative in ['README.md', 'report/individual/2A202603624_DamTuanLinh.md', 'results/AUDIT_REVIEW.md']:
        path = ROOT / relative
        text = path.read_text(encoding='utf-8')
        for target in re.findall(r'\[[^\]\n]*\]\(([^)]+)\)', text):
            target = target.strip('<>')
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            target = target.split('#', 1)[0]
            if target and not (path.parent / target).exists():
                errors.append({'path': relative, 'issue': 'broken local link', 'target': target})
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'passed_with_disclosed_ai_audit' if not errors else 'failed',
              'candidate_files_checked': len(candidates), 'python_files_syntax_checked': syntax_count,
              'secrets_scan': 'credential-shaped strings and environment file paths; no values printed',
              'locked_benchmark_valid': True, 'selected_config': selection['selected_config'],
              'audit_origin': method['review_method'], 'human_verified': method['human_verified'],
              'errors': errors,
              'remaining_user_actions': ['Review AI labels if required by coach; independent human grading is not claimed.',
                                         'Submit the repository link through the instructor-designated channel.']}
    (results / 'submission_check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
