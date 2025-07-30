from multipyline import multipyline, multipyline_inner, multipyline_format


def test_multipyline_code():
    raw_text = """PROCEDURE SimulateComplexProcess(data_stream)

    INITIALIZE process_id = 1

    LOOP for each data_packet in data_stream
        // Level 1: Main processing loop for each packet

        IF data_packet is NOT valid
            // Level 2: Handle invalid data
            LOG error "Invalid packet received"
            CONTINUE to next packet
        END IF

        AUTHENTICATE user from data_packet
        IF user is_authorized
            // Level 2: Authorized user workflow

            PRINT "User " + user.name + " authorized."
            FOR each task in user.tasks
                // Level 3: Loop through user's tasks

                IF task.type IS 'HighPriority'
                    // Level 4: Handle high-priority tasks
                    ALLOCATE exclusive_resources
                    EXECUTE task with high priority

                    IF task.result IS 'success'
                        // Level 5: Deeply nested success condition
                        NOTIFY admin_group
                    END IF

                ELSE
                    // Level 4: Handle standard tasks
                    ADD task to general_queue
                END IF
            END FOR
        ELSE
            // Level 2: Unauthorized user workflow
            LOG warning "Unauthorized access attempt"
        END IF

        INCREMENT process_id

    END LOOP

    PRINT "Simulation Complete."

END PROCEDURE"""

    inner_loop = multipyline("""
        FOR each task in user.tasks
            // Level 3: Loop through user's tasks

            IF task.type IS 'HighPriority'
                // Level 4: Handle high-priority tasks
                ALLOCATE exclusive_resources
                EXECUTE task with high priority

                IF task.result IS 'success'
                    // Level 5: Deeply nested success condition
                    NOTIFY admin_group
                END IF

            ELSE
                // Level 4: Handle standard tasks
                ADD task to general_queue
            END IF
        END FOR
    """)

    formatted_text = multipyline(f"""
        PROCEDURE SimulateComplexProcess(data_stream)

            INITIALIZE process_id = 1

            LOOP for each data_packet in data_stream
                // Level 1: Main processing loop for each packet

                IF data_packet is NOT valid
                    // Level 2: Handle invalid data
                    LOG error "Invalid packet received"
                    CONTINUE to next packet
                END IF

                AUTHENTICATE user from data_packet
                IF user is_authorized
                    // Level 2: Authorized user workflow

                    PRINT "User " + user.name + " authorized."
                    {multipyline_inner(inner_loop, " " * 4 * 5)}
                ELSE
                    // Level 2: Unauthorized user workflow
                    LOG warning "Unauthorized access attempt"
                END IF

                INCREMENT process_id

            END LOOP

            PRINT "Simulation Complete."

        END PROCEDURE
    """)

    assert formatted_text == raw_text


def test_multipyline_empty_string_and_whitespace():
    assert multipyline("") == ""
    assert multipyline("   ") == ""
    assert multipyline("\n\n\n") == ""
    assert multipyline("  \n  \n  ") == ""
    assert multipyline("\t\t") == ""
    assert multipyline("  \n\t\t\n  ") == ""
    assert multipyline("\n        Hello\n        World\n    ") == "Hello\nWorld"


def test_multipyline_inner_with_empty_prefix():
    assert multipyline_inner("", "") == ""
    assert multipyline_inner("   ", "") == ""
    assert multipyline_inner("\n\n", "") == ""
    assert multipyline_inner("\t\t", "") == ""
    assert multipyline_inner("  \n\t\t\n  ", "") == ""
    assert (
        multipyline_inner("\n        Hello\n        World\n    ", "") == "Hello\nWorld"
    )


