# Versioning Recommendations for iRacing Grafana Observability

This document outlines recommendations for versioning the iRacing Grafana Observability project using semantic versioning (SemVer).

## Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/) with the format `MAJOR.MINOR.PATCH`:

1. **MAJOR** version increments for incompatible API changes or significant architectural changes
2. **MINOR** version increments for new functionality added in a backward-compatible manner
3. **PATCH** version increments for backward-compatible bug fixes

## When to Increment Versions

### PATCH Version (e.g., 1.0.0 → 1.0.1)

- Bug fixes
- Performance improvements without API changes
- Documentation updates
- Internal refactoring without functional changes
- Small UI fixes or improvements

Example:
```bash
./scripts/bump-version.sh patch
```

### MINOR Version (e.g., 1.0.0 → 1.1.0)

- New dashboards
- New metrics or collectors
- New features that don't break existing functionality
- Enhanced visualization capabilities
- Added connectivity options
- New exporters or data sources

Example:
```bash
./scripts/bump-version.sh minor
```

### MAJOR Version (e.g., 1.0.0 → 2.0.0)

- Changes requiring manual migration of data
- Fundamental architectural changes
- Removal of deprecated features
- Changes to dashboard structure requiring manual updating
- Switching core technologies (database systems, etc.)

Example:
```bash
./scripts/bump-version.sh major
```

## Release Process

1. Update the `CHANGELOG.md` with details of changes
2. Run the version bump script: `./scripts/bump-version.sh [major|minor|patch]`
3. Push changes and tags: `git push && git push --tags`
4. Create a GitHub release from the tag with release notes

## Releases and GitHub Actions

We recommend setting up GitHub Actions to:

1. Automatically generate release notes from CHANGELOG entries
2. Build and publish Docker images with version tags
3. Create GitHub releases automatically when a version tag is pushed

## Pre-release Versions

For pre-release versions, use the following format:
- Alpha: `1.0.0-alpha.1`
- Beta: `1.0.0-beta.1`
- Release Candidate: `1.0.0-rc.1`

## Initial Development

During initial development (before 1.0.0), the API is considered unstable and subject to change. We recommend:

- Start with version 0.1.0
- Increment MINOR for feature additions
- Increment PATCH for bug fixes
- Release 1.0.0 when the project is stable and ready for production use