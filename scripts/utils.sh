#!/usr/bin/env bash

info() { printf '\e[34m  [ → ] %s\e[0m\n' "$*"; }
success() { printf '\e[32m  [ ✓ ] %s\e[0m\n' "$*"; }
skip() { printf '\e[33m  [ ↷ ] %s\e[0m\n' "$*"; }
error() { printf '\e[31m  [ ✗ ] %s\e[0m\n' "$*" >&2; }

require_command() {
  local command_name
  for command_name in "$@"; do
    if ! command -v "$command_name" &>/dev/null; then
      error "Required command not found: $command_name"
      return 127
    fi
  done
}
