#!/usr/bin/env python3.13
import os
import re
import sys
from pathlib import PosixPath, WindowsPath
from typing import Optional

# Detect proper Path subclass to inherit from based on the user's platform,
# since the top-level Path subclass is not designed to be subclassed directly
if sys.platform == "win32":
    BasePath = WindowsPath
else:
    BasePath = PosixPath


class ExpandedPath(BasePath):
    """
    Path subclass that automatically expands the user's home directory (i.e. ~)
    """

    def __new__(cls, path: str, **kwargs: object) -> "ExpandedPath":
        return super().__new__(cls, os.path.expanduser(path), **kwargs)


def extract_code_blocks(md_text: str) -> list[str]:
    """
    Extract contents of all fenced code blocks from the given Markdown text into
    a list, where each list item represents the contents of that code block
    (minus any optional language specifier)
    """
    code_blocks = re.findall(
        r"```(?:[\w\-]*)\n(|.*?\n)```",
        md_text,
        flags=re.DOTALL,
    )
    # If number of code blocks is not even
    if len(code_blocks) % 2 != 0:
        raise RuntimeError(
            "Replacement file must have an even number of fenced code blocks."
        )
    return code_blocks


def get_indent_unit(text: str) -> Optional[str]:
    """
    Find the string representing the base unit of indentation in a given string
    of text; this can be either two spaces, four spaces, or a tab character
    """
    for indent_level in ((" " * 2), (" " * 4), "\t"):
        # The positive lookahead is because since 2-space indent is really a
        # subset of 4-space indent, we need to be able to distinguish between
        # the two, so we check to see if there
        if re.search(rf"^{indent_level}(?=\S)", text, flags=re.MULTILINE):
            return indent_level
    return None


def evaluate_wildcard_variables(text: str) -> str:
    """
    Evaluate textual wildcard variables in the given target text to achieve
    certain behaviors (like wildcard-matching through the end of a line, or a
    wildcard-match for only a single word)
    """
    wildcard_evaluations = {
        # Match all non-newline characters until the end of the line is reached
        "MATCH_UNTIL_END_OF_LINE": r"[^\n]*",
        # Match all non-newline characters between two delimiters (like quotes)
        "MATCH_ALL_BETWEEN": r"[^\n]*?",
    }
    for wildcard_var_name, replacement in wildcard_evaluations.items():
        text = re.sub(
            re.escape(wildcard_var_name),
            replacement,
            text,
        )
    return text


def evaluate_environment_variables(text: str) -> str:
    """
    Evaluate environment variables in the given target text by replacing
    environment variables with their values; every environment variable is
    represented by MATCH_ENV_{var_name}
    """
    return re.sub(r"MATCH_ENV_(\w+)", lambda m: os.environ.get(m.group(1), ""), text)


def evaluate_variables(text: str) -> str:
    """
    Evaluate textual variables in the given target text to achieve certain
    behaviors (like wildcard-matching and environment variable evaluation)
    """
    text = evaluate_wildcard_variables(text)
    text = evaluate_environment_variables(text)
    return text


def replace_text(input_text: str, target_text: str, replacement_text: str) -> str:
    """
    Replace the given text in the input text with the replacement text,
    preserving indentation; the return value is the full output text after
    replacements have been made
    """
    replace_this_patt = "\n".join(
        (
            # Evaluate wildcard and environment variables on the line
            evaluate_variables(rf"([ \t]*){re.escape(line.strip())}") if line else ""
        )
        for line in target_text.splitlines()
    )
    # If replacement text is empty, then we need to ensure that the lines are
    # actually removed (as opposed to being replaced with an empty string)
    if replacement_text == "":
        replace_this_patt += "\n"
    # Retrieve the base indentation level in the target text to ensure that the
    # replacement text is indented the same amount
    base_indent_matches = re.search(replace_this_patt, input_text)
    if not base_indent_matches:
        return input_text  # No match found, return original text
    base_indent_level = base_indent_matches.group(1)
    # Ensure that the replacement text's preferred indentation unit matches that
    # of the input text
    input_indent_unit = get_indent_unit(input_text)
    replacement_indent_unit = get_indent_unit(replacement_text)
    if replacement_indent_unit and input_indent_unit:
        replacement_text = re.sub(
            replacement_indent_unit,
            input_indent_unit,
            replacement_text,
        )
    # Ensure that the replacement text is indented to the same amount as the
    # target text it is replacing
    replacement_text = "\n".join(
        # The ternary syntax is to prevent trailing whitespace from being added
        # to blank lines
        base_indent_level + line if line else ""
        for line in replacement_text.splitlines()
    )
    input_text = re.sub(replace_this_patt, replacement_text, input_text)
    input_text = evaluate_environment_variables(input_text)
    return input_text
