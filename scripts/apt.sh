#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

info "Updating apt packages..."
sudo apt update -qq
success "Apt packages updated."

info "Installing extrepo..."
sudo apt install -y extrepo
success "extrepo installed."

info "Adding apt repositories..."
sudo extrepo enable mise
sudo extrepo enable github-cli
success "Apt repositories added."

info "Updating apt packages..."
sudo apt update -qq
success "Apt packages updated."
