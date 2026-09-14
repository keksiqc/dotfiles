"""
create = ["~/projects", "~/.local/bin"]

[create]
"~/.ssh" = { mode = 0o700 }
"""

from __future__ import annotations

import os
from typing import Any

from dot import Context, entries, plugin


@plugin("create")
def create(ctx: Context, data: Any) -> bool:
    success = True
    for path, options in entries(data, "create"):
        options = {**ctx.defaults("create"), **options}
        directory = ctx.target(path)
        name = ctx.pretty(directory)
        if os.path.isdir(directory):
            ctx.log.skip(f"{name}/  (exists)")
            continue
        if os.path.lexists(directory):
            ctx.log.error(f"{name}: exists but is not a directory")
            success = False
            continue
        ctx.mkdir(directory, mode=int(options.get("mode", 0o777)))
        if not ctx.dry_run:
            ctx.log.ok(f"{name}/")
    return success
