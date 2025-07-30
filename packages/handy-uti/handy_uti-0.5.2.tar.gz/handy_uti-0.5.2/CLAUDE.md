# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based collection of daily utility tools, published as `handy-uti` on PyPI. The application uses a modular page system where each utility is implemented as a separate module in the `handy_uti/` directory.

## Commands

### Development
- **Install dependencies**: `uv sync`
- **Run locally**: `streamlit run handy_uti/main.py`
- **Run tests**: `pytest`
- **Lint**: `ruff check .` (extend-ignore configured in pyproject.toml)
- **Format**: `ruff format .`

### Testing with Playwright
Tests use Playwright to test the Streamlit UI. The test server runs on port 9507 with headless mode.
- **Run specific test**: `pytest tests/test_<module_name>.py`
- **Test assets**: Located in `tests/assets/` (sample files for testing utilities)

### Build & Distribution
- **Build package**: `uv build`
- **Install locally**: `uv tool install .`
- **Run installed version**: `handy-uti [optional/path/to/.env]`

## Architecture

### Core Components

1. **Entry Points**:
   - `launcher.py`: CLI entry point using Click, handles .env loading and Streamlit launch
   - `main.py`: Main Streamlit app that dynamically loads all utility pages

2. **Page System**:
   - Each utility is a Python module in `handy_uti/` (e.g., `yt_transcriber.py`, `token_counter.py`)
   - Pages are registered in `__init__.py` via `page_metadata` dictionary
   - Each page module must expose: `app()` function, `title` string, `icon` string
   - Pages are automatically discovered and loaded by `main.py`

3. **Shared UI Components** (`ui.py`):
   - `app_header()`: Standard page header with icon and description
   - `main_container()`: Wrapper for main content area
   - `api_key_input()`: Standardized API key input with auto-fill from env vars
   - `divider()`: Visual separator component

4. **Utilities** (`utils.py`):
   - `get_api_key()`: Retrieves API keys from session state or environment
   - `url_path()`: Converts page titles to URL-friendly paths

### API Key Management
The app supports auto-filling API keys from environment variables:
- `GOOGLE_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`, `HUGGINGFACE_API_KEY`
- Keys are cached in Streamlit session state once loaded

### Adding New Utilities
1. Create new Python file in `handy_uti/` (e.g., `new_tool.py`)
2. Implement required exports: `app()`, `title`, `icon`
3. Add entry to `page_metadata` in `__init__.py`
4. Follow UI patterns: use `app_header()`, `main_container()`, consistent styling

### Directory Structure
- `handy_uti/`: Main package with all utilities
- `handy_uti/deDRM/`: DRM removal functionality (Adobe Digital Edition)
- `handy_uti/yt_transcriber/`: YouTube transcription with utils module
- `handy_uti/static/`: Assets (logo, banner, fonts)
- `tests/`: Playwright-based UI tests with sample assets
- `screenshots/`: WebP screenshots for README documentation

## Key Dependencies
- **Streamlit**: UI framework
- **AI Services**: google-genai, mistralai, groq, transformers
- **Media Processing**: pytubefix, yt-dlp, pypandoc_binary, ebooklib
- **Crypto**: pycryptodome (for DRM removal)
- **Testing**: pytest, playwright