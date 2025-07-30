# Obsipub

Convert your Obsidian knowledge base to beautifully formatted EPUB ebooks with proper chapter structure and attachment handling.

## Features

🔧 **Smart Processing**
- Bulletproof YAML front matter handling
- Wikilink conversion to standard markdown links
- Automatic attachment processing and inclusion
- Hidden/system file exclusion (.git, .obsidian, etc.)

📚 **Perfect EPUB Structure**
- Folders become chapters with proper heading hierarchy
- Notes become sections with shifted headers for clean TOC
- Automatic table of contents generation
- Proper metadata handling

🎯 **Flexible Options**
- Include or exclude attachments
- Keep or remove Obsidian tags
- Custom book title and author
- Verbose logging for debugging

## Installation

### From PyPI (recommended)

```bash
pip install obsipub
```

### From Source

```bash
git clone https://github.com/yourusername/obsipub.git
cd obsipub
pip install -e .
```

## Requirements

- Python 3.7+
- [Pandoc](https://pandoc.org/installing.html) (for EPUB generation)

### Installing Pandoc

**Ubuntu/Debian:**
```bash
sudo apt install pandoc
```

**macOS:**
```bash
brew install pandoc
```

**Windows:**
Download from [pandoc.org](https://pandoc.org/installing.html)

## Quick Start

### Command Line Usage

```bash
# Basic conversion
obsipub /path/to/obsidian/vault output.epub

# With custom title and author
obsipub /path/to/vault mybook.epub --title "My Knowledge Base" --author "Your Name"

# Exclude attachments and keep tags
obsipub /path/to/vault book.epub --no-attachments --include-tags

# Verbose output for debugging
obsipub /path/to/vault book.epub --verbose
```

### Python API Usage

```python
from obsipub import ObsidianToEpubConverter

# Basic usage
converter = ObsidianToEpubConverter(
    vault_path="/path/to/obsidian/vault",
    output_epub_path="output.epub",
    title="My Knowledge Base",
    author="Your Name"
)

success = converter.convert()
if success:
    print("Conversion completed!")
else:
    print("Conversion failed - check warning.log")

# Advanced usage with options
converter = ObsidianToEpubConverter(
    vault_path="/path/to/vault", 
    output_epub_path="book.epub",
    title="Advanced Guide",
    author="Expert Author",
    include_attachments=True,  # Include images and files
    include_tags=False         # Remove #tags from content
)

converter.convert()
```

## How It Works

### File Processing
1. **Scanning**: Recursively scans your vault, ignoring system directories
2. **Structure**: Maps folder hierarchy to EPUB chapter structure
3. **Processing**: Handles YAML front matter, wikilinks, and attachments
4. **Generation**: Uses Pandoc to create the final EPUB

### Heading Hierarchy
```
Folder/                     → # Chapter (H1)
├── Subfolder/             → ## Subchapter (H2)  
│   ├── Note.md           → ### Note Title (H3)
│   │   ├── # Header      → #### Header (H4)
│   │   └── ## Subheader  → ##### Subheader (H5)
```

### What Gets Processed
- ✅ Markdown files (.md)
- ✅ Images (PNG, JPG, GIF, etc.)
- ✅ Documents (PDF, DOCX, etc.)
- ✅ Wikilinks `[[Note Name]]`
- ✅ Attachments `![[image.png]]`

### What Gets Excluded
- ❌ Hidden directories (`.obsidian`, `.git`, `.trash`)
- ❌ System files (`.DS_Store`, `Thumbs.db`)
- ❌ Temporary files (`.tmp`, `.log`, `.pyc`)

## Command Line Options

```bash
obsipub [-h] [--title TITLE] [--author AUTHOR] [--no-attachments] 
        [--include-tags] [--verbose] [--version] 
        vault_path output_epub_path
```

### Arguments
- `vault_path`: Path to your Obsidian vault directory
- `output_epub_path`: Where to save the generated EPUB file

### Options
- `--title`: Custom book title (default: "Obsidian Vault")
- `--author`: Book author name
- `--no-attachments`: Skip including images and attachments
- `--include-tags`: Keep Obsidian tags like `#important` in text
- `--verbose`: Enable detailed logging output
- `--version`: Show version information

## Examples

### Convert Specific Subfolder
```bash
# Convert only your "Projects" folder
obsipub "/path/to/vault/Projects" projects.epub --title "My Projects"
```

### Academic Paper Collection
```bash
obsipub "/path/to/research" research.epub \
  --title "Research Collection" \
  --author "Dr. Smith" \
  --include-tags
```

### Clean Documentation Export
```bash
obsipub "/path/to/docs" documentation.epub \
  --title "Project Documentation" \
  --no-attachments
```

## Troubleshooting

### Common Issues

**"Command not found: pandoc"**
- Install Pandoc following the [installation guide](https://pandoc.org/installing.html)

**"Permission denied" errors**
- Ensure you have read access to the vault directory
- Check write permissions for the output directory

**Empty or missing content**
- Check `warning.log` for specific file processing issues
- Use `--verbose` flag for detailed logging
- Ensure markdown files have actual content after YAML processing

**Large file sizes**
- Use `--no-attachments` to exclude images and documents
- Consider converting subfolders instead of entire vault

### Getting Help

1. Check `warning.log` for detailed error information
2. Run with `--verbose` for debug output
3. Ensure all file paths are absolute or correctly relative
4. Verify Pandoc installation: `pandoc --version`

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

### Development Setup
```bash
git clone https://github.com/yourusername/obsipub.git
cd obsipub
pip install -e ".[dev]"
```

## License

MIT License - see LICENSE file for details.

## Changelog

### v1.0.0
- Initial release
- Modular architecture
- CLI and Python API
- Bulletproof YAML processing
- Smart header hierarchy
- Attachment handling
- System file exclusion