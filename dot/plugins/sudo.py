"""
sudo = true

[sudo]
nopasswd = true           # let the user run sudo without a password
user = "keksi"            # default: the user running dot

Writes /etc/sudoers.d/<user>-nopasswd after validating it with visudo and
rolls the file back if the resulting sudoers configuration is invalid.
Refuses to touch a file that already exists with different content.
"""

from __future__ import annotations

import os
import shlex
import tempfile
from typing import Any

from dot import ConfigError, Context, normalize, plugin


@plugin("sudo")
def sudo(ctx: Context, data: Any) -> bool:
    if data is True:
        options = {}
    elif isinstance(data, dict):
        options = normalize(data)
    else:
        raise ConfigError("[sudo] must be true or a table")
    if not options.get("nopasswd", True):
        ctx.log.skip("nopasswd = false, nothing to do")
        return True

    user = str(options.get("user") or ctx.user)
    if user == "root":
        ctx.log.error("root does not need a sudoers rule; run dot as your normal user or set user = \"...\"")
        return False
    for tool in ("sudo", "visudo", "install", "cmp"):
        if not ctx.which(tool):
            ctx.log.error(f"required command not found: {tool}")
            return False

    sudoers_file = f"/etc/sudoers.d/{user}-nopasswd"
    rule = f"{user} ALL=(ALL:ALL) NOPASSWD: ALL\n"
    fd, temporary = tempfile.mkstemp(prefix="dot-sudoers-")
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(rule)
        os.chmod(temporary, 0o644)  # root must be able to read it through sudo
        return _apply(ctx, user, sudoers_file, temporary)
    finally:
        os.unlink(temporary)


def _apply(ctx: Context, user: str, sudoers_file: str, temporary: str) -> bool:
    quiet = dict(stdout=False, stderr=False)
    file = shlex.quote(sudoers_file)
    if ctx.run(ctx.sudo(f"test -e {file}"), **quiet) == 0:
        if ctx.run(ctx.sudo(f"cmp -s {temporary} {file}"), **quiet) == 0:
            ctx.log.skip(f"passwordless sudo already configured for {user}")
            return True
        ctx.log.error(f"refusing to overwrite existing {sudoers_file} with different content")
        return False

    ctx.log.info(f"enabling passwordless sudo for {user}")
    if ctx.dry_run:
        return True
    if ctx.run(ctx.sudo("visudo -c"), **quiet) != 0:
        ctx.log.error("the current sudoers configuration is invalid; fix it before adding a rule")
        return False
    if ctx.run(ctx.sudo(f"visudo -cf {temporary}"), **quiet) != 0:
        ctx.log.error("the new sudoers rule failed validation")
        return False
    if ctx.run(ctx.sudo(f"install -o root -g root -m 0440 {temporary} {file}")) != 0:
        ctx.log.error(f"could not write {sudoers_file}")
        return False
    if ctx.run(ctx.sudo("visudo -c"), **quiet) != 0:
        ctx.run(ctx.sudo(f"rm -f {file}"))
        ctx.log.error("the sudoers configuration failed validation; the new rule was removed")
        return False
    ctx.log.ok(f"passwordless sudo enabled for {user}")
    return True
