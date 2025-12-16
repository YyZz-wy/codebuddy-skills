#!/usr/bin/env python3
"""
GitHub Workflows Analysis Tool

Analyzes workflow runs to identify performance bottlenecks and optimization opportunities.
Requires GitHub CLI (gh) to be installed and authenticated.

Usage:
    python3 analyze_workflows.py --repo owner/repo --workflow tests.yml
    python3 analyze_workflows.py --repo owner/repo --last-runs 50
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import argparse


def run_command(cmd: str) -> str:
    """Execute shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_workflow_runs(repo: str, workflow: str = None, limit: int = 50) -> List[Dict]:
    """Fetch workflow runs from GitHub."""
    if workflow:
        cmd = f"gh run list --repo {repo} --workflow {workflow} --limit {limit} --json id,conclusion,durationMinutes,createdAt,name"
    else:
        cmd = f"gh run list --repo {repo} --limit {limit} --json id,conclusion,durationMinutes,createdAt,name"
    
    output = run_command(cmd)
    return json.loads(output)


def get_job_details(repo: str, run_id: str) -> List[Dict]:
    """Fetch job details for a specific run."""
    cmd = f"gh run view {run_id} --repo {repo} --json jobs --jq '.jobs[]'"
    output = run_command(cmd)
    jobs = [json.loads(line) for line in output.strip().split('\n') if line]
    return jobs


def get_step_timings(repo: str, run_id: str, job_id: str) -> List[Dict]:
    """Fetch step timings for a specific job."""
    cmd = f"gh run view {run_id} --repo {repo} --log | grep -E '(^\[|^  .*s$)' || true"
    output = run_command(cmd)
    # Parse step logs to extract timing information
    return parse_step_logs(output)


def parse_step_logs(log_output: str) -> List[Dict]:
    """Parse GitHub Actions log format to extract step timings."""
    steps = []
    current_step = None
    
    for line in log_output.split('\n'):
        if line.startswith('['):
            # Step header line
            if current_step:
                steps.append(current_step)
            current_step = {'name': line, 'duration': 0}
        elif current_step and 's$' in line:
            # Duration line
            try:
                duration_str = line.strip().split()[-1]
                duration = float(duration_str.rstrip('s'))
                current_step['duration'] = duration
            except (ValueError, IndexError):
                pass
    
    if current_step:
        steps.append(current_step)
    
    return steps


def analyze_performance(runs: List[Dict]) -> Dict:
    """Analyze workflow performance metrics."""
    if not runs:
        return {}
    
    durations = [run['durationMinutes'] for run in runs]
    successes = sum(1 for run in runs if run['conclusion'] == 'success')
    failures = sum(1 for run in runs if run['conclusion'] == 'failure')
    
    return {
        'total_runs': len(runs),
        'success_rate': f"{(successes / len(runs) * 100):.1f}%",
        'failures': failures,
        'avg_duration_minutes': f"{sum(durations) / len(durations):.1f}",
        'min_duration_minutes': min(durations),
        'max_duration_minutes': max(durations),
        'median_duration_minutes': sorted(durations)[len(durations) // 2],
    }


def identify_slowest_jobs(repo: str, runs: List[Dict]) -> List[Tuple[str, float]]:
    """Identify consistently slow jobs."""
    job_times = {}
    
    for run in runs[:10]:  # Analyze last 10 runs
        try:
            jobs = get_job_details(repo, run['id'])
            for job in jobs:
                job_name = job.get('name', 'Unknown')
                duration = job.get('durationMinutes', 0)
                
                if job_name not in job_times:
                    job_times[job_name] = []
                job_times[job_name].append(duration)
        except Exception as e:
            print(f"Warning: Could not fetch job details for run {run['id']}: {e}")
            continue
    
    # Calculate average duration per job
    avg_job_times = [
        (job_name, sum(times) / len(times))
        for job_name, times in job_times.items()
    ]
    
    return sorted(avg_job_times, key=lambda x: x[1], reverse=True)


def print_analysis_report(repo: str, runs: List[Dict], workflow: str = None):
    """Print formatted analysis report."""
    print("\n" + "=" * 70)
    print(f"GitHub Workflows Analysis Report")
    print("=" * 70)
    print(f"Repository: {repo}")
    if workflow:
        print(f"Workflow: {workflow}")
    print(f"Analysis Date: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Overall performance
    perf = analyze_performance(runs)
    print("\n📊 Overall Performance Metrics:")
    for key, value in perf.items():
        print(f"  {key}: {value}")
    
    # Slowest jobs
    print("\n🐢 Slowest Jobs (Average Duration):")
    slowest = identify_slowest_jobs(repo, runs)
    for job_name, avg_duration in slowest[:5]:
        print(f"  {job_name}: {avg_duration:.1f} min")
    
    # Recommendations
    print("\n💡 Optimization Recommendations:")
    
    success_rate = float(perf['success_rate'].rstrip('%'))
    if success_rate < 90:
        print("  ⚠️  Low success rate (<90%). Investigate flaky tests or infrastructure issues.")
    
    avg_duration = float(perf['avg_duration_minutes'])
    if avg_duration > 10:
        print("  ⚠️  High average duration (>10 min). Consider parallelization or caching.")
    
    if slowest:
        slowest_job = slowest[0]
        if slowest_job[1] > 5:
            print(f"  ⚠️  Slowest job '{slowest_job[0]}' takes {slowest_job[1]:.1f} min. Consider optimization.")
    
    print("\n✅ Optimization Strategies:")
    print("  • Enable dependency caching (npm, pip, maven)")
    print("  • Use matrix strategy to parallelize tests")
    print("  • Implement retry logic for flaky steps")
    print("  • Review and optimize slowest jobs first")
    print("  • Consider self-hosted runners for resource-intensive tasks")
    
    print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze GitHub Actions workflow performance'
    )
    parser.add_argument(
        '--repo',
        required=True,
        help='Repository in format owner/repo'
    )
    parser.add_argument(
        '--workflow',
        help='Specific workflow file to analyze'
    )
    parser.add_argument(
        '--last-runs',
        type=int,
        default=50,
        help='Number of recent runs to analyze (default: 50)'
    )
    
    args = parser.parse_args()
    
    # Fetch runs
    print(f"📡 Fetching workflow runs from {args.repo}...")
    runs = get_workflow_runs(
        args.repo,
        args.workflow,
        args.last_runs
    )
    
    if not runs:
        print("No workflow runs found.")
        sys.exit(1)
    
    # Print analysis report
    print_analysis_report(args.repo, runs, args.workflow)


if __name__ == '__main__':
    main()
