# GitHub Actions Best Practices

Comprehensive guidelines for reliable, performant, and maintainable workflows.

## Security Best Practices

### Secrets Management
- **Never hardcode secrets** in workflow files or repository
- Use GitHub Secrets for all sensitive data (API tokens, credentials, keys)
- Reference secrets with `${{ secrets.SECRET_NAME }}`
- Use `GITHUB_TOKEN` for repo access; it's automatically scoped and temporary
- Rotate secrets regularly; implement expiration policies
- Use organization secrets for shared credentials across multiple repos

```yaml
# ✅ Correct
- name: Deploy
  env:
    API_TOKEN: ${{ secrets.API_TOKEN }}
  run: deploy.sh

# ❌ Avoid
- name: Deploy
  run: deploy.sh --token abc123xyz  # Hardcoded secrets!
```

### Permissions & Access Control
- Scope `GITHUB_TOKEN` permissions minimally using `permissions:` block
- Use environment-specific protection rules (require approvals for production)
- Implement branch protection rules requiring workflow success before merge
- Use separate GitHub apps for different environments (staging vs. production)
- Audit access logs regularly for suspicious activity

```yaml
jobs:
  deploy:
    permissions:
      contents: read           # Read-only repo access
      packages: read           # Read container registry
      deployments: write       # Write deployment status
    runs-on: ubuntu-latest
```

### Action Validation
- Pin action versions using full commit SHA (not `@v2` which can change)
- Review third-party action code before using
- Prefer official actions (github/actions) over community alternatives
- Use `dependabot` to receive security updates for actions

```yaml
# ✅ Secure (pinned to specific version)
- uses: actions/checkout@a81bbbf8298c0fa03ea29cdc473d45769f953675

# ⚠️ Risky (version can change unexpectedly)
- uses: actions/checkout@v4
```

## Performance Optimization

### Caching Dependencies
- Enable caching for package managers (npm, pip, maven, etc.)
- Cache sizes exceed 10GB trigger eviction; monitor cache usage
- Use consistent cache keys to ensure cache hits

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 18
    cache: npm
    cache-dependency-path: package-lock.json
```

### Parallelization
- Use matrix strategy to run tests across multiple configurations in parallel
- Split large test suites across multiple jobs
- Reduce overall job duration by running independent tasks concurrently

```yaml
strategy:
  matrix:
    test-group: [unit, integration, e2e]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:${{ matrix.test-group }}
```

### Resource Usage
- Set `timeout-minutes` on long-running jobs (prevents runaway workflows)
- Use concurrency groups to prevent duplicate workflows on rapid pushes
- Archive only necessary artifacts; set retention policies
- Consider self-hosted runners for resource-intensive tasks

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    timeout-minutes: 30
    steps:
      - uses: actions/upload-artifact@v3
        with:
          retention-days: 7
```

## Reliability & Robustness

### Error Handling & Retries
- Implement retry logic for flaky tests or network operations
- Use conditional steps to skip unnecessary operations
- Set `continue-on-error: true` for non-critical steps
- Log diagnostics for debugging failures

```yaml
- name: Run tests with retry
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 5
    command: npm test
```

### Status Checks & Notifications
- Require workflow success before merging PRs
- Send Slack/email notifications on workflow failure
- Use GitHub annotations to highlight issues in code view
- Implement health checks and alerting for production workflows

```yaml
- name: Report test failure
  if: failure()
  uses: actions/github-script@v6
  with:
    script: |
      core.setFailed('Tests failed in pull request')
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '❌ Tests failed. Please review logs.'
      })
```

### Log Management
- Store logs with appropriate retention (e.g., 30 days for prod, 7 days for dev)
- Use log retention policies to manage storage costs
- Archive critical logs for audit trails
- Implement centralized logging for cross-workflow analysis

```yaml
- uses: actions/upload-artifact@v3
  with:
    name: test-logs
    path: logs/
    retention-days: 30
```

## Maintainability & Code Quality

### Workflow Organization
- Use descriptive workflow and job names for easy identification
- Keep workflows focused on single responsibility (don't create mega-workflows)
- Use environment variables to centralize configuration
- Document workflow purpose in comments

```yaml
name: Integration Tests
on:
  pull_request:
    paths:
      - src/**
      - tests/**

env:
  NODE_VERSION: 20.x
  TEST_TIMEOUT: 5m

jobs:
  integration-tests:
    runs-on: ubuntu-latest
```

### Reusable Workflows & Composite Actions
- Create composite actions for frequently repeated steps
- Use reusable workflows to share logic across repos
- Document inputs/outputs clearly
- Version reusable workflows for stability

```yaml
# reusable-deploy.yml
on:
  workflow_call:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: string
    secrets:
      api_token:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
```

### Input Validation
- Validate workflow inputs to prevent injection attacks
- Use strict event filters to trigger workflows only when appropriate
- Validate secrets exist before using them

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment target'
        required: true
        type: choice
        options:
          - staging
          - production

jobs:
  deploy:
    if: contains(fromJson('["staging", "production"]'), inputs.environment)
```

## Common Pitfalls to Avoid

| Issue | Problem | Solution |
|-------|---------|----------|
| Secrets exposed in logs | Sensitive data visible in job output | Use `::add-mask::` or `::mask::` to redact sensitive values |
| Workflow triggers wrong branch | Workflow runs on unintended events | Use explicit branch filters: `branches: [main]` |
| Large artifact bloat | Runner disk fills up; deployments slow | Set retention policies; upload only necessary files |
| Flaky tests halt CI/CD | Tests pass locally but fail in CI sporadically | Add retry logic; improve test isolation; fix timing issues |
| Action version drift | Updates introduce breaking changes | Pin to commit SHA instead of version tags |
| Poor job isolation | State leaks between jobs causing flakiness | Use `runs-on` to isolate environments; reset state between jobs |
| Inadequate logging | Difficult to debug workflow failures | Add informative logs; use GitHub annotations |
| Missing environment config | Inconsistent behavior across environments | Use GitHub Environments with protection rules and secrets |

## Monitoring & Observability

### Workflow Metrics
- Track workflow duration and success rates over time
- Monitor runner availability and resource utilization
- Set up alerts for consistently failing jobs
- Use GitHub API to export metrics to external monitoring systems

### GitHub CLI for Analysis
```bash
# View workflow runs
gh run list --workflow=tests.yml

# View job logs
gh run view <run-id> --log

# Export metrics
gh api repos/owner/repo/actions/runs --jq '.workflow_runs[] | {id, conclusion, created_at}'
```

### Debugging Techniques
- Enable step debug logging: `ACTIONS_STEP_DEBUG: true` as secret
- Use GitHub Actions debugging to see internal runner operations
- Re-run failed jobs with debug mode enabled
- Compare successful vs. failed runs to identify differences

## Cost Optimization

- Use GitHub-hosted runners for standard workloads (most cost-effective)
- Reserve self-hosted runners for resource-intensive tasks
- Implement caching to reduce runner minutes
- Use matrix strategy efficiently to avoid redundant builds
- Archive old workflow runs to manage storage costs
