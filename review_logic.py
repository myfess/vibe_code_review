import os
from diff import get_commit_changes, is_git_repo, get_changed_files_list
from ai_chat import ask_deepseek
from html_writer import save_review_to_html, open_in_chrome
from gpt_prompts import REVIEW_PROMPT
from git_subprocess import checkout_branch, pull_branch
from logger import logger

def setup_git_branch(repo_path: str, branch_name: str) -> bool:
    """
    Setup git branch by pulling latest changes, checking out, and pulling again
    """
    if not branch_name:
        logger.log("Error: Branch name is not specified")
        return False

    if not pull_branch(repo_path):
        return False

    if not checkout_branch(repo_path, branch_name):
        return False

    if not pull_branch(repo_path):
        return False

    return True

def review_last_commit(repo_path: str) -> str:
    """
    Get changes from the last commit and send them for AI code review
    """
    if not os.path.exists(repo_path):
        return f"Error: Path {repo_path} does not exist"

    if not is_git_repo(repo_path):
        return f"Error: {repo_path} is not a git repository"

    changes = get_commit_changes(repo_path)

    if not changes.strip():
        return "No changes found in the last commit"

    prompt = REVIEW_PROMPT.format(changes=changes)

    file_path = None
    files_list = get_changed_files_list(repo_path)
    if files_list:
        file_path = repo_path + '/' + files_list[0]

    review = ask_deepseek(prompt, file_path)
    if review is None:
        return "Error: Could not get AI review response"
    return review

def run_code_review(repo_path: str, branch_name: str) -> str:
    """
    Main function to run the code review process
    """
    if not repo_path:
        return "Error: REPO_PATH environment variable is not set"

    if not branch_name:
        return "Error: GIT_BRANCH environment variable is not set"

    if not setup_git_branch(repo_path, branch_name):
        return "Error: Failed to setup git branch"

    review = review_last_commit(repo_path)

    # Save review to HTML file
    output_file = save_review_to_html(review)

    # Open review in Chrome browser
    open_in_chrome(output_file)

    return review
