#!/usr/bin/env bash
set -euo pipefail

if ! command -v apt >/dev/null 2>&1; then
  echo "This installer is for Pop!_OS/Ubuntu (apt)."
  exit 1
fi

sudo apt update
sudo apt install -y mpv python3 python3-pip pipx

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pipx ensurepath >/dev/null 2>&1 || true
pipx install -f yt-dlp

chmod +x "${SCRIPT_DIR}/yt_player.py"

sudo ln -sfn "${SCRIPT_DIR}/yt_player.py" /usr/local/bin/ytp

echo "Done."
echo "Run: ytp"
echo "Or: ${SCRIPT_DIR}/yt_player.py"
if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "Note: yt-dlp not in PATH yet. Try:"
  echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
  echo "Or log out and log in again."
fi
