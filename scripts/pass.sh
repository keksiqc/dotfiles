#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=utils.sh
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

require_command pass-cli

if pass-cli info &>/dev/null; then
  skip "pass-cli already authenticated."
else
  info "Authenticating with Proton Pass..."
  pass-cli login
  success "Authenticated with Proton Pass."
fi
