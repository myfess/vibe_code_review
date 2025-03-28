import os
from diff import get_commit_changes, is_git_repo, get_changed_files_list
from ai_chat import ask_deepseek
from html_writer import save_review_to_html, open_in_chrome
from gpt_prompts import REVIEW_PROMPT
from git_subprocess import checkout_branch, pull_branch


def setup_git_branch(repo_path: str, branch_name: str) -> bool:
    """
    Setup git branch by checking out and pulling latest changes

    Args:
        repo_path: Path to git repository
        branch_name: Name of the branch to checkout

    Returns:
        bool: True if setup successful, False otherwise
    """
    if not branch_name:
        print("Error: Branch name is not specified")
        return False

    # Checkout to specified branch
    if not checkout_branch(repo_path, branch_name):
        return False

    # Pull latest changes
    if not pull_branch(repo_path):
        return False

    return True

def review_last_commit(repo_path: str) -> str:
    """
    Get changes from the last commit and send them for AI code review

    Args:
        repo_path: Path to git repository

    Returns:
        str: Code review feedback from AI
    """
    if not os.path.exists(repo_path):
        return f"Error: Path {repo_path} does not exist"

    if not is_git_repo(repo_path):
        return f"Error: {repo_path} is not a git repository"

    # Get the changes from last commit
    changes = get_commit_changes(repo_path)

    # If there are no changes, return early
    if not changes.strip():
        return "No changes found in the last commit"

    # Create the review prompt
    prompt = REVIEW_PROMPT.format(changes=changes)

    file_path = None
    files_list = get_changed_files_list(repo_path)
    if files_list:
        file_path = repo_path + '/' + files_list[0]

    # Get AI review
    review = ask_deepseek(prompt, file_path)
    if review is None:
        return "Error: Could not get AI review response"
    return review

def main():
    repo_path = os.getenv('REPO_PATH')
    if not repo_path:
        print("Error: REPO_PATH environment variable is not set")
        return

    branch_name = os.getenv('GIT_BRANCH')
    if not branch_name:
        print("Error: GIT_BRANCH environment variable is not set")
        return

    # Setup git branch
    if not setup_git_branch(repo_path, branch_name):
        print("Error: Failed to setup git branch")
        return

    print("Getting AI code review for the last commit...")
    review = review_last_commit(repo_path)

    # Save review to HTML file
    print("Saving to file")

    output_file = save_review_to_html(review)
    print(f"Review saved to: {output_file}")

    # Open review in Chrome browser
    print("Opening review in Chrome...")
    open_in_chrome(output_file)

if __name__ == "__main__":
    main()
