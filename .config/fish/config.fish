# disable greeting
set fish_greeting ""

# show fastfetch on interactive shell
if status --is-interactive && type -q fastfetch
   fastfetch
end

# https://github.com/jorgebucaran/fisher
# curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
# fisher install catppuccin/fish
fish_config theme choose "catppuccin-mocha"

# -------------------------------- #
# Directory Listing (eza)
# -------------------------------- #
# https://github.com/eza-community/eza

set -gx EZA_BASE "eza --group --header --group-directories-first --long --git --icons"

alias l="$EZA_BASE -1"
alias ls="$EZA_BASE --no-permissions --no-user"
alias ll="$EZA_BASE"
alias la="$EZA_BASE --all"

# -------------------------------- #
# Essentials
# -------------------------------- #

alias cd="z"
alias poe="uv run poe"
alias neofetch="fastfetch"
alias fetch="fastfetch"
alias bat="batcat"
alias cat="bat"

# -------------------------------- #
# Node Package Manager
# -------------------------------- #
# https://github.com/antfu/ni

set -gx NI_DEFAULT_AGENT "bun"
set -gx NI_GLOBAL_AGENT "bun"

alias nrr="nr -r"
alias ng="na -g"
alias nio="ni --prefer-offline"
alias s="nr start"
alias d="nr dev"
alias b="nr build"
alias bw="nr build --watch"
alias t="nr test"
alias tu="nr test -u"
alias tw="nr test --watch"
alias w="nr watch"
alias p="nr play"
alias c="nr typecheck"
alias lint="nr lint"
alias lintf="nr lint --fix"
alias release="nr release"
alias re="nr release"

# -------------------------------- #
# Python Package Manager
# -------------------------------- #
# https://github.com/astral-sh/uv

alias uvr="uv run"

# -------------------------------- #
# Git
# -------------------------------- #

# Use jj-vcs/jj
# alias git=jj

# -------------------------------- #
# Path
# -------------------------------- #

fish_add_path /home/keksi/.opencode/bin

# -------------------------------- #
# Initialization
# -------------------------------- #

# mise
if type -q ~/.local/bin/mise
  ~/.local/bin/mise activate fish | source
end

# starship
if type -q starship
  starship init fish | source
end

# zoxide
if type -q zoxide
  zoxide init fish | source
end

# atuin
if type -q atuin
  atuin init fish | source
end

# pnpm
set -gx PNPM_HOME "/home/keksi/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end

# Vite+ bin (https://viteplus.dev)
test -f "$HOME/.vite-plus/env.fish" && source "$HOME/.vite-plus/env.fish"
