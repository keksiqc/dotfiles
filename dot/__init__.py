"""
dot - a small, dependency-free dotfiles installer driven by a TOML file.

    bin/dot                  run every step in dot.toml
    bin/dot -n               dry run: show what would change, change nothing
    bin/dot --only link      run only these steps
    bin/dot --list           show the steps and the plugins that handle them

Every top-level table (or key) in the config is a step. Steps run in the
order they appear in the file and each one is handled by the plugin of the
same name. Built-in plugins live in dot/plugins/; extra plugins are plain
Python files that register a handler:

    import dot

    @dot.plugin("brew")
    def brew(ctx, data):
        ...
        return True

Needs Python 3.11+ (for the built-in TOML parser) and nothing else.
"""

from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    sys.exit("dot: Python 3.11 or newer is required (it ships the TOML parser)")

from dot.context import Context, Log
from dot.plugin import PLUGINS, ConfigError, entries, listing, normalize, plugin

__version__ = "1.1.0"
__all__ = ["Context", "Log", "PLUGINS", "ConfigError", "entries", "listing", "normalize", "plugin", "__version__"]
