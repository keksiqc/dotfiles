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

if test -f /etc/apt/sources.list.d/extrepo_mise.sources; then
    skip "Mise repository already added."
    info "Updating Mise repository..."
    sudo extrepo update mise
    success "Mise repository updated."
else
    info "Adding Mise apt repository..."
    sudo extrepo enable mise
    success "Mise apt repository added."
fi

if test -f /etc/apt/sources.list.d/extrepo_github-cli.sources; then
    skip "GitHub CLI repository already added."
    info "Updating GitHub CLI repository..."
    sudo extrepo update github-cli
    success "GitHub CLI repository updated."
else
    info "Adding GitHub CLI apt repository..."
    sudo extrepo enable github-cli
    success "GitHub CLI apt repository added."
fi

if test -f /etc/apt/sources.list.d/fish-shell-ubuntu-release-4-resolute.sources; then
    skip "Fish repository already added."
else
    info "Adding Fish repository..."
    sudo add-apt-repository ppa:fish-shell/release-4 -y
    success "Fish repository added."
fi

info "Updating apt packages..."
sudo apt update -qq
success "Apt packages updated."
