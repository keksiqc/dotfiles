"""
shell = "scripts/setup.sh"

[[shell]]
run = "scripts/mise.sh"
desc = "Install mise"
if = "command -v curl"             # skip the step when this exits non-zero
quiet = false                      # true silences stdin/stdout/stderr
cwd = "~"                          # default: the repo directory
env = { FOO = "bar" }

Commands run with DOT_BASE_DIR and DOT_DRY_RUN in their environment.
"""

from __future__ import annotations

from typing import Any

from dot import ConfigError, Context, normalize, plugin


@plugin("shell")
def shell(ctx: Context, data: Any) -> bool:
    items = data if isinstance(data, list) else [data]
    success = True
    for item in items:
        options = ctx.defaults("shell")
        if isinstance(item, str):
            options["run"] = item
        elif isinstance(item, dict):
            options.update(normalize(item))
        else:
            raise ConfigError("[shell] entries must be a command string or a table")

        command = options.get("run") or options.get("command")
        if not command:
            raise ConfigError('[shell] each entry needs  run = "..."')
        description = options.get("desc") or options.get("description") or command

        condition = options.get("if")
        if condition is not None and not ctx.check(condition):
            ctx.log.skip(f"{description}  (if: {condition})")
            continue

        ctx.log.info(description)
        if ctx.dry_run:
            ctx.log.debug(f"would run: {command}")
            continue

        loud = not options.get("quiet", False)
        code = ctx.run(
            command,
            cwd=ctx.target(options["cwd"]) if options.get("cwd") else None,
            stdin=options.get("stdin", loud),
            stdout=options.get("stdout", loud),
            stderr=options.get("stderr", loud),
            env=options.get("env"),
        )
        if code == 0:
            ctx.log.ok(description)
        else:
            ctx.log.error(f"{description}  (exit code {code})")
            success = False
            if not ctx.keep_going:
                break
    return success
