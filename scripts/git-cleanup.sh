#!/usr/bin/env bash
# git-cleanup.sh - Script to clean up merged branches

set -e

# Change to the repository root directory
cd "$(git rev-parse --show-toplevel)"

echo "===== iRacing Grafana Observability Git Cleanup Tool ====="
echo "This script will delete local and remote branches that have been merged into master."
echo "Main branch is protected and will not be deleted."
echo

# Ensure we have the latest information
echo "Fetching latest updates from remote..."
git fetch --prune

# Get the default branch (usually master or main)
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
echo "Default branch identified as: $DEFAULT_BRANCH"
echo

# Switch to the default branch and update it
echo "Switching to $DEFAULT_BRANCH and pulling latest changes..."
git checkout "$DEFAULT_BRANCH"
git pull
echo

# Find merged local branches
echo "Finding local branches that have been merged into $DEFAULT_BRANCH..."
MERGED_LOCAL_BRANCHES=$(git branch --merged "$DEFAULT_BRANCH" | grep -v "\*" | grep -v "$DEFAULT_BRANCH" | tr -d ' ')

# Find merged remote branches
echo "Finding remote branches that have been merged into $DEFAULT_BRANCH..."
MERGED_REMOTE_BRANCHES=$(git branch -r --merged "$DEFAULT_BRANCH" | grep -v "$DEFAULT_BRANCH" | sed 's/origin\///' | tr -d ' ')

# If no merged branches, exit
if [ -z "$MERGED_LOCAL_BRANCHES" ] && [ -z "$MERGED_REMOTE_BRANCHES" ]; then
  echo "No merged branches found to clean up. Exiting."
  exit 0
fi

# Display branches that will be deleted
echo "The following local branches will be deleted:"
if [ -z "$MERGED_LOCAL_BRANCHES" ]; then
  echo "  None"
else
  echo "$MERGED_LOCAL_BRANCHES" | sed 's/^/  /'
fi
echo

echo "The following remote branches will be deleted:"
if [ -z "$MERGED_REMOTE_BRANCHES" ]; then
  echo "  None"
else
  echo "$MERGED_REMOTE_BRANCHES" | sed 's/^/  /'
fi
echo

# Confirm before proceeding
read -p "Do you want to proceed with deletion? (y/n): " CONFIRM
if [[ $CONFIRM != "y" && $CONFIRM != "Y" ]]; then
  echo "Operation cancelled. Exiting."
  exit 0
fi

# Delete local branches
if [ -n "$MERGED_LOCAL_BRANCHES" ]; then
  echo "Deleting local branches..."
  echo "$MERGED_LOCAL_BRANCHES" | xargs -n 1 git branch -d
fi

# Delete remote branches
if [ -n "$MERGED_REMOTE_BRANCHES" ]; then
  echo "Deleting remote branches..."
  echo "$MERGED_REMOTE_BRANCHES" | xargs -I{} git push origin --delete {}
fi

echo
echo "Cleanup complete!"
echo "All merged branches have been removed."
echo

# Suggest running garbage collection
echo "Consider running 'git gc' to clean up and optimize the local repository."