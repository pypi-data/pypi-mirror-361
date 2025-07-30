"""
Command Line Interface for Obsipub
"""

import argparse
import sys
from .converter import ObsidianToEpubConverter
from .utils import setup_logging

def main():
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description="Convert an Obsidian vault to EPUB format",
        prog="obsipub"
    )
    
    parser.add_argument(
        "vault_path", 
        type=str, 
        help="Path to the Obsidian vault directory"
    )
    
    parser.add_argument(
        "output_epub_path", 
        type=str, 
        help="Path and filename for the output EPUB file"
    )
    
    parser.add_argument(
        "--title", 
        type=str, 
        default="Obsidian Vault", 
        help="Title of the EPUB book (default: 'Obsidian Vault')"
    )
    
    parser.add_argument(
        "--author", 
        type=str, 
        default="", 
        help="Author of the EPUB book"
    )
    
    parser.add_argument(
        "--no-attachments", 
        action="store_true", 
        help="Do not include attachments in the EPUB"
    )
    
    parser.add_argument(
        "--include-tags", 
        action="store_true", 
        help="Keep Obsidian tags in the text (they are removed by default)"
    )
    
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 1.0.0"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(getattr(__import__('logging'), log_level))

    # Create converter and run conversion
    converter = ObsidianToEpubConverter(
        vault_path=args.vault_path,
        output_epub_path=args.output_epub_path,
        title=args.title,
        author=args.author,
        include_attachments=not args.no_attachments,
        include_tags=args.include_tags
    )

    success = converter.convert()
    
    if success:
        print(f"✅ Conversion completed successfully!")
        print(f"📖 EPUB created: {args.output_epub_path}")
        print(f"⚠️  Check warning.log for any warnings or issues")
        sys.exit(0)
    else:
        print(f"❌ Conversion failed!")
        print(f"⚠️  Check warning.log and console output for details")
        sys.exit(1)

if __name__ == "__main__":
    main()