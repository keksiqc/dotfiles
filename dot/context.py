"""Console output and the context object handed to every plugin."""

from __future__ import annotations

import os
import pwd
import shutil
import subprocess
import sys

from dot.plugin import ConfigError, normalize


class Log:
    """Console output in the same style as scripts/utils.sh."""

    BLUE, GREEN, YELLOW, RED, MAGENTA, DIM, BOLD, RESET = (
        "\033[34m", "\033[32m", "\033[33m", "\033[31m", "\033[35m",
        "\033[2m", "\033[1m", "\033[0m",
    )

    def __init__(self, verbose: bool = False, color: bool = True) -> None:
        self.verbose = verbose
        self.color = color

    def _line(self, color: str, mark: str, msg: str, stream=sys.stdout) -> None:
        text = f"  [ {mark} ] {msg}"
        if self.color:
            text = f"{color}{text}{self.RESET}"
        print(text, file=stream, flush=True)

    def section(self, name: str) -> None:
        text = f"\n{name}"
        print(f"{self.BOLD}{text}{self.RESET}" if self.color else text, flush=True)

    def info(self, msg: str) -> None:
        self._line(self.BLUE, "→", msg)

    def ok(self, msg: str) -> None:
        self._line(self.GREEN, "✓", msg)

    def skip(self, msg: str) -> None:
        self._line(self.YELLOW, "↷", msg)

    def warn(self, msg: str) -> None:
        self._line(self.MAGENTA, "!", msg)

    def error(self, msg: str) -> None:
        self._line(self.RED, "✗", msg, stream=sys.stderr)

    def debug(self, msg: str) -> None:
        if self.verbose:
            self._line(self.DIM, "·", msg)


class Context:
    """Everything a plugin needs: paths, logging, and shell helpers."""

    def __init__(self, base_dir: str, config: dict, log: Log, dry_run: bool, keep_going: bool) -> None:
        self.base_dir = base_dir
        self.real_base_dir = os.path.realpath(base_dir)
        self.home = os.path.expanduser("~")
        self.user = pwd.getpwuid(os.getuid()).pw_name
        self.is_root = os.getuid() == 0
        self.config = config
        self.log = log
        self.dry_run = dry_run
        self.keep_going = keep_going
        self.env = dict(
            os.environ,
            DOT_BASE_DIR=base_dir,
            DOT_DRY_RUN="1" if dry_run else "0",
        )
        self._pretend_dirs: set[str] = set()  # directories "created" during a dry run

    # -- paths ------------------------------------------------------------- #

    def defaults(self, plugin_name: str) -> dict:
        """The ``[defaults.<plugin>]`` table, or ``{}``."""
        table = self.config.get("defaults", {}).get(plugin_name, {})
        if not isinstance(table, dict):
            raise ConfigError(f"[defaults.{plugin_name}] must be a table")
        return normalize(table)

    def source(self, path: str, canonical: bool = True) -> str:
        """Absolute path of a file in the dotfiles repo (``~`` and ``$VAR`` expanded)."""
        path = os.path.expandvars(os.path.expanduser(path))
        if not os.path.isabs(path):
            path = os.path.join(self.real_base_dir if canonical else self.base_dir, path)
        return os.path.normpath(path)

    def target(self, path: str) -> str:
        """Absolute path on the machine; relative paths are relative to ``~``."""
        path = os.path.expandvars(os.path.expanduser(path))
        if not os.path.isabs(path):
            path = os.path.join(self.home, path)
        return os.path.normpath(path)

    def pretty(self, path: str) -> str:
        """Shorten paths for output: repo files become relative, ``/home/you/x`` becomes ``~/x``."""
        for base in (self.real_base_dir, self.base_dir):
            if path.startswith(base + os.sep):
                return path[len(base) + 1:]
        if path == self.home or path.startswith(self.home + os.sep):
            return "~" + path[len(self.home):]
        return path

    # -- processes --------------------------------------------------------- #

    def run(
        self,
        command: str,
        *,
        cwd: str | None = None,
        stdin: bool = True,
        stdout: bool = True,
        stderr: bool = True,
        env: dict | None = None,
    ) -> int:
        """Run ``command`` through the shell in the repo dir, return its exit code."""
        self.log.debug(f"$ {command}")
        full_env = dict(self.env, **{k: str(v) for k, v in (env or {}).items()})
        proc = subprocess.run(
            command,
            shell=True,
            cwd=cwd or self.base_dir,
            env=full_env,
            stdin=None if stdin else subprocess.DEVNULL,
            stdout=None if stdout else subprocess.DEVNULL,
            stderr=None if stderr else subprocess.DEVNULL,
        )
        return proc.returncode

    def capture(self, command: str, *, cwd: str | None = None, env: dict | None = None) -> tuple[int, str]:
        """Run ``command`` silently and return ``(exit code, stdout)``."""
        self.log.debug(f"$ {command}")
        full_env = dict(self.env, **{k: str(v) for k, v in (env or {}).items()})
        proc = subprocess.run(
            command,
            shell=True,
            cwd=cwd or self.base_dir,
            env=full_env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
        )
        return proc.returncode, proc.stdout

    def check(self, condition: str) -> bool:
        """True when the shell ``condition`` exits 0 (used for ``if = "..."``)."""
        return self.run(condition, stdin=False, stdout=False, stderr=False) == 0

    def which(self, command: str) -> str | None:
        return shutil.which(command)

    def sudo(self, command: str) -> str:
        """Prefix ``command`` with ``sudo`` unless dot already runs as root."""
        return command if self.is_root else f"sudo {command}"

    # -- filesystem (all honour --dry-run) ---------------------------------- #

    def remove(self, path: str) -> None:
        if self.dry_run:
            self.log.info(f"would remove {self.pretty(path)}")
            return
        if os.path.islink(path) or not os.path.isdir(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
        self.log.debug(f"removed {self.pretty(path)}")

    def isdir(self, path: str) -> bool:
        return os.path.isdir(path) or any(path == d or path.startswith(d + os.sep) for d in self._pretend_dirs)

    def mkdir(self, path: str, mode: int = 0o777) -> None:
        if self.dry_run:
            if not self.isdir(path):
                self.log.info(f"would create {self.pretty(path)}/")
                self._pretend_dirs.add(path)
            return
        os.makedirs(path, mode=mode, exist_ok=True)
        self.log.debug(f"created {self.pretty(path)}/")

    def symlink(self, source: str, target: str, relative: bool = False) -> None:
        value = os.path.relpath(source, os.path.dirname(target)) if relative else source
        if self.dry_run:
            self.log.info(f"would link {self.pretty(target)} → {self.pretty(source)}")
            return
        os.symlink(value, target)
