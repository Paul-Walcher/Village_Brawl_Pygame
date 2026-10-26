#!/usr/bin/env python3
"""Generate an expandable folder-tree page for pdoc HTML documentation.

By default, scans ./src and writes ./docs/folder_view.html.
Run from anywhere, e.g.:
    python generate_folder_view.py --src src --docs docs

The tree is derived from the real filesystem each time this script runs.
Module links are added only when the corresponding pdoc HTML page exists.
"""

from __future__ import annotations

import argparse
import html
import os
from pathlib import Path

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "build",
    "dist",
    "docs",
    ".mypy_cache",
    ".pytest_cache",
}


def find_doc_page(docs_dir: Path, relative_module_path: Path) -> Path | None:
    """Find likely pdoc output locations for a dotted module path.

    Current pdoc writes e.g. Frames.frame -> docs/Frames/frame.html.
    The index.html form is also accepted for compatibility with other setups.
    """
    stem = relative_module_path.as_posix()
    candidates = (
        docs_dir / f"{stem}.html",
        docs_dir / stem / "index.html",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def relative_href(from_file: Path, target_file: Path) -> str:
    """Return a portable relative link from the generated page to a docs page."""
    return Path(os.path.relpath(target_file, start=from_file.parent)).as_posix()


def make_link(label: str, doc_page: Path | None, output_file: Path) -> str:
    safe_label = html.escape(label)
    if doc_page is None:
        return (
            f'<span class="node-label unavailable" title="No matching pdoc HTML page found">'
            f'<span class="file-icon" aria-hidden="true">PY</span>{safe_label}'
            f'<span class="missing">not documented</span></span>'
        )
    href = html.escape(relative_href(output_file, doc_page), quote=True)
    return (
        f'<a class="node-label" href="{href}" title="Open documentation for {safe_label}">'
        f'<span class="file-icon" aria-hidden="true">PY</span>{safe_label}</a>'
    )


def render_tree(current_dir: Path, root_src: Path, docs_dir: Path, output_file: Path, excluded: set[str]) -> str:
    """Build nested details/summary elements for current_dir, relative to root_src."""
    entries = sorted(current_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold()))
    chunks: list[str] = []

    for entry in entries:
        if entry.is_dir():
            if entry.name in excluded or entry.name.startswith("."):
                continue
            folder_module_path = entry.relative_to(root_src)
            folder_doc = find_doc_page(docs_dir, folder_module_path)
            # A directory is always shown, even if pdoc did not make a package page.
            folder_label = html.escape(entry.name)
            if folder_doc is not None:
                href = html.escape(relative_href(output_file, folder_doc), quote=True)
                shown_name = (
                    f'<a class="folder-link" href="{href}" '
                    f'title="Open package documentation">{folder_label}</a>'
                )
            else:
                shown_name = f'<span class="folder-name">{folder_label}</span>'

            child_html = render_tree(entry, root_src, docs_dir, output_file, excluded)
            chunks.append(
                '<li class="tree-node folder-node">'
                '<details>'
                f'<summary><span class="folder-icon" aria-hidden="true"></span>{shown_name}</summary>'
                f'<ul>{child_html}</ul>'
                '</details>'
                '</li>'
            )
            continue

        if entry.is_file() and entry.suffix.lower() == ".py" and entry.name != "__init__.py":
            module_path = entry.relative_to(root_src).with_suffix("")
            doc_page = find_doc_page(docs_dir, module_path)
            node_name = entry.name
            chunks.append(
                '<li class="tree-node file-node" '
                f'data-search="{html.escape((str(module_path) + " " + node_name).casefold(), quote=True)}">'
                f'{make_link(node_name, doc_page, output_file)}'
                '</li>'
            )

    return "\n".join(chunks)


