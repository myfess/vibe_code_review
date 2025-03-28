"""
Pavlov Dima
"""

import os
import sys
from typing import List
from git_subprocess import run_git_command, is_git_repo, is_merge_commit

def get_changed_files_output(repo_path: str) -> str:
    """
    Get the git diff output for the last commit

    Args:
        repo_path: Path to git repository

    Returns:
        str: Git diff output
    """
    if not is_git_repo(repo_path):
        print(f"Error: {repo_path} is not a git repository")
        sys.exit(1)

    if is_merge_commit(repo_path):
        # Get files changed in the merge
        files_command = ["git", "diff-tree", "--name-status", "-r", "--no-commit-id", "HEAD^1..HEAD"]
    else:
        # For regular commits
        files_command = ["git", "show", "--name-status", "--oneline", "HEAD"]

    return run_git_command(files_command, repo_path)

def get_changed_files_list(repo_path: str) -> List[str]:
    """
    Returns a list of changed file names from the last commit.

    Args:
        repo_path: Path to git repository

    Returns:
        List[str]: List of file paths that were changed in the last commit
    """
    output = get_changed_files_output(repo_path)
    files = []

    for line in output.split('\n'):
        if line.strip():
            parts = line.split('\t')
            if len(parts) >= 2:
                files.append(parts[-1])

    return files

def get_last_commit_info(repo_path: str) -> str:
    """
    Get information about the last commit

    Args:
        repo_path: Path to git repository

    Returns:
        str: Formatted commit information
    """
    if not is_git_repo(repo_path):
        print(f"Error: {repo_path} is not a git repository")
        sys.exit(1)

    commit_command = ["git", "log", "-1",
                     "--format=%C(yellow)commit %H%n%C(auto)%d%nAuthor: %an <%ae>%nDate: %ad%n%n    %s%n"]
    return run_git_command(commit_command, repo_path)

def format_file_status(output: str) -> str:
    """
    Format the git status output

    Args:
        output: Git status output to format

    Returns:
        str: Formatted status message
    """
    # Split output into lines and remove empty lines
    lines = [line for line in output.split('\n') if line.strip()]

    # Format the output
    result = []
    result.append("\nИзмененные файлы:")
    result.append("-" * 40)

    if not lines:
        result.append("Нет измененных файлов")
        return '\n'.join(result)

    for line in lines:
        parts = line.split('\t')
        if len(parts) >= 2:
            status, file_path = parts[0], parts[-1]
            status_text = {
                'M': 'Изменен',
                'A': 'Добавлен',
                'D': 'Удален',
                'R': 'Переименован',
                'C': 'Скопирован'
            }.get(status[0], status)

            result.append(f"{status_text}: {file_path}")

    return '\n'.join(result)

def get_commit_changes(repo_path: str) -> str:
    """
    Get detailed changes (diff) from the last commit showing actual code changes

    Args:
        repo_path: Path to git repository

    Returns:
        str: Formatted diff output showing the actual changed code
    """
    if not is_git_repo(repo_path):
        print(f"Error: {repo_path} is not a git repository")
        sys.exit(1)

    # Base command to get changes
    if is_merge_commit(repo_path):
        base_command = ["git", "diff", "HEAD^1..HEAD"]
    else:
        base_command = ["git", "diff", "HEAD^..HEAD"]

    # Add options for better diff readability
    base_command.extend([
        "--patch",  # Show the actual patch/changes
        "--unified=3",  # Show 3 lines of context
        "--color=always",  # Add colors
        "--no-prefix"  # Remove a/ and b/ prefixes
    ])

    return run_git_command(base_command, repo_path)

def main():
    repo_path = str(os.getenv('REPO_PATH'))

    if not os.path.exists(repo_path):
        print(f"Error: Path {repo_path} does not exist")
        sys.exit(1)

    if not is_git_repo(repo_path):
        print(f"Error: {repo_path} is not a git repository")
        sys.exit(1)

    # Get and display commit info
    commit_info = get_last_commit_info(repo_path)
    print(commit_info)

    # Get and display changed files
    changed_files_output = get_changed_files_output(repo_path)
    print(format_file_status(changed_files_output))

    # Get list of changed files
    files_list = get_changed_files_list(repo_path)
    if files_list:
        print("\nСписок измененных файлов:")
        for file in files_list:
            print(f"- {file}")

        print("\nИзменения в коде:")
        print("-" * 40)
        changes = get_commit_changes(repo_path)
        print(changes)

if __name__ == "__main__":
    main()
