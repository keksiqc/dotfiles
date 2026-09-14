#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

if fish -c 'type -q fisher'; then
  skip "fisher already installed."
else
  info "Installing fisher..."
  fish -c 'curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source; and fisher install jorgebucaran/fisher'
  success "fisher installed."
fi

if fish -c 'fisher list | string match -q -- "*joseluisq/gitnow*"'; then
  skip "fisher plugins already installed."
else
  info "Installing fisher plugins..."
  fish -c 'fisher install joseluisq/gitnow'
  success "fisher plugins installed."
fi
