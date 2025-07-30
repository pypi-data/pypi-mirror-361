# hamel_tools

CLI tools that wrap the [hamel](https://github.com/hamelsmu/hamel) Python library for working with YouTube videos and generating content.

## Installation

```bash
# Install in development mode
pip install -e .

# Or using the Makefile
make install-dev
```

This installs three CLI commands:
- `ai-transcribe` - Download YouTube transcripts  
- `ai-chapters` - Generate YouTube chapter summaries
- `ai-annotate-talk` - Create annotated blog posts from technical talks

## Usage

### Transcript Tool
```bash
# Download transcript with timestamps
ai-transcribe "https://youtu.be/VIDEO_ID"

# Use seconds-only timestamps
ai-transcribe "https://youtu.be/VIDEO_ID" --seconds

# Save to file
ai-transcribe "https://youtu.be/VIDEO_ID" > transcript.txt
```

### Chapter Generator
```bash
# Generate chapters (requires GEMINI_API_KEY)
export GEMINI_API_KEY="your-api-key"
ai-chapters "https://youtu.be/VIDEO_ID"
```

### Annotated Talk Generator
```bash
# Generate annotated blog post (requires both API keys)
export GEMINI_API_KEY="your-api-key"
export JINA_READER_KEY="your-api-key"

# Basic usage
ai-annotate-talk "https://youtu.be/VIDEO_ID" slides.pdf output_images/

# With custom transcript
ai-annotate-talk "https://youtu.be/VIDEO_ID" slides.pdf output_images/ --transcript transcript.txt

# Save to file
ai-annotate-talk "https://youtu.be/VIDEO_ID" slides.pdf output_images/ --output post.md
```

### Prerequisites

For annotate-talk, you need poppler-utils:
```bash
# macOS
brew install poppler

# Ubuntu/Debian
apt-get install poppler-utils
```

## Development

### Running Tests
```bash
./test.sh
```

### Version Management

The Makefile includes version bump commands that update both `pyproject.toml` and `__init__.py`:

```bash
# Bump versions
make bump-patch     # 0.1.0 -> 0.1.1
make bump-minor     # 0.1.0 -> 0.2.0  
make bump-major     # 0.1.0 -> 1.0.0

# Create a release (bump + git tag)
make release-patch  # Bumps patch and tags
make release-minor  # Bumps minor and tags
make release-major  # Bumps major and tags
```

### Publishing to PyPI

#### Setup
1. Install publishing tools:
   ```bash
   make install-publish-tools
   ```

2. Configure twine (see `.pypirc.example`):
   ```bash
   cp .pypirc.example ~/.pypirc
   # Edit ~/.pypirc with your PyPI tokens
   ```

#### Release Workflow
```bash
# 1. Create a release
make release-minor  # or release-patch, release-major

# 2. Push to GitHub
git push && git push --tags

# 3. Build and check
make check

# 4. Upload to PyPI
make test-upload  # Test first
make upload       # Then production
```

The Makefile uses twine for secure uploads and includes:
- `make check` - Validates distributions before upload
- `make test-upload` - Tests on TestPyPI first
- `make upload` - Publishes to PyPI with confirmation prompt

## Architecture

Each tool is implemented as a Typer CLI application that wraps functionality from the hamel library:

- `transcribe.py` → `hamel.yt.transcribe()`
- `chapters.py` → `hamel.yt.yt_chapters()`  
- `annotate_talk.py` → `hamel.writing.generate_annotated_talk_post()`

The tools follow a consistent pattern using Typer's app decorator approach without `if __name__ == "__main__"` blocks.