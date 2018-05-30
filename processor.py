"""
    module serves as the controller
        Examines a text string for tel commands and evaluates the tel string
            the text string can be a pure tel string (simple_tel) or mixed tel and text
            processor evaluates each of the tel strings
"""


# import tel
def tel_process(input_str):
    """
    :param input_str: string potentially containing tel to be interpreted and evaluated
    :return: string with any tel evaluated and replaced with returned value
    """
    if is_simple_tel(input_str):
        tel_evaluate(input_str)
    print(input_str)
    pass


def tel_evaluate(tel_string):
    """
    :param tel_string: a string of text containing only tel commands and functions
    :return: a single value that the tel string evaluates to
    breaks tel_string into a list of commands and iterates through the list
    """
    stack = []
    commands = tel_string.split("|")
    for command in commands:
        if command[0].upper() == "C":
            stack.append(command[1:])

    tel_string = tel_string + ' evaluated'
    return False


def is_simple_tel(tel_str):
    """
    tests for whether a tel string is pure tel (simple) or mixed
    :return: boolean true if is only a tel string, false if a mixed tel string
    """
    # true if begins with"[" and ends with"]"
    if tel_str.startswith("[") and tel_str.endswith("]"):
        simple_tel = True

    # no brackets but can still be simple tel in the following cases
    # singleton functions:  FSYSTEM, FPRINT, FTODAY, FTIME, FCLONE, FHOME, FFINISH, FTRACE
    # All other tel strings must start with C and have at least one pipe character not at the end of the string

    elif tel_str.upper() in (['FSYSTEM', 'FPRINT', 'FTODAY', 'FTIME', 'FCLONE', 'FHOME', 'FFINISH', 'FTRACE']) or \
            (tel_str.upper().startswith('C') and len(tel_str) > 3 and '|' in tel_str and not tel_str.endswith("|")):
        simple_tel = True
    else:
        simple_tel = False

    return simple_tel


def parse_mixed_string(tel_string):
    """
    if simple_tel() is false, then the tel_string passed may have embedded tel commands that need to be evaluated
    :param tel_string:
    :return: the original string with embedded tel string(s) replaced by tel_evaluate() returned value(s)
    """
    print(tel_string)
    pass
