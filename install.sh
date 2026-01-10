#!/bin/bash
set -e

# wtf installation script
# Usage: curl -sSL https://raw.githubusercontent.com/davefowler/wtf-terminal-ai/main/install.sh | bash

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

# Find a suitable Python version (3.8+, prefer newest)
REQUIRED_VERSION="3.9"
PYTHON_CMD=""
PYTHON_VERSION=""

# Build list of Python commands to try (newest first)
PYTHON_CANDIDATES="python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python"

# Also check common install locations on macOS/Linux
for brew_python in /opt/homebrew/bin/python3* /usr/local/bin/python3* /usr/bin/python3*; do
    if [ -x "$brew_python" ] 2>/dev/null; then
        PYTHON_CANDIDATES="$brew_python $PYTHON_CANDIDATES"
    fi
done

# Try each candidate
for cmd in $PYTHON_CANDIDATES; do
    if command -v $cmd &> /dev/null || [ -x "$cmd" ]; then
        version=$($cmd -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null)
        if [ -n "$version" ]; then
            # Check if version meets minimum requirement
            if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$version" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
                # Prefer newer versions - keep checking but remember this one
                if [ -z "$PYTHON_CMD" ]; then
                    PYTHON_CMD=$cmd
                    PYTHON_VERSION=$version
                elif [ "$(printf '%s\n' "$PYTHON_VERSION" "$version" | sort -V | tail -n1)" = "$version" ]; then
                    # This version is newer
                    PYTHON_CMD=$cmd
                    PYTHON_VERSION=$version
                fi
            fi
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}✗ Python $REQUIRED_VERSION or higher not found${NC}"
    echo ""
    # Check what version they have
    if command -v python3 &> /dev/null; then
        CURRENT=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null)
        if [ -n "$CURRENT" ]; then
            echo "You have Python $CURRENT, but wtf requires Python $REQUIRED_VERSION+"
            echo ""
        fi
    fi
    echo "Please install Python $REQUIRED_VERSION or higher:"
    echo "  macOS:   brew install python3"
    echo "  Ubuntu:  sudo apt install python3 python3-pip"
    echo "  Fedora:  sudo dnf install python3 python3-pip"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION detected ($PYTHON_CMD)"

# Check if pip is available for our Python
PIP_CMD="$PYTHON_CMD -m pip"
if ! $PIP_CMD --version &> /dev/null; then
    echo -e "${RED}✗ pip not available for $PYTHON_CMD${NC}"
    echo "Please install pip for Python $PYTHON_VERSION"
    exit 1
fi

echo -e "${GREEN}✓${NC} pip detected"
echo ""

# Check for existing wtf command or alias
echo "Checking for command collisions..."

COLLISION_FOUND=false
COLLISION_TYPE=""
COLLISION_LOCATION=""
COLLISION_LINE=""
IS_OUR_ALIAS=false

# Check for alias in shell config files
for config_file in ~/.zshrc ~/.bashrc ~/.bash_profile ~/.profile ~/.config/fish/config.fish; do
    if [ -f "$config_file" ]; then
        # Check if it's OUR alias (noglob wtf) - that's fine, not a collision
        if grep -qE "alias wtf='noglob wtf'|alias wtf=\"noglob wtf\"" "$config_file" 2>/dev/null; then
            IS_OUR_ALIAS=true
            break
        fi
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

# Check if wtf command exists in PATH (and it's not our installed version)
if command -v wtf &> /dev/null && [ "$COLLISION_FOUND" = false ] && [ "$IS_OUR_ALIAS" = false ]; then
    # Check if it's our wtf by looking for wtf-ai in pip
    if $PIP_CMD show wtf-ai &> /dev/null; then
        IS_OUR_ALIAS=true  # It's our package, not a collision
    else
        COLLISION_FOUND=true
        COLLISION_TYPE="command"
        COLLISION_LOCATION=$(which wtf)
    fi
fi

if [ "$IS_OUR_ALIAS" = true ]; then
    echo -e "${GREEN}✓${NC} wtf-ai already installed, updating..."
    COMMAND_NAME="wtf"
elif [ "$COLLISION_FOUND" = true ]; then
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
    
    # Check if we're in interactive mode
    if [ -t 0 ]; then
        read -p "Choose [1-3]: " choice
    else
        echo "Non-interactive mode detected. Defaulting to 'wtfai'."
        choice=1
    fi

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

