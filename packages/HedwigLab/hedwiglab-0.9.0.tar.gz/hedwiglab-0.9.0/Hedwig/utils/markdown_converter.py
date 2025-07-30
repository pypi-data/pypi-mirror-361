#
# Copyright (c) 2025 Seoul National University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Markdown to Slack format converter"""

import re
import json
from typing import List, Dict, Any, Union, Optional, Tuple


def markdown_to_slack_mrkdwn(content: str) -> str:
    """Convert Markdown to Slack mrkdwn format

    Args:
        content: Markdown formatted text

    Returns:
        Slack mrkdwn formatted text
    """
    # Split the input string into parts based on code blocks and inline code
    parts = re.split(r"(?s)(```.+?```|`[^`\n]+?`)", content)

    # Apply the bold, italic, and strikethrough formatting to text not within code
    result = ""
    for part in parts:
        if part.startswith("```") or part.startswith("`"):
            result += part
        else:
            for o, n in [
                (r"\*\*\*(?!\s)([^\*\n]+?)(?<!\s)\*\*\*", r"_*\1*_"),  # ***bold italic*** to *_bold italic_*
                (r"(?<![\*_])\*(?!\s)([^\*\n]+?)(?<!\s)\*(?![\*_])", r"_\1_"),  # *italic* to _italic_
                (r"\*\*(?!\s)([^\*\n]+?)(?<!\s)\*\*", r"*\1*"),  # **bold** to *bold*
                (r"__(?!\s)([^_\n]+?)(?<!\s)__", r"*\1*"),  # __bold__ to *bold*
                (r"~~(?!\s)([^~\n]+?)(?<!\s)~~", r"~\1~"),  # ~~strike~~ to ~strike~
                (r"(\n|^)# ([^\n]+)", r"\1\n :star: *\2*"),  # heading 1
                (r"(\n|^)## ([^\n]+)", r"\1\n :arrow_forward: *\2*"),  # heading 2
                (r"(\n|^)### ([^\n]+)", r"\1\n :point_right: *\2*"),  # heading 3
                (r"(?m)^(\s*)\d+\.\s+(.*)", r"\1* \2"),  # numbered list to bullet list
            ]:
                part = re.sub(o, n, part)
            result += part
    return result


def markdown_to_slack_canvas(content: str) -> str:
    """Convert Markdown to Slack Canvas format

    Args:
        content: Markdown formatted text

    Returns:
        Slack Canvas formatted text
    """
    # Split the input string into parts based on code blocks and inline code
    parts = re.split(r"(?s)(```.+?```|`[^`\n]+?`)", content)

    # Apply minimal formatting for canvas
    result = ""
    for part in parts:
        if part.startswith("```") or part.startswith("`"):
            result += part
        else:
            # Convert numbered lists to bullet lists
            part = re.sub(r"(?m)^(\s*)\d+\.\s+(.*)", r"\1* \2", part)
            result += part
    return result


