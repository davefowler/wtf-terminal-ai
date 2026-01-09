#!/bin/bash
# Publish wtf-ai to PyPI
set -e

cd "$(dirname "$0")"

# Get current version
CURRENT=$(grep '^version' pyproject.toml | cut -d'"' -f2)

# Auto-bump patch version (0.1.0 -> 0.1.1)
MAJOR=$(echo "$CURRENT" | cut -d. -f1)
MINOR=$(echo "$CURRENT" | cut -d. -f2)
PATCH=$(echo "$CURRENT" | cut -d. -f3)
NEW_PATCH=$((PATCH + 1))
VERSION="$MAJOR.$MINOR.$NEW_PATCH"

echo "Bumping version: $CURRENT -> $VERSION"
sed -i '' "s/^version = .*/version = \"$VERSION\"/" pyproject.toml

echo "Publishing wtf-ai v$VERSION to PyPI..."

# Clean and build
rm -rf dist/ build/ *.egg-info
python -m build

# Upload
python -m twine upload dist/*

echo ""
echo "✅ Published wtf-ai v$VERSION"
echo "   https://pypi.org/project/wtf-ai/$VERSION/"
