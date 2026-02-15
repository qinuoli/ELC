#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
from typing import Dict, List, Tuple


HEADER_RE = re.compile(r"^\[(?P<sid>[^\[\]]+)\]\s*$")


def parse_articles(text: str) -> List[Tuple[str, str]]:
    """
    Parse text with sections like:
    [sample_001]
    <content...>

    Returns list of (sample_id, content).
    """
    articles: List[Tuple[str, str]] = []
    cur_id: str = ""
    buf: List[str] = []

    def flush():
        nonlocal cur_id, buf
        if cur_id:
            content = "\n".join(buf).strip("\n").strip()
            if content:
                articles.append((cur_id, content))
        buf = []

    for line in text.splitlines():
        m = HEADER_RE.match(line.strip())
        if m:
            flush()
            cur_id = m.group("sid").strip()
            continue
        buf.append(line)

    flush()
    return articles


def safe_write(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.rstrip() + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_file", required=True, help="Path to articles_with_id.txt")
    ap.add_argument("--out_dir", required=True, help="Output dir, e.g. ./articles")
    ap.add_argument("--ext", default=".txt", help="Output extension")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = ap.parse_args()

    with open(args.in_file, "r", encoding="utf-8") as f:
        raw = f.read()

    items = parse_articles(raw)
    if not items:
        raise RuntimeError("No [sample_id] sections found. Check the input format.")

    os.makedirs(args.out_dir, exist_ok=True)

    index: Dict[str, Dict[str, str]] = {}
    written = 0
    skipped = 0

    for sid, content in items:
        out_path = os.path.join(args.out_dir, f"{sid}{args.ext}")
        if (not args.overwrite) and os.path.exists(out_path):
            skipped += 1
            continue
        safe_write(out_path, content)
        index[sid] = {"file": out_path, "chars": str(len(content))}
        written += 1

    index_path = os.path.join(args.out_dir, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "count": len(items),
                "written": written,
                "skipped": skipped,
                "out_dir": os.path.abspath(args.out_dir),
                "items": index,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Parsed: {len(items)}")
    print(f"Written: {written}, Skipped: {skipped}")
    print(f"Index: {index_path}")


if __name__ == "__main__":
    main()
