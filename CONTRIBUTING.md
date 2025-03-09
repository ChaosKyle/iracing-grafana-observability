# Contributing Guide

Thank you for considering contributing to the iRacing Grafana Observability project! This document outlines the standards and workflow for contributing to this project using trunk-based development principles.

## Development Workflow

We follow a trunk-based development workflow:

1. **Main Branch**: The `main` branch is our trunk and is always deployable.
2. **Short-Lived Feature Branches**: Create short-lived branches for features, fixes, or improvements.
3. **Frequent Integration**: Merge changes to main frequently (at least daily).
4. **Small, Incremental Changes**: Keep changes small and focused to minimize merge conflicts.

## Getting Started

1. **Fork the Repository**: Start by forking the repository to your GitHub account.

2. **Clone Your Fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/iracing-grafana-observability.git
   cd iracing-grafana-observability
   ```

3. **Add Upstream Remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/iracing-grafana-observability.git
   ```

4. **Create a Feature Branch**:
   ```bash
   # Keep branch names descriptive and prefixed with type
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

## Development Standards

### Branch Naming Conventions

- `feature/short-description` - For new features
- `fix/issue-description` - For bug fixes
- `docs/what-changed` - For documentation changes
- `refactor/what-changed` - For code refactoring
- `test/what-changed` - For test additions or changes
- `ci/what-changed` - For CI/CD pipeline changes

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

For example:
- `feat(collector): add support for new telemetry format`
- `fix(dashboard): resolve time range selection issue`
- `docs(readme): update installation instructions`

### Pull Request Process

1. **Update Your Branch**: Always pull the latest changes from upstream before submitting a PR:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run Tests**: Ensure all tests pass before submitting:
   ```bash
   # Run pytest for Python tests
   pytest python/tests/
   
   # Validate dashboard JSON
   python python/utils/dashboard_validator.py terraform/modules/grafana/dashboards/
   ```

3. **Submit PR**: Create a pull request to the `main` branch of the original repository.

4. **Code Review**: Address any feedback from code reviewers promptly.

5. **CI Checks**: Ensure all CI checks pass before requesting a merge.

## Security Best Practices

1. **No Secrets**: Never commit credentials, API keys, or sensitive information.

2. **Environment Variables**: Use environment variables for all configuration values.

3. **Input Validation**: Validate all user input before processing.

4. **Dependency Security**: Only add dependencies that are actively maintained and secure.

5. **Code Review Focus**: Pay special attention to security during code reviews.

## Documentation

- Update documentation when you change functionality.
- Document new features, options, and notable changes.
- Keep the README.md and other documentation files up to date.

## Testing

- Add tests for new features or bug fixes.
- Ensure all existing tests pass when making changes.
- Aim for good test coverage (>80% for new code).

## Release Process

1. Releases are made from the `main` branch.
2. Versioning follows [Semantic Versioning](https://semver.org/).
3. Each release will have an associated tag and release notes.

## Questions?

If you have questions about contributing, please create an issue with the label "question".

Thank you for contributing to making this project better!