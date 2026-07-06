#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

if command -v mise &>/dev/null; then
    skip "mise already installed."
else
    info "Installing mise..."
    sudo add-apt-repository -y ppa:jdxcode/mise
    sudo apt update
    sudo apt install -y mise
    success "mise installed."
fi

info "Running mise trust..."
mise trust

info "Installing mise packages..."
mise install

success "mise setup complete."
