#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

info "Updating apt packages..."
sudo apt update -qq
success "Apt packages updated."

info "Adding apt repositories..."

info "Adding Fish repository..."
if sudo grep -RqsE \
  '^[[:space:]]*(deb(-src)?|URIs:)[[:space:]]+.*fish-shell/release-4([[:space:]]|/|$)' \
  /etc/apt/sources.list /etc/apt/sources.list.d; then
  skip "Fish repository already added."
else
  sudo add-apt-repository ppa:fish-shell/release-4 -y
  success "Fish repository added."
fi

info "Updating apt packages..."
sudo apt update -qq
success "Apt packages updated."
