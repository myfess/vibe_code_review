import os
import tkinter as tk
from tkinter import ttk, messagebox
from review_logic import run_code_review
from logger import logger


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Code Review")
        self.root.geometry("800x600")

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Repository path input
        ttk.Label(main_frame, text="Repository Path:").grid(row=0, column=0, sticky="w", pady=5)
        self.repo_path = ttk.Entry(main_frame, width=50)
        self.repo_path.grid(row=0, column=1, sticky="ew", pady=5)

        # Pre-fill repository path from environment variable
        repo_path = os.getenv('REPO_PATH')
        if repo_path:
            self.repo_path.insert(0, repo_path)

        # Branch name input
        ttk.Label(main_frame, text="Branch Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.branch_name = ttk.Entry(main_frame, width=50)
        self.branch_name.grid(row=1, column=1, sticky="ew", pady=5)

        # Pre-fill branch name from environment variable
        git_branch = os.getenv('GIT_BRANCH')
        if git_branch:
            self.branch_name.insert(0, git_branch)

        # Button frame for button and progress
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        # Review button
        self.button = ttk.Button(button_frame, text="Get Review", command=self.get_review)
        self.button.pack(side=tk.LEFT, padx=5)

        # Progress indicator
        self.progress = ttk.Label(button_frame, text="")
        self.progress.pack(side=tk.LEFT, padx=5)

        # Status output
        self.output_text = tk.Text(main_frame, height=20, width=80)
        self.output_text.grid(row=3, column=0, columnspan=2, pady=10)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        # Set up logger callback
        logger.set_gui_callback(self.log_message)

    def log_message(self, message: str):
        """Add a message to the output text area"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update()

    def set_processing_state(self, is_processing: bool):
        """Update UI elements based on processing state"""
        if is_processing:
            self.button.state(['disabled'])
            self.progress.config(text="Processing...")
        else:
            self.button.state(['!disabled'])
            self.progress.config(text="")
        self.root.update()

    def get_review(self):
        repo_path = self.repo_path.get().strip()
        branch_name = self.branch_name.get().strip()

        if not repo_path or not branch_name:
            messagebox.showerror("Error", "Please enter both repository path and branch name")
            return

        # Clear previous output and set processing state
        self.output_text.delete("1.0", tk.END)
        self.log_message("Starting code review process...")
        self.log_message(f"Repository: {repo_path}")
        self.log_message(f"Branch: {branch_name}")
        self.set_processing_state(True)

        try:
            # Get the review
            run_code_review(repo_path, branch_name)
            self.log_message("Review completed successfully!")
            self.log_message("Results have been saved to file and opened in browser.")
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)
        finally:
            # Always restore UI state
            self.set_processing_state(False)

def main():
    root = tk.Tk()
    # pylint: disable=unused-variable
    # ruff: noqa: F841
    app = App(root)
    # pylint: enable=unused-variable
    root.mainloop()

if __name__ == "__main__":
    main()
