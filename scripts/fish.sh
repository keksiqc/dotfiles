#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

if test -f "$HOME/.config/fish/functions/fisher.fish"; then
    skip "fisher already installed."
else
    info "Installing fisher..."
    fish -c "curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source; fisher install jorgebucaran/fisher"
    success "fisher installed."
fi

info "Installing fisher plugins..."
fish -c "fisher install joseluisq/gitnow"
success "fisher plugins installed."
