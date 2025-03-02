#!/usr/bin/env bash
# bump-version.sh - Script to bump version numbers using semantic versioning

set -e

# Change to the repository root directory
cd "$(git rev-parse --show-toplevel)"

# Current version
CURRENT_VERSION=$(cat VERSION)
echo "Current version: $CURRENT_VERSION"

# Validate and parse current version
if [[ ! $CURRENT_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Current version is not in semantic versioning format (X.Y.Z)"
  exit 1
fi

MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
MINOR=$(echo $CURRENT_VERSION | cut -d. -f2)
PATCH=$(echo $CURRENT_VERSION | cut -d. -f3)

# Functions to bump version parts
bump_major() {
  MAJOR=$((MAJOR + 1))
  MINOR=0
  PATCH=0
}

bump_minor() {
  MINOR=$((MINOR + 1))
  PATCH=0
}

bump_patch() {
  PATCH=$((PATCH + 1))
}

# Process arguments
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 [major|minor|patch]"
  exit 1
fi

case "$1" in
  major)
    bump_major
    ;;
  minor)
    bump_minor
    ;;
  patch)
    bump_patch
    ;;
  *)
    echo "Invalid argument: $1. Must be one of: major, minor, patch"
    exit 1
    ;;
esac

# Build new version
NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
echo "New version: $NEW_VERSION"

# Update VERSION file
echo "$NEW_VERSION" > VERSION

# Update version in other files if needed
# Examples:
# sed -i "s/version = \"${CURRENT_VERSION}\"/version = \"${NEW_VERSION}\"/" setup.py
# sed -i "s/\"version\": \"${CURRENT_VERSION}\"/\"version\": \"${NEW_VERSION}\"/" package.json

# Create a release commit
git add VERSION
git commit -m "chore: bump version to ${NEW_VERSION}"

# Create a git tag
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"

echo
echo "Version bumped from ${CURRENT_VERSION} to ${NEW_VERSION}"
echo "Changes committed locally and tag created."
echo
echo "To push changes and tag to remote:"
echo "  git push && git push --tags"