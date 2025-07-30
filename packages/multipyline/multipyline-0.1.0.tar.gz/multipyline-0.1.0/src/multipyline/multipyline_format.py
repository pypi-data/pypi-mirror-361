import textwrap

from multipyline.multipyline import multipyline
from multipyline.multipyline_inner import multipyline_inner


def multipyline_format(s: str, *args: str) -> str:
    """
    Format a multiline string with placeholders which are also multiline strings.
    Handles proper indentation for each placeholder.

    Args:
        s: The input string containing placeholders `{}`.
        *args: The arguments to fill in the placeholders.

    Returns:
        A formatted string with the placeholders replaced by the provided arguments.
    Raises:
        ValueError: If any single line contains multiple `{}` placeholders.
    Examples:
        Basic usage with a single placeholder:
        >>> func_impl = '''
        ...     # Inner part
        ...     if (x > 0):
        ...         print('Another line')
        ... '''
        >>> result = multipyline_format(
        ...     '''
        ...     def fun(x: int):
        ...         print('Outer part')
        ...         {}
        ...     ''',
        ...     func_impl,
        ... )
        >>> print(result)
        def fun(x: int):
            print('Outer part')
            # Inner part
            if (x > 0):
                print('Another line')
    """

    TEMPLATE = "{}"

    formatted_args = [""] * len(args)
    arg_counter = 0

    for line in s.splitlines():
        if TEMPLATE not in line:
            continue

        if line.count(TEMPLATE) > 1:
            raise ValueError(
                f"Multiple '{TEMPLATE}' placeholders found in a single line of the string."
            )

        argument = args[arg_counter]
        formatted_argument = argument

        if len(argument.splitlines()) > 1 and textwrap.dedent(line).startswith(
            TEMPLATE
        ):
            prefix = line[: line.find(TEMPLATE)]
            formatted_argument = multipyline_inner(argument, prefix)

        formatted_args[arg_counter] = formatted_argument
        arg_counter += 1

    formatted = s.format(*formatted_args)
    return multipyline(formatted)
