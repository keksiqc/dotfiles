"""
apt = ["curl", "git"]

[apt]
packages = ["curl", "git"]
update = false            # run apt-get update before installing missing packages
no-recommends = false     # pass --no-install-recommends

Packages that dpkg already reports as installed are skipped.
"""

from __future__ import annotations

import shlex
from typing import Any

from dot import Context, listing, plugin


@plugin("apt")
def apt(ctx: Context, data: Any) -> bool:
    packages, options = listing(data, "packages", "apt")
    if not ctx.which("apt-get"):
        ctx.log.error("apt-get not found; the apt plugin needs Debian or Ubuntu")
        return False
    if not packages:
        ctx.log.skip("no packages listed")
        return True

    missing = [package for package in packages if not installed(ctx, package)]
    if not missing:
        ctx.log.skip(f"already installed: {', '.join(packages)}")
        return True

    ctx.log.info(f"installing: {', '.join(missing)}")
    if ctx.dry_run:
        return True
    if options.get("update", False) and ctx.run(ctx.sudo("apt-get update -qq")) != 0:
        ctx.log.error("apt-get update failed")
        return False
    flags = "--no-install-recommends " if options.get("no_recommends") else ""
    if ctx.run(ctx.sudo(f"apt-get install -y {flags}{shlex.join(missing)}")) != 0:
        ctx.log.error(f"apt-get install failed for: {', '.join(missing)}")
        return False
    ctx.log.ok(f"installed: {', '.join(missing)}")
    return True


def installed(ctx: Context, package: str) -> bool:
    code, output = ctx.capture(f"dpkg-query -W -f='${{Status}}' {shlex.quote(package)}")
    return code == 0 and "install ok installed" in output
