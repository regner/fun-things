#!/usr/bin/env python3
"""Extract reproducible readable public-doc text, then exact numbered evidence ranges."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SCRATCH = Path('/tmp/s03-s-valve-api-public')
PRIOR = Path('/tmp/s03-s-upstream/sources/valve/include/steam')


class DocText(HTMLParser):
    """Select Valve's documentation body without page navigation or scripts."""
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if self.depth:
                self.depth += 1
            elif dict(attrs).get('class') == 'documentation_bbcode':
                self.depth = 1
        if self.depth and tag in ('br', 'h1', 'h2', 'h3', 'h4', 'p', 'div', 'tr', 'li'):
            self.parts.append('\n')
        if self.depth and tag in ('td', 'th'):
            self.parts.append('\t')

    def handle_endtag(self, tag):
        if self.depth and tag in ('h1', 'h2', 'h3', 'h4', 'p', 'div', 'tr', 'li'):
            self.parts.append('\n')
        if tag == 'div' and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)

    def result(self):
        return '\n'.join(line.strip() for line in ''.join(self.parts).splitlines()
                         if line.strip()) + '\n'


def main():
    """Materialize text once; snapshots are selected separately after inspection."""
    for path in SCRATCH.glob('*.html'):
        parser = DocText()
        parser.feed(path.read_text())
        text = parser.result()
        assert len(text) > 1000, path
        path.with_suffix('.text').write_text(text)
        print(path.name, len(text), len(text.splitlines()))


if __name__ == '__main__':
    main()
