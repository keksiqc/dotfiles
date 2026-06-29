#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

if command -v fish &>/dev/null; then
    skip "fish already installed."
else
    info "Installing fish 4..."
    sudo add-apt-repository -y ppa:fish-shell/release-4
    sudo apt update -qq
    sudo apt install -y fish
    success "fish installed."
fi

if [[ "$SHELL" == "$(command -v fish)" ]]; then
    skip "fish is already the default shell."
else
    info "Setting fish as default shell..."
    chsh -s "$(command -v fish)"
    success "Default shell set to fish."
fi

if test -f "$HOME/.config/fish/functions/fisher.fish"; then
    skip "fisher already installed."
else
    info "Installing fisher..."
    fish -c "curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source; fisher install jorgebucaran/fisher"
    success "fisher installed."
fi

info "Installing fisher plugins..."
fish -c "fisher install joseluisq/gitnow catppuccin/fish"
success "fisher plugins installed."
