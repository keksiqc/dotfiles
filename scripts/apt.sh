#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=utils.sh
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

if [[ ! -r /etc/os-release ]]; then
  error "Cannot determine the operating system."
  exit 1
fi

# shellcheck source=/etc/os-release
source /etc/os-release
if [[ "${ID:-}" != "ubuntu" ]]; then
  error "This bootstrap currently supports Ubuntu only (detected: ${ID:-unknown})."
  exit 1
fi

require_command apt-get sudo

info "Installing apt bootstrap prerequisites..."
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  software-properties-common
success "Apt bootstrap prerequisites installed."

info "Adding apt repositories..."

info "Adding Fish repository..."
fish_repo_present() {
  local source_file
  for source_file in /etc/apt/sources.list /etc/apt/sources.list.d/*; do
    [[ -f "$source_file" ]] || continue
    if sudo grep -qsE \
      '^[[:space:]]*(deb(-src)?|URIs:)[[:space:]]+.*fish-shell/release-4([[:space:]]|/|$)' \
      "$source_file"; then
      return 0
    fi
  done
  return 1
}

if fish_repo_present; then
  skip "Fish repository already added."
else
  sudo add-apt-repository ppa:fish-shell/release-4 -y
  success "Fish repository added."
fi

info "Updating apt packages..."
sudo apt-get update -qq
success "Apt packages updated."
