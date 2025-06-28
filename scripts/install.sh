#!/bin/bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if stow is installed
if ! command -v stow &> /dev/null; then
    print_error "stow is not installed. Please install it first."
    exit 1
fi

# Check if we're in a dotfiles directory
if [[ ! -d ".config" && ! -d "git" ]]; then
    print_error "This doesn't appear to be a dotfiles directory (.config or git directories not found)"
    exit 1
fi

print_status "Starting dotfiles installation..."

# Stow .config if it exists
if [[ -d ".config" ]]; then
    print_status "Stowing .config directory..."
    if stow --adopt -t ~/.config .config; then
        print_status "Successfully stowed .config"
    else
        print_error "Failed to stow .config"
        exit 1
    fi
else
    print_warning ".config directory not found, skipping..."
fi

# Stow git if it exists
if [[ -d "git" ]]; then
    print_status "Stowing git directory..."
    if stow git; then
        print_status "Successfully stowed git"
    else
        print_error "Failed to stow git"
        exit 1
    fi
else
    print_warning "git directory not found, skipping..."
fi

print_status "Dotfiles installation completed successfully!"
