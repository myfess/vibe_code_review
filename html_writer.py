import os
import glob
import webbrowser

def get_next_file_number(results_dir: str) -> int:
    """Get the next available file number in the results directory"""
    existing_files = glob.glob(os.path.join(results_dir, '*.html'))
    if not existing_files:
        return 1

    numbers = [int(os.path.splitext(os.path.basename(f))[0]) for f in existing_files]
    return max(numbers) + 1 if numbers else 1

def save_review_to_html(review: str, results_dir: str = 'results') -> str:
    """
    Save review content to an HTML file in the results directory

    Args:
        review: Review content to save
        results_dir: Directory to save results in (default: 'results')

    Returns:
        str: Path to the saved file
    """
    # Create results directory if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)

    # Get next available number and create file path
    next_number = get_next_file_number(results_dir)
    output_file = os.path.join(results_dir, f"{next_number}.html")

    # Read the HTML template
    template_path = os.path.join(os.path.dirname(__file__), 'template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Replace content placeholder with actual review
    html_content = template.replace('{content}', review)

    # Save the review with HTML wrapper
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_file

def open_in_chrome(file_path: str) -> None:
    """
    Opens the specified HTML file in Chrome browser

    Args:
        file_path: Path to the HTML file to open
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return

    # Convert to absolute path if needed
    abs_path = os.path.abspath(file_path)

    # Create file URL with proper formatting for Windows
    file_url = 'file:///' + abs_path.replace('\\', '/').replace(' ', '%20')

    try:
        # List of possible Chrome paths on Windows
        chrome_paths = [
            'C:/Program Files/Google Chrome/Application/chrome.exe',
            'C:/Program Files (x86)/Google Chrome/Application/chrome.exe',
            os.path.expandvars('%LocalAppData%/Google/Chrome/Application/chrome.exe')
        ]

        # Try each Chrome path
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                browser = webbrowser.get(f'"{chrome_path}" %s')
                browser.open(file_url)
                print(f"Opened in Chrome: {file_url}")
                return

        # If Chrome not found, try default browser
        print("Chrome not found, trying default browser...")
        webbrowser.open(file_url)
        print(f"Opened in default browser: {file_url}")
    except Exception as e:
        print(f"Error opening browser: {str(e)}")
        print(f"Try opening this URL manually: {file_url}")
