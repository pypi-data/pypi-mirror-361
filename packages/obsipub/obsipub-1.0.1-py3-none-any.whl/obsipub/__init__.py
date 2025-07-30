"""
Obsipub - Convert Obsidian vaults to EPUB format

A Python package for converting Obsidian knowledge bases to EPUB ebooks
with proper chapter structure, YAML preprocessing, and attachment handling.
"""

__version__ = "1.0.0"
__author__ = "TCSenpai"
__description__ = "Convert Obsidian vaults to EPUB format"

from .converter import ObsidianToEpubConverter
from .file_scanner import FileScanner
from .markdown_processor import MarkdownProcessor
from .utils import resolve_obsidian_path

__all__ = [
    'ObsidianToEpubConverter',
    'FileScanner', 
    'MarkdownProcessor',
    'resolve_obsidian_path'
]