import os
import streamlit as st
from handy_uti import page_metadata

sess = st.session_state


def get_api_key(brand: str) -> str | None:
    """Get API key from session state or environment variable otherwise return None"""
    key_name = f"{brand.upper()}_API_KEY"

    if key_name in sess:
        return sess[key_name]

    if value := os.environ.get(key_name):
        sess[key_name] = value
        return value
    return None


def url_path(title: str) -> str:
    """convert utility title to url path"""
    return title.lower().replace(" ", "_")


def get_page_info(page_key: str) -> tuple[str, str, str]:
    """Get page metadata (title, colored_icon, description) for a given page key
    
    Args:
        page_key: The key from page_metadata (e.g., 'yt_transcriber')
    
    Returns:
        Tuple of (title, colored_icon, description)
        - title: Page title from metadata
        - colored_icon: Formatted as ":color[material/icon_name]:"
        - description: Page description from metadata
    
    Raises:
        KeyError: If page_key is not found in page_metadata
    """
    if page_key not in page_metadata:
        raise KeyError(f"Page key '{page_key}' not found in page_metadata")
    
    metadata = page_metadata[page_key]
    title = metadata["title"]
    color = metadata["color"]
    icon = metadata["icon"]
    description = metadata["description"]
    
    colored_icon = f":{color}[material/{icon}]:"
    
    return title, colored_icon, description
