"""``.hotreloadignore`` parsing and gitignore-like matching (stdlib subset)."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from .paths import is_subpath


@dataclass(frozen=True)
class IgnoreRules:
    """Path matchers keyed by resolved plugin directory + merged module-name globs."""

    path_specs: dict[Path, list[Callable[[str], bool]]]
    module_patterns: tuple[str, ...]


def pattern_lines_from_text(text: str) -> list[str]:
    """Non-empty, non-comment lines from ``.hotreloadignore``."""
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        lines.append(line.rstrip("\r\n"))
    return lines


def translate_glob(segment: str) -> str:
    """
    Turn one pattern body into a regex fragment.

    Supported metacharacters (subset of gitignore): ``**/``, ``**``, ``*``, ``?``.
    """
    i = 0
    n = len(segment)
    out: list[str] = []
    while i < n:
        if i <= n - 3 and segment[i : i + 3] == "**/":
            out.append("(?:.*/)?")
            i += 3
        elif i <= n - 2 and segment[i : i + 2] == "**":
            out.append(".*")
            i += 2
        elif segment[i] == "*":
            out.append("[^/]*")
            i += 1
        elif segment[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            c = segment[i]
            if c in r".^$+{}[]|()":
                out.append("\\" + c)
            elif c == "\\":
                out.append(r"\\")
            else:
                out.append(c)
            i += 1
    return "".join(out)


def compile_ignore_line(pattern_line: str) -> Optional[Callable[[str], bool]]:
    """
    Build a matcher for one pattern line.

    Subset (similar to ``.gitignore``, not identical):

    - Leading ``/`` — pattern is rooted at the plugin folder only.
    - Trailing ``/`` — directory-only; matches that folder and everything under it.
    - ``*`` — any characters except ``/`` within one path segment.
    - ``**`` — across segments (including empty); ``**/`` means optional prefix path.
    - ``?`` — one character except ``/``.

    Unsupported: ``!`` negation (lines starting with ``!`` should be skipped by caller).
    """
    raw = pattern_line.strip()
    if not raw:
        return None
    if raw.startswith("!"):
        raise ValueError("negation patterns (`!`) are not supported")

    directory_only = len(raw) > 1 and raw.endswith("/")
    pat = raw[:-1] if directory_only else raw
    anchored = pat.startswith("/")
    body = pat[1:] if anchored else pat
    if not body:
        return None

    try:
        trans = translate_glob(body)
        if directory_only:
            if anchored:
                rx = re.compile(rf"^{trans}(?:/|$)")
            else:
                rx = re.compile(rf"(?:^|.*/){trans}(?:/|$)")
        else:
            if anchored:
                rx = re.compile(rf"^{trans}$")
            else:
                rx = re.compile(rf"(?:^|.*/){trans}$")
    except re.error as e:
        raise ValueError(str(e)) from e

    return lambda rel: bool(rx.match(rel))


def load_ignore_rules(api_base: Path) -> IgnoreRules:
    """
    Load every ``API.x64/<Plugin>/.hotreloadignore``:

    - Path globs — scoped to that plugin folder (unchanged).
    - ``mod:`` lines — dotted module name globs (``fnmatch`` ``*`` / ``?``); merged from
      all plugins so heavy packages under ``site-packages`` can be skipped.
    """
    specs: dict[Path, list[Callable[[str], bool]]] = {}
    module_patterns: list[str] = []
    for child in api_base.iterdir():
        if not child.is_dir():
            continue
        ig = child / ".hotreloadignore"
        if not ig.is_file():
            continue
        try:
            text = ig.read_text(encoding="utf-8")
        except OSError as e:
            print(f"HotReload - Warning: could not read {ig}: {e}")
            continue
        lines = pattern_lines_from_text(text)
        if not lines:
            continue
        matchers: list[Callable[[str], bool]] = []
        neg_warned = False
        for line in lines:
            stripped = line.strip()
            low = stripped.lower()
            if low.startswith("mod:"):
                mpat = stripped.split(":", 1)[1].strip()
                if mpat:
                    module_patterns.append(mpat)
                else:
                    print(f"HotReload - Warning: {ig}: empty `mod:` pattern skipped")
                continue
            try:
                m = compile_ignore_line(line)
            except ValueError as e:
                if "negation" in str(e).lower():
                    if not neg_warned:
                        print(
                            f"HotReload - Warning: {ig}: `!` negation is not supported; "
                            "those lines were skipped"
                        )
                        neg_warned = True
                    continue
                print(f"HotReload - Warning: {ig}: ignoring invalid pattern {line!r}: {e}")
                continue
            if m is not None:
                matchers.append(m)
        if matchers:
            specs[child.resolve()] = matchers

    uniq_mod = tuple(sorted(set(module_patterns)))
    return IgnoreRules(path_specs=specs, module_patterns=uniq_mod)


def module_name_matches_ignore_rules(module_name: str, rules: IgnoreRules) -> bool:
    if not rules.module_patterns:
        return False
    return any(fnmatch.fnmatchcase(module_name, pat) for pat in rules.module_patterns)


def path_matches_ignore_rules(module_path_resolved: Path, rules: IgnoreRules) -> bool:
    specs_by_root = rules.path_specs
    if not specs_by_root:
        return False
    matching_roots = [root for root in specs_by_root if is_subpath(module_path_resolved, root)]
    if not matching_roots:
        return False
    plugin_root = max(matching_roots, key=lambda p: len(p.parts))
    try:
        rel = module_path_resolved.relative_to(plugin_root)
    except ValueError:
        return False
    posix_rel = rel.as_posix()
    return any(m(posix_rel) for m in specs_by_root[plugin_root])
