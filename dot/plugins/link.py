"""
[link]
"~/.config/bat" = true                 # source is the same path inside the repo
"~/.vimrc" = "vim/vimrc"               # explicit source (relative to the repo)
"~/.config/nvim" = { path = "nvim", create = true, relink = true, force = false,
                     if = "command -v nvim", relative = false, ignore-missing = false }
"~/.config" = { path = "config/*", glob = true, exclude = ["config/private*"] }
"""

from __future__ import annotations

import glob
import os
import re
from typing import Any

from dot import ConfigError, Context, normalize, plugin


@plugin("link")
def link(ctx: Context, data: Any) -> bool:
    if not isinstance(data, dict):
        raise ConfigError("[link] must be a table of  target = source")
    success = True
    for target, spec in data.items():
        options = ctx.defaults("link")
        if isinstance(spec, str):
            options["path"] = spec
        elif isinstance(spec, dict):
            options.update(normalize(spec))
        elif spec is not True:
            raise ConfigError(f"[link] {target!r}: value must be a path, a table, or true")
        success &= _entry(ctx, target, options)
        if not success and not ctx.keep_going:
            return False
    return success


def _entry(ctx: Context, target: str, options: dict) -> bool:
    target_path = ctx.target(target)
    condition = options.get("if")
    if condition is not None and not ctx.check(condition):
        ctx.log.skip(f"{ctx.pretty(target_path)}  (if: {condition})")
        return True

    path = options.get("path") or ""
    if not path:
        # Mirror the target's location inside the repo: ~/.config/bat -> .config/bat
        if target_path.startswith(ctx.home + os.sep):
            path = os.path.relpath(target_path, ctx.home)
        else:
            path = os.path.basename(target_path)
    source = ctx.source(path, canonical=options.get("canonicalize", True))

    if not options.get("glob"):
        return _symlink(ctx, source, target_path, options)

    excluded: set[str] = set()
    excludes = options.get("exclude", [])
    for pattern in [excludes] if isinstance(excludes, str) else excludes:
        excluded.update(glob.glob(ctx.source(pattern), recursive=True))
    matches = [m for m in sorted(glob.glob(source, recursive=True)) if m not in excluded]
    if not matches:
        ctx.log.warn(f"{ctx.pretty(target_path)}: glob {path!r} matched nothing")
        return True
    root = _glob_root(source)
    success = True
    for match in matches:
        destination = os.path.join(target_path, os.path.relpath(match, root))
        success &= _symlink(ctx, match, destination, options)
    return success


def _glob_root(pattern: str) -> str:
    """The directory part of a pattern before its first wildcard."""
    fixed = []
    for part in pattern.split(os.sep):
        if re.search(r"[*?\[]", part):
            break
        fixed.append(part)
    return os.sep.join(fixed) or os.sep


def _symlink(ctx: Context, source: str, target: str, options: dict) -> bool:
    log = ctx.log
    name = ctx.pretty(target)

    if not os.path.lexists(source) and not options.get("ignore_missing"):
        log.error(f"{name}: source does not exist: {ctx.pretty(source)}")
        return False

    if os.path.islink(target):
        if os.path.realpath(target) == os.path.realpath(source):
            log.skip(f"{name} → {ctx.pretty(source)}  (already linked)")
            return True
        if not options.get("relink"):
            log.error(f"{name}: already a link to {os.readlink(target)}  (set relink = true to replace it)")
            return False
        ctx.remove(target)
    elif os.path.lexists(target):
        if not options.get("force"):
            log.error(f"{name}: already exists  (set force = true to replace it)")
            return False
        ctx.remove(target)

    parent = os.path.dirname(target)
    if not ctx.isdir(parent):
        if not options.get("create"):
            log.error(f"{name}: parent directory does not exist  (set create = true)")
            return False
        ctx.mkdir(parent)

    ctx.symlink(source, target, relative=bool(options.get("relative")))
    if not ctx.dry_run:
        log.ok(f"{name} → {ctx.pretty(source)}")
    return True
