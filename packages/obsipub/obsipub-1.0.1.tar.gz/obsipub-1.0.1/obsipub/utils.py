"""
Utility functions for Obsipub
"""

import os
import logging

def resolve_obsidian_path(current_file_path, target_path, vault_path):
    """
    Resolve relative and absolute paths for Obsidian links.
    
    Args:
        current_file_path (str): Path to the current markdown file
        target_path (str): Target path to resolve
        vault_path (str): Root path of the Obsidian vault
        
    Returns:
        str or None: Resolved absolute path or None if not found
    """
    logging.debug(f"Attempting to resolve path: {target_path} from {current_file_path}")
    
    if os.path.isabs(target_path):
        return target_path

    # Try relative to current file
    resolved_path = os.path.normpath(os.path.join(os.path.dirname(current_file_path), target_path))
    if os.path.exists(resolved_path):
        logging.debug(f"Resolved to relative path: {resolved_path}")
        return resolved_path

    # Try relative to vault root
    resolved_path = os.path.normpath(os.path.join(vault_path, target_path))
    if os.path.exists(resolved_path):
        logging.debug(f"Resolved to vault root path: {resolved_path}")
        return resolved_path

    logging.warning(f"Could not resolve path: {target_path}")
    return None

def setup_logging(log_level=logging.INFO):
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=log_level, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def setup_warning_logger():
    """
    Setup a separate warning logger that writes to warning.log file.
    
    Returns:
        logging.Logger: Configured warning logger
    """
    warning_logger = logging.getLogger('warning_logger')
    warning_logger.setLevel(logging.WARNING)
    warning_handler = logging.FileHandler('warning.log', mode='w')
    warning_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    warning_logger.addHandler(warning_handler)
    return warning_logger