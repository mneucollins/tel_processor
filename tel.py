from datetime import date
from datetime import datetime
from datetime import timedelta
# import pymysql
import mysql.connector
from mysql.connector import errorcode

import config.database as database

# _cnx = mysql.connector.connect(**database.pop_user)


class Tel:
    """
    A tel object consists of a stack list of values and an operation on the stack
    tel methods are called by operator name and passed the stack list,
        e.g. P_EQUAL_TO (stack)
    The function:
     1. operates on the stack,
     2. pushes the result of the operation back on the stack, and
     3. returns the stack
    """

    def __init__(self, stack, user_id=0):
        self.stack = stack
        self.user_id = user_id

        try:
            self.cnx = mysql.connector.connect(**database.pop_user)
        except:
            print ("unable to connect to SQL server")

        self.cursor = self.cnx.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.cnx.close()

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
            val_to_return = ("err:bool_eval:cannot convert '{}' to boolean".format(val_to_test))
        return val_to_return

    @staticmethod
    def is_number(x):
        try:
            float(x)
            return True
        except ValueError:
            return False


    def matches (self, table, field, testval):
        # Does table exist
        sql = "show tables like %s"
        find_table = self.cursor.execute(sql, (table,))
        if find_table is None:
            err_str = ('err: matches: tablename "{}" does not exist in this database'.format(table))
            return err_str        
        
        # Does field exist in this table
        sql = "SHOW COLUMNS FROM %s LIKE %s"
        find_col = self.cursor.execute(sql, (table, field))
        if find_col is None:
            err_str = ('err: matches: fieldname "{}" does not exist in tablename {}'.format(field,table))
            return err_str        

        # how many rows match testval        
        sql = "SELECT COUNT(*) FROM %s WHERE %s=%s"
        self.cursor.execute(sql, (table, field, testval))
        result = self.cursor.fetchone()
        return result[0]


    # -----------------
    # Logical Operators
    # -----------------
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

    def p_logical_not(self):
        """
        Pops the last item off the stack. 
        Pushes onto the stack:
            false, if the value can be evaluated as true
            true if the value is false, not boolean, or empty
        """
        if len(self.stack) < 1:
            self.stack.append("err:p_logical_not:too few parameters")
            return self.stack
        else:
            a = self.stack.pop()
            bool_eval = self.bool_eval(a)
            if bool_eval is True:
                self.stack.append(False)
            elif bool_eval is False:
                self.stack.append(True)
            else:
                self.stack.append (bool_eval)
        return self.stack


    # ----------------------
    # Mathematical Operators
    # ----------------------

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

    # ----------------------
    # String Operators
    # ----------------------

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

    # ----------------------
    # Date Functions
    # ----------------------

    def f_today(self):
        """
        :param: none
        Pushes today's date in the format YYYY-MM-DD onto the stack
        :return:  stack (list) with last element being todays date
        :example: [FTODAY]
        """
        today = str(date.today())
        self.stack.append(today)
        return self.stack

    def f_time(self):
        """
        No Parameters
        Pushes today's datetime in the format YYYY-MM-DD HH:MM:SS onto the stack
        :return:  stack (list) with last element being current datetime (no microsecond)
        :example: [FTIME]
        """
        time = datetime.now().replace(microsecond=0).isoformat(' ')
        self.stack.append(time)
        return self.stack

    def f_timestamp(self):
        """
        :param: none
        Pushes current platform-dependent timestamp onto the stack
        :return:  stack (list) with last element being current system timestamp
        :example: [FTIME]
        """
        ts = datetime.now().timestamp()
        self.stack.append(ts)
        return self.stack

    #  FELAPSED
    #  holding off on FELAPSED for now

    def f_dateadd(self):
        """
        Returns the date that is <number of days> from <date>. Negative days value subtracts
        :param: stack: stack[-2]=number of days, stack[-1]=date
        :return:  result or error message placed back on the stack
        :tel example: [C10|C2018-10-11|FDATEADD]
        """

        if len(self.stack) < 2:
            self.stack.append("err:f_dateadd:too few parameters (need 2)")
            return self.stack

        base_date_str = str(self.stack.pop())
        try:
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
        except ValueError:
            err_str = ('err:f_date_add:second parameter, "{}", is not a valid date in the proper format YYYY-MM-DD'
                       .format(base_date_str))
            self.stack.append(err_str)
            return self.stack

        num_days_str = str(self.stack.pop())
        try:
            num_days = int(num_days_str)
        except ValueError:
            err_str = ('err:f_date_add: first parameter, "{}", must be an integer (number of days)'
                       .format(num_days_str))
            self.stack.append(err_str)
            return self.stack

        new_date = base_date + timedelta(days=num_days)
        new_date_str = new_date.strftime('%Y-%m-%d')
        self.stack.append(new_date_str)
        return self.stack


    def f_datediff(self):
        """
        Returns an integer indicating the number of days difference between two dates.
        if date1 is prior to date2, returned integer will be positive
        if date1 is after than date2, returned integer will be negative
        :param: stack: stack[-2]=date1, stack[-1]=date2
        :return:  result or error message placed back on the stack
        :tel example: [C2017-01-01|C2018-01-01|FDATEDIFF]
        """
        if len(self.stack) < 2:
            self.stack.append("err:f_datediff:too few parameters (need 2)")
            return self.stack

        d2_str = str(self.stack.pop())
        d1_str = str(self.stack.pop())
        try:
            d2 = datetime.strptime(d2_str, '%Y-%m-%d')
            d1 = datetime.strptime(d1_str, '%Y-%m-%d')
        except ValueError:
            err_str = ('err:f_date_diff: both parameters, "{}", "{}", must be valid dates in the format YYYY-MM-DD'
                       .format(d1_str, d2_str))
            self.stack.append(err_str)
            return self.stack

        days_difference = (d2 - d1).days
        self.stack.append(days_difference)
        return self.stack


    def f_dow(self):
        """
        Returns a 3 char string indicating the number of days difference between two dates.
        if date1 is prior to date2, returned integer will be positive
        if date1 is after than date2, returned integer will be negative
        :param: stack[-1]=date
        :return:  result or error message placed back on the stack
        :tel example: [C2017-01-01|FDOW]
        """
        if len(self.stack) < 1:
            self.stack.append("err:f_dow:too few parameters (need 1)")
            return self.stack

        dt_str = str(self.stack.pop())
        try:
            dt = datetime.strptime(dt_str, '%Y-%m-%d')
        except ValueError:
            err_str = ('err:f_dow: parameter "{}" is not a valid date in format YYYY-MM-DD'
                       .format(dt_str))
            self.stack.append(err_str)
            return self.stack

        dow = dt.strftime("%a")
        self.stack.append(dow)
        return self.stack


    def f_dateformat(self):
        """
        Returns a string date representation
        :param: stack[-1]=format, stack[-2]=date
        :return:  result or error message placed back on the stack. The format string is not tested
        :tel example: [C2018-07-02|C%A %B %d, %Y|FDATEFORMAT] produces Tuesday January 02, 2018
        """
        if len(self.stack) < 2:
            self.stack.append("err:f_dateformat:too few parameters (need 2)")
            return self.stack

        format_str = self.stack.pop()
        dt_str = self.stack.pop()

        try:
            dt = datetime.strptime(dt_str, '%Y-%m-%d')
        except ValueError:
            err_str = ('err:f_dateformat: parameter "{}" is not a valid date in format YYYY-MM-DD'
                       .format(dt_str))
            self.stack.append(err_str)
            return self.stack

        date_formatted = dt.strftime(format_str)
        self.stack.append(date_formatted)
        return self.stack

    # ----------------------
    # Patient Functions
    # -- require a current session/patient
    # ----------------------
    
    @staticmethod
    def patient_column_exists(self, fieldname):
        """
        local test for the existance of fieldname in patients table,
        :param: fieldname to test
        :return: true if fieldname exists in the patient table, false if it does not
        :notes: 
            this is used by f_patset and f_patget methods. Follows the procedure:
            --execute an query on the patients table that will return no value
            --fetch the empty recordset or else next query will generate an 'unread result found' error message
            --doing this creates a readonly list if column names that can be used to test fielname existance
        """
        self.cursor.execute("select * from patients where id = 0")
        self.cursor.fetchall()

        if fieldname not in self.cursor.column_names:
            return False
        else:
            return True

    @staticmethod
    def patient_exists(self, user_id):
        """
        local test for the existance of patient record
        :param: user_id to find
        :return: true if user_id exists in the patient table, false if it does not
        """
        sql = "SELECT COUNT(*) FROM `patients` WHERE `user_id`=%s"
        self.cursor.execute(sql, (user_id,))
        result = self.cursor.fetchone()
        if result[0] != 1:
            return False
        else:
            return True


    def f_patset(self, user_id):
        """
        stores a <value> in the <fieldname> of the current patient record.
        :param: stack[-1]=value, stack[-2] = fieldname
        :return:  boolean true if successful, err if otherwise (no patient record found)
        :tel example: [C<fieldname>|C<value>|FPatSet]
        """

        if len(self.stack) < 2:
            self.stack.append("err:f_patset:too few parameters (need 2)")
            return self.stack

        # look for an existing patient record
        if not self.patient_exists(self,user_id):
            err_str = ('err:f_patset: user "{}" was not found in patients table'.format(user_id))
            self.stack.append(err_str)
            return self.stack
        else:
            # update the found record
            value = self.stack.pop()
            fieldname = self.stack.pop()

            # does fieldname exist?
            if not self.patient_column_exists(self,fieldname):
                err_str = ('err:f_patset: fieldname "{}" is not in the patients table'.format(fieldname))
                self.stack.append(err_str)
                return self.stack
            else:
                # fieldname exists in patient table, update it
                # note the sql statement with %s parameters is created with the .format method in order to substitutie 
                # the fieldname in the query statement. Fieldnames cannot be substituted in the execute statement
                # using %s parameter substitution
                sql = ('UPDATE patients SET {} = %s WHERE user_id = %s'.format(fieldname))
                self.cursor.execute(sql, (value, user_id))
                self.cnx.commit()

                # affected_rows does not work as expected here, but the cursor rowcount property returns the proper value
                num_rows = self.cursor.rowcount
                if num_rows == 1:
                    self.stack.append(True)
                else:
                    self.stack.append(False)
        return self.stack


    def f_patget(self, user_id):
        """
        user_id must be passed in as parameter
        retrieves the value in the <fieldname> of the current patient record.
        :param: stack[-1] = fieldname
        :return:  value in fieldname if successful, err if otherwise
            (no patient record found, no fieldname found)
        :tel example: [C<fieldname>|FPATGET]
        """
        # test for correct number of parameters
        if len(self.stack) < 1:
            self.stack.append("err:f_patget:missing fieldname parameter")
            return self.stack

        # look for an existing patient record
        if not self.patient_exists(self,user_id):
            err_str = ('err:f_patget: user "{}" was not found in patients table'.format(user_id))
            self.stack.append(err_str)
            return self.stack
        
        # does fieldname exist?
        fieldname = self.stack.pop()
        if not self.patient_column_exists(self,fieldname):
            err_str = ('err:f_patget: fieldname "{}" is not in the patients table'.format(fieldname))
            self.stack.append(err_str)
            return self.stack
        else:
            # fieldname exists in patient table, return its value
            sql = ('SELECT {} FROM patients WHERE user_id = %s'.format(fieldname))
            self.cursor.execute(sql, (user_id,))
            result = self.cursor.fetchone()
            self.stack.append(result[0])
            return self.stack


    def f_patxset(self, user_id):
        """
        stores or updates <fieldname><value>in the patients_extended table for the current patient.
        :param: stack[-2] = fieldname, stack[-1] = value
        :return:  true if successful, err if otherwise
            (no patient record found, no fieldname found)
        :tel example: [C<fieldname>|C<value>FPATXSET]
        """
        pass
        # parameters?
        # if len(self.stack) < 2:
        #     self.stack.append("err:f_patxset:too few parameters (need 2)")
        #     return self.stack

        # value = self.stack.pop()
        # fieldname = self.stack.pop()
        
        # sql = "SELECT COUNT(*) FROM `patients` WHERE `user_id`=%s"



    # FPATXSETR

    # FPATXGET
    # def f_patxget(self, user_id):
        """
        stores or updates <fieldname><value>in the patients_extended table for the current patient.
        :param: stack[-2] = fieldname, stack[-1] = value
        :return:  true if successful, err if otherwise
            (no patient record found, no fieldname found)
        :tel example: [C<fieldname>|C<value>FPATXSET]
        """

    #  FCLONE
    #  FPCLONE

    # Survey Functions
    #  FSETGLOBAL
    #  FGETGLOBAL
    #  FRETANS
    #  FCLEARANS
    #  FSETANS (synonym for FSTORE)
    #  FSTORE
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

    # SpineChart-Specific Functions
    #

    

    @staticmethod
    def db_error(err):
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
            return None
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
            return None       
        else:
            print(err)
            return None

