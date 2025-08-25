# set greeting
set fish_greeting "$(fastfetch)"

# https://github.com/jorgebucaran/fisher
# curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
# fisher install rose-pine/fish
fish_config theme choose "Rosé Pine"

# -------------------------------- #
# Directory Listing (eza)
# -------------------------------- #
# https://github.com/eza-community/eza

alias l="eza -1 --group-directories-first --color=always --icons --git-ignore"
alias ls="l --long --no-permissions --no-user"
alias ll="l --long --header"
alias la="ll --all"

# -------------------------------- #
# Essentials
# -------------------------------- #

alias cd=z
alias neofetch=fastfetch
alias fetch=fastfetch
alias cat=batcat

# -------------------------------- #
# Node Package Manager
# -------------------------------- #
# https://github.com/antfu/ni

export NI_GLOBAL_AGENT="pnpm"

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
# Initialization
# -------------------------------- #

# mise
~/.local/bin/mise activate fish | source

# starship
starship init fish | source

# zoxide
zoxide init fish | source

# atuin
atuin init fish | source

# pnpm
set -gx PNPM_HOME "/home/keksi/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end

# corepack
corepack enable

# -------------------------------- #
# Directories
#
# I put
# `~/i` for my projects
# `~/f` for forks
# `~/r` for reproductions
# -------------------------------- #

function i
  if test -z "$argv[1]"
    cd ~/i
    return
  end
  cd ~/i/$argv[1]
end

function forks
  if test -z "$argv[1]"
    cd ~/f
    return
  end
  cd ~/f/$argv[1]
end

function repros
  if test -z "$argv[1]"
    cd ~/r
    return
  end
  cd ~/r/$argv[1]
end

function dir
  if test -z "$argv[1]"
    echo "Usage: dir <directory>"
    return 1
  end
  mkdir $argv[1]; and cd $argv[1]
end

function clone
  if test (count $argv) -lt 2
    git clone $argv; and cd (basename $argv[1] .git)
  else
    git clone $argv; and cd $argv[2]
  end
end

function clonei
  i; and clone $argv; and code .; and cd -2
end

function cloner
  repros; and clone $argv; and code .; and cd -2
end

function clonef
  forks; and clone $argv; and code .; and cd -2
end

function codei
  i; and code $argv; and cd -
end
