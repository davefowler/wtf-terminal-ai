#!/bin/bash
# Publish wtf-ai to PyPI
set -e

cd "$(dirname "$0")"

# Use venv if available, otherwise python3
if [ -d "venv" ]; then
    source venv/bin/activate
fi
PYTHON="${PYTHON:-python3}"

# Get current version
CURRENT=$(grep '^version' pyproject.toml | cut -d'"' -f2)

# Use provided version or auto-bump patch version (0.1.0 -> 0.1.1)
if [ -n "$1" ]; then
    VERSION="$1"
else
    MAJOR=$(echo "$CURRENT" | cut -d. -f1)
    MINOR=$(echo "$CURRENT" | cut -d. -f2)
    PATCH=$(echo "$CURRENT" | cut -d. -f3)
    NEW_PATCH=$((PATCH + 1))
    VERSION="$MAJOR.$MINOR.$NEW_PATCH"
fi

echo "Bumping version: $CURRENT -> $VERSION"
sed -i '' "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
sed -i '' "s/^__version__ = .*/__version__ = \"$VERSION\"/" wtf/__init__.py

echo "Publishing wtf-ai v$VERSION to PyPI..."

# Clean and build
rm -rf dist/ build/ *.egg-info
$PYTHON -m build

# Upload
$PYTHON -m twine upload dist/*

echo ""
echo "✅ Published wtf-ai v$VERSION"
echo "   https://pypi.org/project/wtf-ai/$VERSION/"
