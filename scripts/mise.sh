#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

if command -v mise &>/dev/null; then
    skip "mise already installed."
else
    info "Installing mise..."
    curl -fsSL https://mise.run | sh
    success "mise installed."
fi

info "Running mise trust..."
mise trust

info "Installing mise packages..."
mise install

success "mise setup complete."