def test_multipyline_inner_with_prefix():
    assert multipyline_inner("", "<prefix>") == ""
    assert multipyline_inner("   ", "<prefix>") == ""
    assert multipyline_inner("\n\n", "<prefix>") == ""
    assert multipyline_inner("\t\t", "<prefix>") == ""
    assert multipyline_inner("  \n\t\t\n  ", "<prefix>") == ""
    assert (
        multipyline_inner("\n        Hello\n        World\n    ", "<prefix>")
        == "<prefix>Hello\n<prefix>World"
    )
    assert (
        multipyline_inner("\n        Hello\n        World\n    ", "    ")
        == "Hello\n    World"
    )
    assert (
        multipyline_inner("\n        Hello\n        World\n    ", "> ")
        == "> Hello\n> World"
    )


def test_multipyline_no_indentation():
    s1 = "def func():\n    pass"
    expected1 = "def func():\n    pass"
    assert multipyline(s1) == expected1


def test_multipyline_inner_no_indentation():
    s2 = "Inner line 1\nInner line 2"
    prefix = "    "
    expected2 = "Inner line 1\n    Inner line 2"
    assert multipyline_inner(s2, prefix) == expected2


def test_multipyline_with_multipyline_inner():
    outer_code = f"def main():\n    {multipyline_inner("    print('Hello')", '    ')}"
    expected_outer = "def main():\n    print('Hello')"
    assert multipyline(outer_code) == expected_outer


def test_multipyline_doc_simple_function():
    # We have the implementation separate from the function header
    func_impl = """
        print('Inner part')
        print('Another line')
    """

    # We add the implementation into the header specifying how many spaces are before the formatting string `{multipyline_inner(...)}`
    # We can use the literal string `"            "`, or use string multiplication `" " * 12`
    result = multipyline(f"""
        def main():
            {multipyline_inner(func_impl, " " * 12)}
    """)

    # We expect a well formatted function string
    expected_output = "def main():\n    print('Inner part')\n    print('Another line')"
    assert result == expected_output


def test_multipyline_doc_markdown_blockquotes():
    # We have a multiline question
    question = "Can you help me with:\n\n1. This thing?\n2. Another thing?\n"

    # We want to have the answer in a blockquote
    answer = (
        "Yes, here is what you can do:\n"
        "\n"
        "1. Do this for this thing\n"
        "2. Do this for the other thing\n"
    )

    # Now we combine them into a single string
    # The question is just a basic paragraph text
    # The answer is in a blockquote
    result = multipyline(f"""
        # Q&A

        {multipyline_inner(question, 8 * " ")}

        {multipyline_inner(answer, 8 * " " + "> ")}
    """)

    # We expect a well-formated markdown
    expect = "\n".join(
        [
            "# Q&A",
            "",
            "Can you help me with:",
            "",
            "1. This thing?",
            "2. Another thing?",
            "",
            "> Yes, here is what you can do:",
            "> ",
            "> 1. Do this for this thing",
            "> 2. Do this for the other thing",
        ]
    )

    assert result == expect


def test_multipyline_doc_basic():
    text = """
        First line:
            Indented second line
        Third line
    """
    result = multipyline(text)
    expected = "First line:\n    Indented second line\nThird line"

    assert result == expected


def test_multipyline_doc_inner():
    func_impl = """
        First line:
            Indented second line
        Third line
    """

    result = multipyline(f"""
        Text below is indented:
            {multipyline_inner(func_impl, " " * 12)}
    """)
    expected = "Text below is indented:\n    First line:\n        Indented second line\n    Third line"

    assert result == expected


def test_multipyline_format_doc_simple_function():
    # We have the implementation separate from the function header
    func_impl = """
        # Inner part
        if (x > 0):
            print('Another line')
    """

    # We add the implementation into the header specifying how many spaces are before the formatting string `{multipyline_inner(...)}`
    result = multipyline_format(
        """
        def fun(x: int):
            print('Outer part')
            {}
        """,
        func_impl,
    )

    # We expect a well formatted function string
    expected_output = "def fun(x: int):\n    print('Outer part')\n    # Inner part\n    if (x > 0):\n        print('Another line')"
    assert result == expected_output
