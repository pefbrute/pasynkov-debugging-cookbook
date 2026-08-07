#!/usr/bin/env python3
"""
fetch_api_docs.py — Retrieve C declarations and docstrings from GNOME documentation.

Usage:
    python3 tools/fetch_api_docs.py <function_or_method_name> [--namespace clutter|st|gjs]

Examples:
    python3 tools/fetch_api_docs.py clutter_actor_get_preferred_height
    python3 tools/fetch_api_docs.py get_width --namespace clutter
"""

import argparse
import re
import sys
import urllib.request
from html.parser import HTMLParser


class DocParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_decl = False
        self.decl_text = []
        self.in_desc = False
        self.desc_paragraphs = []
        self.current_tag = None
        self.current_class = ""

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attr_dict = dict(attrs)
        self.current_class = attr_dict.get('class', '')

        if 'c-decl' in self.current_class or 'decl' in self.current_class:
            self.in_decl = True
        elif 'description' in self.current_class or 'docblock' in self.current_class:
            self.in_desc = True

    def handle_endtag(self, tag):
        if tag in ['div', 'pre'] and self.in_decl:
            self.in_decl = False
        elif tag == 'div' and self.in_desc:
            self.in_desc = False
        self.current_tag = None

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self.in_decl:
            self.decl_text.append(text)
        elif self.in_desc:
            self.desc_paragraphs.append(text)


def fetch_docs(symbol: str, namespace: str = None):
    # Normalize function symbol
    method_name = symbol
    if symbol.startswith('clutter_actor_'):
        method_name = symbol.replace('clutter_actor_', '')
    elif symbol.startswith('st_box_layout_'):
        method_name = symbol.replace('st_box_layout_', '')

    urls = [
        f"https://gnome.pages.gitlab.gnome.org/mutter/clutter/method.Actor.{method_name}.html",
        f"https://mutter.gnome.org/clutter/method.Actor.{method_name}.html",
        f"https://gnome.pages.gitlab.gnome.org/gnome-shell/st/class.ScrollView.html",
        f"https://gnome.pages.gitlab.gnome.org/gnome-shell/st/class.BoxLayout.html",
    ]

    headers = {'User-Agent': 'Pasynkov-Debugging-Cookbook/1.0'}

    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    html_content = response.read().decode('utf-8')
                    parser = DocParser()
                    parser.feed(html_content)

                    print(f"=== {symbol} ===")
                    print(f"URL: {url}\n")
                    if parser.decl_text:
                        print("DECLARATION:")
                        print(" ".join(parser.decl_text))
                    else:
                        print(f"Fetched documentation page successfully: {url}")
                    if parser.desc_paragraphs:
                        print("\nDESCRIPTION SUMMARY:")
                        for p in parser.desc_paragraphs[:5]:
                            print(f"- {p}")
                    return True
        except Exception:
            continue

    print(f"Could not fetch online docs for '{symbol}'.")
    print("Please verify the symbol name or search online at:")
    print("  https://gnome.pages.gitlab.gnome.org/mutter/clutter/")
    print("  https://gnome.pages.gitlab.gnome.org/gnome-shell/st/")
    return False


def main():
    parser = argparse.ArgumentParser(description="Fetch GNOME C API declarations and docs.")
    parser.add_argument("symbol", type=str, help="Function or method name (e.g. clutter_actor_get_preferred_height)")
    parser.add_argument("--namespace", type=str, default="clutter", help="Namespace (clutter, st, gjs)")
    args = parser.parse_args()

    fetch_docs(args.symbol, args.namespace)


if __name__ == '__main__':
    main()
