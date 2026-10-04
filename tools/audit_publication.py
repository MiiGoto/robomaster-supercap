"""Audit Git candidates and local Markdown links without printing matched secrets."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{30,}',
    r'AKIA[0-9A-Z]{16}', r'sk-[A-Za-z0-9_-]{20,}',
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    r'(?i)(?:password|api[_-]?key|access[_-]?token)\s*[:=]\s*["\x27][^"\x27]{8,}',
    r'(?i)https?://[^/\s]+:[^@\s]+@',
]

def run(*args):
    return subprocess.check_output(['git', '-c', 'safe.directory='+ROOT.as_posix(), *args], cwd=ROOT)

def main():
    names = run('ls-files', '-z', '--cached', '--others', '--exclude-standard').decode().split('\0')
    names = sorted(set(filter(None, names)))
    problems = []
    for name in names:
        path = ROOT / name
        if not path.is_file():
            problems.append((name, 'not a regular file'))
            continue
        # JSON connectivity and KiCad symbol files are original project sources.
        if path.suffix.lower() not in {'.md', '.py', '.json', '.kicad_sym', '.kicad_pro', '.kicad_sch', '.kicad_pcb', ''}:
            problems.append((name, 'unexpected file type / provenance review required'))
        content = path.read_text(encoding='utf-8')
        for pattern in PATTERNS:
            if re.search(pattern, content):
                problems.append((name, 'possible secret; inspect locally'))
        for address in re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', content):
            if not address.endswith('@users.noreply.github.com'):
                problems.append((name, 'personal email candidate'))
        if path.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', content):
                if '://' not in target and not target.startswith('#'):
                    local = target.split('#')[0]
                    if not (path.parent / local).exists():
                        problems.append((name, 'broken relative link'))
    # Audit every reachable commit, including metadata and earlier versions.
    commits = run('rev-list', '--all').decode().splitlines()
    for commit in commits:
        metadata = run('show', '-s', '--format=%ae%n%ce', commit).decode()
        if any(not x.endswith('@users.noreply.github.com') for x in metadata.splitlines()):
            problems.append((commit[:7], 'non-noreply author/committer email'))
        for name in run('ls-tree', '-r', '--name-only', commit).decode().splitlines():
            blob = run('show', commit + ':' + name).decode('utf-8')
            if any(re.search(pattern, blob) for pattern in PATTERNS):
                problems.append((commit[:7] + ':' + name, 'possible historical secret'))
    for name, reason in problems:
        print(name + ': ' + reason)
    print(f'Audited {len(names)} candidate files and {len(commits)} commits; findings={len(problems)}')
    print('Manual review still required for proprietary/private content and third-party rights.')
    return int(bool(problems))

if __name__ == '__main__':
    sys.exit(main())
