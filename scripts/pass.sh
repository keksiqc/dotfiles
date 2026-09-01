#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

if pass-cli info &>/dev/null; then
    skip "pass-cli already authenticated."
else
    info "Authenticating with Proton Pass..."
    pass-cli login
    success "Authenticated with Proton Pass."
fi
