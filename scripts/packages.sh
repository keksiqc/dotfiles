#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

info "Updating apt..."
sudo apt update -qq

info "Autoremove unnecessary packages..."
sudo apt autoremove -y

info "Installing packages..."
sudo apt install -y \
    git \
    wget \
    curl \
    stow \
    gpg \
    fastfetch \
    btop \
    bat \
    eza \
    zoxide \
    git-delta

success "Packages installed."
