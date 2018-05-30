class Tel:
    """
    A tel object consists of a stack list of values and an operation on the stack
    tel methods are called by operator name and passed the stack list,
        e.g. P_EQUAL_TO (stack)
    The function:
     1. operates on the stack,
     2. pushes the result of the operation back on the stack, and
     3. returns the stack

    they then appends the results of perform an operation on the stack and return a single value
    """

    def __init__(self, stack):
        self.stack = stack

    @staticmethod
    def bool_eval(val_to_test):
        """
        :param val_to_test:
        :return: boolean True or False
        Interprets text("TRUE", "FALSE"), text("0", "1") and numeric (0,1) val_to_test and returns boolean (True, False)
        """
        if val_to_test is True or str(val_to_test).upper() == "TRUE" or val_to_test == 1 or val_to_test == '1':
            val_to_return = True
        elif val_to_test is False or str(val_to_test).upper() == "FALSE" or val_to_test == 0 or val_to_test == '0':
            val_to_return = False
        else:
            val_to_return = "err:bool_eval:cannot convert " + val_to_test + " to boolean"

        return val_to_return

    @staticmethod
    def is_number(x):
        try:
            float(x)
            return True
        except ValueError:
            return False

    # Logical Operators

    def p_equal_to(self):
        """
        Pops the last two items off the stack, compares for equality, pushes result of comparison onto stack
        :return: stack (list) with last value boolean or err message
        :example: [C1|C2|P=]
        """
        if len(self.stack) < 2:
            self.stack.append("err:p_equal_to:too few parameters")
        else:
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack.append(a == b)
        return self.stack

    def p_not_equal_to(self):
        """
        Pops the last two items off the stack, compares for inequality, pushes result of comparison onto stack
        :return: stack (list) with last value boolean or err message
        :example: [C1|C2|P#]
        """
        if len(self.stack) < 2:
            self.stack.append("err:p_not_equal_to:too few parameters")
        else:
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack.append(a != b)
        return self.stack

    def p_less_than(self):
        """
        Pops the last two items off the stack pop1 and pop2,
        p_less_than is true if pop1 variable is greater than pop2
        pushes result of comparison onto stack
        :return: stack (list) with last value boolean or err message
        :example: [C1|C2|P<]
        """
        if len(self.stack) < 2:
            self.stack.append("err:p_less_than:too few parameters")
        else:
            pop1 = self.stack.pop()
            pop2 = self.stack.pop()
            self.stack.append(pop1 > pop2)
        return self.stack

    def p_greater_than(self):
        """
        Pops the last two items off the stack pop1 and pop2,
        p_greater_than is true if  pop1 variable is less than pop2
        pushes result of comparison onto stack
        :return: stack (list) with last value boolean or err message
        :example: [C1|C2|P>]
        """
        if len(self.stack) < 2:
            self.stack.append("err:p_greater_than:too few parameters")
        else:
            pop1 = self.stack.pop()
            pop2 = self.stack.pop()
            self.stack.append(pop1 < pop2)
        return self.stack

    def p_logical_and(self):
        """
        Pops the last two items off the stack, and compares the boolean evaluation of each.
        Pushes result onto the stack:
            error if less stack length is less than 2, true if both values are true, otherwise false
        :return:  stack (list) with last value boolean or err message
        :example: [C1|C2|P+]
        """
        if len(self.stack) < 2:
            self.stack.append("err:p_logical_and:too few parameters")
        else:
            a = self.stack.pop()
            b = self.stack.pop()
            if self.bool_eval(a) & self.bool_eval(b):
                self.stack.append(True)
            else:
                self.stack.append(False)
        return self.stack

    def p_logical_or(self):
        """
        Pops the last two items off the stack, and compares the boolean evaluation of each.
        Pushes boolean result onto the stack:
            error if less stack length is less than 2, true at least one of the values are true, otherwise false
        :return:  stack (list) with last value boolean or err message
        :example: [C1|C2|P*]
        """
        if len(self.stack) < 2:
            self.stack.append("err:p_logical_or:too few parameters")
        else:
            a = self.stack.pop()
            b = self.stack.pop()
            if self.bool_eval(a) or self.bool_eval(b):
                self.stack.append(True)
            else:
                self.stack.append(False)
        return self.stack

    # Mathematical Operators
    def a_multiply(self):
        """
        Pops the last two items off the stack and multiplies them
        Pushes mathematical result onto the stack:
            errors:
                stack length is less than 2,
                list element cannot be converted to a number
        :return:  stack (list) with result of mathematical operation
        :example: [C1|C2|A*]
        """
        if len(self.stack) < 2:
            self.stack.append("err:a_multiply:too few parameters")
            return self.stack
        b = self.stack.pop()
        a = self.stack.pop()
        if self.is_number(a) and self.is_number(b):
            self.stack.append(float(a) * float(b))
        else:
            self.stack.append("err:a_multiply:non-numeric parameter")
        return self.stack

    def a_add(self):
        """
        Pops the last two items off the stack and adds them.
        Pushes mathematical result onto the stack:
            errors:
                stack length is less than 2,
                list element cannot be converted to a number
        :return:  stack (list) with result of mathematical operation
        :example: [C1|C2|A+]
        """
        if len(self.stack) < 2:
            self.stack.append("err:a_add:too few parameters")
            return self.stack
        b = self.stack.pop()
        a = self.stack.pop()
        if self.is_number(a) and self.is_number(b):
            self.stack.append(float(a) + float(b))
        else:
            self.stack.append("err:a_add:non-numeric parameter")
        return self.stack

    def a_subtract(self):
        """
        Pops the last two items off the stack and subtracts the first list element from the second list element.
        (in reverse order of how they are popped off the stack)
        Pushes mathematical result onto the stack:
            errors:
                stack length is less than 2,
                list element cannot be converted to a number
        :return:  stack (list) with result of mathematical operation
        :example: [C2|C1|A-] = 1
        """
        if len(self.stack) < 2:
            self.stack.append("err:a_subtract:too few parameters")
            return self.stack
        b = self.stack.pop()
        a = self.stack.pop()
        if self.is_number(a) and self.is_number(b):
            self.stack.append(float(a) - float(b))
        else:
            self.stack.append("err:a_subtract:non-numeric parameter")
        return self.stack

    def a_divide(self):
        """
        Pops the last two items off the stack and divides the first list element by the second list element.
        (in reverse order of how they are popped off the stack)
        Pushes mathematical result onto the stack:
            errors:
                stack length is less than 2,
                list element cannot be converted to a number
                attempt to divide by zero
        :return:  stack (list) with result of mathematical operation
        :example: [C1|C2|A/]
        """
        if len(self.stack) < 2:
            self.stack.append("err:a_divide:too few parameters")
            return self.stack
        b = self.stack.pop()
        a = self.stack.pop()
        if not (self.is_number(a) and self.is_number(b)):
            self.stack.append("err:a_divide:non-numeric parameter")
            return self.stack
        if float(b) == 0:
            self.stack.append("err:a_divide:divide by zero error")
            return self.stack

        self.stack.append(float(a) / float(b))
        return self.stack

    # String Operators
    def f_cat(self):
        """
        Pops the last two items off the stack, converts to strings and concatenates them.
        Pushes concatenated result onto the stack:
            errors:
                stack length is less than 2,
        :return:  stack (list) with result of concatenation
        :example: [CHello |CWorld|FCAT]
        """
        if len(self.stack) < 2:
            self.stack.append("err:f_cat:too few parameters")
            return self.stack

        str_b = str(self.stack.pop())
        str_a = str(self.stack.pop())
        self.stack.append(str_a + str_b)
        return self.stack

    def f_length(self):
        """
        Pops the last item off the stack, converts to string and tests length
        Pushes string length back onto the stack:
            errors:
                no errors, a blank stack returns 0
        :return:  stack (list) with result of concatenation
        :example: [CHello World|FLENGTH]
        """
        if self.stack:
            str_a = str(self.stack.pop())
            self.stack.append(len(str_a))
        else:
            self.stack.append(0)
        return self.stack

    def f_mid(self):
        """
        Pops last 3 Parameters from the stack: String|Start|#Characters
        Selects #Characters from String beginning at Start and pushes the result back onto the stack
        Start position is 1-based (first character in the string is position 1 rather than native python 0)
            errors:
                less than 3 parameters
                invalid start position
                non-numeric parameter 2 or 3
                non-string parameter 1
        :return:  stack (list) with extracted substring as last element
        :example: [CHello World|C7|C1|FMID] = "W"
        """
        if len(self.stack) < 3:
            self.stack.append("err:f_mid:too few parameters")
            return self.stack

        num_char = self.stack.pop()
        start_pos = self.stack.pop()
        str_a = self.stack.pop()

        if not isinstance(str_a, str):
            self.stack.append("err:f_mid:first parameter is not a string")
            return self.stack
        if self.is_number(start_pos):
            start_pos = int(start_pos)
        else:
            self.stack.append("err:f_mid:non-numeric parameter start")
            return self.stack
        if self.is_number(num_char):
            num_char = int(num_char)
        else:
            self.stack.append("err:f_mid:non-numeric parameter length")
            return self.stack
        if start_pos < 1 or start_pos > len(str_a):
            self.stack.append("err:f_mid:invalid start parameter")
            return self.stack
        # all tests have passed
        self.stack.append(str_a[start_pos - 1:start_pos + num_char - 1])
        return self.stack

    def f_find(self):
        """
        Pops last 2 Parameters from the stack: Haystack|Needle
        Searches for the first occurrence of Needle in the Haystack.
        If found, pushes the starting character position onto the stack
        If not found, pushes 0 on the stack
        String position is 1-based (first character in the string is position 1 rather than native python 0)
            errors:
                less than 2 parameters
                non-string Haystack (parameter 1, stack location 2)
        :return:  stack (list) with last element being the position in haystack of found needle or 0 if not found
        :example: [CStringToSearch|CTo|FFIND] = 7
        """
        if len(self.stack) < 2:
            self.stack.append("err:f_find:too few parameters")
            return self.stack

        needle = str(self.stack.pop())
        haystack = self.stack.pop()
        if not isinstance(haystack, str):
            self.stack.append("err:f_find:first parameter is not a string")
            return self.stack

        position = haystack.find(needle) + 1
        self.stack.append(position)
        return self.stack

    def f_replace(self):
        """
        Pops last 3 Parameters from the stack: base_str, find_str, repl_str
        Replaces all occurrences of find_str in base_str with repl_str
        Pushes the resulting string (or original string if find_str not found in base_str) back onto the stack
        String position is 1-based (first character in the string is position 1 rather than native python 0)
            errors:
                less than 3 parameters
                non-string base_str (parameter 1, stack location 3)
        :return:  stack (list) with last element being the new string created by substitution
        :example: [CBaseString|CFindStr|CReplaceStr|FREPLACE]
        """
        if len(self.stack) < 3:
            self.stack.append("err:f_replace:too few parameters")
            return self.stack

        repl_str = str(self.stack.pop())
        find_str = str(self.stack.pop())
        base_str = self.stack.pop()

        if not isinstance(base_str, str):
            self.stack.append("err:f_replace:first parameter is not a string")
            return self.stack

        new_str = base_str.replace(find_str, repl_str)
        self.stack.append(new_str)
        return self.stack


    # Date Functions
    #  FTODAY
    #  FTIME
    #  FELAPSED
    #  FDATEADD
    #  FDATEDIFF
    #  FDOW
    #  FDATEFORMAT

    # Patient Functions
    #  FPATSET
    #  FPATGET
    #  FPATXSET
    #  FPATXSETR
    #  FPATXGET
    #  FCLONE
    #  FPCLONE

    # Survey Functions
    #  FSETGLOBAL
    #  FGETGLOBAL
    #  FRETANS
    #  FCLEARANS
    #  FSETANS
    #  FSTORE (synonym for FSTORE)
    #  FLINK
    #  FIMAGE
    #  FWINDOW
    #  FFINISH
    #  FCONTINUE

    # Email Functions
    #  FCHECKEMAIL
    #  FMAIL

    # Info Functions
    #  FSYSTEM
    #  FPRINT
    #  FGETPROCGLOBAL (get processor global)
    #  FUSER
    #  FPARAM
    #  FTRACE
    #  FSQL?
    #  FTIMESTART
    #  FTIMESTOP

    # Control Structures
    #  FIIF
    #  FGOTO
    #  FGOIF
    #  FDO
    #  FHOME

    # SpineChart-Specific Funtions
    #
