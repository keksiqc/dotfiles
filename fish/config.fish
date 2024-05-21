if status is-interactive
    # Commands to run in interactive sessions can go here
end

# set theme
fish_config theme choose "Rosé Pine"

# load aliases from .config/fish/aliases.fish
source ~/.config/fish/aliases.fish

# starship
starship init fish | source

# zoxide
zoxide init fish | source

# pipx
set PATH $PATH /root/.local/bin

# mise
~/.local/bin/mise activate fish | source

# brew
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# set greeting
set fish_greeting "$(macchina)"
# pnpm
set -gx PNPM_HOME "/home/keksi/.local/share/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end
