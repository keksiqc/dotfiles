#!/usr/bin/env bash

# Set noninteractive mode for apt
export DEBIAN_FRONTEND=noninteractive

# Check if Gum is installed
if ! command -v gum &> /dev/null; then
    echo "Gum is not installed. Installing Gum..."
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
    echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
    sudo apt update && sudo apt install gum
fi

function log_info() {
    gum log --time TimeOnly --level info "$1"
}

# Run Gum to select setup options
CHOICES=$(gum choose --no-limit "Update & Upgrade System" "Install Essential Packages" "Install Optional Packages" "Setup Dotfiles")

log_info "Starting setup with your selected options..."

if echo "$CHOICES" | grep -q "Update & Upgrade System"; then
    gum spin --spinner dot --title "Updating & Upgrading system..." -- bash -c "
        sudo apt update && sudo apt upgrade -y
    "
    log_info "System updated & upgraded."
fi

if echo "$CHOICES" | grep -q "Install Essential Packages"; then
    gum spin --spinner dot --title "Installing essential packages..." -- bash -c "
        sudo apt install -y git gh wget curl stow fish gpg starship fastfetch btop bat eza zoxide git-delta
    "
    log_info "Essential packages installed."
fi
