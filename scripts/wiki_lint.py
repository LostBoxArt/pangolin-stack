#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from collections import defaultdict

ROOT = Path('/home/jesus/pangolin-stack')
WIKI = ROOT / 'docs/wiki'
REQUIRED_FRONTMATTER = {
    'title', 'slug', 'type', 'status', 'tags', 'aliases', 'entities', 'related',
    'sources', 'confidence', 'audience_level', 'last_ingested', 'last_lint'
}
TOP_LEVEL_CHECK = [
    WIKI / 'README.md',
    WIKI / 'index.md',
    WIKI / 'glossary.md',
    WIKI / 'llms.txt',
    WIKI / 'llms-full.txt',
    WIKI / 'system-overview.md',
    WIKI / 'maintenance-workflow.md',
    WIKI / 'log.md',
]
SERVICE_DIRS = [WIKI / 'services', WIKI / 'services-nasus']
CANONICAL_PATHS = [
    WIKI / 'services', WIKI / 'services-nasus', WIKI / 'hosts', WIKI / 'networks',
    WIKI / 'runbooks', WIKI / 'index.md', WIKI / 'glossary.md', WIKI / 'README.md',
    WIKI / 'system-overview.md', WIKI / 'maintenance-workflow.md', WIKI / 'llms.txt',
    WIKI / 'llms-full.txt', WIKI / 'log.md', WIKI / 'compose-review-2026-04-17.md',
    WIKI / 'nasus-review-2026-04-17.md', WIKI / 'llm-wiki-pattern.md',
    WIKI / 'llm-wiki-research-and-best-practices.md'
]


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith('---\n'):
        return {}
    parts = text.split('\n---\n', 1)
    if len(parts) != 2:
        return {}
    lines = parts[0].splitlines()[1:]
    data: dict[str, str] = {}
    current = None
    for line in lines:
        if not line.strip():
            continue
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*:', line):
            key, val = line.split(':', 1)
            data[key.strip()] = val.strip()
            current = key.strip()
        elif current:
            data[current] += '\n' + line
    return data


def strip_fenced_code(text: str) -> str:
    return re.sub(r'```.*?```', '', text, flags=re.S)


def md_links(text: str):
    return re.findall(r'\((\./[^)]+)\)', strip_fenced_code(text))


def wikilinks(text: str):
    return re.findall(r'\[\[([^\]]+)\]\]', strip_fenced_code(text))


def rel(path: Path) -> str:
    return str(path.relative_to(WIKI))


def normalize_target(path: str) -> str:
    return path.split('#', 1)[0]


def main() -> int:
    files = sorted(WIKI.rglob('*.md'))
    issues: list[tuple[str, str, str]] = []
    slug_to_files = defaultdict(list)

    for p in files:
        text = p.read_text(errors='ignore')
        fm = parse_frontmatter(text)
        if not fm:
            issues.append(('critical', rel(p), 'missing frontmatter'))
            continue
        missing = sorted(REQUIRED_FRONTMATTER - set(fm))
        if missing:
            issues.append(('critical', rel(p), f'missing frontmatter keys: {", ".join(missing)}'))
        slug = fm.get('slug', '')
        if slug:
            slug_to_files[slug].append(rel(p))

        for link in md_links(text):
            target = (p.parent / normalize_target(link[2:])).resolve()
            if not target.exists():
                issues.append(('critical', rel(p), f'broken markdown link: {link}'))

        for link in wikilinks(text):
            if fm.get('type') == 'research-note':
                continue
            if link.startswith('http') or '*' in link or '…' in link or 'citation' in link or 'wikilinks' in link or 'fix' == link:
                continue
            target = (p.parent / normalize_target(link)).resolve()
            if not target.exists():
                issues.append(('warning', rel(p), f'unresolved wikilink target: [[{link}]]'))

    for slug, paths in sorted(slug_to_files.items()):
        if len(paths) > 1:
            issues.append(('critical', 'frontmatter', f'duplicate slug {slug}: {paths}'))

    index_text = (WIKI / 'index.md').read_text(errors='ignore') if (WIKI / 'index.md').exists() else ''
    for d in SERVICE_DIRS:
        for p in sorted(d.glob('*.md')):
            if f'(./{p.relative_to(WIKI).as_posix()})' not in index_text:
                issues.append(('warning', 'index.md', f'missing service entry for {rel(p)}'))

    for req in TOP_LEVEL_CHECK:
        if not req.exists():
            issues.append(('critical', 'top-level', f'missing required entry point {rel(req)}'))

    for req in CANONICAL_PATHS:
        if not req.exists():
            issues.append(('warning', 'structure', f'missing expected path {rel(req)}'))

    by_sev = defaultdict(list)
    for sev, where, msg in issues:
        by_sev[sev].append((where, msg))

    print(f'Checked {len(files)} markdown files under {WIKI}')
    for sev in ['critical', 'warning', 'info']:
        print(f'\n## {sev.upper()}')
        items = by_sev.get(sev, [])
        if not items:
            print('- none')
            continue
        for where, msg in items:
            print(f'- {where}: {msg}')

    return 1 if by_sev.get('critical') else 0


if __name__ == '__main__':
    raise SystemExit(main())
