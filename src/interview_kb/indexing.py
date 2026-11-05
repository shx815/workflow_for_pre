"""Rebuild generated company/topic indexes from validated Markdown notes."""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from pathlib import Path
import re

from .validation import _frontmatter_lines, validate_tree


def topic_slug(topic: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]+', '-', topic).strip('-') or 'unknown'


def rebuild_indexes(kb_dir: Path) -> None:
    if validate_tree(kb_dir):
        raise ValueError("Fix structured note validation failures before indexing")
    companies = defaultdict(list)
    topics = defaultdict(list)
    for path in sorted((kb_dir / 'by-company').glob('**/*.md')):
        text = path.read_text(encoding='utf-8')
        meta = _frontmatter_lines(text)
        company = str(ast.literal_eval(meta['company']))
        note_topics = ast.literal_eval(meta['topics'])
        title = re.search(r'^# (.+)$', text, re.MULTILINE)[1]
        link = f"[[{path.relative_to(kb_dir).with_suffix('').as_posix()}|{title}]]"
        companies[company].append(link)
        for topic in note_topics:
            topics[topic].append(link)
    index = ['# 大模型算法工程师面试知识库', '', '## 按公司', '']
    for company, links in sorted(companies.items()):
        index.extend([f'### {company}', '', *[f'- {link}' for link in links], ''])
    index.extend(['## 按主题', ''])
    topic_dir = kb_dir / 'by-topic'
    topic_dir.mkdir(parents=True, exist_ok=True)
    for topic, links in sorted(topics.items()):
        slug = topic_slug(topic)
        index.append(f'- [[by-topic/{slug}|{topic}]]')
        (topic_dir / f'{slug}.md').write_text(
            f'# {topic}\n\n' + '\n'.join(f'- {link}' for link in links) + '\n', encoding='utf-8')
    (kb_dir / 'index.md').write_text('\n'.join(index) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kb-dir', type=Path, default=Path('interview-kb'))
    args = parser.parse_args()
    rebuild_indexes(args.kb_dir)
