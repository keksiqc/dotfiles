#!/bin/bash
set -euo pipefail

# === CONFIGURATION ===
NAME="Keksi"
EMAIL="me@keksi.dev"
EXPIRE="3y"
COMMENT="GitHub Signing Key"

# === DETECT HOSTNAME & WSL ===
HOSTNAME_STR=$(hostname)
if grep -qi microsoft /proc/version 2>/dev/null; then
    ENV_TAG="WSL"
else
    ENV_TAG="Linux"
fi

# === CHECK DEPENDENCIES ===
command -v gpg >/dev/null || { echo "Error: gpg not installed"; exit 1; }
command -v gh >/dev/null || { echo "Error: gh not installed"; exit 1; }

# === CREATE GPG KEY (Ed25519) ===
echo "🔑 Creating Ed25519 GPG key for ${NAME} <${EMAIL}>..."
gpg --batch --full-generate-key <<EOF
Key-Type: eddsa
Key-Curve: ed25519
Subkey-Type: eddsa
Subkey-Curve: ed25519
Name-Real: ${NAME}
Name-Comment: ${COMMENT} - ${HOSTNAME_STR} - ${ENV_TAG}
Name-Email: ${EMAIL}
Expire-Date: ${EXPIRE}
%no-protection
%commit
EOF

# === GET KEY ID (machine-readable) ===
KEY_ID=$(gpg --list-secret-keys --with-colons "$EMAIL" | \
    awk -F: '/^sec/ {print $5; exit}')

if [ -z "$KEY_ID" ]; then
    echo "❌ Error: Could not find generated GPG key for $EMAIL"
    exit 1
fi

echo "✅ Generated GPG key ID: $KEY_ID"

# === EXPORT AND ADD TO GITHUB ===
echo "📤 Adding GPG key to GitHub..."
gpg --armor --export "$KEY_ID" | \
    gh gpg-key add - --title "GPG Key - ${HOSTNAME_STR} - ${ENV_TAG} - $(date +%Y-%m-%d)"

# === UPDATE GIT CONFIG ===
echo "📝 Updating global git config..."
git config --global user.name "$NAME"
git config --global user.email "$EMAIL"
git config --global user.signingkey "$KEY_ID"
git config --global commit.gpgsign true
git config --global gpg.program gpg

echo "🎉 All done!"
echo "Your commits will now be signed with GPG key: $KEY_ID"
