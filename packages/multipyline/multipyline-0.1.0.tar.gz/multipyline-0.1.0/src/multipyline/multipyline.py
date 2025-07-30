import textwrap


def multipyline(s: str) -> str:
    """
    Format a multiline string by removing common leading whitespace and trailing/leading newlines.

    Args:
        s: The input string to format. Can contain multiple lines with varying indentation.

    Returns:
        A cleaned string with common leading whitespace removed and stripped of leading/trailing whitespace.
        Returns empty string for whitespace-only inputs.

    Examples:
        Basic usage - multiline strings using `multipyline`:
        >>> text = '''
        ...     First line:
        ...         Indented second line
        ...     Third line
        ... '''
        >>> result = multipyline(text)
        >>> print(result)
        First line:
            Indented second line
        Third line

        Working with multiline f-strings using `multipyline_inner`:
        >>> result = multipyline(f'''
        ...     Text below is indented:
        ...         {multipyline_inner(text, " " * 12)}
        ... ''')
        >>> print(result)
        Text below is indented:
            First line:
                Indented second line
            Third line

        Handling empty or whitespace-only strings:
        >>> multipyline("   ") == ""
        True
        >>> multipyline("\n\n\n") == ""
        True
    """
    s = textwrap.dedent(s)
    return s.strip()
