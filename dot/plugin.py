"""Plugin registry and the helpers shared by built-in and user plugins."""

from __future__ import annotations

import glob
import importlib
import importlib.util
import os
import pkgutil
import re
import sys
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from dot.context import Context, Log


class ConfigError(Exception):
    """A malformed step. Reported as a plain message, without a traceback."""


Handler = Callable[["Context", Any], bool]
PLUGINS: dict[str, Handler] = {}


def plugin(*names: str) -> Callable[[Handler], Handler]:
    """Register a step handler: ``@dot.plugin("name")``.

    The handler is called as ``handler(ctx, data)`` where ``data`` is the raw
    TOML value of the step. It returns True on success, False on failure.
    Raise ``dot.ConfigError`` for a malformed step.
    """

    def register(fn: Handler) -> Handler:
        for name in names:
            PLUGINS[name] = fn
        return fn

    return register


def resolve(step: str) -> tuple[str, Handler] | None:
    """Map a step name to ``(plugin name, handler)``.

    ``[apt]`` is handled by the ``apt`` plugin; so is ``[apt-fish]``, which
    lets a plugin run more than once at different points of the config.
    """
    if step in PLUGINS:
        return step, PLUGINS[step]
    for match in reversed(list(re.finditer("-", step))):
        name = step[: match.start()]
        if name in PLUGINS:
            return name, PLUGINS[name]
    return None


def load_builtin_plugins() -> None:
    """Import every module in dot/plugins/."""
    import dot.plugins

    for info in pkgutil.iter_modules(dot.plugins.__path__):
        importlib.import_module(f"dot.plugins.{info.name}")


def load_plugins(paths: list[str], log: Log) -> None:
    """Import plugin files (or every ``*.py`` of a directory) so they register."""
    files: list[str] = []
    for path in paths:
        if os.path.isdir(path):
            files.extend(sorted(glob.glob(os.path.join(path, "*.py"))))
        elif os.path.isfile(path):
            files.append(path)
        else:
            raise ConfigError(f"plugin not found: {path}")
    for file in files:
        module_name = "dot_plugin_" + re.sub(r"\W", "_", os.path.splitext(os.path.basename(file))[0])
        spec = importlib.util.spec_from_file_location(module_name, file)
        if spec is None or spec.loader is None:
            raise ConfigError(f"cannot load plugin: {file}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        log.debug(f"loaded plugin {file}")


# --------------------------------------------------------------------------- #
# Helpers for reading step data
# --------------------------------------------------------------------------- #


def normalize(options: dict) -> dict:
    """Accept both ``ignore-missing`` and ``ignore_missing`` style keys."""
    return {str(key).replace("-", "_"): value for key, value in options.items()}


def entries(data: Any, what: str) -> list[tuple[str, dict]]:
    """Turn ``"x"``, ``["x", "y"]`` or ``{ x = true, y = { ... } }`` into
    a list of ``(path, options)`` pairs."""
    if isinstance(data, str):
        return [(data, {})]
    if isinstance(data, list):
        if not all(isinstance(item, str) for item in data):
            raise ConfigError(f"[{what}] list entries must be strings")
        return [(item, {}) for item in data]
    if isinstance(data, dict):
        result = []
        for path, options in data.items():
            if options is True or options == "":
                result.append((path, {}))
            elif isinstance(options, dict):
                result.append((path, normalize(options)))
            else:
                raise ConfigError(f"[{what}] {path!r}: value must be true or a table")
        return result
    raise ConfigError(f"[{what}] must be a string, a list of strings, or a table")


def listing(data: Any, key: str, what: str) -> tuple[list[str], dict]:
    """Turn ``x = ["a", "b"]`` or ``[x] key = ["a", "b"] <options>`` into
    ``(items, options)``."""
    if isinstance(data, str):
        return [data], {}
    if isinstance(data, list):
        items, options = data, {}
    elif isinstance(data, dict):
        options = normalize(data)
        items = options.pop(key, [])
        if isinstance(items, str):
            items = [items]
    else:
        raise ConfigError(f"[{what}] must be a list of strings or a table with {key} = [...]")
    if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
        raise ConfigError(f"[{what}] {key} must be a list of strings")
    return items, options
