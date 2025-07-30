"""Command-line interface for Shadow VCS."""
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional

import click

from zed.core.commit import CommitManager
from zed.core.fingerprint import FingerprintGenerator
from zed.core.policy import PolicyManager
from zed.core.repo import Repository
from zed.core.metrics import MetricsCollector
from zed.core.config import get_config, reload_config, ConfigManager

# Standardized exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_USER_ERROR = 2  # User input errors
EXIT_SYSTEM_ERROR = 3  # System/environment errors


def handle_error(error: Exception, operation: str):
    """Standardized error handling with consistent exit codes."""
    if isinstance(error, ValueError):
        click.echo(f"❌ Error: {error}", err=True)
        sys.exit(EXIT_USER_ERROR)
    elif isinstance(error, FileNotFoundError):
        click.echo(f"❌ File not found during {operation}: {error}", err=True)
        sys.exit(EXIT_USER_ERROR)
    elif isinstance(error, PermissionError):
        click.echo(f"❌ Permission denied during {operation}: {error}", err=True)
        sys.exit(EXIT_SYSTEM_ERROR)
    else:
        click.echo(f"❌ Unexpected error during {operation}: {error}", err=True)
        sys.exit(EXIT_ERROR)


def _auto_apply_if_safe(repo: Repository, commit, fingerprint, policy_result: dict) -> bool:
    """Auto-apply changes for very safe commits."""
    from zed.core.config import get_config
    
    config = get_config(repo.path)
    
    # Check if auto-apply is enabled
    if not config.security.auto_apply_enabled:
        return False
    
    if not policy_result.get("approved"):
        return False
    
    # Check if commit meets auto-apply criteria
    risk_threshold = config.security.auto_apply_risk_threshold
    max_lines = config.security.auto_apply_max_lines
    allowed_patterns = config.security.auto_apply_file_patterns
    
    # Check risk score and line count
    if fingerprint.risk_score >= risk_threshold or fingerprint.lines_added > max_lines:
        return False
    
    # Check if all files match allowed patterns
    import fnmatch
    for file_path in commit.files:
        file_str = str(file_path)
        if not any(fnmatch.fnmatch(file_str, pattern) for pattern in allowed_patterns):
            return False
    
    # Apply changes to working tree
    applied_files = _apply_commit_to_working_tree(repo, commit)
    
    # Update status in database
    from zed.core.db import connect
    with connect(repo.db_path, repo.path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE commits SET status = ?, approved_at = ? WHERE id = ?",
            ("applied", int(time.time()), commit.id)
        )
        
        # Add to audit log
        cursor.execute(
            """
            INSERT INTO audit_log (timestamp, action, commit_id, user, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                int(time.time()),
                "commit_auto_applied",
                commit.id,
                "system",
                f"Auto-applied {len(applied_files)} safe files to working tree"
            ),
        )
        
        conn.commit()
    
    return True


def _apply_commit_to_working_tree(repo: Repository, commit) -> list[Path]:
    """Copy committed files to working directory."""
    commit_dir = repo.commits_dir / commit.id
    files_dir = commit_dir / "files"
    
    applied_files = []
    for stored_file in files_dir.rglob("*"):
        if stored_file.is_file():
            rel_path = stored_file.relative_to(files_dir)
            dest_path = repo.path / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stored_file, dest_path)
            applied_files.append(rel_path)
    
    return applied_files


def _run_test_command(test_cmd: str) -> bool:
    """Run test command and return success status."""
    import subprocess
    from zed.core.config import get_config
    
    config = get_config()
    timeout = config.performance.test_timeout_seconds
    
    try:
        # Run test command with configurable timeout
        result = subprocess.run(
            test_cmd,
            shell=True,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.echo("✅ Tests passed")
            return True
        else:
            click.echo(f"❌ Tests failed (exit code {result.returncode})")
            if result.stdout:
                click.echo("STDOUT:")
                click.echo(result.stdout[-500:])  # Last 500 chars
            if result.stderr:
                click.echo("STDERR:")
                click.echo(result.stderr[-500:])  # Last 500 chars
            return False
            
    except subprocess.TimeoutExpired:
        click.echo(f"❌ Test command timed out ({timeout} seconds)")
        return False
    except Exception as e:
        click.echo(f"❌ Test command failed: {e}")
        return False


@click.group()
@click.version_option(version="0.1.0", prog_name="zed")
def cli():
    """Shadow VCS - A local-first staging VCS for AI agents.
    
    Provides isolation, provenance, and policy enforcement for AI-generated code.
    
    \b
    Quick Start:
      zed init                    # Initialize repository
      zed commit -m "msg" file.py # Create commit
      zed status                  # Check pending reviews
      zed review <commit-id>      # Review changes
      zed approve <commit-id>     # Apply to working tree
    
    \b
    Learn more: https://github.com/AKIFQ/zed
    """
    pass


@cli.command()
def version():
    """Show detailed version information."""
    import platform
    import sqlite3
    
    click.echo("Shadow VCS (zed) version 0.1.0")
    click.echo(f"Python {platform.python_version()} on {platform.system()}")
    click.echo(f"SQLite {sqlite3.sqlite_version}")
    click.echo()
    click.echo("A local-first staging VCS for AI agents")
    click.echo("Repository: https://github.com/AKIFQ/zed")
    click.echo("License: MIT")


@cli.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Path to initialize the Shadow VCS repository",
)
def init(path: Path):
    """Initialize a new Shadow VCS repository.
    
    \b
    Examples:
      zed init                    # Initialize in current directory
      zed init /path/to/project   # Initialize in specific directory
    """
    try:
        repo = Repository(path)
        repo.init()
        click.echo(f"✅ Initialized Shadow VCS repository in {path.resolve()}/.zed")
        click.echo()
        click.echo("Next steps:")
        click.echo("  1. Make some changes to your files")
        click.echo("  2. Run: zed commit -m 'Your message' <files>")
        click.echo("  3. Check status: zed status")
    except Exception as e:
        if "already exists" in str(e):
            click.echo(f"❌ Error: {e}", err=True)
            click.echo("💡 Tip: Use 'zed status' to see existing commits", err=True)
            sys.exit(EXIT_USER_ERROR)
        else:
            handle_error(e, "init")


@cli.command()
@click.option(
    "--message",
    "-m",
    required=True,
    help="Commit message",
)
@click.option(
    "--author",
    "-a",
    default=lambda: os.environ.get("USER", "unknown"),
    help="Author name (defaults to $USER)",
)
@click.option(
    "--test-cmd",
    "-t",
    help="Run test command before commit (e.g., 'pytest', 'npm test')",
)
@click.argument(
    "files",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def commit(message: str, author: str, test_cmd: Optional[str], files: tuple[Path, ...]):
    """Create a new commit with specified files.
    
    \b
    Examples:
      zed commit -m "Add feature" src/feature.py
      zed commit -m "Update docs" README.md docs/
      zed commit -m "AI: Refactored auth" -a "gpt-4" auth.py
      zed commit -m "Fix bug" -t "pytest tests/" src/fix.py
    """
    try:
        # Find repository
        repo = _find_repository()
        
        # Convert files to list
        file_list = list(files)
        
        # Run tests if test command provided
        test_passed = True
        if test_cmd:
            click.echo(f"🧪 Running tests: {test_cmd}")
            test_passed = _run_test_command(test_cmd)
            if not test_passed:
                click.echo("❌ Tests failed, aborting commit", err=True)
                sys.exit(EXIT_USER_ERROR)
        
        # Create commit with metrics tracking
        commit_mgr = CommitManager(repo)
        metrics = MetricsCollector(repo)
        
        try:
            with metrics.measure_operation("commit_create", {"files": len(file_list), "author": author}):
                commit = commit_mgr.create_commit(message, author, file_list)
        except ValueError as e:
            if "File does not exist" in str(e):
                click.echo(f"❌ {e}", err=True)
                click.echo("💡 Check file paths and try again", err=True)
                sys.exit(EXIT_USER_ERROR)
            elif "File too large" in str(e):
                click.echo(f"❌ {e}", err=True)
                click.echo("💡 Consider using Git LFS for large files", err=True)
                sys.exit(EXIT_USER_ERROR)
            elif "Path traversal" in str(e):
                click.echo(f"❌ {e}", err=True)
                click.echo("💡 Paths must be within the repository", err=True)
                sys.exit(EXIT_USER_ERROR)
            else:
                raise
        
        # Get diff stats from meta.json
        commit_dir = repo.commits_dir / commit.id
        meta_path = commit_dir / "meta.json"
        with open(meta_path, "r") as f:
            meta_data = json.load(f)
        diff_stats = meta_data["diff_stats"]
        
        # Generate fingerprint with metrics
        fingerprint_gen = FingerprintGenerator(repo)
        with metrics.measure_operation("fingerprint_generate", {"files": len(file_list)}):
            fingerprint = fingerprint_gen.generate(commit, diff_stats)
        
        # Adjust risk score based on test results
        if test_cmd and test_passed:
            # Reduce risk slightly for tested changes
            fingerprint.risk_score = max(0.0, fingerprint.risk_score - 0.1)
        
        # Evaluate policy constraints
        policy_mgr = PolicyManager(repo)
        policy_result = policy_mgr.evaluate(fingerprint, file_list)
        
        # Determine initial status
        if policy_result["approved"]:
            status = "approved"
            status_msg = "auto-approved by policy"
            status_icon = "✅"
        elif policy_result["require_role"]:
            status = "waiting_review"
            status_msg = f"requires {policy_result['require_role']} approval"
            status_icon = "⚠️"
        else:
            status = "waiting_review"
            status_msg = "requires review"
            status_icon = "⏳"
        
        # Try auto-apply for ultra-safe changes
        auto_applied = False
        if status == "approved":
            auto_applied = _auto_apply_if_safe(repo, commit, fingerprint, policy_result)
            
            if auto_applied:
                status = "applied"
                status_msg = "auto-approved and applied"
                status_icon = "🚀"
            else:
                # Update commit status to approved (but not applied)
                from zed.core.db import connect
                with connect(repo.db_path, repo.path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE commits SET status = ? WHERE id = ?",
                        (status, commit.id),
                    )
                    conn.commit()
        
        click.echo(f"{status_icon} Created commit {click.style(commit.id[:8], fg='cyan')} ({status_msg})")
        click.echo(f"  📁 Files: {len(file_list)}")
        click.echo(f"  📊 Lines: +{fingerprint.lines_added} -{fingerprint.lines_deleted}")
        click.echo(f"  ⚡ Risk score: {fingerprint.risk_score}")
        
        if auto_applied:
            click.echo(f"  🚀 Changes automatically applied to working directory!")
        elif status == "waiting_review":
            click.echo()
            click.echo("💡 Next steps:")
            click.echo(f"  zed review {commit.id[:8]}   # Review changes")
            click.echo(f"  zed approve {commit.id[:8]}  # Apply to working tree")
        elif status == "approved":
            click.echo()
            click.echo("💡 Next step:")
            click.echo(f"  zed approve {commit.id[:8]}  # Apply to working tree")
        
    except Exception as e:
        handle_error(e, "commit")


@cli.command()
@click.option(
    "--all",
    "-a",
    is_flag=True,
    help="Show all commits (default shows only pending)",
)
def status(all: bool):
    """Show status of commits.
    
    \b
    Examples:
      zed status          # Show pending reviews
      zed status --all    # Show all commits
    """
    try:
        repo = _find_repository()
        
        from zed.core.db import connect
        with connect(repo.db_path, repo.path) as conn:
            cursor = conn.cursor()
            
            if all:
                cursor.execute(
                    "SELECT id, message, author, timestamp, status FROM commits ORDER BY timestamp DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, message, author, timestamp, status FROM commits WHERE status = 'waiting_review' ORDER BY timestamp DESC"
                )
            
            commits = cursor.fetchall()
            
            if not commits:
                if all:
                    click.echo("📭 No commits found.")
                else:
                    click.echo("✨ No commits waiting for review.")
                    click.echo()
                    click.echo("💡 Tip: Create a commit with 'zed commit -m \"message\" <files>'")
                return
            
            # Display header
            if all:
                click.echo("📋 All commits:")
            else:
                click.echo("⏳ Commits waiting for review:")
            click.echo()
            
            # Display commits
            for commit in commits:
                timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(commit["timestamp"]))
                status_color = {
                    "waiting_review": "yellow",
                    "approved": "green", 
                    "applied": "green",
                    "rejected": "red",
                }.get(commit["status"], "white")
                
                status_icon = {
                    "waiting_review": "⏳",
                    "approved": "✅",
                    "applied": "🚀",
                    "rejected": "❌",
                }.get(commit["status"], "❓")
                
                click.echo(
                    f"  {status_icon} {click.style(commit['id'][:8], fg='cyan')} "
                    f"{click.style(commit['status'], fg=status_color)} "
                    f"{timestamp} {commit['author']}: {commit['message']}"
                )
                
    except Exception as e:
        handle_error(e, "status")


@cli.command()
@click.argument("commit_id")
def review(commit_id: str):
    """Review a commit by showing its details.
    
    \b
    Examples:
      zed review abc123           # Review commit abc123
      zed review abc123 | less    # Pipe to pager for large diffs
    """
    try:
        repo = _find_repository()
        
        # Find commit
        commit_id = _resolve_commit_id(repo, commit_id)
        commit_mgr = CommitManager(repo)
        commit = commit_mgr.get_commit(commit_id)
        
        if not commit:
            click.echo(f"❌ Commit {commit_id[:8]} not found", err=True)
            sys.exit(EXIT_USER_ERROR)
        
        # Get fingerprint
        fingerprint_gen = FingerprintGenerator(repo)
        fingerprint = None
        if commit.fingerprint_id:
            fingerprint = fingerprint_gen.get_fingerprint(commit.fingerprint_id)
        
        # Display commit info
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(commit.timestamp))
        click.echo(f"\nCommit: {click.style(commit.id[:8], fg='cyan')}")
        click.echo(f"Author: {commit.author}")
        click.echo(f"Date: {timestamp}")
        click.echo(f"Status: {click.style(commit.status, fg='yellow')}")
        click.echo(f"Message: {commit.message}")
        
        if fingerprint:
            click.echo(f"\nFingerprint:")
            click.echo(f"  Risk score: {fingerprint.risk_score}")
            click.echo(f"  Files changed: {fingerprint.files_changed}")
            click.echo(f"  Lines: +{fingerprint.lines_added} -{fingerprint.lines_deleted}")
            click.echo(f"  Security sensitive: {'Yes' if fingerprint.security_sensitive else 'No'}")
        
        click.echo(f"\nFiles:")
        for file_path in commit.files:
            click.echo(f"  {file_path}")
        
        # Show diff
        diff_path = repo.commits_dir / commit.id / "diff.patch"
        if diff_path.exists():
            click.echo(f"\nDiff:")
            click.echo("-" * 60)
            diff_content = diff_path.read_text(encoding="utf-8")
            if diff_content:
                click.echo(diff_content)
            else:
                click.echo("(No changes)")
            click.echo("-" * 60)
            
    except Exception as e:
        handle_error(e, "review")


@cli.command()
@click.argument("commit_id")
@click.option(
    "--user",
    "-u",
    default=lambda: os.environ.get("USER", "unknown"),
    help="User approving the commit",
)
def approve(commit_id: str, user: str):
    """Approve a commit and apply it to the working tree.
    
    \b
    Examples:
      zed approve abc123          # Approve with current user
      zed approve abc123 -u john  # Approve as specific user
    """
    try:
        repo = _find_repository()
        
        # Find commit
        commit_id = _resolve_commit_id(repo, commit_id)
        commit_mgr = CommitManager(repo)
        commit = commit_mgr.get_commit(commit_id)
        
        if not commit:
            click.echo(f"❌ Commit {commit_id[:8]} not found", err=True)
            sys.exit(EXIT_USER_ERROR)
        
        if commit.status == "applied":
            click.echo(f"❌ Commit {commit_id[:8]} is already applied to working tree", err=True)
            sys.exit(EXIT_USER_ERROR)
        
        if commit.status == "rejected":
            click.echo(f"❌ Commit {commit_id[:8]} has been rejected", err=True)
            sys.exit(EXIT_USER_ERROR)
        
        # Apply files to working tree using shared function
        applied_files = _apply_commit_to_working_tree(repo, commit)
        
        # Update database
        from zed.core.db import connect
        with connect(repo.db_path, repo.path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE commits SET status = ?, approved_by = ?, approved_at = ? WHERE id = ?",
                ("applied", user, int(time.time()), commit.id),
            )
            
            # Add to audit log
            cursor.execute(
                """
                INSERT INTO audit_log (timestamp, action, commit_id, user, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    int(time.time()),
                    "commit_approved",
                    commit.id,
                    user,
                    f"Applied {len(applied_files)} files to working tree",
                ),
            )
            
            conn.commit()
        
        click.echo(f"✅ Approved commit {click.style(commit.id[:8], fg='cyan')}")
        click.echo(f"📁 Applied {len(applied_files)} files to working tree")
        click.echo()
        click.echo("💡 Changes are now live in your working directory!")
        
    except Exception as e:
        handle_error(e, "approve")


