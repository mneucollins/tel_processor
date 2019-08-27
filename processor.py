
from tel import Tel
import app

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
    # If is simple_tel do tel_evaluate else do parse_mixed_string

    elif tel_str.upper() in (['FSYSTEM', 'FPRINT', 'FTODAY', 'FTIME', 'FCLONE', 'FHOME', 'FFINISH', 'FTRACE']) or \
            (tel_str.upper().startswith('C') and len(tel_str) > 3 and '|' in tel_str and not tel_str.endswith("|")):
        simple_tel = True
    else:
        simple_tel = False
        return simple_tel


def tel_evaluate(tel_string):
    """
    :param tel_string: a string of text containing only tel commands and functions
    :return: a single value that the tel string evaluates to
    breaks tel_string into a list of commands and iterates through the list
    """
    stack = []
    commands = tel_string.split("|")
    for command in commands:
        # Begin C Identifier
        if command[0].upper() == "C":
            stack.append(command[1:])
            # End C identifier
            # begin Tel Mathmatical operators
        elif command.upper() == "A*":
            Tel(stack).a_multiply()
        elif command.upper() == "A+":
            Tel(stack).a_add()
        elif command.upper() == "A-":
            Tel(stack).a_subtract()
        elif command.upper() == "A/":
            Tel(stack).a_divide()
        # end Tel Mathmatical operators
        elif command.upper() == "P=":
            Tel(stack).p_equal_to()
        elif command.upper() == "P#":
            Tel(stack).p_not_equal_to()
        elif command.upper() == "P<":
            Tel(stack).p_less_than()
        elif command.upper() == "P>":
            Tel(stack).p_greater_than()
        elif command.upper() == "P+":
            Tel(stack).p_logical_or()
        elif command.upper() == "P*":
            Tel(stack).p_logical_and()
        elif command.upper() == "P!":
            Tel(stack).p_logical_not()
        elif command.upper() == "FREPLACE":
            Tel(stack).f_replace()
        elif command.upper() == "FTRACE":
            Tel(stack).f_trace()
            # begin functions
        elif command.upper() == "FCAT":
            Tel(stack).f_cat()
        elif command.upper() == "FLENGTH":
            Tel(stack).f_length()
        elif command.upper() == "FMID":
            Tel(stack).f_mid()
        elif command.upper() == "FFIND":
            Tel(stack).f_find()
        elif command.upper() == "FTODAY":
            Tel(stack).f_today()
        elif command.upper() == "FTIME":
            Tel(stack).f_time()
        elif command.upper() == "FTIMESTAMP":
            Tel(stack).f_timestamp()
        elif command.upper() == "FDATEADD":
            Tel(stack).f_date_add()
        elif command.upper() == "FDATEDIFF":
            Tel(stack).f_date_diff()
        elif command.upper() == "FDOW":
            Tel(stack).f_dow()
        elif command.upper() == "FDATEFORMAT":
            Tel(stack).f_dateformat()
        elif command.upper() == "FLENGTH":
            Tel(stack).f_length()
        elif command.upper() == "PATIENTCOLUMNEXISTS":
            Tel(stack).patient_column_exists()
        elif command.upper() == "PATIENTEXISTS":
            Tel(stack).patient_exists()
        elif command.upper() == "FPATSET":
            Tel(stack).f_patset()
        elif command.upper() == "FPATGET":
            Tel(stack).f_patget()
        elif command.upper() == "FPATXSET":
            Tel(stack).f_patxset()
        elif command.upper() == "FPATXSETR":
            Tel(stack).f_patxsetr()
        elif command.upper() == "FPATXGET":
            Tel(stack).f_patxget()
        elif command.upper() == "FSETGLOBAL":
            Tel(stack).f_set_global()
        elif command.upper() == "FGETGLOBAL":
            Tel(stack).f_get_global()
        elif command.upper() == "FRETANS":
            Tel(stack).f_fretans()
        elif command.upper() == "FCLEARANS":
            Tel(stack).f_clear_ans()
        elif command.upper() == "FSETANS":
            Tel(stack).f_set_ans()
        elif command.upper() == "FLINK":
            Tel(stack).f_link()
        elif command.upper() == "FIMAGE":
            Tel(stack).f_image()
        elif command.upper() == "FWINDOW":
            Tel(stack).f_window()
        elif command.upper() == "FCHECKEMAIL":
            Tel(stack).f_check_email()
        elif command.upper() == "FMAIL":
            Tel(stack).f_mail()
        elif command.upper() == 'FPRINT':
            Tel(stack).f_print()
        elif command.upper() == 'FPARAM':
            Tel(stack).f_param()
        elif command.upper() == 'FSQL':
            Tel(stack).f_sql()
        elif command.upper() == 'FTIMESTART':
            Tel(stack).f_time_start()
        elif command.upper() == 'FTIMESTOP':
            Tel(stack).f_time_s()
        elif command.upper() == 'FIIF':
            Tel(stack).f_fiif()
        elif command.upper() == 'FGOTO':
            Tel(stack).f_goto()
        elif command.upper() == 'FGOIF':
            Tel(stack).f_goif()
        elif command.upper() == 'FDO':
            Tel(stack).f_do()
        elif command.upper() == 'DELVALUE':
            Tel(stack).delValue()
            bool = Tel([]).bool_eval().pop()
            if bool:
                break
            break

        tel_string = tel_string + ' evaluated'
    return stack  # removed False


def parse_mixed_string(tel_string):
    """
    if simple_tel() is false, then the tel_string passed may have embedded
    tel commands that need to be evaluated
    :param tel_string:
    :return: the original string with embedded tel string(s) replaced by
    tel_evaluate() returned value(s)
    """
    print(tel_string)
    pass
