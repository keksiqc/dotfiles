#!/usr/bin/env bash
set -euo pipefail

GPG_NAME="Keksi"
GPG_EMAIL="git@keksi.dev"
GPG_EXPIRE="3y"

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

if gh auth status &>/dev/null; then
    skip "gh already authenticated."
else
    info "Authenticating with GitHub..."
    gh auth login -s write:gpg_key
    success "Authenticated with GitHub."
fi

if gpg --list-secret-keys --with-colons "$GPG_EMAIL" 2>/dev/null | grep -q '^sec'; then
    skip "GPG key already exists for $GPG_EMAIL."
else
    info "Generating GPG key..."
    hostname_str=$(hostname)
    env_tag="Linux"
    grep -qi microsoft /proc/version 2>/dev/null && env_tag="WSL"

    gpg --batch --full-generate-key <<GPGEOF
Key-Type: eddsa
Key-Curve: ed25519
Subkey-Type: eddsa
Subkey-Curve: ed25519
Name-Real: ${GPG_NAME}
Name-Comment: GitHub Signing Key - ${hostname_str} - ${env_tag}
Name-Email: ${GPG_EMAIL}
Expire-Date: ${GPG_EXPIRE}
%no-protection
%commit
GPGEOF

    key_id=$(gpg --list-secret-keys --with-colons "$GPG_EMAIL" | awk -F: '/^sec/ {print $5; exit}')

    info "Uploading GPG key to GitHub..."
    gpg --armor --export "$key_id" \
        | gh gpg-key add - --title "GPG Key - ${hostname_str} - ${env_tag} - $(date +%Y-%m-%d)"

    info "Configuring git signing..."
    git config --global user.signingkey "$key_id"
    git config --global commit.gpgsign true
    git config --global gpg.program gpg
    git config --global include.path "~/.dotfiles/.gitconfig"

    success "GPG key created and configured (ID: $key_id)."
fi
