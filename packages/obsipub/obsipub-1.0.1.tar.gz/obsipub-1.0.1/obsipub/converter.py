"""
Main converter class for Obsipub
"""

import os
import shutil
import hashlib
import subprocess
import logging
from .file_scanner import FileScanner
from .markdown_processor import MarkdownProcessor
from .utils import setup_warning_logger

class ObsidianToEpubConverter:
    """
    Main converter class that orchestrates the conversion process.
    """
    
    def __init__(self, vault_path, output_epub_path, title="Obsidian Vault", 
                 author="", include_attachments=True, include_tags=False):
        """
        Initialize the converter.
        
        Args:
            vault_path (str): Path to the Obsidian vault
            output_epub_path (str): Path for the output EPUB file
            title (str): Title for the EPUB
            author (str): Author for the EPUB
            include_attachments (bool): Whether to include attachments
            include_tags (bool): Whether to keep Obsidian tags
        """
        self.vault_path = os.path.abspath(vault_path)
        self.output_epub_path = os.path.abspath(output_epub_path)
        self.title = title
        self.author = author
        self.include_attachments = include_attachments
        self.include_tags = include_tags
        
        # Initialize components
        self.file_scanner = FileScanner(self.vault_path)
        self.warning_logger = setup_warning_logger()
        
        # These will be initialized during conversion
        self.attachment_map = {}
        self.markdown_processor = None
        
    def convert(self):
        """
        Execute the full conversion process.
        
        Returns:
            bool: True if conversion successful, False otherwise
        """
        logging.info(f"Starting conversion of Obsidian vault '{self.vault_path}' to ePub '{self.output_epub_path}'")
        logging.info(f"Title: '{self.title}' Author: '{self.author}' Include Attachments: {self.include_attachments}, Include Tags: {self.include_tags}")

        try:
            # Scan vault
            all_vault_items = self.file_scanner.scan_vault()
            
            # Setup temporary directory
            temp_dir = self._setup_temp_directory()
            
            # Process attachments
            if self.include_attachments:
                self._process_attachments(all_vault_items, temp_dir)
            
            # Initialize markdown processor with attachment map
            self.markdown_processor = MarkdownProcessor(
                self.vault_path, self.attachment_map, self.warning_logger
            )
            
            # Process markdown files
            processed_md_paths = self._process_markdown_files(all_vault_items, temp_dir)
            
            # Generate EPUB
            success = self._generate_epub(processed_md_paths, temp_dir)
            
            return success
            
        except Exception as e:
            logging.error(f"Conversion failed: {e}")
            self.warning_logger.error(f"Conversion failed with exception: {e}")
            return False
        
        finally:
            # Cleanup
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logging.info(f"Cleaned up temporary directory: {temp_dir}")
    
    def _setup_temp_directory(self):
        """
        Setup temporary directory for processing.
        
        Returns:
            str: Path to temporary directory
        """
        temp_dir = os.path.join(os.getcwd(), "temp_epub_content")
        temp_attachments_dir = os.path.join(temp_dir, "attachments")
        os.makedirs(temp_attachments_dir, exist_ok=True)
        logging.info(f"Created temporary directory for content: {temp_dir}")
        return temp_dir
    
    def _process_attachments(self, all_vault_items, temp_dir):
        """
        Process and copy attachments to temporary directory.
        
        Args:
            all_vault_items (list): List of all vault items
            temp_dir (str): Temporary directory path
        """
        logging.info("Processing attachments...")
        temp_attachments_dir = os.path.join(temp_dir, "attachments")
        
        for item_path, relative_path, item_type in all_vault_items:
            if item_type == "attachment":
                try:
                    attachment_filename = os.path.basename(item_path)
                    unique_id = hashlib.md5(relative_path.encode()).hexdigest()[:8]
                    unique_attachment_name = f"{unique_id}_{attachment_filename}"
                    dest_path = os.path.join(temp_attachments_dir, unique_attachment_name)
                    shutil.copy2(item_path, dest_path)
                    self.attachment_map[attachment_filename] = os.path.join("attachments", unique_attachment_name).replace("\\", "/")
                    logging.info(f"Copied attachment '{relative_path}' to '{dest_path}'")
                except Exception as e:
                    self.warning_logger.warning(f"Could not copy attachment {item_path}: {e}")
    
    def _process_markdown_files(self, all_vault_items, temp_dir):
        """
        Process markdown files and directories.
        
        Args:
            all_vault_items (list): List of all vault items
            temp_dir (str): Temporary directory path
            
        Returns:
            list: List of processed markdown file paths
        """
        logging.info("Processing Markdown files and directories...")
        processed_md_paths = []
        
        for item_path, relative_path, item_type in all_vault_items:
            if item_type == "directory":
                processed_path = self._process_directory(relative_path, temp_dir)
                processed_md_paths.append(processed_path)
                
            elif item_type == "markdown":
                processed_path = self._process_markdown_file(item_path, relative_path, temp_dir)
                if processed_path:
                    processed_md_paths.append(processed_path)
        
        return processed_md_paths
    
    def _process_directory(self, relative_path, temp_dir):
        """
        Process a directory entry and create a heading file.
        
        Args:
            relative_path (str): Relative path of the directory
            temp_dir (str): Temporary directory path
            
        Returns:
            str: Path to created directory heading file
        """
        heading_level = relative_path.count(os.sep) + 1
        dir_name_for_file = relative_path.replace(os.sep, "_")
        temp_md_path = os.path.join(temp_dir, f"_dir_{dir_name_for_file}.md")
        
        with open(temp_md_path, "w", encoding="utf-8") as f:
            dir_title = os.path.basename(relative_path).replace('_', ' ').title()
            f.write(f"{'#' * heading_level} {dir_title}\n\n")
        
        logging.info(f"Added directory heading for '{relative_path}' to '{temp_md_path}'")
        return temp_md_path
    
    def _process_markdown_file(self, item_path, relative_path, temp_dir):
        """
        Process a single markdown file.
        
        Args:
            item_path (str): Full path to the markdown file
            relative_path (str): Relative path of the file
            temp_dir (str): Temporary directory path
            
        Returns:
            str or None: Path to processed file or None if skipped
        """
        try:
            with open(item_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            processed_content = self.markdown_processor.preprocess_markdown(
                content, item_path, self.include_tags
            )
            
            if not processed_content.strip():
                self.warning_logger.warning(f"Skipping Markdown file {item_path} as it became empty after preprocessing.")
                return None
            
            # Calculate heading level and create file title
            file_dir = os.path.dirname(relative_path) if os.path.dirname(relative_path) else ""
            heading_level = file_dir.count(os.sep) + 2 if file_dir else 1
            file_title = os.path.splitext(os.path.basename(relative_path))[0].replace('_', ' ').replace('-', ' ').title()
            
            # Shift headers down and add file title
            shifted_content = self.markdown_processor.shift_headers_down(processed_content)
            content_with_heading = f"{'#' * heading_level} {file_title}\n\n{shifted_content}"
            
            # Save processed file
            temp_md_filename = os.path.join(temp_dir, relative_path.replace(os.sep, "_"))
            with open(temp_md_filename, "w", encoding="utf-8") as f:
                f.write(content_with_heading)
            
            logging.info(f"Processed Markdown file '{relative_path}' and saved to '{temp_md_filename}'")
            return temp_md_filename
            
        except Exception as e:
            self.warning_logger.warning(f"Skipping Markdown file {item_path} due to processing error: {e}")
            return None
    
    def _generate_epub(self, processed_md_paths, temp_dir):
        """
        Generate the final EPUB using pandoc.
        
        Args:
            processed_md_paths (list): List of processed markdown file paths
            temp_dir (str): Temporary directory path
            
        Returns:
            bool: True if successful, False otherwise
        """
        command = [
            "pandoc",
            "-s", 
            "--toc", 
            "-o", self.output_epub_path,
            f"--metadata=title:{self.title}",
            f"--metadata=author:{self.author}",
            f"--resource-path={temp_dir}"
        ] + processed_md_paths

        try:
            logging.info(f"Executing Pandoc command: {' '.join(command)}")
            subprocess.run(command, check=True, capture_output=True, text=True)
            logging.info(f"Conversion completed successfully: {self.output_epub_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during conversion: {e}")
            logging.error(f"Pandoc stdout:\n{e.stdout}")
            logging.error(f"Pandoc stderr:\n{e.stderr}")
            self.warning_logger.error(f"Pandoc conversion failed. See above for details. Error: {e.stderr}")
            return False