"""
File scanning functionality for Obsipub
"""

import os
import logging

class FileScanner:
    """
    Scans Obsidian vault directory structure and identifies files.
    """
    
    # Directories to skip (common system/hidden directories)
    SKIP_DIRS = {'.git', '.obsidian', '.trash', '__pycache__', 'node_modules', '.DS_Store'}
    
    # File extensions to skip
    SKIP_EXTENSIONS = ('.tmp', '.log', '.pyc')
    
    def __init__(self, vault_path):
        """
        Initialize the file scanner.
        
        Args:
            vault_path (str): Path to the Obsidian vault
        """
        self.vault_path = vault_path
        
    def scan_vault(self):
        """
        Scan the vault and return all files and their structure.
        
        Returns:
            list: List of tuples (file_path, relative_path, file_type)
                  where file_type is 'directory', 'markdown', or 'attachment'
        """
        logging.info(f"Scanning vault: {self.vault_path}")
        all_files = []
        
        for root, dirs, files in os.walk(self.vault_path):
            # Remove skipped directories from dirs list to prevent os.walk from entering them
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            dirs.sort()
            files.sort()

            relative_root = os.path.relpath(root, self.vault_path)
            if relative_root == ".":
                relative_root = ""

            # Add directory entries
            if relative_root and relative_root != ".":
                logging.info(f"Found directory: {relative_root}")
                all_files.append((root, relative_root, "directory"))

            # Process files
            for file in files:
                if self._should_skip_file(file):
                    continue
                    
                file_path = os.path.join(root, file)
                relative_file_path = os.path.join(relative_root, file) if relative_root else file
                
                if file.endswith(".md"):
                    logging.info(f"Found Markdown file: {relative_file_path}")
                    all_files.append((file_path, relative_file_path, "markdown"))
                else:
                    logging.info(f"Found attachment: {relative_file_path}")
                    all_files.append((file_path, relative_file_path, "attachment"))
        
        all_files.sort(key=lambda x: x[1])
        return all_files
    
    def _should_skip_file(self, filename):
        """
        Check if a file should be skipped.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            bool: True if file should be skipped
        """
        # Skip hidden files and files with certain extensions
        return (filename.startswith('.') or 
                filename.endswith(self.SKIP_EXTENSIONS))