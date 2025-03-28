"""
Module for handling subprocess operations with git commands
"""

import subprocess
import sys
import locale
from typing import List
from logger import logger

def run_git_command(command: List[str], repo_path: str, encoding: str = 'utf-8') -> str:
    """
    Runs a git command in the specified repository path

    Args:
        command: List of command arguments
        repo_path: Path to git repository
        encoding: Character encoding to use

    Returns:
        str: Command output
    """
    try:
        result = subprocess.run(command,
                              capture_output=True,
                              text=True,
                              encoding=encoding,
                              check=False,
                              cwd=repo_path)

        if result.returncode != 0:
            logger.log(f"Error executing git command: {' '.join(command)}")
            logger.log(result.stderr)
            sys.exit(1)

        return result.stdout
    except UnicodeDecodeError:
        # Fallback to system encoding if specified encoding fails
        system_encoding = locale.getpreferredencoding()
        result = subprocess.run(command,
                              capture_output=True,
                              text=True,
                              encoding=system_encoding,
                              check=False,
                              cwd=repo_path)
        return result.stdout

def is_git_repo(path: str) -> bool:
    """
    Check if the specified path is a git repository

    Args:
        path: Path to check

    Returns:
        bool: True if path is a git repository, False otherwise
    """
    try:
        subprocess.run(["git", "rev-parse", "--git-dir"],
                      capture_output=True,
                      check=True,
                      cwd=path)
        return True
    except subprocess.CalledProcessError:
        return False

def is_merge_commit(repo_path: str) -> bool:
    """
    Check if the current HEAD is a merge commit

    Args:
        repo_path: Path to git repository

    Returns:
        bool: True if current HEAD is a merge commit, False otherwise
    """
    return subprocess.run(
        ["git", "rev-parse", "HEAD^2"],
        capture_output=True,
        text=True,
        check=False,
        cwd=repo_path
    ).returncode == 0

def checkout_branch(repo_path: str, branch_name: str) -> bool:
    """
    Checkout to specified branch

    Args:
        repo_path: Path to git repository
        branch_name: Name of the branch to checkout

    Returns:
        bool: True if checkout successful, False otherwise
    """
    try:
        run_git_command(["git", "checkout", branch_name], repo_path)
        return True
    except Exception as e:
        logger.log(f"Error checking out branch {branch_name}: {str(e)}")
        return False

def pull_branch(repo_path: str) -> bool:
    """
    Pull latest changes for current branch

    Args:
        repo_path: Path to git repository

    Returns:
        bool: True if pull successful, False otherwise
    """
    try:
        run_git_command(["git", "pull"], repo_path)
        return True
    except Exception as e:
        logger.log(f"Error pulling latest changes: {str(e)}")
        return False
