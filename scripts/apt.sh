#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

info "Updating apt packages..."
sudo apt update -qq
success "Apt packages updated."

info "Adding apt repositories..."

info "Adding Fish repository..."
sudo add-apt-repository ppa:fish-shell/release-4 -y
success "Fish repository added."

info "Updating apt packages..."
sudo apt update -qq
success "Apt packages updated."
