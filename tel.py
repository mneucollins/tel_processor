from datetime import date
from datetime import datetime
from datetime import timedelta
import time
# import pymysql
import mysql.connector
from mysql.connector import errorcode
import pymysql.cursors

import config.database as database
import app
import processor
# Use to escape html formatting
import html
from validate_email import validate_email
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#_cnx = mysql.connector.connect(**database.pop_user)
import re

"""DB Connections"""
analysis_connection = pymysql.connect(
                                host='163.246.173.221',
                                user='analysis_user',
                                password='K[[n`Wv7Q_7R[tObgSPE^{',
                                db='psp_analysis')

analysis_cursor = analysis_connection.cursor()


hand_connection = pymysql.connect(
                                host='163.246.173.221',
                                user='surginet_admin',
                                password='>j^.-5UICcZiM#C{pw|&i,OH',
                                db='psp_emory_hand')


hand_cursor = hand_connection.cursor()

prp_connection = pymysql.connect(
                                host='163.246.173.221',
                                user='prp_user',
                                password='IX8@BZ9ob.]PW^xBWzF<Ka~',
                                db='psp_emory_prp')

prp_cursor = prp_connection.cursor()

inject_connection = pymysql.connect(
                                host='163.246.173.221',
                                user='inject_user',
                                password='!S)aYm-CpOZ8n7#G3u9R0Ec.',
                                db='psp_emory_inject')

inject_cursor = inject_connection.cursor()

ortho_connection = pymysql.connect(
                                host='163.246.173.221',
                                user='ortho_user',
                                password='=?k)Vfg$U7now!JIL*_iABL',
                                db='psp_emory_ortho')

ortho_cursor = ortho_connection.cursor()

spine_connection = pymysql.connect(
                                host='163.246.173.221',
                                user='spine_user',
                                password='^&MfWSfIVY2j*85!V%6x)&mf',
                                db='psp_emory_spine')

spine_cursor = spine_connection.cursor()

sports_connection = pymysql.connect(
                                host='163.246.173.221',
                                user='sports_user',
                                password=',}wf+SAno*8~soS<Pgzxv_@(',
                                db='psp_emory_sports')

sports_cursor = sports_connection.cursor()

global_connection = pymysql.connect(
                                host='163.246.173.221',
                                user='global_user',
                                password='Pz<z{8Z2,rSY-myQ=@MB2aR',
                                db='psp_global_config')

global_cursor = global_connection.cursor()

