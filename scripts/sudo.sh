#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=utils.sh
source "$(dirname "${BASH_SOURCE[0]}")/utils.sh"

require_command cmp id install mktemp sudo visudo

if [[ "$(id -u)" -eq 0 ]]; then
  error "Run this script as your normal user, not root."
  exit 1
fi

target_user="$(id -un)"
sudoers_file="/etc/sudoers.d/${target_user}-nopasswd"
sudoers_rule="${target_user} ALL=(ALL:ALL) NOPASSWD: ALL"
temporary_file="$(mktemp)"

cleanup() {
  rm -f -- "$temporary_file"
}
trap cleanup EXIT

printf '%s\n' "$sudoers_rule" >"$temporary_file"

if sudo test -e "$sudoers_file"; then
  if sudo cmp -s "$temporary_file" "$sudoers_file"; then
    skip "Passwordless sudo is already configured for ${target_user}."
    exit 0
  fi

  error "Refusing to overwrite existing sudoers file: $sudoers_file"
  exit 1
fi

info "Validating sudoers configuration..."
sudo visudo -c >/dev/null
sudo visudo -cf "$temporary_file" >/dev/null

info "Enabling passwordless sudo for ${target_user}..."
sudo install -o root -g root -m 0440 "$temporary_file" "$sudoers_file"

if ! sudo visudo -c >/dev/null; then
  sudo rm -f -- "$sudoers_file"
  error "The sudoers configuration failed validation; the new rule was removed."
  exit 1
fi

success "Passwordless sudo enabled for ${target_user}."