def build_html(src_dir: Path, docs_dir: Path, output_file: Path, excluded: set[str]) -> str:
    tree_markup = render_tree(src_dir, src_dir, docs_dir, output_file, excluded)
    project_name = html.escape(src_dir.resolve().parent.name or "Project")
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{project_name} — Source tree</title>
<style>
  :root {{ color-scheme: light dark; --accent: #6da9e8; --line: color-mix(in srgb, CanvasText 15%, transparent); }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; background: Canvas; color: CanvasText; }}
  header {{ position: sticky; top: 0; z-index: 2; padding: 22px clamp(18px, 4vw, 44px) 16px; background: Canvas; border-bottom: 1px solid var(--line); }}
  h1 {{ font-size: 1.45rem; margin: 0 0 4px; font-weight: 700; }}
  .subtitle {{ margin: 0 0 14px; opacity: .7; font-size: .9rem; }}
  .toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
  #search {{ flex: 1 1 240px; min-width: 0; padding: 10px 12px; border: 1px solid var(--line); border-radius: 9px; background: Canvas; color: CanvasText; font: inherit; }}
  button {{ padding: 9px 12px; border: 1px solid var(--line); border-radius: 9px; background: color-mix(in srgb, CanvasText 5%, Canvas); color: CanvasText; font: inherit; cursor: pointer; }}
  button:hover {{ border-color: var(--accent); }}
  main {{ padding: 22px clamp(18px, 4vw, 44px) 42px; max-width: 1100px; }}
  .root-title {{ display: flex; align-items: center; gap: 9px; font-weight: 700; margin-bottom: 8px; }}
  ul {{ list-style: none; margin: 0; padding-left: 23px; }}
  .root-list {{ padding-left: 0; }}
  li {{ position: relative; margin: 3px 0; }}
  li > ul {{ border-left: 1px solid var(--line); margin-left: 9px; }}
  summary {{ list-style: none; display: flex; align-items: center; gap: 8px; cursor: pointer; min-height: 32px; border-radius: 7px; padding: 3px 7px; }}
  summary::-webkit-details-marker {{ display: none; }}
  summary:hover, .node-label:hover {{ background: color-mix(in srgb, var(--accent) 11%, transparent); }}
  summary::before {{ content: '›'; display: inline-block; width: 11px; color: #8b8b8b; font-size: 1.25rem; line-height: 1; transform: rotate(0deg); transition: transform .12s ease; }}
  details[open] > summary::before {{ transform: rotate(90deg); }}
  .folder-icon {{ display: inline-block; width: 17px; height: 12px; position: relative; border: 1.5px solid #d3a449; border-radius: 2px; background: color-mix(in srgb, #d3a449 22%, transparent); flex: 0 0 auto; }}
  .folder-icon::before {{ content: ''; position: absolute; top: -4px; left: 1px; width: 7px; height: 4px; border: 1.5px solid #d3a449; border-bottom: 0; border-radius: 2px 2px 0 0; background: color-mix(in srgb, #d3a449 22%, transparent); }}
  .folder-name, .folder-link {{ font-weight: 600; }}
  .folder-link {{ color: inherit; text-decoration: none; }}
  .node-label {{ display: inline-flex; align-items: center; gap: 8px; width: fit-content; min-height: 30px; padding: 3px 7px; border-radius: 7px; color: inherit; text-decoration: none; }}
  .file-icon {{ display: inline-grid; place-items: center; height: 18px; min-width: 21px; padding: 0 2px; border-radius: 4px; color: #4c94d8; background: color-mix(in srgb, #4c94d8 13%, transparent); font-size: 9px; font-weight: 800; letter-spacing: -.4px; }}
  .unavailable {{ opacity: .55; cursor: default; }}
  .missing {{ font-size: .72rem; opacity: .75; margin-left: 4px; }}
  .empty {{ opacity: .55; font-style: italic; padding: 6px 0 6px 12px; }}
  #status {{ margin-top: 13px; color: color-mix(in srgb, CanvasText 65%, transparent); font-size: .82rem; }}
  @media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>
</head>
<body>
<header>
  <h1>{project_name} source tree</h1>
  <p class="subtitle">Browse folders and open generated pdoc documentation.</p>
  <div class="toolbar">
    <input id="search" type="search" placeholder="Filter folders and Python files…" aria-label="Filter source tree">
    <button id="expand">Expand all</button>
    <button id="collapse">Collapse all</button>
  </div>
  <div id="status" role="status"></div>
</header>
<main>
  <div class="root-title"><span class="folder-icon" aria-hidden="true"></span>{project_name}</div>
  <ul class="root-list" id="tree">{tree_markup}</ul>
</main>
<script>
(() => {{
  const tree = document.getElementById('tree');
  const search = document.getElementById('search');
  const status = document.getElementById('status');
  const allDetails = () => [...tree.querySelectorAll('details')];

  document.getElementById('expand').addEventListener('click', () => allDetails().forEach(el => el.open = true));
  document.getElementById('collapse').addEventListener('click', () => allDetails().forEach(el => el.open = false));

  function revealSubtree(list) {{
    for (const li of list.children) {{
      li.hidden = false;
      const details = li.querySelector(':scope > details');
      if (details) {{
        details.open = true;
        revealSubtree(details.querySelector(':scope > ul'));
      }}
    }}
  }}

  function filterList(list, query) {{
    let anyVisible = false;
    for (const li of list.children) {{
      const details = li.querySelector(':scope > details');
      if (!details) {{
        const haystack = (li.dataset.search || li.textContent).toLocaleLowerCase();
        li.hidden = !!query && !haystack.includes(query);
      }} else {{
        const summary = details.querySelector(':scope > summary');
        const folderMatches = !!query && summary.textContent.toLocaleLowerCase().includes(query);
        const childList = details.querySelector(':scope > ul');
        if (folderMatches) {{
          revealSubtree(childList);
          details.open = true;
          li.hidden = false;
        }} else {{
          const childVisible = filterList(childList, query);
          li.hidden = !!query && !childVisible;
          if (query && childVisible) details.open = true;
        }}
      }}
      if (!li.hidden) anyVisible = true;
    }}
    return anyVisible;
  }}

  function filterTree() {{
    const query = search.value.trim().toLocaleLowerCase();
    filterList(tree, query);
    status.textContent = query
      ? `Filtering for “${{search.value}}”`
      : `${{tree.querySelectorAll('li.file-node').length}} Python files detected`;
  }}
  search.addEventListener('input', filterTree);
  filterTree();
}})();
</script>
</body>
</html>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, default=Path("src"), help="Source folder to scan (default: ./src)")
    parser.add_argument("--docs", type=Path, default=Path("docs"), help="pdoc output folder (default: ./docs)")
    parser.add_argument("--output", type=Path, default=None, help="Output HTML filename (default: DOCS/folder_view.html)")
    parser.add_argument("--exclude", action="append", default=[], help="Folder name to exclude; can be repeated")
    args = parser.parse_args()

    src_dir = args.src.resolve()
    docs_dir = args.docs.resolve()
    output_file = (args.output.resolve() if args.output else docs_dir / "folder_view.html")

    if not src_dir.is_dir():
        parser.error(f"Source folder does not exist: {src_dir}")

    docs_dir.mkdir(parents=True, exist_ok=True)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    excluded = DEFAULT_EXCLUDED_DIRS | set(args.exclude)
    output_file.write_text(build_html(src_dir, docs_dir, output_file, excluded), encoding="utf-8")

    py_count = sum(1 for p in src_dir.rglob("*.py") if not any(part in excluded or part.startswith(".") for part in p.relative_to(src_dir).parts[:-1]))
    print(f"Folder view generated: {output_file}")
    print(f"Scanned source directory: {src_dir}")
    print(f"Python files found (before __init__.py filtering): {py_count}")
    print("Note: links are active only where matching pdoc HTML files already exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
