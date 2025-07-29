# GitHub Actions Setup

This directory contains GitHub Actions workflows for the uubed project orchestration.

## Workflows

### orchestrate-builds.yml
Triggers builds across all sub-repositories in the correct order:
1. uubed-rs (Rust core)
2. uubed-py (Python bindings, depends on Rust)
3. uubed-docs (Documentation, depends on Python)

### nightly-benchmarks.yml
Runs performance benchmarks every night at 2 AM UTC to catch performance regressions.

### release-coordination.yml
Manages coordinated releases across all repositories, ensuring version consistency.

## Required Secrets

To enable cross-repository workflow triggers, you need to set up the following GitHub Actions secrets:

1. **PAT_TOKEN** (Personal Access Token)
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with the following permissions:
     - `repo` (full control)
     - `workflow` (update GitHub Action workflows)
   - Add this token as a secret named `PAT_TOKEN` in the repository settings

2. **Usage in workflows**
   - Replace `${{ secrets.GITHUB_TOKEN }}` with `${{ secrets.PAT_TOKEN }}` in the workflow files
   - This allows workflows to trigger actions in other repositories

## Setup Instructions

1. Create a Personal Access Token:
   ```
   GitHub → Settings → Developer settings → Personal access tokens → Generate new token
   ```

2. Add the token to repository secrets:
   ```
   Repository → Settings → Secrets and variables → Actions → New repository secret
   Name: PAT_TOKEN
   Value: [Your generated token]
   ```

3. Update the workflow files to use PAT_TOKEN instead of GITHUB_TOKEN for cross-repo triggers.

## Notes

- The default GITHUB_TOKEN has limited permissions and cannot trigger workflows in other repositories
- Personal Access Tokens should be rotated regularly for security
- Consider using GitHub Apps for production deployments for better security and granular permissions