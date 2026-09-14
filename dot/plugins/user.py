"""
[user]
shell = "fish"            # login shell, a name on PATH or an absolute path
groups = ["docker"]       # supplementary groups to join
name = "keksi"            # default: the user running dot

Adds the shell to /etc/shells when needed, changes it with chsh, and adds the
user to groups with usermod. Group changes apply after the next login.
"""

from __future__ import annotations

import grp
import os
import pwd
import shlex
from typing import Any

from dot import ConfigError, Context, normalize, plugin


@plugin("user")
def user(ctx: Context, data: Any) -> bool:
    if not isinstance(data, dict):
        raise ConfigError("[user] must be a table with shell = ... and/or groups = [...]")
    options = normalize(data)
    name = str(options.get("name") or ctx.user)
    try:
        entry = pwd.getpwnam(name)
    except KeyError:
        ctx.log.error(f"no such user: {name}")
        return False

    success = True
    if options.get("shell"):
        success &= _set_shell(ctx, entry, str(options["shell"]))
    groups = options.get("groups", [])
    for group in [groups] if isinstance(groups, str) else groups:
        success &= _add_to_group(ctx, entry, str(group))
    if not options.get("shell") and not groups:
        ctx.log.skip("nothing to do: set shell = ... or groups = [...]")
    return success


def _set_shell(ctx: Context, entry: pwd.struct_passwd, shell: str) -> bool:
    path = shell if os.path.isabs(shell) else ctx.which(shell)
    if not path or not os.path.isfile(path):
        ctx.log.error(f"shell not found: {shell}")
        return False
    if entry.pw_shell == path:
        ctx.log.skip(f"login shell of {entry.pw_name} is already {path}")
        return True

    ctx.log.info(f"setting login shell of {entry.pw_name} to {path}")
    if ctx.dry_run:
        return True
    if path not in _shells():
        if ctx.run(ctx.sudo(f"sh -c {shlex.quote(f'echo {path} >> /etc/shells')}")) != 0:
            ctx.log.error(f"could not add {path} to /etc/shells")
            return False
    if ctx.run(ctx.sudo(f"chsh -s {shlex.quote(path)} {shlex.quote(entry.pw_name)}")) != 0:
        ctx.log.error("chsh failed")
        return False
    ctx.log.ok(f"login shell of {entry.pw_name} is now {path}")
    return True


def _shells() -> list[str]:
    try:
        with open("/etc/shells") as handle:
            return [line.strip() for line in handle if line.strip() and not line.startswith("#")]
    except OSError:
        return []


def _add_to_group(ctx: Context, entry: pwd.struct_passwd, group: str) -> bool:
    try:
        info = grp.getgrnam(group)
    except KeyError:
        ctx.log.error(f"no such group: {group}")
        return False
    if entry.pw_name in info.gr_mem or entry.pw_gid == info.gr_gid:
        ctx.log.skip(f"{entry.pw_name} is already in group {group}")
        return True

    ctx.log.info(f"adding {entry.pw_name} to group {group}")
    if ctx.dry_run:
        return True
    if ctx.run(ctx.sudo(f"usermod -aG {shlex.quote(group)} {shlex.quote(entry.pw_name)}")) != 0:
        ctx.log.error(f"usermod failed for group {group}")
        return False
    ctx.log.ok(f"{entry.pw_name} added to group {group}  (takes effect after the next login)")
    return True
