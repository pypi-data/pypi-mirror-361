from typing import Literal

"""Block Kit (https://api.slack.com/reference/block-kit/blocks)을 사용하려 할 때 도와줄 수 있는 함수들. """


def make_header(header_text: str, text_type: Literal["plain_text", "mrkdwn"] = "mrkdwn") -> dict:
    """Creates a header block for use in Slack's Block Kit.

    Args:
        header_text (str): The text to display in the header. Will be truncated to 145 characters with ellipsis.
        text_type (Literal["plain_text", "mrkdwn"], optional): The type of text formatting. Defaults to "mrkdwn".

    Returns:
        dict: A dictionary representing the header block ready for use in Slack API.

    Examples:
        >>> make_header("Welcome to the channel!", "plain_text")
        {'type': 'header', 'text': {'type': 'plain_text', 'text': 'Welcome to the channel!', 'emoji': True}}
    
    """
    header = {}
    header_text = header_text[:145] + (header_text[145:] and "...")
    header["type"] = "header"
    header["text"] = {"type": text_type, "text": header_text, "emoji": True}
    return header


def make_section_field_with_key_value(key, value):
    """Creates a markdown section with a key and value formatted as a field in Slack's Block Kit.

    Args:
        key: The key or title of the field.
        value: The value or description of the field, truncated at 2000 characters with ellipsis.

    Returns:
        dict: A dictionary representing the markdown section block.
    
    Examples:
        >>> make_section_field_with_key_value("Status", "Active")
        {'type': 'mrkdwn', 'text': '*Status*\nActive'}
    
    """
    result = {}
    value = value[:2000] + (value[2000:] and "...")
    result["type"] = "mrkdwn"
    result["text"] = f"*{key}*\n{value}"
    return result


def make_section_with_text(text):
    """Creates a section block with given text in markdown format for Slack's Block Kit.

    Args:
        text (str): The text to display in the section.

    Returns:
        dict: A dictionary representing the section block with markdown text.
    
    Examples:
        >>> make_section_with_text("Important Update")
        {'type': 'section', 'text': {'type': 'mrkdwn', 'text': '*Important Update*'}}
    
    """
    result = {"type": "section", "text": {"type": "mrkdwn", "text": f"*{text}*"}}
    return result


def make_context_with_text(text):
    """Creates a context block with given text for Slack's Block Kit.

    Args:
        text (str): The text to display in the context block.

    Returns:
        dict: A dictionary representing the context block with plain text.
    
    Examples:
        >>> make_context_with_text("This is additional info.")
        {'type': 'context', 'elements': [{'type': 'plain_text', 'text': 'This is additional info.'}]}
    
    """
    result = {"type": "context", "elements": [{"type": "plain_text", "text": f"{text}"}]}
    return result


def make_divider():
    """Creates a divider block for Slack's Block Kit.

    Returns:
        dict: A dictionary representing the divider block.

    Examples:
        >>> make_divider()
        {'type': 'divider'}
    
    """
    return {"type": "divider"}
