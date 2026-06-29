#!/usr/bin/env bash

info()    { printf '\e[34m  → %s\e[0m\n' "$*"; }
success() { printf '\e[32m  ✓ %s\e[0m\n' "$*"; }
skip()    { printf '\e[33m  ↷ %s\e[0m\n' "$*"; }
