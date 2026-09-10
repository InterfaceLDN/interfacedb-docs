#!/usr/bin/env python3
"""Validate Docs7 navigation/content, optionally including a running preview."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.ids = set()
        self.links = []
        self.images = []
        self.errors = []
        self.feed(content)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if "data-docs7-render-error" in attrs:
            self.errors.append(attrs["data-docs7-render-error"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img" and attrs.get("src"):
            self.images.append(attrs["src"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Also check all rendered pages, links and images, e.g. http://localhost:3333")
    args = parser.parse_args()
    config = json.loads((ROOT / "docs.json").read_text())
    files = {p.relative_to(ROOT).with_suffix("").as_posix(): p for p in ROOT.rglob("*.mdx")}
    navigation = [page for group in config["navigation"]["groups"] for page in group["pages"]]
    errors = []
    if len(navigation) != len(set(navigation)):
        errors.append("Duplicate pages in navigation")
    for slug in sorted(set(navigation) ^ files.keys()):
        errors.append(f"Navigation and content disagree: {slug}")
    for slug, file in files.items():
        content = file.read_text()
        if not re.match(r"^---\n[\s\S]*?\btitle: .+\n[\s\S]*?---\n", content):
            errors.append(f"Missing title frontmatter: {slug}")
        if "{%" in content or "DOCSSEVENPLACEHOLDER" in content:
            errors.append(f"Unconverted Markdoc content: {slug}")
        for asset in re.findall(r"\]\((/img/[^)]+)\)", content):
            if not (ROOT / asset.lstrip("/")).is_file():
                errors.append(f"Missing image: {slug}: {asset}")

    if args.url:
        base = args.url.rstrip("/") + "/"
        routes = {"/" if slug == "index" else "/" + slug for slug in files}

        def fetch(route):
            try:
                with urlopen(urljoin(base, route), timeout=60) as response:
                    return route, response.headers.get_content_type(), response.read().decode("utf-8", errors="replace")
            except Exception as error:
                return route, "error", str(error)

        with ThreadPoolExecutor(max_workers=4) as pool:
            responses = list(pool.map(fetch, sorted(routes)))
        pages = {}
        for route, kind, body in responses:
            if kind != "text/html":
                errors.append(f"Page failed: {route}: {kind}: {body[:150]}")
                continue
            page = Page(body)
            pages[route] = page
            errors.extend(f"{route}: {error}" for error in page.errors)
            if "main-content" not in page.ids:
                errors.append(f"Missing page content: {route}")

        extra = {"/llms.txt", "/llms-full.txt", "/index.md"}
        for route, page in pages.items():
            for href in page.links + page.images:
                target = urlparse(urljoin(urljoin(base, route), href))
                if target.netloc != urlparse(base).netloc:
                    continue
                if target.path not in routes:
                    if target.path.endswith(".md") or target.path.startswith("/docs-assets/"):
                        extra.add(target.path)
                    else:
                        errors.append(f"Broken link: {route}: {href}")
                elif target.fragment and unquote(target.fragment) not in pages.get(target.path, Page("")).ids:
                    errors.append(f"Broken section link: {route}: {href}")
        with ThreadPoolExecutor(max_workers=4) as pool:
            for route, kind, body in pool.map(fetch, sorted(extra)):
                if kind in ("error", "text/html"):
                    errors.append(f"Asset or Markdown export failed: {route}: {kind}: {body[:100]}")

    if errors:
        print("\n".join(sorted(set(errors))), file=sys.stderr)
        return 1
    print(f"Docs7: {len(files)} pages; navigation and images valid" + ("; rendered pages, section links and Markdown exports passed." if args.url else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
