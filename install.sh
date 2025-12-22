#!/bin/bash
set -e

# wtf installation script
# Usage: curl -sSL https://raw.githubusercontent.com/davefowler/wtf-terminal-ai/main/install.sh | bash

VERSION="0.1.0"
REPO="davefowler/wtf-terminal-ai"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   wtf - Because working in the terminal gets you asking wtf  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo ""
    echo "Please install Python 3.10 or higher:"
    echo "  macOS:   brew install python3"
    echo "  Ubuntu:  sudo apt install python3 python3-pip"
    echo "  Fedora:  sudo dnf install python3 python3-pip"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}✗ Python $PYTHON_VERSION is installed, but wtf requires Python $REQUIRED_VERSION or higher${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip3 is not installed${NC}"
    echo "Please install pip3 for your system"
    exit 1
fi

echo -e "${GREEN}✓${NC} pip3 detected"
echo ""

# Check for existing wtf command or alias
echo "Checking for command collisions..."

COLLISION_FOUND=false
COLLISION_TYPE=""
COLLISION_LOCATION=""
COLLISION_LINE=""

# Check for alias in shell config files
for config_file in ~/.zshrc ~/.bashrc ~/.bash_profile ~/.profile ~/.config/fish/config.fish; do
    if [ -f "$config_file" ]; then
        if grep -q "alias wtf=" "$config_file" 2>/dev/null; then
            COLLISION_FOUND=true
            COLLISION_TYPE="alias"
            COLLISION_LOCATION="$config_file"
            COLLISION_LINE=$(grep -n "alias wtf=" "$config_file" | head -1 | cut -d: -f1)
            break
        fi
        if grep -q "function wtf" "$config_file" 2>/dev/null; then
            COLLISION_FOUND=true
            COLLISION_TYPE="function"
            COLLISION_LOCATION="$config_file"
            COLLISION_LINE=$(grep -n "function wtf" "$config_file" | head -1 | cut -d: -f1)
            break
        fi
    fi
done

# Check if wtf command exists in PATH
if command -v wtf &> /dev/null && [ "$COLLISION_FOUND" = false ]; then
    COLLISION_FOUND=true
    COLLISION_TYPE="command"
    COLLISION_LOCATION=$(which wtf)
fi

if [ "$COLLISION_FOUND" = true ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Hold up! You already have a 'wtf' ${COLLISION_TYPE} defined.${NC}"
    echo ""

    if [ "$COLLISION_TYPE" = "alias" ] || [ "$COLLISION_TYPE" = "function" ]; then
        echo "Found in ${COLLISION_LOCATION} (line ${COLLISION_LINE})"
        echo ""
        echo "We get it - everyone has a wtf alias. It's like a developer rite of passage."
    else
        echo "Found at: ${COLLISION_LOCATION}"
    fi

    echo ""
    echo "Options:"
    echo "  1) Install as 'wtfai' instead (recommended)"
    echo "  2) Install as 'wai' (shorter)"
    echo "  3) Cancel installation"
    echo ""
    read -p "Choose [1-3]: " choice

    case $choice in
        1)
            COMMAND_NAME="wtfai"
            ;;
        2)
            COMMAND_NAME="wai"
            ;;
        3)
            echo "Installation cancelled."
            exit 0
            ;;
        *)
            echo "Invalid choice. Installation cancelled."
            exit 1
            ;;
    esac
else
    COMMAND_NAME="wtf"
fi

echo ""
echo "Installing wtf-ai..."
echo ""

# Install wtf-ai from GitHub (not yet published to PyPI)
GITHUB_URL="git+https://github.com/${REPO}.git"

if pip3 install --user "$GITHUB_URL" 2>&1 | grep -q "Successfully installed"; then
    echo -e "${GREEN}✓${NC} wtf-ai installed successfully"
else
    # Try without --user flag
    if pip3 install "$GITHUB_URL" 2>&1 | grep -q "Successfully installed"; then
        echo -e "${GREEN}✓${NC} wtf-ai installed successfully"
    else
        echo -e "${RED}✗${NC} Installation failed"
        echo ""
        echo "You can try installing manually:"
        echo "  pip3 install git+https://github.com/${REPO}.git"
        exit 1
    fi
fi

