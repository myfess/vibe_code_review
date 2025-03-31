import os
import tkinter as tk
from tkinter import ttk, messagebox
from src.review_logic import run_code_review, setup_git_branch
from src.utils.logger import logger
from src.git.diff import get_last_commits


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Code Review")
        self.root.geometry("1400x800")  # Increased window width from 1200 to 1400

        # Create main container frame
        container = ttk.Frame(root)
        container.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # Left frame for existing controls
        left_frame = ttk.Frame(container, padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Right frame for commits history
        right_frame = ttk.Frame(container, padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew")

        # Configure grid weights for left frame
        left_frame.grid_columnconfigure(1, weight=1)
        left_frame.grid_rowconfigure(3, weight=1)  # Make the output text row expandable

        # Repository path input
        ttk.Label(left_frame, text="Repository Path:").grid(row=0, column=0, sticky="w", pady=5)
        self.repo_path = ttk.Entry(left_frame, width=50)
        self.repo_path.grid(row=0, column=1, sticky="ew", pady=5)

        # Pre-fill repository path from environment variable
        repo_path = os.getenv('REPO_PATH')
        if repo_path:
            self.repo_path.insert(0, repo_path)

        # Branch name input
        ttk.Label(left_frame, text="Branch Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.branch_name = ttk.Entry(left_frame, width=50)
        self.branch_name.grid(row=1, column=1, sticky="ew", pady=5)

        # Pre-fill branch name from environment variable
        git_branch = os.getenv('GIT_BRANCH')
        if git_branch:
            self.branch_name.insert(0, git_branch)

        # Button frame for buttons and progress
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        # Checkout button
        self.checkout_button = ttk.Button(button_frame, text="Checkout", command=self.checkout_branch)
        self.checkout_button.pack(side=tk.LEFT, padx=5)

        # Progress indicator
        self.progress = ttk.Label(button_frame, text="")
        self.progress.pack(side=tk.LEFT, padx=5)

        # Status output
        self.output_text = tk.Text(left_frame, width=80)  # Removed fixed height
        self.output_text.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")

        # Add scrollbar for output text
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        # Commits history section
        commits_header = ttk.Frame(right_frame)
        commits_header.pack(fill=tk.X, pady=5)

        ttk.Label(commits_header, text="Recent Commits").pack(side=tk.LEFT)

        # Refresh button for commits
        self.refresh_button = ttk.Button(commits_header, text="Refresh", command=self.refresh_commits)
        self.refresh_button.pack(side=tk.RIGHT)

        # Create frame for tree and scrollbar
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create Treeview for commits
        self.commits_tree = ttk.Treeview(
            tree_frame, columns=("selected", "time", "author", "message", "hash"), show="headings"
        )

        # Configure columns
        self.commits_tree.heading("selected", text="")
        self.commits_tree.heading("time", text="Time")
        self.commits_tree.heading("author", text="Author")
        self.commits_tree.heading("message", text="Message")
        self.commits_tree.heading("hash", text="Hash")

        # Set column widths
        self.commits_tree.column("selected", width=30, anchor="center")
        self.commits_tree.column("time", width=150)
        self.commits_tree.column("author", width=150)
        self.commits_tree.column("message", width=300)
        self.commits_tree.column("hash", width=100)

        # Add scrollbar for commits tree
        commits_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.commits_tree.yview)
        self.commits_tree.configure(yscrollcommand=commits_scrollbar.set)

        # Pack the tree and scrollbar
        self.commits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        commits_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Review button frame under commits
        review_frame = ttk.Frame(right_frame)
        review_frame.pack(fill=tk.X, pady=5)

        # Review button
        self.review_button = tk.Button(review_frame, text="Get Review", command=self.get_review,
                                     bg='#4CAF50', fg='white', relief='raised', padx=10)
        self.review_button.pack(side=tk.RIGHT)

        # Bind click event for checkbox handling
        self.commits_tree.bind('<ButtonRelease-1>', self.on_tree_click)

        # Set up logger callback
        logger.set_gui_callback(self.log_message)

    def on_tree_click(self, event):
        """Handle clicks on the tree view"""
        region = self.commits_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.commits_tree.identify_column(event.x)
            item = self.commits_tree.identify_row(event.y)

            if column == "#1":  # Checkbox column
                values = list(self.commits_tree.item(item)['values'])
                # Toggle checkbox
                values[0] = "☒" if values[0] == "☐" else "☐"
                self.commits_tree.item(item, values=values)

    def log_message(self, message: str):
        """Add a message to the output text area"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update()

    def set_processing_state(self, is_processing: bool):
        """Update UI elements based on processing state"""
        if is_processing:
            self.review_button.config(state='disabled')
            self.checkout_button.state(['disabled'])
            self.refresh_button.state(['disabled'])
            self.progress.config(text="Processing...")
        else:
            self.review_button.config(state='normal')
            self.checkout_button.state(['!disabled'])
            self.refresh_button.state(['!disabled'])
            self.progress.config(text="")
        self.root.update()

    def refresh_commits(self):
        """Refresh the commits list"""
        repo_path = self.repo_path.get().strip()

        if not repo_path:
            messagebox.showerror("Error", "Please enter repository path")
            return

        self.set_processing_state(True)
        try:
            # Clear existing items
            for item in self.commits_tree.get_children():
                self.commits_tree.delete(item)

            # Get and display commits
            commits = get_last_commits(repo_path, count=20)  # Request 20 commits instead of default 10
            for time, author, message, commit_hash in commits:
                # Add checkbox (☐) as first column
                self.commits_tree.insert("", "end", values=("☐", time, author, message, commit_hash))

            # Automatically check the first commit
            first_item = self.commits_tree.get_children()[0]
            values = list(self.commits_tree.item(first_item)['values'])
            values[0] = "☒"  # Check the first commit
            self.commits_tree.item(first_item, values=values)

        except Exception as e:
            error_msg = f"Failed to get commits: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)
        finally:
            self.set_processing_state(False)

    def get_selected_commits(self):
        """Get list of selected commits"""
        selected = []
        for item in self.commits_tree.get_children():
            values = self.commits_tree.item(item)['values']
            if values[0] == "☒":  # Checked checkbox
                selected.append((values[1], values[2], values[3], values[4]))  # (time, author, message, hash)
        return selected

    def checkout_branch(self):
        """Perform git checkout operations"""
        repo_path = self.repo_path.get().strip()
        branch_name = self.branch_name.get().strip()

        if not repo_path or not branch_name:
            messagebox.showerror("Error", "Please enter both repository path and branch name")
            return

        # Clear previous output and set processing state
        self.output_text.delete("1.0", tk.END)
        self.log_message("Starting checkout process...")
        self.log_message(f"Repository: {repo_path}")
        self.log_message(f"Branch: {branch_name}")
        self.set_processing_state(True)

        try:
            if setup_git_branch(repo_path, branch_name):
                self.log_message("Checkout completed successfully!")
                # Refresh commits list after successful checkout
                self.refresh_commits()
            else:
                error_msg = "Failed to setup git branch"
                self.log_message(f"ERROR: {error_msg}")
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)
        finally:
            # Always restore UI state
            self.set_processing_state(False)

    def get_review(self):
        """Get review for selected commits"""
        repo_path = self.repo_path.get().strip()
        selected_commits = self.get_selected_commits()

        if not repo_path:
            messagebox.showerror("Error", "Please enter repository path")
            return

        if not selected_commits:
            messagebox.showerror("Error", "Please select at least one commit to review")
            return

        # Set processing state
        self.log_message("Starting code review process...")
        self.log_message(f"Repository: {repo_path}")
        self.log_message(f"Selected commits: {len(selected_commits)}")
        self.log_message("Selected commit hashes:")
        for _, _, _, commit_hash in selected_commits:
            self.log_message(f"- {commit_hash}")
        self.set_processing_state(True)

        try:
            # Get the review
            run_code_review(repo_path)  # Pass None as branch_name to skip checkout
            self.log_message("Review completed successfully!")
            self.log_message("Results have been saved to file and opened in browser.")
            # Refresh commits list after successful review
            self.refresh_commits()
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)
        finally:
            # Always restore UI state
            self.set_processing_state(False)
