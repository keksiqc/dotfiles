#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=utils.sh
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

MISE_BIN="$HOME/.local/bin/mise"

if [[ -x "$MISE_BIN" ]]; then
  skip "mise already installed."
else
  require_command curl
  info "Installing mise..."
  curl https://mise.run | sh

  if [[ ! -x "$MISE_BIN" ]]; then
    error "mise was not installed at $MISE_BIN."
    exit 1
  fi

  success "mise installed."
fi

info "Running mise trust..."
"$MISE_BIN" trust

info "Running mise bootstrap..."
"$MISE_BIN" bootstrap

success "mise setup complete."
