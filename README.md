<h1 align="center"><i>/home/keksi/.config</i></h1>

<p align="center">
  <img alt="Repo Size" src="https://custom-icon-badges.demolab.com/github/repo-size/keksiqc/dotfiles?style=for-the-badge&logo=file-zip&color=004b72&logoColor=f7f7f7&labelColor=1e1e1e" />
  <img alt="Last Commit (branch)" src="https://custom-icon-badges.demolab.com/github/last-commit/keksiqc/dotfiles?style=for-the-badge&logo=history&color=c586c0&logoColor=f7f7f7&labelColor=1e1e1e" />
  <img alt="License" src="https://custom-icon-badges.demolab.com/github/license/keksiqc/dotfiles?style=for-the-badge&logo=law&color=6a9955&logoColor=f7f7f7&labelColor=1e1e1e" />
</p>

---

<p align="center"><samp>Preview</samp></p>

<p align="center">
  <img alt="Terminal Preview" src="./assets/terminal.png" width="100%">
</p>

<p align="center">
  <sub>
    <samp>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbspTheme | <a href="https://rosepinetheme.com/">Rosé Pine</a><br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Font | <a href="https://usgraphics.com/products/berkeley-mono">Berkeley Mono</a><br>
      Shell | <a href="https://fishshell.com/">Fish</a><br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Prompt | <a href="https://starship.rs/">Starship</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    </samp>
  </sub>
</p>

### Requirements

1. Update system packages

```bash
sudo apt update && sudo apt upgrade -y
```

2. Install git (Python 3.11+ is already part of Ubuntu 24.04 and newer)

```bash
sudo apt install -y git
```

### Installation

```bash
git clone https://github.com/keksiqc/dotfiles ~/.dotfiles && ~/.dotfiles/install
```

This runs [`dot`](./dot) with [`dot.toml`](./dot.toml), which:

- Removes dead symlinks in `~` that point into this repo
- Symlinks the configs under `.config/`
- Sets up passwordless sudo
- Adds apt repositories (fish)
- Installs mise and the tools in `.config/mise`
- Installs fisher and fish plugins
- Logs in to the GitHub CLI and sets up GPG commit signing
- Logs in to Proton Pass and loads SSH keys

Useful flags (all in `./install --help`):

```bash
./install -n              # dry run: show what would change
./install --only link     # run only some steps
./install --skip shell    # run everything except some steps
./install --list          # show steps and loaded plugins
```

### dot

`dot` is a single-file, zero-dependency replacement for [dotbot](https://github.com/anishathalye/dotbot).
It needs nothing but Python 3.11+ (for the built-in TOML parser) and lives in this repo as [`dot`](./dot).
Copy that one file into any dotfiles repo next to a `dot.toml` and it works.

#### Config

Every top-level table (or key) in `dot.toml` is a **step**, handled by the plugin of the same name.
Steps run in the order they appear in the file. `[dot]` and `[defaults]` are settings, not steps.

```toml
[dot]
plugins = ["plugins"]         # extra plugin files or directories (relative to the repo)

[defaults.link]               # default options for every entry of a plugin
create = true
relink = true

clean = ["~", "~/.config"]    # remove dead symlinks that point into this repo
create = ["~/i", "~/.ssh"]    # create directories

[link]
"~/.config/bat" = true        # true = same path inside the repo (.config/bat)
"~/.vimrc" = "vim/vimrc"      # explicit source, relative to the repo
"~/.config/nvim" = { path = "nvim", if = "command -v nvim" }
"~/.config" = { path = "config/*", glob = true, exclude = ["config/private*"] }

[[shell]]
run = "scripts/mise.sh"
desc = "Install mise and packages"
if = "command -v curl"        # skip when this shell condition fails
```

| Plugin   | Entry options                                                                                                                                                                          |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `link`   | `path`, `create` (parent dirs), `relink` (replace other symlinks), `force` (replace files/dirs), `if`, `glob`, `exclude`, `relative`, `ignore-missing`, `canonicalize` (default `true`) |
| `create` | `mode` (e.g. `0o700`)                                                                                                                                                                  |
| `clean`  | `force` (remove every dead symlink, not only ones into this repo), `recursive`                                                                                                          |
| `shell`  | `run` (or `command`), `desc`, `if`, `quiet`, `stdin`/`stdout`/`stderr` (default `true`), `cwd`, `env`                                                                                  |

`clean` and `create` also accept a table (`[clean] "~" = { force = true }`), and `shell` accepts a plain
string or a list of strings. Shell steps run in the repo directory with `DOT_BASE_DIR` and `DOT_DRY_RUN` set.
A failing step stops the run (exit code 1) unless you pass `-k`; a broken config exits with 2.

#### Plugins

A plugin is a Python file that registers a handler for a step name. Point `[dot] plugins` at the file
(or a directory of files), or pass `--plugin FILE` / `--plugin-dir DIR`.

```python
# plugins/apt.py
import dot


@dot.plugin("apt")
def apt(ctx, data):
    """[apt] packages = ["fish", "git"]"""
    packages = data["packages"]
    missing = [p for p in packages if ctx.run(f"dpkg -s {p}", stdin=False, stdout=False, stderr=False) != 0]
    if not missing:
        ctx.log.skip("all apt packages are installed")
        return True
    ctx.log.info("installing " + " ".join(missing))
    if ctx.dry_run:
        return True
    return ctx.run("sudo apt-get install -y " + " ".join(missing)) == 0
```

The handler receives the raw TOML value of the step and returns `True` or `False`. Raise `dot.ConfigError`
for a malformed step. The `ctx` object gives you:

- `ctx.base_dir`, `ctx.home`, `ctx.dry_run`, `ctx.config`
- `ctx.defaults("apt")` for the `[defaults.apt]` table
- `ctx.source(path)` and `ctx.target(path)` to resolve paths against the repo or `~`, `ctx.pretty(path)` for output
- `ctx.run(cmd, ...)`, `ctx.check(condition)`, `ctx.which(cmd)`
- `ctx.remove(path)`, `ctx.mkdir(path)`, `ctx.symlink(src, dst)`, which all respect `--dry-run`
- `ctx.log.info / ok / skip / warn / error / debug`

### Notes on security

Some steps use curl | sh for convenience. Review scripts before running if
unsure.

### License

MIT — see [LICENSE](./LICENSE).
