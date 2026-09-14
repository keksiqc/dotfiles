"""Command line entry point: load config and plugins, run the steps."""

from __future__ import annotations

import argparse
import os
import sys
import tomllib
import traceback

import dot
from dot.context import Context, Log
from dot.plugin import PLUGINS, ConfigError, load_builtin_plugins, load_plugins, resolve

RESERVED = ("dot", "defaults")


def find_config(explicit: str | None) -> str:
    """``-c`` wins, then ./dot.toml, then dot.toml in the repo that contains this package."""
    if explicit:
        if not os.path.isfile(explicit):
            raise ConfigError(f"config not found: {explicit}")
        return os.path.abspath(explicit)
    repo_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    for candidate in ("dot.toml", os.path.join(repo_root, "dot.toml")):
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)
    raise ConfigError("no dot.toml found here or next to the dot package (use -c)")


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dot",
        description="Install dotfiles from a TOML file.",
        epilog="Steps run in the order they appear in the config. Exit code: 0 ok, 1 a step failed, 2 bad config.",
    )
    parser.add_argument("-c", "--config", metavar="FILE", help="config file (default: ./dot.toml, then the repo's)")
    parser.add_argument("-d", "--base-dir", metavar="DIR", help="dotfiles directory (default: the config's directory)")
    parser.add_argument("-n", "--dry-run", action="store_true", help="print what would happen without changing anything")
    parser.add_argument("-k", "--keep-going", action="store_true", help="continue with the next step after a failure")
    parser.add_argument("--only", nargs="+", metavar="STEP", default=[], help="run only these steps (or plugins)")
    parser.add_argument("--skip", nargs="+", metavar="STEP", default=[], help="skip these steps (or plugins)")
    parser.add_argument("-p", "--plugin", action="append", metavar="FILE", default=[], help="load a plugin file")
    parser.add_argument("--plugin-dir", action="append", metavar="DIR", default=[], help="load every *.py in a directory")
    parser.add_argument("-l", "--list", action="store_true", help="list steps and plugins, then exit")
    parser.add_argument("-v", "--verbose", action="store_true", help="show commands and extra detail")
    parser.add_argument("--no-color", action="store_true", help="disable colored output")
    parser.add_argument("--version", action="version", version=f"dot {dot.__version__}")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    color = not args.no_color and not os.environ.get("NO_COLOR") and sys.stdout.isatty()
    log = Log(verbose=args.verbose, color=color)

    try:
        config_path = find_config(args.config)
        base_dir = os.path.abspath(args.base_dir) if args.base_dir else os.path.dirname(config_path)
        with open(config_path, "rb") as handle:
            config = tomllib.load(handle)
        log.debug(f"config {config_path}")
        log.debug(f"base dir {base_dir}")

        ctx = Context(base_dir, config, log, dry_run=args.dry_run, keep_going=args.keep_going)

        settings = config.get("dot", {})
        if not isinstance(settings, dict):
            raise ConfigError("[dot] must be a table")
        load_builtin_plugins()
        plugin_paths = [ctx.source(p) for p in settings.get("plugins", [])]
        plugin_paths += [os.path.abspath(p) for p in args.plugin + args.plugin_dir]
        load_plugins(plugin_paths, log)

        steps = []
        for name, data in config.items():
            if name in RESERVED:
                continue
            found = resolve(name)
            steps.append((name, found[0] if found else None, data))

        def selected(name: str, plugin_name: str | None, names: list[str]) -> bool:
            return name in names or plugin_name in names

        for wanted in args.only + args.skip:
            if not any(selected(name, plugin_name, [wanted]) for name, plugin_name, _ in steps):
                raise ConfigError(f"no step or plugin named {wanted!r} in {config_path}")
        if args.only:
            steps = [s for s in steps if selected(s[0], s[1], args.only)]
        steps = [s for s in steps if not selected(s[0], s[1], args.skip)]
    except tomllib.TOMLDecodeError as error:
        log.error(f"invalid TOML in config: {error}")
        return 2
    except ConfigError as error:
        log.error(str(error))
        return 2

    if args.list:
        print(f"config   {config_path}\nbase dir {base_dir}\n\nsteps")
        for name, plugin_name, data in steps:
            count = len(data) if isinstance(data, (dict, list)) else 1
            handled = f"plugin {plugin_name}" if plugin_name else "<- no plugin registered for this step"
            print(f"  {name:<14} {count:>3} entr{'y' if count == 1 else 'ies'}   {handled}")
        print("\nplugins")
        for name, handler in PLUGINS.items():
            print(f"  {name:<14} {handler.__module__}")
        return 0

    if args.dry_run:
        log.warn("dry run: nothing will be changed")

    failed: list[str] = []
    for name, plugin_name, data in steps:
        log.section(name)
        if plugin_name is None:
            log.error(f"no plugin registered for step [{name}]")
            failed.append(name)
        else:
            try:
                ok = PLUGINS[plugin_name](ctx, data)
            except ConfigError as error:
                log.error(str(error))
                ok = False
            except (KeyboardInterrupt, BrokenPipeError):
                raise
            except Exception:  # noqa: BLE001 - a plugin bug must not take down the run silently
                log.error(f"plugin {plugin_name!r} crashed:")
                traceback.print_exc()
                ok = False
            if not ok:
                failed.append(name)
        if failed and not args.keep_going:
            break

    print()
    if failed:
        log.error(f"{len(failed)} step(s) failed: {', '.join(failed)}")
        return 1
    log.ok(f"all {len(steps)} step(s) completed")
    return 0


def run() -> None:
    """Run ``main`` and exit; handles Ctrl-C and ``dot | head`` quietly."""
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