INSTALL_SUCCESS=false

# Try with --user flag first (--upgrade ensures we get latest version)
if $PIP_CMD install --user --upgrade wtf-ai > /tmp/wtf-install.log 2>&1; then
    INSTALL_SUCCESS=true
else
    # Try without --user flag (needed for some systems/virtual envs)
    if $PIP_CMD install --upgrade wtf-ai > /tmp/wtf-install.log 2>&1; then
        INSTALL_SUCCESS=true
    fi
fi

if [ "$INSTALL_SUCCESS" = true ]; then
    echo -e "${GREEN}✓${NC} wtf-ai installed successfully"
else
    echo -e "${RED}✗${NC} Installation failed"
    echo ""
    echo "Installation log:"
    cat /tmp/wtf-install.log
    echo ""
    echo "You can try installing manually:"
    echo "  $PIP_CMD install wtf-ai"
    exit 1
fi

# If using alternative name, create symlink
if [ "$COMMAND_NAME" != "wtf" ]; then
    INSTALL_DIR=$($PYTHON_CMD -c "import site; print(site.USER_BASE + '/bin')")

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

# Check if user bin is in PATH and add it if not
USER_BIN=$($PYTHON_CMD -c "import site; print(site.USER_BASE + '/bin')" 2>/dev/null || echo "$HOME/.local/bin")

if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
    echo ""
    echo "Adding $USER_BIN to PATH..."
    
    # Determine shell config file
    PATH_CONFIG=""
    if [ -f "$HOME/.zshrc" ]; then
        PATH_CONFIG="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        PATH_CONFIG="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        PATH_CONFIG="$HOME/.bash_profile"
    fi
    
    if [ -n "$PATH_CONFIG" ]; then
        # Check if we already added it
        if ! grep -q "# wtf PATH" "$PATH_CONFIG" 2>/dev/null; then
            echo "" >> "$PATH_CONFIG"
            echo "# wtf PATH - Python user bin directory" >> "$PATH_CONFIG"
            echo "export PATH=\"\$PATH:$USER_BIN\"" >> "$PATH_CONFIG"
            echo -e "${GREEN}✓${NC} Added PATH to $PATH_CONFIG"
        else
            echo -e "${GREEN}✓${NC} PATH already configured"
        fi
    else
        echo -e "${YELLOW}⚠${NC}  Could not find shell config. Add this manually:"
        echo -e "${CYAN}export PATH=\"\$PATH:$USER_BIN\"${NC}"
    fi
fi

# Add noglob alias for better UX (prevents ? and * from being expanded by shell)
echo ""
echo "Setting up shell integration..."
NEEDS_SHELL_RESTART=false

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
        NEEDS_SHELL_RESTART=true
    else
        echo -e "${GREEN}✓${NC} Shell alias already configured"
        NEEDS_SHELL_RESTART=false
    fi
else
    echo -e "${YELLOW}⚠${NC}  Could not detect shell config file"
    echo ""
    echo "For better UX, add this to your shell config:"
    echo ""
    echo "For zsh (~/.zshrc):"
    echo -e "${CYAN}alias $COMMAND_NAME='noglob $COMMAND_NAME'${NC}"
    echo ""
    echo "For bash (~/.bashrc):"
    echo -e "${CYAN}$COMMAND_NAME() { set -f; command $COMMAND_NAME \"\$@\"; local ret=\$?; set +f; return \$ret; }${NC}"
    echo ""
    echo "This prevents ? and * from being expanded by your shell."
    NEEDS_SHELL_RESTART=true
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                    Installation Complete!                    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if [ "$NEEDS_SHELL_RESTART" = true ]; then
    if [ -n "$SHELL_CONFIG" ]; then
        echo -e "${YELLOW}➜ Restart your terminal, or run:${NC}"
        echo ""
        echo -e "  ${CYAN}source $SHELL_CONFIG${NC}"
        echo ""
    else
        echo -e "${YELLOW}➜ Restart your terminal to use wtf.${NC}"
        echo ""
    fi
fi
echo "Try:"
echo ""
echo -e "  ${CYAN}$COMMAND_NAME what's in my git status?${NC}"
echo ""
echo "The setup wizard will run automatically on first use."
echo ""
echo "Learn more: https://github.com/$REPO"
echo ""
