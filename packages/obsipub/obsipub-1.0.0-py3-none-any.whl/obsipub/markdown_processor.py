"""
Markdown processing functionality for Obsipub
"""

import os
import re
import logging
from .utils import resolve_obsidian_path

class MarkdownProcessor:
    """
    Processes Markdown content with Obsidian-specific features.
    """
    
    def __init__(self, vault_path, attachment_map, warning_logger):
        """
        Initialize the markdown processor.
        
        Args:
            vault_path (str): Path to the Obsidian vault
            attachment_map (dict): Mapping of attachment filenames to processed paths
            warning_logger: Logger for warnings
        """
        self.vault_path = vault_path
        self.attachment_map = attachment_map
        self.warning_logger = warning_logger
        
    def preprocess_markdown(self, markdown_content, current_md_file_path, include_tags=False):
        """
        Preprocess markdown content to handle YAML, wikilinks, and attachments.
        
        Args:
            markdown_content (str): Raw markdown content
            current_md_file_path (str): Path to the current markdown file
            include_tags (bool): Whether to keep Obsidian tags
            
        Returns:
            str: Processed markdown content
        """
        logging.info(f"Preprocessing Markdown file: {current_md_file_path}")

        # Handle empty content
        if not markdown_content.strip():
            self.warning_logger.warning(f"Skipping empty or whitespace-only Markdown file: {current_md_file_path}")
            return ""

        # Process YAML front matter
        processed_content = self._process_yaml_frontmatter(markdown_content, current_md_file_path)
        
        # Process wikilinks
        processed_content = self._process_wikilinks(processed_content)
        
        # Process attachments
        processed_content = self._process_attachments(processed_content, current_md_file_path)
        
        # Process tags
        if not include_tags:
            processed_content = self._remove_obsidian_tags(processed_content)
        else:
            logging.info("Keeping Obsidian tags.")

        return processed_content
    
    def shift_headers_down(self, content):
        """
        Shift all markdown headers down by one level (H1->H2, H2->H3, etc.).
        
        Args:
            content (str): Markdown content
            
        Returns:
            str: Content with shifted headers
        """
        lines = content.split('\n')
        shifted_lines = []
        for line in lines:
            # Check if line starts with markdown headers
            if re.match(r'^#{1,6}\s', line):
                # Add one more # to shift the header down one level
                shifted_lines.append('#' + line)
            else:
                shifted_lines.append(line)
        return '\n'.join(shifted_lines)
    
    def _process_yaml_frontmatter(self, markdown_content, current_md_file_path):
        """
        Process and remove YAML front matter to avoid pandoc parsing issues.
        """
        processed_content = markdown_content

        # Step 1: Replace standalone --- lines with *** to avoid YAML parsing issues
        processed_content = re.sub(r'^---$', '***', processed_content, flags=re.MULTILINE)
        
        # Step 2: Handle YAML front matter blocks more robustly
        yaml_match = re.match(r"^---\n(.*?)\n---\n(.*)", markdown_content, re.DOTALL)
        
        if yaml_match:
            yaml_block = yaml_match.group(1)
            content_after_yaml = yaml_match.group(2)
            
            # Always remove YAML front matter completely to avoid pandoc parsing issues
            processed_content = re.sub(r'^---$', '***', content_after_yaml, flags=re.MULTILINE)
            logging.debug(f"YAML front matter detected in {current_md_file_path}. Removing it to avoid pandoc issues.")
                
        elif markdown_content.startswith("---\n"):
            # Handle cases where there's an opening '---' but no closing one
            logging.debug(f"Unclosed YAML front matter detected at the start of {current_md_file_path}. Removing everything until content starts.")
            
            lines = markdown_content.split('\n')
            content_start_index = 1  # Skip the opening ---
            
            for i, line in enumerate(lines[1:], 1):
                # Skip empty lines and lines that look like YAML properties
                if line.strip() == "" or re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_-]*\s*:', line) or line.strip().startswith('- '):
                    continue
                else:
                    content_start_index = i
                    break
            
            if content_start_index < len(lines):
                processed_content = '\n'.join(lines[content_start_index:])
                processed_content = re.sub(r'^---$', '***', processed_content, flags=re.MULTILINE)
            else:
                processed_content = ""  # If no content found, assume entire file is malformed YAML

        return processed_content
    
    def _process_wikilinks(self, content):
        """
        Convert Obsidian wikilinks to standard markdown links.
        """
        def replace_wikilink(match):
            full_link = match.group(1)
            if '|' in full_link:
                target, display_text = full_link.split('|', 1)
            else:
                target = full_link
                display_text = full_link
            
            if not target.endswith(".md") and '#' not in target:
                target += ".md"
            logging.debug(f"Converted wikilink '[[{full_link}]]' to '[{display_text}]({target})'")
            return f"[{display_text}]({target})"

        return re.sub(r"\b\[\[(.*?)\]\]", replace_wikilink, content)
    
    def _process_attachments(self, content, current_md_file_path):
        """
        Process attachment references in markdown content.
        """
        def replace_attachment_path(match):
            original_path = None
            if match.group(1): 
                original_path = match.group(1)
                alt_text = os.path.basename(original_path)
            elif match.group(3): 
                original_path = match.group(3)
                alt_text = match.group(2) if match.group(2) else os.path.basename(original_path)
            
            if not original_path:
                logging.warning(f"Could not extract original path from attachment match: {match.group(0)}")
                return match.group(0)

            resolved_full_path = resolve_obsidian_path(current_md_file_path, original_path, self.vault_path)
            
            if resolved_full_path and os.path.exists(resolved_full_path):
                attachment_filename = os.path.basename(resolved_full_path)
                if attachment_filename in self.attachment_map:
                    new_path = self.attachment_map[attachment_filename]
                    logging.debug(f"Updated attachment path from '{original_path}' to '{new_path}'")
                    return f"![{alt_text}]({new_path})"
                else:
                    logging.warning(f"Attachment found but not mapped: {original_path}")
                    return f"**[Attachment not processed: {alt_text} ({original_path})]**"
            else:
                logging.warning(f"Attachment not found or could not be resolved: {original_path}")
                return f"**[Attachment not found: {alt_text} ({original_path})]**"

        return re.sub(r"!\[\[(.*?)\]\]|!\[(.*?)\]\((.*?)\)", replace_attachment_path, content, flags=re.DOTALL)
    
    def _remove_obsidian_tags(self, content):
        """
        Remove Obsidian tags from content.
        """
        logging.info("Removing Obsidian tags.")
        return re.sub(r"#([a-zA-Z0-9_\-/]+)", "", content)