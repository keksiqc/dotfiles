#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

if command -v mise &>/dev/null; then
    skip "mise already installed."
else
    info "Installing mise..."
    sudo apt install -y mise
    success "mise installed."
fi

info "Running mise trust..."
mise trust

info "Running mise bootstrap..."
mise bootstrap

success "mise setup complete."
