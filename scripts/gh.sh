#!/usr/bin/env bash
set -euo pipefail

GPG_NAME="Keksi"
GPG_EMAIL="git@keksi.dev"
GPG_EXPIRE="3y"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
DOTFILES_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd -P)"

source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

gpg_key_fingerprint() {
  gpg --list-secret-keys --with-colons "$GPG_EMAIL" 2>/dev/null |
    awk -F: '
      $1 == "sec" { in_secret_key = 1; next }
      in_secret_key && $1 == "fpr" && !fingerprint { fingerprint = $10 }
      END {
        if (fingerprint) print fingerprint
        else exit 1
      }
    '
}

if gh auth status --hostname github.com &>/dev/null; then
  skip "gh already authenticated."
else
  info "Authenticating with GitHub..."
  gh auth login --hostname github.com --scopes write:gpg_key
  success "Authenticated with GitHub."
fi

hostname_str=$(hostname)
env_tag="Linux"
if grep -qi microsoft /proc/version 2>/dev/null; then
  env_tag="WSL"
fi

if key_fingerprint=$(gpg_key_fingerprint); then
  skip "GPG key already exists for $GPG_EMAIL."
else
  info "Generating GPG key..."

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

  key_fingerprint=$(gpg_key_fingerprint)
  success "GPG key generated."
fi

short_key_id=${key_fingerprint: -16}
if gh api --hostname github.com user/gpg_keys --jq '.[].key_id' 2>/dev/null |
  awk -v key_id="$short_key_id" 'tolower($0) == tolower(key_id) { found = 1 } END { exit !found }'; then
  skip "GPG key already uploaded to GitHub."
else
  info "Refreshing GitHub permissions for GPG key management..."
  gh auth refresh --hostname github.com --scopes write:gpg_key

  info "Uploading GPG key to GitHub..."
  gpg --armor --export "$key_fingerprint" |
    gh gpg-key add - --title "GPG Key - ${hostname_str} - ${env_tag} - $(date +%Y-%m-%d)"
  success "GPG key uploaded to GitHub."
fi

info "Configuring git signing..."
git config --global user.signingkey "$key_fingerprint"
git config --global commit.gpgsign true
git config --global gpg.program gpg
git config --global include.path "${DOTFILES_DIR}/.gitconfig"

success "Git signing configured (fingerprint: ${key_fingerprint})."
