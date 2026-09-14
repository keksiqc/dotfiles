"""
clean = ["~", "~/.config"]

[clean]
"~/.local/bin" = { force = true, recursive = false }

Removes dead symlinks that point into the dotfiles repo. With
``force = true`` every dead symlink in the directory is removed.
"""

from __future__ import annotations

import os
from typing import Any

from dot import Context, entries, plugin


@plugin("clean")
def clean(ctx: Context, data: Any) -> bool:
    for path, options in entries(data, "clean"):
        options = {**ctx.defaults("clean"), **options}
        directory = ctx.target(path)
        name = ctx.pretty(directory)
        if not os.path.isdir(directory):
            ctx.log.skip(f"{name}/  (not a directory)")
            continue
        removed = 0
        for entry in _walk(directory, recursive=bool(options.get("recursive"))):
            if not os.path.islink(entry) or os.path.exists(entry):
                continue  # not a symlink, or a symlink that still resolves
            destination = os.path.normpath(os.path.join(os.path.dirname(entry), os.readlink(entry)))
            points_into_repo = any(
                destination == base or destination.startswith(base + os.sep)
                for base in (ctx.base_dir, ctx.real_base_dir)
            )
            if points_into_repo or options.get("force"):
                ctx.remove(entry)
                if not ctx.dry_run:
                    ctx.log.ok(f"removed dead link {ctx.pretty(entry)}")
                removed += 1
        if not removed:
            ctx.log.skip(f"{name}/  (nothing to clean)")
    return True


def _walk(directory: str, recursive: bool):
    if not recursive:
        for entry in sorted(os.listdir(directory)):
            yield os.path.join(directory, entry)
        return
    for root, dirs, files in os.walk(directory):
        dirs.sort()
        for entry in sorted(dirs + files):
            yield os.path.join(root, entry)
