---
name: github-workflows-guide
description: This skill provides comprehensive guidance for designing, analyzing, and optimizing GitHub Actions CI/CD workflows. It includes best practices for workflow structure, performance optimization, debugging strategies, and reusable workflow templates. This skill should be used when creating new GitHub workflows, analyzing CI/CD pipeline performance issues, troubleshooting workflow failures, or implementing workflow optimizations and automation.
---

# GitHub Workflows Guide

## Overview

GitHub Actions is GitHub's native CI/CD platform enabling automated testing, building, and deployment directly from repositories. This skill provides comprehensive guidance for designing efficient workflows, diagnosing performance bottlenecks, debugging failures, and optimizing resource usage across diverse use cases (testing, deployment, security scanning, release automation).

## Core Capabilities

### 1. Workflow Design & Structure
To create effective workflows, understand the foundational architecture:
- **Workflow files** live in `.github/workflows/` directory as YAML files
- **Events** trigger workflows (push, pull_request, schedule, workflow_dispatch, etc.)
- **Jobs** run in parallel by default; use `needs:` to create dependencies
- **Steps** execute sequentially within a job using actions or shell commands
- **Matrix** enables testing across multiple configurations (OS, Node versions, etc.)

Best practices:
- Name workflows and jobs descriptively for easy tracking
- Use environment variables for configuration to avoid hardcoding secrets
- Implement conditional execution (`if:`) to skip unnecessary steps
- Cache dependencies to reduce build time significantly
- Use `actions/upload-artifact@v3` to persist build outputs between jobs

### 2. Optimization Strategies

**Reduce Execution Time:**
- Enable caching for dependencies (`actions/cache@v3`, npm cache, Docker layers)
- Parallelize independent jobs using matrix strategy
- Use conditional steps to skip unnecessary operations (`if: steps.changes.outputs.service == 'true'`)
- Split large test suites across multiple matrix jobs
- Leverage GitHub's faster runners for time-sensitive workflows

**Manage Resource Costs:**
- Set job `timeout-minutes` to prevent runaway jobs (default: 360 minutes)
- Use job-level concurrency groups to prevent resource waste on duplicate runs
- Archive only essential artifacts; implement retention policies
- Consider self-hosted runners for resource-intensive or frequent workflows
- Monitor action market to replace bloated third-party actions with optimized alternatives

**Reliability & Robustness:**
- Implement retry logic with exponential backoff for flaky tests (`uses: nick-invision/retry@v2`)
- Use composite actions to reduce duplication and centralize common logic
- Implement status checks and notifications for visibility
- Store workflow logs and artifacts with appropriate retention policies

### 3. Debugging & Troubleshooting

**Common Issues & Solutions:**

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| Workflow doesn't trigger | Event filter misconfigured or wrong branch | Verify event filters in `on:` section; check branch protection rules |
| Steps fail intermittently | Flaky tests or external service issues | Add retry logic, increase timeout, add logging for diagnostics |
| Large resource usage | Unoptimized caching, excessive artifacts | Enable caching, implement retention policies, parallelize jobs |
| Secret access errors | Secret misconfiguration or scope issues | Verify secret name matches exactly; check if secret exists in repo settings |
| Job timeout | Slow steps or resource constraints | Profile step duration; add parallelization; increase timeout as last resort |

**Debugging Techniques:**
- Enable workflow debug logging via secrets `ACTIONS_STEP_DEBUG: true` (shows internal runner diagnostics)
- Add `echo` statements or GitHub annotations to capture runtime state (`echo "::error::message"`)
- Re-run failed jobs with debug logging enabled to capture additional diagnostics
- Check runner logs in Actions tab for step-by-step execution details
- Use GitHub CLI (`gh run view <run-id> --log`) for local log inspection

### 4. Workflow Templates

See `references/workflow_templates.md` for reusable templates covering:
- Node.js testing and deployment
- Python linting and packaging
- Docker image building and pushing
- Release automation
- Security scanning

Load template files from `assets/templates/` directory for quick workflow setup.

### 5. Performance Analysis

To analyze workflow performance:
1. **Identify bottlenecks**: Review timing for each step in Actions UI; note consistently slow steps
2. **Profile dependencies**: Use caching visualization to detect frequently-missed cache hits
3. **Parallelize where possible**: Convert sequential steps to matrix jobs where independent
4. **Benchmark changes**: Compare execution time before and after optimization
5. **Monitor trends**: Use GitHub API to track performance over time (see `scripts/analyze_workflows.py`)

## Workflow Decision Tree

When approaching a workflow problem, follow this decision tree:

```
Is the workflow not running?
├─ No → Check if events are configured correctly
├─ Yes → Is there a syntax error?
│  ├─ Yes → Fix YAML structure (check indentation, quotes, null values)
│  └─ No → Check branch/event filters match your setup
│
Are jobs failing?
├─ Yes → Is it a flaky test?
│  ├─ Yes → Add retry logic or improve test isolation
│  ├─ No → Is it a timeout?
│  │  ├─ Yes → Parallelize, optimize, or increase timeout
│  │  └─ No → Check step output and error logs
└─ No → Proceed to performance optimization
│
Performance concerns?
├─ Yes → Is caching enabled?
│  ├─ No → Enable caching (likely 5-10x speedup)
│  ├─ Yes → Check cache hit ratio in logs
│  └─ Consider parallelization with matrix strategy
└─ No → Workflow is running well!
```

## Practical Examples

### Example 1: Multi-Platform Testing with Caching
```yaml
name: Test Matrix

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [18, 20]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm
      - run: npm ci
      - run: npm test
```

### Example 2: Conditional Deployment
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        run: |
          echo "Deploying to production..."
          # deployment script here
```

### Example 3: Artifact Management
```yaml
name: Build & Archive

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run build
      - uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/
          retention-days: 7
```

## References & Resources

- **Workflow Templates**: See `references/workflow_templates.md` for copy-paste templates
- **Best Practices**: See `references/best_practices.md` for comprehensive guidelines
- **API Documentation**: Official [GitHub Actions documentation](https://docs.github.com/actions)
- **Tools & Scripts**: See `scripts/` directory for Python tools for workflow analysis

---

**Next Steps:**
1. Choose appropriate template from `references/workflow_templates.md` based on your use case
2. Copy template from `assets/templates/` to `.github/workflows/` in your repository
3. Customize variables, secrets, and triggers to match your environment
4. Test workflow by pushing to a test branch
5. Monitor performance in GitHub Actions tab; optimize if needed using strategies in section 2
