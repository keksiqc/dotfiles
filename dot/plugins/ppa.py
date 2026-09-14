"""
ppa = ["fish-shell/release-4"]

[ppa]
repos = ["ppa:fish-shell/release-4"]
update = true             # apt-get update after adding repositories

Installs software-properties-common when add-apt-repository is missing and
skips repositories that are already configured under /etc/apt.
"""

from __future__ import annotations

import shlex
from typing import Any

from dot import Context, listing, plugin
from dot.plugins.apt import installed


@plugin("ppa")
def ppa(ctx: Context, data: Any) -> bool:
    repos, options = listing(data, "repos", "ppa")
    repos = [repo.removeprefix("ppa:") for repo in repos]
    if not ctx.which("apt-get"):
        ctx.log.error("apt-get not found; the ppa plugin needs Ubuntu")
        return False

    missing = [repo for repo in repos if not present(ctx, repo)]
    if not missing:
        ctx.log.skip(f"already added: {', '.join(repos) or 'nothing listed'}")
        return True

    ctx.log.info(f"adding: {', '.join(missing)}")
    if ctx.dry_run:
        return True

    if not ctx.which("add-apt-repository") and not installed(ctx, "software-properties-common"):
        ctx.log.info("installing software-properties-common for add-apt-repository")
        if ctx.run(ctx.sudo("apt-get install -y --no-install-recommends software-properties-common")) != 0:
            ctx.log.error("could not install software-properties-common")
            return False

    for repo in missing:
        if ctx.run(ctx.sudo(f"add-apt-repository -y -n {shlex.quote('ppa:' + repo)}")) != 0:
            ctx.log.error(f"add-apt-repository failed for {repo}")
            return False
        ctx.log.ok(f"added ppa:{repo}")

    if options.get("update", True) and ctx.run(ctx.sudo("apt-get update -qq")) != 0:
        ctx.log.error("apt-get update failed")
        return False
    return True


def present(ctx: Context, repo: str) -> bool:
    """True when a deb line or a deb822 URIs line under /etc/apt mentions the PPA."""
    escaped = "".join("\\" + char if char in ".+" else char for char in repo)
    pattern = rf"^[[:space:]]*(deb(-src)?|URIs:)[[:space:]]+.*{escaped}([[:space:]]|/|$)"
    command = f"grep -qsE {shlex.quote(pattern)} /etc/apt/sources.list /etc/apt/sources.list.d/*"
    return ctx.run(ctx.sudo(command), stdin=False, stdout=False, stderr=False) == 0
