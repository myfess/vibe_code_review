import os
from src.git.diff import get_commit_changes, is_git_repo, get_changed_files_list
from src.ai.ai_chat import ask_openai_router
from src.html_writer import save_review_to_html, open_in_chrome
from src.gpt_prompts import REVIEW_PROMPT
from src.git.git_subprocess import checkout_branch, pull_branch
from src.utils.logger import logger

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
    logger.log(f"Starting review of last commit in repository: {repo_path}")

    if not os.path.exists(repo_path):
        error_msg = f"Error: Path {repo_path} does not exist"
        logger.log(error_msg)
        return error_msg

    if not is_git_repo(repo_path):
        error_msg = f"Error: {repo_path} is not a git repository"
        logger.log(error_msg)
        return error_msg

    logger.log("Getting commit changes...")
    changes = get_commit_changes(repo_path)

    if not changes.strip():
        msg = "No changes found in the last commit"
        logger.log(msg)
        return msg

    logger.log("Preparing review prompt...")
    prompt = REVIEW_PROMPT.format(changes=changes)

    file_path = None
    files_list = get_changed_files_list(repo_path)
    if files_list:
        for file in files_list:
            file_path = repo_path + '/' + file
            logger.log(f"Changed file: {file_path}")
        file_path = repo_path + '/' + files_list[0]
        logger.log(f"Using file context from: {file_path}")

    logger.log("Requesting AI review...")
    review = ask_openai_router(prompt, file_path)
    if review is None:
        error_msg = "Error: Could not get AI review response"
        logger.log(error_msg)
        return error_msg

    logger.log("Successfully received AI review")
    return review

def run_code_review(repo_path: str) -> str:
    """
    Main function to run the code review process
    """
    logger.log(f"Starting code review process for repository: {repo_path}")

    logger.log("Getting review from last commit...")
    review = review_last_commit(repo_path)
    if review.startswith("Error:"):
        logger.log(f"Error during review: {review}")
        return review
    logger.log("Successfully received review from last commit")

    logger.log("Saving review to HTML file...")
    output_file = save_review_to_html(review)
    logger.log(f"Review saved to: {output_file}")

    logger.log("Opening review in Chrome browser...")
    open_in_chrome(output_file)
    logger.log("Review opened in Chrome browser")

    logger.log("Code review process completed successfully")
    return review