@cli.command()
@click.argument("commit_id")
@click.option(
    "--user",
    "-u",
    default=lambda: os.environ.get("USER", "unknown"),
    help="User rejecting the commit",
)
@click.option(
    "--reason",
    "-r",
    help="Reason for rejection",
)
def reject(commit_id: str, user: str, reason: Optional[str]):
    """Reject a commit.
    
    \b
    Examples:
      zed reject abc123                       # Reject with current user
      zed reject abc123 -r "Security issue"  # Reject with reason
    """
    try:
        repo = _find_repository()
        
        # Find commit
        commit_id = _resolve_commit_id(repo, commit_id)
        commit_mgr = CommitManager(repo)
        commit = commit_mgr.get_commit(commit_id)
        
        if not commit:
            click.echo(f"❌ Commit {commit_id[:8]} not found", err=True)
            sys.exit(EXIT_USER_ERROR)
        
        if commit.status == "applied":
            click.echo(f"❌ Commit {commit_id[:8]} is already applied to working tree", err=True)
            sys.exit(EXIT_USER_ERROR)
        
        if commit.status == "rejected":
            click.echo(f"❌ Commit {commit_id[:8]} is already rejected", err=True)
            sys.exit(EXIT_USER_ERROR)
        
        # Update database
        from zed.core.db import connect
        with connect(repo.db_path, repo.path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE commits SET status = ? WHERE id = ?",
                ("rejected", commit.id),
            )
            
            # Add to audit log
            details = f"Rejected commit"
            if reason:
                details += f": {reason}"
            
            cursor.execute(
                """
                INSERT INTO audit_log (timestamp, action, commit_id, user, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    int(time.time()),
                    "commit_rejected",
                    commit.id,
                    user,
                    details,
                ),
            )
            
            conn.commit()
        
        click.echo(f"❌ Rejected commit {click.style(commit.id[:8], fg='cyan')}")
        if reason:
            click.echo(f"📝 Reason: {reason}")
        
    except Exception as e:
        handle_error(e, "reject")


@cli.group()
def policy():
    """Policy management commands."""
    pass


@cli.group()
def metrics():
    """Metrics and monitoring commands."""
    pass


@cli.group()
def config():
    """Configuration management commands."""
    pass


@policy.command()
@click.option(
    "--rule",
    "-r",
    required=True,
    help="Rule to test (JSON format)",
)
@click.option(
    "--context",
    "-c",
    required=True,
    help="Test context (JSON format with risk_score, lines_added, lines_deleted)",
)
def test(rule: str, context: str):
    """Test a policy rule with given context."""
    try:
        import json
        
        repo = _find_repository()
        policy_mgr = PolicyManager(repo)
        
        # Parse inputs
        rule_dict = json.loads(rule)
        test_context = json.loads(context)
        
        # Test the rule
        result = policy_mgr.test_rule(rule_dict, test_context)
        
        click.echo(f"Rule test result: {result}")
        click.echo(f"Rule: {rule}")
        click.echo(f"Context: {context}")
        
    except json.JSONDecodeError as e:
        click.echo(f"❌ Error: Invalid JSON - {e}", err=True)
        sys.exit(EXIT_USER_ERROR)
    except Exception as e:
        handle_error(e, "policy test")


@policy.command()
def validate():
    """Validate policy rules in constraints.yaml."""
    try:
        repo = _find_repository()
        constraints_path = repo.zed_dir / "constraints.yaml"
        
        if not constraints_path.exists():
            click.echo(f"❌ No constraints.yaml found at {constraints_path}")
            click.echo("💡 Create one with 'zed init' or manually create the file")
            sys.exit(EXIT_USER_ERROR)
        
        click.echo(f"🔍 Validating {constraints_path}...")
        
        # Create a new policy manager to trigger validation
        policy_mgr = PolicyManager(repo)
        
        if policy_mgr.rules:
            click.echo(f"✅ {len(policy_mgr.rules)} valid rules loaded successfully")
            click.echo()
            click.echo("Rules summary:")
            for i, rule in enumerate(policy_mgr.rules):
                click.echo(f"  {i+1}. match: {rule.match}")
                if rule.auto_approve:
                    click.echo(f"     → auto-approve: true")
                elif rule.require_role:
                    click.echo(f"     → require_role: {rule.require_role}")
                if rule.condition:
                    click.echo(f"     → condition: {rule.condition}")
        else:
            click.echo("⚠️  No valid rules found")
            
    except Exception as e:
        handle_error(e, "policy validate")


@metrics.command()
def stats():
    """Show usage statistics."""
    try:
        repo = _find_repository()
        collector = MetricsCollector(repo)
        stats = collector.get_usage_stats()
        
        click.echo("📊 Usage Statistics")
        click.echo("=" * 50)
        click.echo(f"Total commits: {stats.total_commits}")
        click.echo(f"  🚀 Auto-approved: {stats.auto_approved_commits}")
        click.echo(f"  ✅ Manual approved: {stats.manual_approved_commits}")
        click.echo(f"  ❌ Rejected: {stats.rejected_commits}")
        click.echo()
        click.echo(f"Average risk score: {stats.avg_risk_score}")
        click.echo(f"Total files committed: {stats.total_files_committed}")
        click.echo(f"Total lines added: {stats.total_lines_added}")
        click.echo(f"Total lines deleted: {stats.total_lines_deleted}")
        click.echo(f"Average commit size: {stats.avg_commit_size} files")
        
    except Exception as e:
        handle_error(e, "metrics stats")


@metrics.command()
def performance():
    """Show performance metrics."""
    try:
        repo = _find_repository()
        collector = MetricsCollector(repo)
        perf = collector.get_performance_summary()
        
        if not perf:
            click.echo("📈 No performance data available yet")
            return
        
        click.echo("📈 Performance Summary")
        click.echo("=" * 50)
        
        for operation, stats in perf.items():
            click.echo(f"\n{operation}:")
            click.echo(f"  Count: {stats['count']}")
            click.echo(f"  Average: {stats['avg_ms']:.1f}ms")
            click.echo(f"  Min/Max: {stats['min_ms']:.1f}ms / {stats['max_ms']:.1f}ms")
            click.echo(f"  P50/P95: {stats['p50_ms']:.1f}ms / {stats['p95_ms']:.1f}ms")
        
    except Exception as e:
        handle_error(e, "metrics performance")


@metrics.command()
def health():
    """Check system health."""
    try:
        repo = _find_repository()
        collector = MetricsCollector(repo)
        health = collector.health_check()
        
        status_icons = {
            'healthy': '✅',
            'warning': '⚠️',
            'degraded': '❌'
        }
        
        status_colors = {
            'healthy': 'green',
            'warning': 'yellow',
            'degraded': 'red'
        }
        
        icon = status_icons.get(health['status'], '❓')
        color = status_colors.get(health['status'], 'white')
        
        click.echo(f"{icon} System Health: {click.style(health['status'].upper(), fg=color)}")
        
        if health['issues']:
            click.echo("\nIssues:")
            for issue in health['issues']:
                click.echo(f"  • {issue}")
        else:
            click.echo("  All checks passed!")
        
        click.echo(f"\nLast checked: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(health['timestamp']))}")
        
    except Exception as e:
        handle_error(e, "metrics health")


@metrics.command()
@click.option(
    "--days",
    "-d",
    default=90,
    help="Number of days of data to keep (default: 90)",
)
@click.confirmation_option(prompt="Are you sure you want to delete old data?")
def cleanup(days: int):
    """Clean up old metrics and audit data."""
    try:
        repo = _find_repository()
        collector = MetricsCollector(repo)
        result = collector.cleanup_old_data(days)
        
        click.echo(f"🧹 Cleanup completed:")
        click.echo(f"  Deleted {result['deleted_audit_logs']} old audit log entries")
        click.echo(f"  Deleted {result['deleted_metrics']} old metrics")
        click.echo(f"  Kept data from last {days} days")
        
    except Exception as e:
        handle_error(e, "metrics cleanup")


@config.command()
def show():
    """Show current configuration."""
    try:
        repo = None
        try:
            repo = _find_repository()
        except ValueError:
            pass  # No repository found, use global config
        
        cfg = get_config(repo.path if repo else None)
        
        click.echo("🔧 Shadow VCS Configuration")
        click.echo("=" * 50)
        
        # Show config file path if available
        if cfg.config_file_path:
            click.echo(f"Config file: {cfg.config_file_path}")
        else:
            click.echo("Config file: Using defaults")
        
        click.echo(f"Log level: {cfg.log_level}")
        click.echo(f"Debug mode: {cfg.debug_mode}")
        click.echo()
        
        click.echo("Database:")
        click.echo(f"  Timeout: {cfg.database.timeout_seconds}s")
        click.echo(f"  Cache size: {cfg.database.cache_size_mb}MB")
        click.echo(f"  WAL mode: {cfg.database.wal_mode}")
        click.echo()
        
        click.echo("Security:")
        click.echo(f"  Max file size: {cfg.security.max_file_size_mb}MB")
        click.echo(f"  Auto-apply enabled: {cfg.security.auto_apply_enabled}")
        click.echo(f"  Auto-apply risk threshold: {cfg.security.auto_apply_risk_threshold}")
        click.echo(f"  Auto-apply max lines: {cfg.security.auto_apply_max_lines}")
        click.echo()
        
        click.echo("Performance:")
        click.echo(f"  Fingerprint cache size: {cfg.performance.fingerprint_cache_size}")
        click.echo(f"  Test timeout: {cfg.performance.test_timeout_seconds}s")
        click.echo(f"  Metrics retention: {cfg.performance.metrics_retention_days} days")
        click.echo()
        
        click.echo("Monitoring:")
        click.echo(f"  Health checks: {cfg.monitoring.health_check_enabled}")
        click.echo(f"  Metrics collection: {cfg.monitoring.metrics_collection_enabled}")
        click.echo(f"  Disk space warning: {cfg.monitoring.disk_space_warning_mb}MB")
        
    except Exception as e:
        handle_error(e, "config show")


@config.command()
@click.argument("output_path", type=click.Path(path_type=Path))
def sample(output_path: Path):
    """Generate a sample configuration file."""
    try:
        config_manager = ConfigManager()
        config_manager.save_sample_config(output_path)
        
        click.echo(f"✅ Sample configuration saved to {output_path}")
        click.echo()
        click.echo("Edit the file and place it in one of these locations:")
        click.echo("  ~/.zed/config.yaml")
        click.echo("  ~/.config/zed/config.yaml")
        click.echo("  /etc/zed/config.yaml")
        click.echo()
        click.echo("Or set ZED_CONFIG_PATH environment variable to specify a custom location.")
        
    except Exception as e:
        handle_error(e, "config sample")


@config.command()
def env():
    """Show environment variable help."""
    try:
        config_manager = ConfigManager()
        help_text = config_manager.get_env_help()
        click.echo(help_text)
        
    except Exception as e:
        handle_error(e, "config env")


@config.command()
def reload():
    """Reload configuration from all sources."""
    try:
        repo = None
        try:
            repo = _find_repository()
        except ValueError:
            pass  # No repository found, use global config
        
        cfg = reload_config(repo.path if repo else None)
        click.echo("✅ Configuration reloaded")
        
        if cfg.config_file_path:
            click.echo(f"Loaded from: {cfg.config_file_path}")
        else:
            click.echo("Using default configuration")
        
    except Exception as e:
        handle_error(e, "config reload")


def _find_repository() -> Repository:
    """Find repository with helpful error context."""
    current = Path.cwd()
    checked_paths = []
    
    while current != current.parent:
        checked_paths.append(current)
        repo = Repository(current)
        if repo.exists():
            return repo
        current = current.parent
    
    # Provide helpful error with context
    error_msg = "❌ Not in a Shadow VCS repository\n\n"
    error_msg += "Searched in:\n"
    for path in checked_paths[:3]:  # Show first 3 paths
        error_msg += f"  {path}\n"
    if len(checked_paths) > 3:
        error_msg += f"  ... and {len(checked_paths) - 3} more\n"
    error_msg += "\n💡 Run 'zed init' to create a repository"
    
    raise ValueError(error_msg)


def _resolve_commit_id(repo: Repository, partial_id: str) -> str:
    """Resolve a partial commit ID to full ID."""
    from zed.core.db import connect
    
    with connect(repo.db_path, repo.path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM commits WHERE id LIKE ? || '%'",
            (partial_id,),
        )
        matches = cursor.fetchall()
        
        if not matches:
            raise ValueError(f"No commit found matching '{partial_id}'")
        
        if len(matches) > 1:
            commit_list = [match["id"][:8] for match in matches[:5]]
            if len(matches) > 5:
                commit_list.append("...")
            raise ValueError(
                f"Ambiguous commit ID '{partial_id}' matches {len(matches)} commits: {', '.join(commit_list)}\n"
                f"💡 Use a longer prefix to disambiguate"
            )
        
        return matches[0]["id"]


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main() 