"""End DB Connections"""


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
            self.cnx = mysql.connector.connect(**database.analysis_db)
        except():
            print("unable to connect to SQL server")

        self.cursor = self.cnx.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.cnx.close()

    @staticmethod
    def bool_eval(bools=""):
        """
        :param val_to_test:
        :return: boolean True or False
        Interprets text("TRUE", "FALSE"), text("0", "1") and numeric (0,1) val_to_test and returns boolean (True, False)
        changed bool to bools, as parameter for isinstance cannot have same keyword 'bool' as bool method
        """
        if bools is None:
            return False
        else:
            if bools == 'TRUE' or (isinstance(bools, bool) and bools is True) or bools == '1' or bools == 1:
                return True
            else:
                return False

    @staticmethod
    def is_number(x):
        try:
            float(x)
            return True
        except ValueError:
            return False

    def matches(self, table, field, testval):
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

    # Logical Operators
    def p_equal_to(self):
        """
        Pops the last two items off the stack, compares for equality,
        pushes result of comparison onto stack
        :return: stack (list) with last value boolean or err message
        :example: [C1|C2|P=]
        """
        a = self.stack.pop()
        b = self.stack.pop()
        #if isinstance(a, str):
            #a = a.upper().strip()
        #b = self.stack.pop()
        #if isinstance(b, str):
            #b = b.upper().strip()
        if a == b:
            self.stack.append(True)
        else:
            self.stack.append(False)

    def p_not_equal_to(self):
        """
        Pops the last two items off the stack, compares for inequality, pushes result of comparison onto stack
        :return: stack (list) with last value boolean or err message
        :example: [C1|C2|P#]
        """
        if len(self.stack) < 2:
            self.stack.append("err:p_equal_to:too few parameters")
        else:
            a = self.stack.pop()
            if isinstance(a, str):
                a = a.strip()
            b = self.stack.pop()
            if isinstance(b, str):
                b = b.strip()
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
        Pops the last two items off the stack,
        and compares the boolean evaluation of each.
        Pushes result onto the stack:
            error if less stack length is less than 2, true if both values are true, otherwise false
        :return:  stack (list) with last value boolean or err message
        :example: [C1|C2|P*]
        """
        if len(self.stack) < 2:
            self.stack.append("err:p_logical_and:too few parameters")
        else:
            a = self.stack.pop()
            b = self.stack.pop()
            if self.bool_eval(a) and self.bool_eval(b):
                self.stack.append(
                    True
                    )
            else:
                self.stack.append(
                    False
                    )
        return self.stack

    def p_logical_or(self):
        """
        Pops the last two items off the stack, and compares the boolean evaluation of each.
        Pushes boolean result onto the stack:
            error if less stack length is less than 2, true at least one of the values are true, otherwise false
        :return:  stack (list) with last value boolean or err message
        :example: [C1|C2|P+]
        """
        if len(self.stack) < 2:
            self.stack.append("err:p_logical_and:too few parameters")
        else:
            a = self.stack.pop()
            b = self.stack.pop()
            if self.bool_eval(a) or self.bool_eval(b):
                self.stack.append(
                    True
                    )
            else:
                self.stack.append(
                    False
                    )
        return self.stack

    def p_logical_not(self):
        """
        Pops the last item off the stack.
        Pushes onto the stack:
            false, if the value can be evaluated as true
            true if the value is false, not boolean, or empty
            :example: [C1|C1|P!]
        """
        if len(self.stack) < 1:
            self.stack.append("err:p_logical_not:too few parameters")
            return self.stack
        else:
            a = self.stack.pop()
            if self.bool_eval(a):
                self.stack.append(False)
            else:
                self.stack.append(True)

    # ----------------------#
    # Mathematical Operators
    # ----------------------#
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
        #return self.stack

    # ----------------------#
    # String Operators
    # ----------------------#

    def f_cat(self):
        """
        Pops the last two items off the stack, converts to strings and concatenates them.
        Pushes concatenated result onto the stack:
            errors:
                stack length is less than 2,
        :return:  stack (list) with result of concatenation
        :example: [CHello|CWorld|FCAT]
        """
        if len(self.stack) < 2:
            self.stack.append("err:f_cat:too few parameters")
            return self.stack

        str_b = str(self.stack.pop())
        str_a = str(self.stack.pop())
        self.stack.append(str_a + str_b)
        #return self.stack

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

    # FTRACE
    def f_trace(self):
        # debug_var(self.stack)
        debug_var = self.stack.pop()
        return debug_var

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

    def f_date_add(self):
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

    def f_date_diff(self):
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

    def patient_exists(self):
        """
        local test for the existance of patient record
        :param: user_id to find
        :return: true if user_id exists in the patient table, false if it does not
        URI syntax:
        <domain>/get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=C4|C51246156|PATIENTEXISTS&database_name=psp_emory_prp
        """
        database = app.database_name()
        mrn = self.stack.pop()
        if database == 'psp_emory_hand':
            rows_count = hand_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                self.stack.pop()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.pop()
                self.stack.append(False)
        elif database == 'psp_emory_prp':
            rows_count = prp_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                self.stack.pop()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.pop()
                self.stack.append(False)
        elif database == 'psp_emory_inject':
            rows_count = inject_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                self.stack.pop()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.pop()
                self.stack.append(False)
        elif database == 'psp_emory_ortho':
            rows_count = ortho_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                self.stack.pop()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.pop()
                self.stack.append(False)
        elif database == 'psp_emory_spine':
            rows_count = spine_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                self.stack.pop()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.pop()
                self.stack.append(False)
        elif database == 'psp_emory_sports':
            rows_count = sports_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                self.stack.pop()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.pop()
                self.stack.append(False)

    def f_patset(self):
        """
        stores a <value> in the <fieldname> of the current patient record.
        :param: stack[-1]=value, stack[-2] = fieldname
        :return:  boolean true if successful, err if otherwise (no patient record found)
        :tel example: [C<fieldname>|C<value>|FPATSET]
        :URL example: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=Cprimary_email|Ceee@rrr.com|FPATSET&mrn=1234567890&database_name=psp_emory_hand
        """

        if len(self.stack) < 2:
            self.stack.append("err:f_patset:too few parameters (need 2)")
            return self.stack
        value = self.stack.pop()
        fieldname = self.stack.pop()
        database = app.database_name()
        mrn = app.mrn()
        if database == 'psp_emory_hand':
            rows_count = hand_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                sql = "UPDATE `patients` SET {}='{}' WHERE medical_record_number = '{}'".format(fieldname, value, mrn)
                hand_cursor.execute(sql)
                hand_connection.commit()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.append(False)
        elif database == 'psp_emory_prp':
            rows_count = prp_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                sql = "UPDATE `patients` SET {}='{}' WHERE medical_record_number = '{}'".format(fieldname, value, mrn)
                prp_cursor.execute(sql)
                prp_connection.commit()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.append(False)
        elif database == 'psp_emory_inject':
            rows_count = inject_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                sql = "UPDATE `patients` SET {}='{}' WHERE medical_record_number = '{}'".format(fieldname, value, mrn)
                inject_cursor.execute(sql)
                inject_connection.close()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.append(False)
        elif database == 'psp_emory_ortho':
            rows_count = ortho_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                sql = "UPDATE `patients` SET {}='{}' WHERE medical_record_number = '{}'".format(fieldname, value, mrn)
                ortho_cursor.execute(sql)
                ortho_connection.close()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.append(False)
        elif database == 'psp_emory_spine':
            rows_count = spine_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                sql = "UPDATE `patients` SET {}='{}' WHERE medical_record_number = '{}'".format(fieldname, value, mrn)
                spine_cursor.execute(sql)
                spine_connection.close()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.append(False)
        elif database == 'psp_emory_sports':
            rows_count = sports_cursor.execute(
                "SELECT * FROM patients WHERE medical_record_number = %s", mrn)
            if rows_count == 1:
                sql = "UPDATE `patients` SET {}='{}' WHERE medical_record_number = '{}'".format(fieldname, value, mrn)
                sports_cursor.execute(sql)
                sports_connection.close()
                self.stack.append(True)
            elif rows_count == 0:
                self.stack.append(False)

    def f_patget(self):
        """
        user_id must be passed in as parameter
        retrieves the value in the <fieldname> of the current patient record.
        :param: stack[-1] = fieldname
        :return:  value in fieldname if successful, err if otherwise
            (no patient record found, no fieldname found)
        :tel example: [C<fieldname>|FPATGET]
        : URI example: <domain>/get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=Cmedical_record_number|FPATGET&database_name=psp_emory_hand&user_id=69518
        """
        # test for correct number of parameters
        if len(self.stack) < 1:
            self.stack.append("err:f_patget:missing fieldname parameter")
            return self.stack
        database = app.database_name()
        fieldname = self.stack.pop()
        f_user_id = app.user_id()
        if database == 'psp_emory_hand':
            sql = "SELECT {} FROM `patients` WHERE f_user_id = {}".format(fieldname, f_user_id)
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_prp':
            sql = "SELECT {} FROM `patients` WHERE f_user_id = {}".format(fieldname, f_user_id)
            prp_cursor.execute(sql)
            result = prp_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_inject':
            sql = "SELECT {} FROM `patients` WHERE f_user_id = {}".format(fieldname, f_user_id)
            inject_cursor.execute(sql)
            result = inject_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_ortho':
            sql = "SELECT {} FROM `patients` WHERE f_user_id = {}".format(fieldname, f_user_id)
            ortho_cursor.execute(sql)
            result = ortho_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_spine':
            sql = "SELECT {} FROM `patients` WHERE f_user_id = {}".format(fieldname, f_user_id)
            spine_cursor.execute(sql)
            result = prp_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_sports':
            sql = "SELECT {} FROM `patients` WHERE f_user_id = {}".format(fieldname, f_user_id)
            sports_cursor.execute(sql)
            result = sports_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)

    def f_patxset(self):
        """
        stores or updates <fieldname><value>in the patients_extended table for the current patient.
        :param: stack[-2] = fieldname, stack[-1] = value
        :return:  true if successful, err if otherwise
            (no patient record found, no fieldname found)
        :tel example: [C<fieldname>|C<value>FPATXSET]
        :URL example: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=Cprimary_email|Ceee@rrr.com|FPATXSET&mrn=1234567890&database_name=psp_emory_hand
        """
        if len(self.stack) < 2:
            self.stack.append("err:f_patset:too few parameters (need 2)")
            return self.stack
        fieldvalue = self.stack.pop()
        fieldname = self.stack.pop()
        database = app.database_name()
        f_patient_id = app.user_id()
        if database == 'psp_emory_hand':
            rows_count = """SELECT * FROM patients_extended
                            WHERE f_patient_id = {}""".format(
                                                              f_patient_id
                                                              )
            hand_cursor.execute(rows_count)
            hand_connection.commit()
            if rows_count is not None:
                sql_fieldname = """UPDATE `patients_extended`
                        SET field_name='{}' WHERE
                         f_patient_id = {} AND
                         field_value ='{}' """.format(
                                                    fieldname,
                                                    f_patient_id,
                                                    fieldvalue)
                hand_cursor.execute(sql_fieldname)
                hand_connection.commit()
                sql_fieldvalue = """UPDATE `patients_extended`
                        SET field_value='{}' WHERE
                         f_patient_id = {} AND
                         field_name ='{}' """.format(
                                                    fieldvalue,
                                                    f_patient_id,
                                                    fieldname)
                hand_cursor.execute(sql_fieldvalue)
                hand_connection.commit()
                self.stack.append(True)
            elif rows_count is None:
                self.stack.append(False)
        elif database == 'psp_emory_prp':
            rows_count = """SELECT * FROM patients_extended
                            WHERE f_patient_id = {}""".format(
                                                              f_patient_id
                                                              )
            prp_cursor.execute(rows_count)
            prp_connection.commit()
            if rows_count is not None:
                sql_fieldname = """UPDATE `patients_extended`
                        SET field_name='{}' WHERE
                         f_patient_id = {} AND
                         field_value ='{}' """.format(
                                                    fieldname,
                                                    f_patient_id,
                                                    fieldvalue)
                prp_cursor.execute(sql_fieldname)
                prp_connection.commit()
                sql_fieldvalue = """UPDATE `patients_extended`
                        SET field_value='{}' WHERE
                         f_patient_id = {} AND
                         field_name ='{}' """.format(
                                                    fieldvalue,
                                                    f_patient_id,
                                                    fieldname)
                prp_cursor.execute(sql_fieldvalue)
                prp_connection.commit()
                self.stack.append(True)
            elif rows_count is None:
                self.stack.append(False)
        elif database == 'psp_emory_ortho':
            rows_count = """SELECT * FROM patients_extended
                            WHERE f_patient_id = {}""".format(
                                                              f_patient_id
                                                              )
            ortho_cursor.execute(rows_count)
            ortho_connection.commit()
            if rows_count is not None:
                sql_fieldname = """UPDATE `patients_extended`
                        SET field_name='{}' WHERE
                         f_patient_id = {} AND
                         field_value ='{}' """.format(
                                                    fieldname,
                                                    f_patient_id,
                                                    fieldvalue)
                ortho_cursor.execute(sql_fieldname)
                ortho_connection.commit()
                sql_fieldvalue = """UPDATE `patients_extended`
                        SET field_value='{}' WHERE
                         f_patient_id = {} AND
                         field_name ='{}' """.format(
                                                    fieldvalue,
                                                    f_patient_id,
                                                    fieldname)
                ortho_cursor.execute(sql_fieldvalue)
                ortho_connection.commit()
                self.stack.append(True)
            elif rows_count is None:
                self.stack.append(False)
        elif database == 'psp_emory_sports':
            rows_count = """SELECT * FROM patients_extended
                            WHERE f_patient_id = {}""".format(
                                                              f_patient_id
                                                              )
            sports_cursor.execute(rows_count)
            sports_connection.commit()
            if rows_count is not None:
                sql_fieldname = """UPDATE `patients_extended`
                        SET field_name='{}' WHERE
                         f_patient_id = {} AND
                         field_value ='{}' """.format(
                                                    fieldname,
                                                    f_patient_id,
                                                    fieldvalue)
                sports_cursor.execute(sql_fieldname)
                sports_connection.commit()
                sql_fieldvalue = """UPDATE `patients_extended`
                        SET field_value='{}' WHERE
                         f_patient_id = {} AND
                         field_name ='{}' """.format(
                                                    fieldvalue,
                                                    f_patient_id,
                                                    fieldname)
                sports_cursor.execute(sql_fieldvalue)
                sports_connection.commit()
                self.stack.append(True)
            elif rows_count is None:
                self.stack.append(False)

    # FPATXSETR
    def f_patxsetr(self):
        """
        stores or updates <fieldname><value>in the patients_extended table for the current patient.
        :param: stack[-2] = fieldname, stack[-1] = value
        :return:  true if successful, err if otherwise
            (no patient record found, no fieldname found)
        :tel example: Cvalue|Cfieldname|FPATXSETR
        :URI example: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=CCCeee@rrr.com|Cprimary_EMail|FPATXSETR&user_id=168707&database_name=psp_emory_hand
        """
        if len(self.stack) < 2:
            self.stack.append("err:f_patset:too few parameters (need 2)")
            return self.stack
        fieldname = self.stack.pop()
        fieldvalue = self.stack.pop()
        database = app.database_name()
        f_patient_id = app.user_id()
        if database == 'psp_emory_hand':
            rows_count = """SELECT * FROM patients_extended
                            WHERE f_patient_id = {}""".format(
                                                              f_patient_id
                                                              )
            hand_cursor.execute(rows_count)
            hand_connection.commit()
            if rows_count is not None:
                sql_fieldvalue = """UPDATE `patients_extended`
                        SET field_value='{}' WHERE
                         f_patient_id = {} AND
                         field_name ='{}' """.format(
                                                    fieldvalue,
                                                    f_patient_id,
                                                    fieldvalue)
                hand_cursor.execute(sql_fieldvalue)
                hand_connection.commit()
                sql_fieldname = """UPDATE `patients_extended`
                        SET field_name='{}' WHERE
                         f_patient_id = {} AND
                         field_value ='{}' """.format(
                                                    fieldname,
                                                    f_patient_id,
                                                    fieldvalue)
                hand_cursor.execute(sql_fieldname)
                hand_connection.commit()
                self.stack.append(True)
            elif rows_count is None:
                self.stack.append(False)
        elif database == 'psp_emory_prp':
            rows_count = """SELECT * FROM patients_extended
                            WHERE f_patient_id = {}""".format(
                                                              f_patient_id
                                                              )
            prp_cursor.execute(rows_count)
            prp_connection.commit()
            if rows_count is not None:
                sql_fieldvalue = """UPDATE `patients_extended`
                        SET field_value='{}' WHERE
                         f_patient_id = {} AND
                         field_name ='{}' """.format(
                                                    fieldvalue,
                                                    f_patient_id,
                                                    fieldvalue)
                prp_cursor.execute(sql_fieldvalue)
                prp_connection.commit()
                sql_fieldname = """UPDATE `patients_extended`
                        SET field_name='{}' WHERE
                         f_patient_id = {} AND
                         field_value ='{}' """.format(
                                                    fieldname,
                                                    f_patient_id,
                                                    fieldvalue)
                prp_cursor.execute(sql_fieldname)
                prp_connection.commit()
                self.stack.append(True)
            elif rows_count is None:
                self.stack.append(False)
        elif database == 'psp_emory_ortho':
            rows_count = """SELECT * FROM patients_extended
                            WHERE f_patient_id = {}""".format(
                                                              f_patient_id
                                                              )
            ortho_cursor.execute(rows_count)
            ortho_connection.commit()
            if rows_count is not None:
                sql_fieldvalue = """UPDATE `patients_extended`
                        SET field_value='{}' WHERE
                         f_patient_id = {} AND
                         field_name ='{}' """.format(
                                                    fieldvalue,
                                                    f_patient_id,
                                                    fieldvalue)
                ortho_cursor.execute(sql_fieldvalue)
                ortho_connection.commit()
                sql_fieldname = """UPDATE `patients_extended`
                        SET field_name='{}' WHERE
                         f_patient_id = {} AND
                         field_value ='{}' """.format(
                                                    fieldname,
                                                    f_patient_id,
                                                    fieldvalue)
                ortho_cursor.execute(sql_fieldname)
                ortho_connection.commit()
                self.stack.append(True)
            elif rows_count is None:
                self.stack.append(False)
        elif database == 'psp_emory_sports':
            rows_count = """SELECT * FROM patients_extended
                            WHERE f_patient_id = {}""".format(
                                                              f_patient_id
                                                              )
            sports_cursor.execute(rows_count)
            sports_connection.commit()
            if rows_count is not None:
                sql_fieldvalue = """UPDATE `patients_extended`
                        SET field_value='{}' WHERE
                         f_patient_id = {} AND
                         field_name ='{}' """.format(
                                                    fieldvalue,
                                                    f_patient_id,
                                                    fieldvalue)
                sports_cursor.execute(sql_fieldvalue)
                sports_connection.commit()
                sql_fieldname = """UPDATE `patients_extended`
                        SET field_name='{}' WHERE
                         f_patient_id = {} AND
                         field_value ='{}' """.format(
                                                    fieldname,
                                                    f_patient_id,
                                                    fieldvalue)
                sports_cursor.execute(sql_fieldname)
                sports_connection.commit()
                self.stack.append(True)
            elif rows_count is None:
                self.stack.append(False)

    # FPATXGET
    def f_patxget(self):
        """
        retrieves the value in PatX.fieldname record for current patient.
        Patients_extended "id" must be passed to user_id parameter.
        :tel example: [C<fieldname>|FPATXGET]
        :URI example: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=Cfield_name|FPATXGET&database_name=psp_emory_hand&user_id=21
        """
        if len(self.stack) < 1:
            self.stack.append("err:f_patget:missing fieldname parameter")
            return self.stack
        database = app.database_name()
        fieldname = self.stack.pop()
        f_patient_id = app.user_id()
        if database == 'psp_emory_hand':
            sql = "SELECT '{}' FROM `patients_extended` WHERE id = {}".format(fieldname, f_patient_id)
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_prp':
            sql = "SELECT fieldname FROM `patients_extended` WHERE f_patient_id = {}".format(fieldname, f_patient_id)
            prp_cursor.execute(sql)
            result = prp_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_inject':
            sql = "SELECT {} FROM `patients_extended` WHERE id = {}".format(fieldname, f_patient_id)
            inject_cursor.execute(sql)
            result = inject_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_ortho':
            sql = "SELECT {} FROM `patients_extended` WHERE id = {}".format(fieldname, f_patient_id)
            ortho_cursor.execute(sql)
            result = ortho_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_spine':
            sql = "SELECT {} FROM `patients_extended` WHERE id = {}".format(fieldname, f_patient_id)
            spine_cursor.execute(sql)
            result = prp_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_sports':
            sql = "SELECT {} FROM `patients_extended` WHERE id = {}".format(fieldname, f_patient_id)
            sports_cursor.execute(sql)
            result = sports_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)

    #  FCLONE
    def f_clone(self):
        param = app.param()
        if param < 1:
            self.stack.append("err:mrn parameter must be included.")
        else:
            self.stack.append(param)

    #  FPCLONE

    # Survey Functions

    #  FSETGLOBAL
    def f_set_global(self):
        """sets the value of a global variable. Global variables last for the duration of the survey
        ex: CglobalKey|CglobalValue|FSETGLOBAL
        URI ex: (Update): /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=CSURVEYNAME|CEmory%20Sports%20Patient%20Outcomes%20Program|FSETGLOBAL&database_name=psp_emory_hand&user_id=2
        """
        if len(self.stack) < 2:
            self.stack.append("err:f_patset:too few parameters (need 2)")
            return self.stack
        globalValue = self.stack.pop()
        globalKey = self.stack.pop()
        database = app.database_name()
        surveySessionID = app.surveySessionID()
        id = app.user_id()
        if database == 'psp_emory_hand':
            sql = "select id from `SurveyGlobals` WHERE `id` = {}".format(id)
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                sql_update_key = """UPDATE `SurveyGlobals`
                        SET globalKey='{}' WHERE
                         id = {}""".format(
                                            globalKey,
                                            id)
                hand_cursor.execute(sql_update_key)
                hand_connection.commit()
                sql_update_value = """UPDATE `SurveyGlobals`
                        SET globalValue='{}' WHERE
                         id = {}""".format(
                                            globalValue,
                                            id)
                hand_cursor.execute(sql_update_value)
                hand_connection.commit()
                self.stack.append(True)
        elif database == 'psp_emory_prp':
            sql = "select id from `SurveyGlobals` WHERE `id` = {}".format(id)
            prp_cursor.execute(sql)
            result = prp_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                sql_update_key = """UPDATE `SurveyGlobals`
                        SET globalKey='{}' WHERE
                         id = {}""".format(
                                            globalKey,
                                            id)
                prp_cursor.execute(sql_update_key)
                prp_connection.commit()
                sql_update_value = """UPDATE `SurveyGlobals`
                        SET globalValue='{}' WHERE
                         id = {}""".format(
                                            globalValue,
                                            id)
                prp_cursor.execute(sql_update_value)
                prp_connection.commit()
                self.stack.append(True)
        elif database == 'psp_emory_inject':
            sql = "select id from `SurveyGlobals` WHERE `id` = {}".format(id)
            inject_cursor.execute(sql)
            result = inject_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                sql_update_key = """UPDATE `SurveyGlobals`
                        SET globalKey='{}' WHERE
                         id = {}""".format(
                                            globalKey,
                                            id)
                inject_cursor.execute(sql_update_key)
                inject_connection.commit()
                sql_update_value = """UPDATE `SurveyGlobals`
                        SET globalValue='{}' WHERE
                         id = {}""".format(
                                            globalValue,
                                            id)
                inject_cursor.execute(sql_update_value)
                inject_connection.commit()
                self.stack.append(True)
        elif database == 'psp_emory_ortho':
            sql = "select id from `SurveyGlobals` WHERE `id` = {}".format(id)
            ortho_cursor.execute(sql)
            result = ortho_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                sql_update_key = """UPDATE `SurveyGlobals`
                        SET globalKey='{}' WHERE
                         id = {}""".format(
                                            globalKey,
                                            id)
                ortho_cursor.execute(sql_update_key)
                ortho_connection.commit()
                sql_update_value = """UPDATE `SurveyGlobals`
                        SET globalValue='{}' WHERE
                         id = {}""".format(
                                            globalValue,
                                            id)
                ortho_cursor.execute(sql_update_value)
                ortho_connection.commit()
                self.stack.append(True)
        elif database == 'psp_emory_spine':
            sql = "select id from `SurveyGlobals` WHERE `id` = {}".format(id)
            spine_cursor.execute(sql)
            result = spine_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                sql_update_key = """UPDATE `SurveyGlobals`
                        SET globalKey='{}' WHERE
                         id = {}""".format(
                                            globalKey,
                                            id)
                spine_cursor.execute(sql_update_key)
                spine_connection.commit()
                sql_update_value = """UPDATE `SurveyGlobals`
                        SET globalValue='{}' WHERE
                         id = {}""".format(
                                            globalValue,
                                            id)
                spine_cursor.execute(sql_update_value)
                spine_connection.commit()
                self.stack.append(True)
        elif database == 'psp_emory_sports':
            sql = "select id from `SurveyGlobals` WHERE `id` = {}".format(id)
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                sql_update_key = """UPDATE `SurveyGlobals`
                        SET globalKey='{}' WHERE
                         id = {}""".format(
                                            globalKey,
                                            id)
                sports_cursor.execute(sql_update_key)
                sports_connection.commit()
                sql_update_value = """UPDATE `SurveyGlobals`
                        SET globalValue='{}' WHERE
                         id = {}""".format(
                                            globalValue,
                                            id)
                sports_cursor.execute(sql_update_value)
                sports_connection.commit()
                self.stack.append(True)

    # FGETGLOBAL
    def f_get_global(self):
        """returns the value stored in global variable
            ex: Cglobalvarname|FGETGLOBAL
            ex URI: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=CSURVEYNAME|FGETGLOBAL&database_name=psp_emory_hand&surveySessionID=21135
        """
        globalKey = self.stack.pop()
        database = app.database_name()
        surveySessionID = app.surveySessionID()
        id = app.user_id()
        if database == 'psp_emory_hand':
            sql = """SELECT `globalValue` FROM `SurveyGlobals`
                      WHERE `sessionID` = {}
                      AND `globalKey` = '{}' """.format(
                                            surveySessionID,
                                            globalKey
                                            )
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_prp':
            sql = """SELECT `globalValue` FROM `SurveyGlobals`
                      WHERE `sessionID` = {}
                      AND `globalKey` = '{}' """.format(
                                            surveySessionID,
                                            globalKey
                                            )
            prp_cursor.execute(sql)
            result = prp_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_inject':
            sql = """SELECT `globalValue` FROM `SurveyGlobals`
                      WHERE `sessionID` = {}
                      AND `globalKey` = '{}' """.format(
                                            surveySessionID,
                                            globalKey
                                            )
            inject_cursor.execute(sql)
            result = inject_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_ortho':
            sql = """SELECT `globalValue` FROM `SurveyGlobals`
                      WHERE `sessionID` = {}
                      AND `globalKey` = '{}' """.format(
                                            surveySessionID,
                                            globalKey
                                            )
            ortho_cursor.execute(sql)
            result = ortho_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_spine':
            sql = """SELECT `globalValue` FROM `SurveyGlobals`
                      WHERE `sessionID` = {}
                      AND `globalKey` = '{}' """.format(
                                            surveySessionID,
                                            globalKey
                                            )
            spine_cursor.execute(sql)
            result = spine_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_sports':
            sql = """SELECT `globalValue` FROM `SurveyGlobals`
                      WHERE `sessionID` = {}
                      AND `globalKey` = '{}' """.format(
                                            surveySessionID,
                                            globalKey
                                            )
            sports_cursor.execute(sql)
            result = sports_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)

    #  FRETANS
    def f_fretans(self):
        """Returns the response (SurveyResponses.value) in the current survey stored in varname
            ex: CPhysician_A|FRETANS
            URI ex: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=CPhysician_A|FRETANS&database_name=psp_emory_hand&surveySessionID=16731
        """
        varName = self.stack.pop()
        database = app.database_name()
        surveySessionID = app.surveySessionID()
        if database == 'psp_emory_hand':
            sql = """SELECT `value` FROM `SurveyResponses`
                      WHERE `f_surveysession_id` = {}
                      AND `varname` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_prp':
            sql = """SELECT `value` FROM `SurveyResponses`
                      WHERE `f_surveysession_id` = {}
                      AND `varname` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            prp_cursor.execute(sql)
            result = prp_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_inject':
            sql = """SELECT `value` FROM `SurveyResponses`
                      WHERE `f_surveysession_id` = {}
                      AND `varname` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            inject_cursor.execute(sql)
            result = inject_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_ortho':
            sql = """SELECT `value` FROM `SurveyResponses`
                      WHERE `f_surveysession_id` = {}
                      AND `varname` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            ortho_cursor.execute(sql)
            result = ortho_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_spine':
            sql = """SELECT `value` FROM `SurveyResponses`
                      WHERE `f_surveysession_id` = {}
                      AND `varname` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            spine_cursor.execute(sql)
            result = spine_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_sports':
            sql = """SELECT `value` FROM `SurveyResponses`
                      WHERE `f_surveysession_id` = {}
                      AND `varname` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            sports_cursor.execute(sql)
            result = sports_cursor.fetchone()
            if result is None:
                # Valid id and sessionID must be sent
                self.stack.append(False)
            else:
                self.stack.append(result)

    #  FCLEARANS
    def f_clear_ans(self):
        """Returns the response (SurveyResponses.value) in the current survey stored in varname
            ex: CPhysician_A|FRETANS
            URI ex:/get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=Ccomments_A|Csomename|FSETANS&database_name=psp_emory_hand&surveySessionID=16731&surveyScreenID=Surgery%20Date
            """
        varName = self.stack.pop()
        database = app.database_name()
        surveySessionID = app.surveySessionID()
        if database == 'psp_emory_hand':
            sql = """UPDATE `SurveyResponses`
                     SET `value` = NULL
                      WHERE `f_surveysession_id` = {}
                      AND `varName` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            hand_cursor.execute(sql)
            hand_connection.commit()
            self.stack.append(True)
        elif database == 'psp_emory_prp':
            sql = """UPDATE `SurveyResponses`
                     SET `value` = NULL
                      WHERE `f_surveysession_id` = {}
                      AND `varName` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            prp_cursor.execute(sql)
            prp_connection.commit()
            self.stack.append(True)
        elif database == 'psp_emory_inject':
            sql = """UPDATE `SurveyResponses`
                     SET `value` = NULL
                      WHERE `f_surveysession_id` = {}
                      AND `varName` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            prp_cursor.execute(sql)
            prp_connection.commit()
            self.stack.append(True)
        elif database == 'psp_emory_ortho':
            sql = """UPDATE `SurveyResponses`
                     SET `value` = NULL
                      WHERE `f_surveysession_id` = {}
                      AND `varName` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            ortho_cursor.execute(sql)
            ortho_connection.commit()
            self.stack.append(True)
        elif database == 'psp_emory_spine':
            sql = """UPDATE `SurveyResponses`
                     SET `value` = NULL
                      WHERE `f_surveysession_id` = {}
                      AND `varName` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            spine_cursor.execute(sql)
            spine_connection.commit()
            self.stack.append(True)
        elif database == 'psp_emory_sports':
            sql = """UPDATE `SurveyResponses`
                     SET `value` = NULL
                      WHERE `f_surveysession_id` = {}
                      AND `varName` = '{}' """.format(
                                            surveySessionID,
                                            varName
                                            )
            sports_cursor.execute(sql)
            sports_connection.commit()
            self.stack.append(True)

    #  FSETANS (synonym for FSTORE)
    def f_set_ans(self):
        """
        Sets value field in SurveyResponses
        If f_surveysession_id, and varName are not valid; new record is created.
        If f_surveysession_id, and varName are valid, true is returned and record updated.
        If f_surveysession_id, and varName are not valid, false is returned and record inserted.
        :tel example: Cvalue|Clabel|FSETANS
        :URI example: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=Ccomments_A|CActivity_A|FSETANS&database_name=psp_emory_hand&surveySessionID=16731&surveyScreenID=Surgery%20Date
        """
        varName = self.stack.pop()  # is label varName?
        value = self.stack.pop()
        surveySessionID = app.surveySessionID()
        surveyScreenID = app.surveyScreenID()
        database = app.database_name()
        if database == 'psp_emory_hand':
            sql = """SELECT * FROM SurveyResponses
                    WHERE f_surveysession_id = {}
                    AND `varName` = '{}'""".format(
                                                surveySessionID,
                                                varName
                                                )
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            if result is not None:
                sql_update = """UPDATE `SurveyResponses`
                                SET `value` = '{}'
                                WHERE `f_surveysession_id` = {}
                                AND `varName` = '{}' """.format(
                                                               value,
                                                               surveySessionID,
                                                               varName
                                                                )
                hand_cursor.execute(sql_update)
                hand_connection.commit()
                self.stack.append(True)
            else:
                sql_insert = """INSERT INTO SurveyResponses
                               (f_surveysession_id, f_surveyscreen_id,
                               varName, value, last_modified)
                               VALUES ({}, '{}', '{}', '{}',
                               CURRENT_TIMESTAMP)""".format(
                                                            surveySessionID,
                                                            surveyScreenID,
                                                            varName,
                                                            value
                                                            )
                hand_cursor.execute(sql_insert)
                hand_connection.commit()
                self.stack.append(False)
        elif database == 'psp_emory_prp':
            sql = """SELECT * FROM SurveyResponses
                    WHERE f_surveysession_id = {}
                    AND `varName` = '{}'""".format(
                                                surveySessionID,
                                                varName
                                                )
            prp_cursor.execute(sql)
            result = prp_cursor.fetchone()
            if result is not None:
                sql_update = """UPDATE `SurveyResponses`
                                SET `value` = '{}'
                                WHERE `f_surveysession_id` = {}
                                AND `varName` = '{}' """.format(
                                                               value,
                                                               surveySessionID,
                                                               varName
                                                                )
                prp_cursor.execute(sql_update)
                prp_connection.commit()
                self.stack.append(True)
            else:
                sql_insert = """INSERT INTO SurveyResponses
                               (f_surveysession_id, f_surveyscreen_id,
                               varName, value, last_modified)
                               VALUES ({}, '{}', '{}', '{}',
                               CURRENT_TIMESTAMP)""".format(
                                                            surveySessionID,
                                                            surveyScreenID,
                                                            varName,
                                                            value
                                                            )
                prp_cursor.execute(sql_insert)
                prp_connection.commit()
                self.stack.append(False)
        elif database == 'psp_emory_inject':
            sql = """SELECT * FROM SurveyResponses
                    WHERE f_surveysession_id = {}
                    AND `varName` = '{}'""".format(
                                                surveySessionID,
                                                varName
                                                )
            inject_cursor.execute(sql)
            result = inject_cursor.fetchone()
            if result is not None:
                sql_update = """UPDATE `SurveyResponses`
                                SET `value` = '{}'
                                WHERE `f_surveysession_id` = {}
                                AND `varName` = '{}' """.format(
                                                               value,
                                                               surveySessionID,
                                                               varName
                                                                )
                inject_cursor.execute(sql_update)
                inject_connection.commit()
                self.stack.append(True)
            else:
                sql_insert = """INSERT INTO SurveyResponses
                               (f_surveysession_id, f_surveyscreen_id,
                               varName, value, last_modified)
                               VALUES ({}, '{}', '{}', '{}',
                               CURRENT_TIMESTAMP)""".format(
                                                            surveySessionID,
                                                            surveyScreenID,
                                                            varName,
                                                            value
                                                            )
                inject_cursor.execute(sql_insert)
                inject_connection.commit()
                self.stack.append(False)
        elif database == 'psp_emory_ortho':
            sql = """SELECT * FROM SurveyResponses
                    WHERE f_surveysession_id = {}
                    AND `varName` = '{}'""".format(
                                                surveySessionID,
                                                varName
                                                )
            ortho_cursor.execute(sql)
            result = ortho_cursor.fetchone()
            if result is not None:
                sql_update = """UPDATE `SurveyResponses`
                                SET `value` = '{}'
                                WHERE `f_surveysession_id` = {}
                                AND `varName` = '{}' """.format(
                                                               value,
                                                               surveySessionID,
                                                               varName
                                                                )
                ortho_cursor.execute(sql_update)
                ortho_connection.commit()
                self.stack.append(True)
            else:
                sql_insert = """INSERT INTO SurveyResponses
                               (f_surveysession_id, f_surveyscreen_id,
                               varName, value, last_modified)
                               VALUES ({}, '{}', '{}', '{}',
                               CURRENT_TIMESTAMP)""".format(
                                                            surveySessionID,
                                                            surveyScreenID,
                                                            varName,
                                                            value
                                                            )
                ortho_cursor.execute(sql_insert)
                ortho_connection.commit()
                self.stack.append(False)
        elif database == 'psp_emory_spine':
            sql = """SELECT * FROM SurveyResponses
                    WHERE f_surveysession_id = {}
                    AND `varName` = '{}'""".format(
                                                surveySessionID,
                                                varName
                                                )
            spine_cursor.execute(sql)
            result = spine_cursor.fetchone()
            if result is not None:
                sql_update = """UPDATE `SurveyResponses`
                                SET `value` = '{}'
                                WHERE `f_surveysession_id` = {}
                                AND `varName` = '{}' """.format(
                                                               value,
                                                               surveySessionID,
                                                               varName
                                                                )
                spine_cursor.execute(sql_update)
                spine_connection.commit()
                self.stack.append(True)
            else:
                sql_insert = """INSERT INTO SurveyResponses
                               (f_surveysession_id, f_surveyscreen_id,
                               varName, value, last_modified)
                               VALUES ({}, '{}', '{}', '{}',
                               CURRENT_TIMESTAMP)""".format(
                                                            surveySessionID,
                                                            surveyScreenID,
                                                            varName,
                                                            value
                                                            )
                spine_cursor.execute(sql_insert)
                spine_connection.commit()
                self.stack.append(False)
        elif database == 'psp_emory_sports':
            sql = """SELECT * FROM SurveyResponses
                    WHERE f_surveysession_id = {}
                    AND `varName` = '{}'""".format(
                                                surveySessionID,
                                                varName
                                                )
            sports_cursor.execute(sql)
            result = prp_cursor.fetchone()
            if result is not None:
                sql_update = """UPDATE `SurveyResponses`
                                SET `value` = '{}'
                                WHERE `f_surveysession_id` = {}
                                AND `varName` = '{}' """.format(
                                                               value,
                                                               surveySessionID,
                                                               varName
                                                                )
                sports_cursor.execute(sql_update)
                sports_connection.commit()
                self.stack.append(True)
            else:
                sql_insert = """INSERT INTO SurveyResponses
                               (f_surveysession_id, f_surveyscreen_id,
                               varName, value, last_modified)
                               VALUES ({}, '{}', '{}', '{}',
                               CURRENT_TIMESTAMP)""".format(
                                                            surveySessionID,
                                                            surveyScreenID,
                                                            varName,
                                                            value
                                                            )
                sports_cursor.execute(sql_insert)
                sports_connection.commit()
                self.stack.append(False)

        #  FSTORE
        def f_store(self):
            Tel.f_set_ans()

    #  FLINK
    def f_link(self):
        site = self.stack.pop()
        url = 'https://'+ site
        surveyScreenID = app.surveyScreenID()
        surveySessionID = app.surveySessionID()
        database = app.database_name()
        today = str(date.today())
        """
        Intended to be placed in the OnNext field. 1)Writes record to the Responses table:
        varname=url and value=date clicked 2)Closes and marks survey as complete, and 3)
        Returns URL to stack.
        :tel ex; Cheathgrades.com|FLINK
        :URI example: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=Cheathgrades.com|FLINK&database_name=psp_emory_hand&surveySessionID=16731&surveyScreenID=TestScreenID
        """
        if database == 'psp_emory_hand':
            sql_insert = """INSERT INTO SurveyResponses
                            (f_surveysession_id, f_surveyscreen_id,
                            varName, value, last_modified)
                            VALUES ({}, '{}', '{}', '{}',
                            CURRENT_TIMESTAMP)""".format(
                                                        surveySessionID,
                                                        surveyScreenID,
                                                        site,
                                                        today
                                                             )
            hand_cursor.execute(sql_insert)
            hand_connection.commit()
            self.stack.append(url)
        elif database == 'psp_emory_prp':
            sql_insert = """INSERT INTO SurveyResponses
                            (f_surveysession_id, f_surveyscreen_id,
                            varName, value, last_modified)
                            VALUES ({}, '{}', '{}', '{}',
                            CURRENT_TIMESTAMP)""".format(
                                                        surveySessionID,
                                                        surveyScreenID,
                                                        site,
                                                        today
                                                             )
            prp_cursor.execute(sql_insert)
            prp_connection.commit()
            self.stack.append(url)
        elif database == 'psp_emory_inject':
            sql_insert = """INSERT INTO SurveyResponses
                            (f_surveysession_id, f_surveyscreen_id,
                            varName, value, last_modified)
                            VALUES ({}, '{}', '{}', '{}',
                            CURRENT_TIMESTAMP)""".format(
                                                        surveySessionID,
                                                        surveyScreenID,
                                                        site,
                                                        today
                                                             )
            inject_cursor.execute(sql_insert)
            inject_connection.commit()
            self.stack.append(url)
        elif database == 'psp_emory_ortho':
            sql_insert = """INSERT INTO SurveyResponses
                            (f_surveysession_id, f_surveyscreen_id,
                            varName, value, last_modified)
                            VALUES ({}, '{}', '{}', '{}',
                            CURRENT_TIMESTAMP)""".format(
                                                        surveySessionID,
                                                        surveyScreenID,
                                                        site,
                                                        today
                                                             )
            ortho_cursor.execute(sql_insert)
            ortho_connection.commit()
            self.stack.append(url)
        elif database == 'psp_emory_spine':
            sql_insert = """INSERT INTO SurveyResponses
                            (f_surveysession_id, f_surveyscreen_id,
                            varName, value, last_modified)
                            VALUES ({}, '{}', '{}', '{}',
                            CURRENT_TIMESTAMP)""".format(
                                                        surveySessionID,
                                                        surveyScreenID,
                                                        site,
                                                        today
                                                             )
            spine_cursor.execute(sql_insert)
            spine_connection.commit()
            self.stack.append(url)
        elif database == 'psp_emory_sports':
            sql_insert = """INSERT INTO SurveyResponses
                            (f_surveysession_id, f_surveyscreen_id,
                            varName, value, last_modified)
                            VALUES ({}, '{}', '{}', '{}',
                            CURRENT_TIMESTAMP)""".format(
                                                        surveySessionID,
                                                        surveyScreenID,
                                                        site,
                                                        today
                                                             )
            sports_cursor.execute(sql_insert)
            sports_connection.commit()
            self.stack.append(url)


    #  FIMAGE Need to figure out how we are going to do image.
        """
        Pops the last 3 items off the stack, formats contents into image src,
        pushes results onto stack
        :example: C1|C2|C3|FIMAGE
        """
    def f_image(self):
        imagename = self.stack.pop()
        width = self.stack.pop()
        height = self.stack.pop()
        image_props_src = html.escape(
            '<img src="https://emoryorthopaedics.org/'
            'hand/images/survey_img/{}" width="{}" height="{}" alt="" />'
            .format(
                imagename,
                width,
                height))
        self.stack.append(image_props_src)

    #  FWINDOW
    def f_window(self):
        url = self.stack.pop()
        link_title = self.stack.pop()
        link = html.escape(
            '<a href="https://emoryorthopaedics.org/hand/images/survey_img/{}"'
            ' onclick="window.open(\'https://emoryorthopaedics.org/hand/'
            'images/survey_img/{}\', \'_blank\', \'width=800,height=800,'
            'scrollbars=yes,menubar=no,status=yes,'
            'resizable=yes,screenx=0,screeny=0\'); return false;">'
            '{}</a>'.format(
                            url,
                            url,
                            link_title))
        self.stack.append(link)

        #  FFINISH
        """NOT CURRENTLY USED"""

        #  FCONTINUE
        """NOT CURRENTLY USED"""

        # Email Functions
    #  FCHECKEMAIL
    def f_check_email(self):
        """
        Checks to see whether an email is a real address.
        Csam@sam.com|FCHECKEMAIL
        """
        emailToCheck = self.stack.pop()
        is_valid = validate_email(emailToCheck, verify=True)
        if is_valid is True:
            self.stack.append(True)
        else:
            self.stack.append(False)

    #  FMAIL
    def f_mail(self):
        """
        "Generates email and sends. First 5 parameters (through <body>) cannot
        be null Remaining parameters can be null, but need to be pushed onto
        the stack, i.e. all 9 parameters must be included even if null. CC
        and BCC can be a single email addresses or a comma-separated list
        of email addresses. ATTACH is the path (on the server) to a file
        to attach. This last one will need some
        work to make it reasonably easy to use"
        """
        try:
            attach = self.stack.pop()
            reply_to = self.stack.pop()
            bcc = self.stack.pop()
            cc = self.stack.pop()
            body = self.stack.pop()
            subject = self.stack.pop()
            to = self.stack.pop()
            from_email = self.stack.pop()
            from_name = self.stack.pop()
        except IndexError:
            error = html.escape(
                'err: f_mail. from_name,from_email, to,subject, body, must be included'
                '. Complete 9 parameter format must be included'
                ' in URI string even if null. '
                ' e.g.C<from_name>|C<from_email>|C<to>|C<subject>|C<body>|'
                'C<cc>|C<bcc>|C<reply_to>|C<attach>|FMAIL]'
                )
            self.stack.append(error)
        else:
            port = 587  # For starttls
            smtp_server = "emoryorthopaedics.org"
            sender_email = "admin@emoryorthopaedics.org"
            receiver_email = to
            password = "r703YHkf[pTz"
            message = (
                        ' From: {}'
                        '\n From Email: {}'
                        '\n To Email: {}'
                        '\n Subject: {}'
                        '\n Body: {}'
                        ).format(
                                from_name,
                                from_email,
                                to,
                                subject,
                                body
                                )

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls(context=context)
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
                self.stack.append(message)
        # Info Functions

    #  FSYSTEM
    """
    Returns the current system being utilized.
    database paramater must be passed through URL.
    This parameter is then passed back into the stack.
    :tel ex: FSYSTEM
    URI:
    """
    #def f_system(self):


    #  FPRINT
    """
    Returns last value(s) on the stack.
    :stack ex: CLastItem|FPRINT
    :url ex: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=CLastItem|FPRINT
    """
    def f_print(self):
        val = self.stack.pop()
        if len(self.stack) >= 1:
            self.stack.append("err:p_print_to:too few parameters")
        else:
            self.stack.append(val)
        #  FGETPROCGLOBAL (get processor global)
        #  FUSER

    # FPARAM
    """
    Retrieves the value in the parameter table returnfield name
    in the row identified by the unique parameter_name.
    Valid returnfield names are p1..p14.
    If record does not exist, stack appends to false.
    :tel ex: Cparam_name|Creturn_field|FPARAM
    :uri ex: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=CApril|Cp1|FPARAM&database_name=psp_emory_hand
    """
    def f_param(self):
        returnfield = self.stack.pop()
        param = self.stack.pop()
        database = app.database_name()
        if database == 'psp_emory_hand':
            sql = """SELECT {} from parameters
                     WHERE parameter_name = '{}'""".format(returnfield,
                                                           param
                                                           )
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            try:
                for row in result:
                    if row is not None:
                        self.stack.append(result)
            except TypeError:
                self.stack.append(False)
        elif database == 'psp_emory_prp':
            sql = """SELECT {} from parameters
                     WHERE parameter_name = '{}'""".format(returnfield,
                                                           param
                                                           )
            prp_cursor.execute(sql)
            result = prp_cursor.fetchone()
            try:
                for row in result:
                    if row is not None:
                        self.stack.append(result)
            # exception of possible NoneType for no row returned
            except TypeError:
                self.stack.append(False)
        elif database == 'psp_emory_inject':
            sql = """SELECT {} from parameters
                     WHERE parameter_name = '{}'""".format(returnfield,
                                                           param
                                                           )
            inject_cursor.execute(sql)
            result = inject_cursor.fetchone()
            try:
                for row in result:
                    if row is not None:
                        self.stack.append(result)
            except TypeError:
                self.stack.append(False)
        elif database == 'psp_emory_ortho':
            sql = """SELECT {} from parameters
                     WHERE parameter_name = '{}'""".format(returnfield,
                                                           param
                                                           )
            ortho_cursor.execute(sql)
            result = ortho_cursor.fetchone()
            try:
                for row in result:
                    if row is not None:
                        self.stack.append(result)
            except TypeError:
                self.stack.append(False)
        elif database == 'psp_emory_spine':
            sql = """SELECT {} from parameters
                     WHERE parameter_name = '{}'""".format(returnfield,
                                                           param
                                                           )
            spine_cursor.execute(sql)
            result = spine_cursor.fetchone()
            try:
                for row in result:
                    if row is not None:
                        self.stack.append(result)
            except TypeError:
                self.stack.append(False)
        elif database == 'psp_emory_sports':
            sql = """SELECT {} from parameters
                     WHERE parameter_name = '{}'""".format(returnfield,
                                                           param
                                                           )
            sports_cursor.execute(sql)
            result = sports_cursor.fetchone()
            try:
                for row in result:
                    if row is not None:
                        self.stack.append(result)
            except TypeError:
                self.stack.append(False)

    #  FSQL
    def f_sql(self):
        """
        Generates a simple query (SELECT <field> FROM <table>
        WHERE<where_clause>) Returns first result only.
        :tel ex: Ctable|Cfield|Cwhere clause|FSQL
        :uri ex: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=Cpatients|C*|Cid=168707|FSQL&database_name=psp_emory_hand
        """
        where = self.stack.pop()
        field = self.stack.pop()
        table = self.stack.pop()
        database = app.database_name()
        if database == 'psp_emory_hand':
            sql = """ SELECT {} FROM `{}` WHERE {}""".format(field,
                                                             table,
                                                             where
                                                             )
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_prp':
            sql = """ SELECT {} FROM `{}` WHERE {}""".format(field,
                                                             table,
                                                             where
                                                             )
            prp_cursor.execute(sql)
            result = prp_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_inject':
            sql = """ SELECT {} FROM `{}` WHERE {}""".format(field,
                                                             table,
                                                             where
                                                             )
            inject_cursor.execute(sql)
            result = inject_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_ortho':
            sql = """ SELECT {} FROM `{}` WHERE {}""".format(field,
                                                             table,
                                                             where
                                                             )
            ortho_cursor.execute(sql)
            result = ortho_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_spine':
            sql = """ SELECT {} FROM `{}` WHERE {}""".format(field,
                                                             table,
                                                             where
                                                             )
            spine_cursor.execute(sql)
            result = spine_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)
        elif database == 'psp_emory_sports':
            sql = """ SELECT {} FROM `{}` WHERE {}""".format(field,
                                                             table,
                                                             where
                                                             )
            sports_cursor.execute(sql)
            result = sports_cursor.fetchone()
            if result is None:
                self.stack.append(False)
            else:
                self.stack.append(result)

    #  FTIMESTART
    """Checks for record in timekeeper table.
    If record is found, it is deleted, and re-inserted using a Unix time_stamp
    :tel ex: CSFLoop|FTIMESTOP
    :uri ex: /get_tel?auth=gUbVdmDVN5fwuZxHQmVK&string=CSFLoop|FTIMESTART&database_name=psp_emory_hand&surveySessionID=998&user_id=999 """
    def f_time_start(self):
        label = self.stack.pop()
        sessionID = app.surveySessionID()
        patients_id = app.user_id()
        database = app.database_name()
        # Unix timestamp
        time_stamp = int(time.time())
        if database == 'psp_emory_hand':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_delete = """DELETE FROM `timekeeper`
                                WHERE id={}""".format(id)
                hand_cursor.execute(sql_delete)
                hand_connection.commit()
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, surveysession_id, label,
                                time_start) VALUES({}, {}, '{}',
                                {})""".format(
                                              patients_id,
                                              sessionID,
                                              label,
                                              time_stamp
                                              )
                hand_cursor.execute(sql_insert)
                hand_connection.commit()
                self.stack.append(True)
        elif database == 'psp_emory_prp':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            prp_cursor.execute(sql)
            result = prp_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_delete = """DELETE FROM `timekeeper`
                                WHERE id={}""".format(id)
                prp_cursor.execute(sql_delete)
                prp_connection.commit()
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, surveysession_id, label,
                                time_start) VALUES({}, {}, '{}',
                                {})""".format(
                                              patients_id,
                                              sessionID,
                                              label,
                                              time_stamp
                                              )
                prp_cursor.execute(sql_insert)
                prp_connection.commit()
                self.stack.append(True)
        elif database == 'psp_emory_inject':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            inject_cursor.execute(sql)
            result = inject_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_delete = """DELETE FROM `timekeeper`
                                WHERE id={}""".format(id)
                inject_cursor.execute(sql_delete)
                inject_connection.commit()
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, surveysession_id, label,
                                time_start) VALUES({}, {}, '{}',
                                {})""".format(
                                              patients_id,
                                              sessionID,
                                              label,
                                              time_stamp
                                              )
                inject_cursor.execute(sql_insert)
                inject_connection.commit()
                self.stack.append(True)
        elif database == 'psp_emory_ortho':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            ortho_cursor.execute(sql)
            result = ortho_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_delete = """DELETE FROM `timekeeper`
                                WHERE id={}""".format(id)
                ortho_cursor.execute(sql_delete)
                ortho_connection.commit()
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, surveysession_id, label,
                                time_start) VALUES({}, {}, '{}',
                                {})""".format(
                                              patients_id,
                                              sessionID,
                                              label,
                                              time_stamp
                                              )
                ortho_cursor.execute(sql_insert)
                ortho_connection.commit()
                self.stack.append(True)
        elif database == 'psp_emory_spine':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            spine_cursor.execute(sql)
            result = spine_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_delete = """DELETE FROM `timekeeper`
                                WHERE id={}""".format(id)
                spine_cursor.execute(sql_delete)
                spine_connection.commit()
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, surveysession_id, label,
                                time_start) VALUES({}, {}, '{}',
                                {})""".format(
                                              patients_id,
                                              sessionID,
                                              label,
                                              time_stamp
                                              )
                spine_cursor.execute(sql_insert)
                spine_connection.commit()
                self.stack.append(True)
        elif database == 'psp_emory_sports':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            sports_cursor.execute(sql)
            result = sports_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_delete = """DELETE FROM `timekeeper`
                                WHERE id={}""".format(id)
                sports_cursor.execute(sql_delete)
                sports_connection.commit()
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, surveysession_id, label,
                                time_start) VALUES({}, {}, '{}',
                                {})""".format(
                                              patients_id,
                                              sessionID,
                                              label,
                                              time_stamp
                                              )
                sports_cursor.execute(sql_insert)
                sports_connection.commit()
                self.stack.append(True)

    #  FTIMESTOP
    def f_time_stop(self):
        """Ends a named time record and returns the elapsed time since FTIMESTART.
        Writes time record to "timekeeper" table for later analysis"""
        label = self.stack.pop()
        sessionID = app.surveySessionID()
        patients_id = app.user_id()
        database = app.database_name()
        # Unix timestamp
        time_stamp = int(time.time())
        if database == 'psp_emory_hand':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, time_stop) VALUES({})""".format(
                                              id,
                                              time_stamp
                                              )
                hand_cursor.execute(sql_insert)
                hand_connection.commit()
                self.stack.append(True)
        if database == 'psp_emory_prp':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            prp_cursor.execute(sql)
            result = prp_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, time_stop) VALUES({})""".format(
                                              id,
                                              time_stamp
                                              )
                prp_cursor.execute(sql_insert)
                prp_connection.commit()
                self.stack.append(True)
        if database == 'psp_emory_inject':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            inject_cursor.execute(sql)
            result = inject_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, time_stop) VALUES({})""".format(
                                              id,
                                              time_stamp
                                              )
                inject_cursor.execute(sql_insert)
                inject_connection.commit()
                self.stack.append(True)
        if database == 'psp_emory_ortho':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            ortho_cursor.execute(sql)
            result = ortho_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, time_stop) VALUES({})""".format(
                                              id,
                                              time_stamp
                                              )
                ortho_cursor.execute(sql_insert)
                ortho_connection.commit()
                self.stack.append(True)
        if database == 'psp_emory_spine':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            spine_cursor.execute(sql)
            result = spine_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, time_stop) VALUES({})""".format(
                                              id,
                                              time_stamp
                                              )
                spine_cursor.execute(sql_insert)
                spine_connection.commit()
                self.stack.append(True)
        if database == 'psp_emory_sports':
            sql = """SELECT id from `timekeeper`
                    WHERE label='{}'
                    AND surveysession_id = {}""".format(
                                                        label,
                                                        sessionID
                                                        )
            sports_cursor.execute(sql)
            result = sports_cursor.fetchone()
            self.stack.append(result)
            if result is None:
                self.stack.append(False)
            else:
                id = result[0]
                sql_insert = """INSERT INTO `timekeeper`
                                (patients_id, time_stop) VALUES({})""".format(
                                              id,
                                              time_stamp
                                              )
                sports_cursor.execute(sql_insert)
                sports_connection.commit()
                self.stack.append(True)

    # Control Structures

    #  FIIF
    """Evaluate first parameter bool_val, return 2nd parameter if true,
        third parameter if false"""
    def f_fiif(self):
        f = self.stack.pop()
        t = self.stack.pop()
        b = self.stack.pop()
        if self.bool_eval(b) is True:
            self.stack.append(t)
        else:
            self.stack.append(f)

    #  FGOTO
    """Returns stack as is; no changes made"""
    def f_goto(self):
        no_change = self.stack.pop()
        self.stack.append(no_change)

    #  FGOIF
    def f_goif(self):
        """If bool_val is true, go to surveyScreenID
            Cbool_val|CsurveyScreenID|FGOIF"""
        surveyScreenID = self.stack.pop()
        bool_val = self.stack.pop()
        if self.bool_eval(bool_val) is True:
            q_alpha = surveyScreenID
            self.stack.append(q_alpha)
        else:
            self.stack.append(False)

    #  FDO
    """
    Action_name identitifies a tel string stored in the Do_Actions table
    (fdo_actions). FDO looks up the action, runs the tel script, and returns
    the last value on the stack. The function can be used recursively.
    (i.e. an action itself can contain a call to FDO another action)
        elif tel_str.upper() in (['FSYSTEM', 'FPRINT', 'FTODAY', 'FTIME', 'FCLONE', 'FHOME', 'FFINISH', 'FTRACE']) or \
                (tel_str.upper().startswith('C') and len(tel_str) > 3 and '|' in tel_str and not tel_str.endswith("|")):

    result.upper().startswith('C') and len(result) > 3 and '|' not in result and not tel_str.endswith("|")):
    """
    def f_do(self):
        act_name = self.stack.pop()
        if act_name is not None:
            sql = """SELECT tel_string from
                     fdo_actions where act_name = '{}'""".format(act_name)
            hand_cursor.execute(sql)
            result = hand_cursor.fetchone()
            if sql is not None:
                self.stack.append(result)
            else:
                result = 'No Do Action Found'

        #  FHOME

        # SpineChart-Specific Functions
        #

    def delValue(self):
        """
        Must pass in currentSessionID
        and varName in URI string parameters
        """
        currentSessionID = app.surveySessionID()
        varName = app.varName()
        sql = """SELECT id FROM SurveyResponses'
                WHERE f_surveysession_id = {}
                AND varName = '{}'""".format(
                                             currentSessionID,
                                             varName
                                             )

        hand_cursor.execute(sql)
        result = hand_cursor.fetchone()
        if result is not None:
            delete_record = """DELETE FROM SurveyResponses'
                                WHERE id = {}""".format(result)
            hand_cursor.execute(delete_record)
            hand_cursor.commit()
        else:
            self.stack.append(False)

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