def markdown_to_slack_rich_text(markdown_text: str, return_json: bool = False) -> Union[Dict[str, Any], str]:
    """
    Convert Markdown text to Slack rich_text block format.

    Supports:
    - Headings (# through ######)
    - Bold text (**text** or __text__)
    - Italic text (*text* or _text_)
    - Bullet lists (lines starting with - or *)
    - Inline code (`code`)

    Note: Slack's rich_text format has limited support for nested lists.
    This converter will flatten nested lists and add indent markers.

    Args:
        markdown_text: The Markdown formatted text to convert
        return_json: If True, returns JSON string; if False, returns dict

    Returns:
        A dictionary or JSON string representing a Slack rich_text block
    """
    lines = markdown_text.strip().split('\n')
    sections = []
    current_paragraph = []
    current_list_items = []
    in_list = False

    def parse_inline_formatting(text: str) -> List[Dict[str, Any]]:
        """Parse inline formatting (bold, italic, and code) in a text string."""
        elements = []

        # Combined pattern to match:
        # - Bold: **text** or __text__
        # - Italic: *text* or _text_ (but not ** or __)
        # - Code: `text`
        # Using negative lookahead/lookbehind to distinguish single from double markers
        pattern = r'(\*\*|__|(?<!\*)\*(?!\*)|(?<!_)_(?!_)|`)(.+?)\1'
        last_end = 0

        for match in re.finditer(pattern, text):
            # Add any plain text before the match
            if match.start() > last_end:
                plain_text = text[last_end:match.start()]
                if plain_text:
                    elements.append({
                        "type": "text",
                        "text": plain_text
                    })

            # Add the formatted text
            delimiter = match.group(1)
            content = match.group(2)

            if delimiter == '`':
                # Code formatting
                elements.append({
                    "type": "text",
                    "text": content,
                    "style": {
                        "code": True
                    }
                })
            elif delimiter in ['**', '__']:
                # Bold formatting
                elements.append({
                    "type": "text",
                    "text": content,
                    "style": {
                        "bold": True
                    }
                })
            elif delimiter in ['*', '_']:
                # Italic formatting
                elements.append({
                    "type": "text",
                    "text": content,
                    "style": {
                        "italic": True
                    }
                })

            last_end = match.end()

        # Add any remaining plain text
        if last_end < len(text):
            remaining_text = text[last_end:]
            if remaining_text:
                elements.append({
                    "type": "text",
                    "text": remaining_text
                })

        # If no formatting was found, return the entire text as plain
        if not elements:
            elements.append({
                "type": "text",
                "text": text
            })

        return elements

    def create_paragraph_section(lines: List[str]) -> Dict[str, Any]:
        """Create a paragraph section from lines of text."""
        combined_text = ' '.join(lines)
        elements = parse_inline_formatting(combined_text)

        return {
            "type": "rich_text_section",
            "elements": elements
        }

    def is_list_item(line: str) -> Tuple[bool, int, str]:
        """
        Check if a line is a list item and return its properties.
        Returns (is_list_item, indent_level, content)
        """
        # Match list item with optional indentation
        match = re.match(r'^(\s*)[-*]\s+(.*)$', line)
        if match:
            indent = match.group(1)
            content = match.group(2).strip()
            # Calculate indent level (4 spaces or 1 tab = 1 level)
            indent_level = len(indent.replace('\t', '    ')) // 4
            return True, indent_level, content
        return False, 0, line

    def create_list_section(items: List[Tuple[int, str]]) -> List[Dict[str, Any]]:
        """
        Create list sections from items with indentation levels.
        Returns a list of sections (lists at different indent levels).
        """
        if not items:
            return []

        result_sections = []
        current_level_items = []
        current_level = 0

        # Group items by consecutive same-level items
        for indent_level, content in items:
            if not current_level_items or indent_level == current_level:
                current_level = indent_level
                current_level_items.append(content)
            else:
                # Flush current level items
                if current_level_items:
                    list_elements = []
                    for item_text in current_level_items:
                        item_elements = parse_inline_formatting(item_text)
                        list_elements.append({
                            "type": "rich_text_section",
                            "elements": item_elements
                        })

                    list_block = {
                        "type": "rich_text_list",
                        "style": "bullet",
                        "elements": list_elements
                    }

                    if current_level > 0:
                        list_block["indent"] = current_level

                    result_sections.append(list_block)

                # Start new level
                current_level = indent_level
                current_level_items = [content]

        # Don't forget the last group
        if current_level_items:
            list_elements = []
            for item_text in current_level_items:
                item_elements = parse_inline_formatting(item_text)
                list_elements.append({
                    "type": "rich_text_section",
                    "elements": item_elements
                })

            list_block = {
                "type": "rich_text_list",
                "style": "bullet",
                "elements": list_elements
            }

            if current_level > 0:
                list_block["indent"] = current_level

            result_sections.append(list_block)

        return result_sections

    def create_heading_section(line: str) -> Dict[str, Any]:
        """Create a heading section from a markdown heading."""
        # Match heading pattern and extract level and text
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if not match:
            return None

        heading_text = match.group(2).strip()

        # Parse inline formatting in the heading text
        elements = parse_inline_formatting(heading_text)

        # Add bold style to all elements for heading emphasis
        for element in elements:
            if element.get("type") == "text":
                if "style" in element:
                    element["style"]["bold"] = True
                else:
                    element["style"] = {"bold": True}

        return {
            "type": "rich_text_section",
            "elements": elements
        }

    # Process each line
    for i, line in enumerate(lines):
        # Check if this line is a heading
        heading_match = re.match(r'^#{1,6}\s+', line)

        # Check if this line is a list item
        is_list, indent_level, content = is_list_item(line)

        if heading_match:
            # Save any pending paragraph
            if current_paragraph:
                sections.append(create_paragraph_section(current_paragraph))
                current_paragraph = []

            # Save any pending list
            if current_list_items:
                sections.extend(create_list_section(current_list_items))
                current_list_items = []
                in_list = False

            # Create and add the heading section
            heading_section = create_heading_section(line)
            if heading_section:
                sections.append(heading_section)

        elif is_list:
            # Save any pending paragraph
            if current_paragraph and not in_list:
                sections.append(create_paragraph_section(current_paragraph))
                current_paragraph = []

            in_list = True
            current_list_items.append((indent_level, content))

        else:
            # Save any pending list
            if current_list_items:
                sections.extend(create_list_section(current_list_items))
                current_list_items = []
                in_list = False

            # Add to current paragraph if line is not empty
            if line.strip():
                current_paragraph.append(line)
            else:
                # Empty line - save current paragraph if any
                if current_paragraph:
                    sections.append(create_paragraph_section(current_paragraph))
                    current_paragraph = []

    # Handle any remaining content
    if current_list_items:
        sections.extend(create_list_section(current_list_items))
    elif current_paragraph:
        sections.append(create_paragraph_section(current_paragraph))

    # Create the final rich_text block
    result = {
        "type": "rich_text",
        "elements": sections
    }

    # Return as JSON string if requested (ensures proper boolean serialization)
    if return_json:
        return json.dumps(result)
    else:
        return result


def limit_text_length(text: str, limit: int) -> str:
    """Limit text length with ellipsis

    Args:
        text: Text to limit
        limit: Maximum length

    Returns:
        Limited text with ellipsis if truncated
    """
    if len(text) > limit:
        return text[:limit-3] + '…'
    return text
