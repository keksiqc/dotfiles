if status is-interactive
    # Set theme to Catppuccin Mocha
    fish_config theme choose "catppuccin-mocha"

    # Add local bin to path
    fish_add_path $HOME/.local/bin

    # Better cat with bat
    command -v bat &> /dev/null && alias cat="bat"

    # Better ls with eza
    command -v eza &> /dev/null && alias ls="eza --group --header --group-directories-first --git --icons -1"

    # Abbrs
    abbr l "ls"
    abbr ll "ls -l"
    abbr la "ls -la"
    abbr tree "ls -T"

    abbr neofetch "fastfetch"
    abbr fetch "fastfetch"

    abbr m "mise"
    abbr mr "mise run"
    abbr mx "mise exec"
    abbr mi "mise install"

    # Initialization
    command -v fzf &> /dev/null && fzf --fish | source
    command -v starship &> /dev/null && starship init fish | source
    command -v atuin &> /dev/null && atuin init fish | source
    command -v zoxide &> /dev/null && zoxide init fish --cmd cd | source
    command -v mise &> /dev/null && mise activate fish | source

    # Environment variables
    set -gx PROTON_PASS_KEY_PROVIDER "fs"

    set -gx NI_DEFAULT_AGENT "bun"
    set -gx NI_GLOBAL_AGENT "bun"
end
