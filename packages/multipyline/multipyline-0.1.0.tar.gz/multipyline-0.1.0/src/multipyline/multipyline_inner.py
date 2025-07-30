import textwrap

from multipyline.multipyline import multipyline


def multipyline_inner(s: str, prefix: str) -> str:
    """
    Use inside a `multipyline` f-string to format the inner multiline content.

    Here the inner content template is offset 8 spaces from the left
    >>> text = multipyline(f'''
    ...     Text below is indented:
    ...         {multipyline_inner(inner_text, '        ')}''')
    ... #       ^ until here is the prefix;     ^^^^^^^^ equals 8 spaces

    See more examples below.

    Args:
        s: The input string to format.
        prefix: The entire prefix to this template

    Returns:
        A formatted string with the specified prefix applied to each line.

    Examples:
        Intended usage:
        >>> first_text = '''
        ...     First line:
        ...         Indented second line
        ...     Third line
        ... '''
        >>> second_text = 'Oneline text'
        >>> result = multipyline(f'''
        ...     Text below is indented:
        ...         {multipyline_inner(first_text, " " * 8)}
        ...
        ...     This text doesn't need to use inner because there isn't whitespace before it: {second_text}
        ... ''')
        >>> print(result)
        Text below is indented:
            First line:
                Indented second line
            Third line
        This text doesn't need to use inner because there isn't whitespace before it: Oneline text

        Handling empty or whitespace-only strings:
        >>> multipyline("   ") == ""
        True
        >>> multipyline("\n\n\n") == ""
        True
    """
    s = multipyline(s)
    s = textwrap.indent(s, prefix, lambda _: True)
    return s.strip()
