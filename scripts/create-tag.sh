#!/usr/bin/env bash
# create-tag.sh - Script to create a tag and version

set -e

# Change to the repository root directory
cd "$(git rev-parse --show-toplevel)"

# Get the current version from VERSION file
CURRENT_VERSION=$(cat VERSION)
echo "Current version: $CURRENT_VERSION"

# Validate tag name
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <tag-name>"
  echo "Example: $0 v1.2.3"
  exit 1
fi

TAG_NAME=$1

# Validate tag format
if [[ ! $TAG_NAME =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Tag name must be in format v1.2.3"
  exit 1
fi

# Extract version number without 'v' prefix
VERSION_NUMBER=${TAG_NAME#v}

# Update VERSION file
echo "$VERSION_NUMBER" > VERSION

# Create a release commit
git add VERSION
git commit -m "chore: set version to ${VERSION_NUMBER}"

# Create a git tag
git tag -a "$TAG_NAME" -m "Release $TAG_NAME"

echo
echo "Version set to ${VERSION_NUMBER}"
echo "Tag $TAG_NAME created."
echo
echo "To push changes and tag to remote:"
echo "  git push && git push --tags"