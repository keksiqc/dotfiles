#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

if ! command -v pass-cli &>/dev/null; then
    info "Installing pass-cli..."
    curl -fsSL https://proton.me/download/pass-cli/install.sh | bash
    success "pass-cli installed."
else 
    info "pass-cli already installed."
fi 

if pass-cli info &>/dev/null; then
    skip "pass-cli already authenticated."
else
    info "Authenticating with Proton Pass..."
    pass-cli login
    success "Authenticated with Proton Pass."
fi
