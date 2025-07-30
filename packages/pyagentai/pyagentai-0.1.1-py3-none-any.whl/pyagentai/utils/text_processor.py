"""Text processing utilities for pyagentai."""


def sanitize_text(text: str) -> str:
    """Sanitize text for use in file names.

    Args:
        text: The text to sanitize.

    Returns:
        The sanitized text.
    """
    # Replace invalid characters with underscores
    return "".join(
        c if c.isalnum() or c in "._- " else "_" for c in text
    ).strip()