# If using alternative name, create symlink
if [ "$COMMAND_NAME" != "wtf" ]; then
    INSTALL_DIR=$(python3 -c "import site; print(site.USER_BASE + '/bin')")

    if [ ! -d "$INSTALL_DIR" ]; then
        mkdir -p "$INSTALL_DIR"
    fi

    if [ -f "$INSTALL_DIR/wtf" ]; then
        ln -sf "$INSTALL_DIR/wtf" "$INSTALL_DIR/$COMMAND_NAME"
        echo -e "${GREEN}✓${NC} Created symlink: $COMMAND_NAME -> wtf"
    else
        echo -e "${YELLOW}⚠${NC}  Could not create symlink. You may need to add it manually."
    fi
fi

# Check if user bin is in PATH
USER_BIN=$(python3 -c "import site; print(site.USER_BASE + '/bin')" 2>/dev/null || echo "$HOME/.local/bin")

if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
    echo ""
    echo -e "${YELLOW}⚠${NC}  The installation directory is not in your PATH."
    echo ""
    echo "Add this to your shell config file (~/.zshrc or ~/.bashrc):"
    echo ""
    echo -e "${CYAN}export PATH=\"\$PATH:$USER_BIN\"${NC}"
    echo ""
    echo "Then restart your shell or run:"
    echo -e "${CYAN}source ~/.zshrc${NC}  # or ~/.bashrc"
    echo ""
fi

# Add noglob alias for better UX (prevents ? and * from being expanded by shell)
echo ""
echo "Setting up shell integration..."

SHELL_CONFIG=""
SHELL_TYPE=""
if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
    SHELL_TYPE="zsh"
elif [ -n "$BASH_VERSION" ] || [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
    SHELL_TYPE="bash"
fi

if [ -n "$SHELL_CONFIG" ]; then
    # Check if alias already exists
    if ! grep -q "alias $COMMAND_NAME=" "$SHELL_CONFIG" 2>/dev/null; then
        echo "" >> "$SHELL_CONFIG"
        echo "# wtf - disable glob expansion so you don't need quotes" >> "$SHELL_CONFIG"
        
        if [ "$SHELL_TYPE" = "zsh" ]; then
            # zsh has noglob built-in
            echo "unalias $COMMAND_NAME 2>/dev/null || true  # Remove any existing alias" >> "$SHELL_CONFIG"
            echo "alias $COMMAND_NAME='noglob $COMMAND_NAME'" >> "$SHELL_CONFIG"
        else
            # bash doesn't have noglob, so we need a function wrapper
            echo "unalias $COMMAND_NAME 2>/dev/null || true  # Remove any existing alias" >> "$SHELL_CONFIG"
            echo "$COMMAND_NAME() { set -f; command $COMMAND_NAME \"\$@\"; local ret=\$?; set +f; return \$ret; }" >> "$SHELL_CONFIG"
        fi
        
        echo -e "${GREEN}✓${NC} Added alias to $SHELL_CONFIG"
        echo ""
        echo -e "${CYAN}Important:${NC} Restart your shell or run:"
        echo -e "${CYAN}source $SHELL_CONFIG${NC}"
        echo ""
        echo "This lets you use: ${CYAN}$COMMAND_NAME are you there?${NC}"
        echo "Instead of:        ${CYAN}$COMMAND_NAME \"are you there?\"${NC}"
    else
        echo -e "${GREEN}✓${NC} Shell alias already configured"
    fi
else
    echo -e "${YELLOW}⚠${NC}  Could not detect shell config file"
    echo ""
    echo "For better UX, add this to your shell config:"
    echo ""
    echo "For zsh:"
    echo -e "${CYAN}alias $COMMAND_NAME='noglob $COMMAND_NAME'${NC}"
    echo ""
    echo "For bash:"
    echo -e "${CYAN}$COMMAND_NAME() { set -f; command $COMMAND_NAME \"\$@\"; local ret=\$?; set +f; return \$ret; }${NC}"
    echo ""
    echo "This prevents ? and * from being expanded by your shell."
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                    Installation Complete!                    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Get started:"
echo ""
echo -e "  ${CYAN}$COMMAND_NAME \"what's in my git status?\"${NC}"
echo ""
echo "The setup wizard will run automatically on first use."
echo ""
echo "Learn more: https://github.com/$REPO"
echo ""
