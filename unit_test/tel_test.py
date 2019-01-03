import unittest
# import pymysql
import mysql.connector
from mysql.connector import errorcode

# from pymysql.connections import Connection

import config.database as database
import processor
from tel import Tel

_cnx = mysql.connector.connect(**database.pop_user)


class ProcessorTest(unittest.TestCase):
    def test_is_simple_tel(self):
        """ simple_tel should return true if text is a valid tel string only"""
        self.assertTrue(processor.is_simple_tel("[c1|c2|p=]"))
        self.assertTrue(processor.is_simple_tel("c1|c2|p="))
        self.assertTrue(processor.is_simple_tel("c1|c2|p=".upper()))
        self.assertTrue(processor.is_simple_tel("ftoday"))
        self.assertTrue(processor.is_simple_tel("ftoday".upper()))
        self.assertFalse(processor.is_simple_tel(""))
        self.assertFalse(processor.is_simple_tel("aosirt|u"))
        self.assertFalse(processor.is_simple_tel("[aosirt|u"))
        self.assertFalse(processor.is_simple_tel("aosir[c1|c2|p=]"))
        self.assertFalse(processor.is_simple_tel("C|"))

    def test_tel_evaluate(self):
        self.assertEqual(processor.tel_evaluate("[c1|c1|p=]"), False)


class TelTest(unittest.TestCase):

    def test_bool_eval(self):
        self.assertTrue(Tel([]).bool_eval(True))
        self.assertTrue(Tel([]).bool_eval("True"))
        self.assertTrue(Tel([]).bool_eval("1"))
        self.assertTrue(Tel([]).bool_eval(1))
        self.assertFalse(Tel([]).bool_eval(False))
        self.assertFalse(Tel([]).bool_eval("False"))
        self.assertFalse(Tel([]).bool_eval("0"))
        self.assertFalse(Tel([]).bool_eval(0))

    # def test_matches(self):
    #     self.assertEqual(Tel[].matches('no_tbl', 'no_fld', 'no_val').pop, "err:matches:")

    def test_p_equal_to(self):
        self.assertEqual(Tel(["1"]).p_equal_to().pop(), "err:p_equal_to:too few parameters")

        self.assertTrue(Tel(["1", "1"]).p_equal_to().pop())
        self.assertTrue(Tel([True, 1]).p_equal_to().pop())
        self.assertTrue(Tel([False, 0]).p_equal_to().pop())

        self.assertFalse(Tel(["1", "0"]).p_equal_to().pop())
        self.assertFalse(Tel([True, 0]).p_equal_to().pop())
        self.assertFalse(Tel([False, 1]).p_equal_to().pop())

        self.assertFalse(Tel([True, "1"]).p_equal_to().pop())
        self.assertFalse(Tel([False, "0"]).p_equal_to().pop())

    def test_p_not_equal_to(self):
        self.assertEqual(Tel([1]).p_not_equal_to().pop(), "err:p_not_equal_to:too few parameters")

        self.assertFalse(Tel(["1", "1"]).p_not_equal_to().pop())
        self.assertFalse(Tel([True, 1]).p_not_equal_to().pop())
        self.assertFalse(Tel([False, 0]).p_not_equal_to().pop())

        self.assertTrue(Tel(["1", "0"]).p_not_equal_to().pop())
        self.assertTrue(Tel([True, 0]).p_not_equal_to().pop())
        self.assertTrue(Tel([False, 1]).p_not_equal_to().pop())

        self.assertTrue(Tel([True, "1"]).p_not_equal_to().pop())
        self.assertTrue(Tel([False, "0"]).p_not_equal_to().pop())

    def test_p_less_than(self):
        self.assertEqual(Tel([1]).p_less_than().pop(), "err:p_less_than:too few parameters")

        self.assertTrue(Tel([0, 1]).p_less_than().pop())
        self.assertTrue(Tel(["0", "1"]).p_less_than().pop())
        self.assertTrue(Tel([False, True]).p_less_than().pop())

        self.assertFalse(Tel(["0", "0"]).p_less_than().pop())
        self.assertFalse(Tel([1, 1]).p_less_than().pop())
        self.assertFalse(Tel([1, 0]).p_less_than().pop())
        self.assertFalse(Tel(["1", "0"]).p_less_than().pop())

    def test_p_greater_than(self):
        self.assertEqual(Tel([1]).p_greater_than().pop(), "err:p_greater_than:too few parameters")
        self.assertFalse(Tel([0, 1]).p_greater_than().pop())
        self.assertFalse(Tel(["0", "1"]).p_greater_than().pop())
        self.assertFalse(Tel(["0", "0"]).p_greater_than().pop())
        self.assertFalse(Tel([1, 1]).p_greater_than().pop())

        self.assertTrue(Tel([1, 0]).p_greater_than().pop())
        self.assertTrue(Tel(["1", "0"]).p_greater_than().pop())
        self.assertTrue(Tel([True, False]).p_greater_than().pop())

    def test_p_logical_and(self):
        self.assertEqual(Tel([1]).p_logical_and().pop(), "err:p_logical_and:too few parameters")

        self.assertTrue(Tel([True, True]).p_logical_and().pop())
        self.assertTrue(Tel([True, 1]).p_logical_and().pop())
        self.assertTrue(Tel([True, "1"]).p_logical_and().pop())

        self.assertFalse(Tel([True, False]).p_logical_and().pop())
        self.assertFalse(Tel([True, 0]).p_logical_and().pop())
        self.assertFalse(Tel([True, "0"]).p_logical_and().pop())

    def test_p_logical_or(self):
        self.assertEqual(Tel([1]).p_logical_or().pop(), "err:p_logical_or:too few parameters")

        self.assertTrue(Tel([True, True]).p_logical_or().pop())
        self.assertTrue(Tel([True, 1]).p_logical_or().pop())
        self.assertTrue(Tel([True, "1"]).p_logical_or().pop())

        self.assertTrue(Tel([True, False]).p_logical_or().pop())
        self.assertTrue(Tel([True, 0]).p_logical_or().pop())
        self.assertTrue(Tel([True, "0"]).p_logical_or().pop())

        self.assertFalse(Tel([False, False]).p_logical_or().pop())
        self.assertFalse(Tel([False, 0]).p_logical_or().pop())
        self.assertFalse(Tel([False, "0"]).p_logical_or().pop())

    def test_p_logical_not(self):
        # not enough parameters to evaluate
        self.assertEqual(Tel([]).p_logical_not().pop(), "err:p_logical_not:too few parameters")

        # booleans
        self.assertTrue(Tel([False]).p_logical_not().pop())
        self.assertFalse(Tel([True]).p_logical_not().pop())

        # interpreting strings as boolean
        self.assertTrue(Tel(["False",]).p_logical_not().pop())
        self.assertFalse(Tel(["True",]).p_logical_not().pop())

        # interpreting 0 and 1 as boolean
        self.assertTrue(Tel([0]).p_logical_not().pop())
        self.assertFalse(Tel([1]).p_logical_not().pop())

        # handling other non-boolean conditions
        self.assertEqual(Tel([1234]).p_logical_not().pop(),"err:bool_eval:cannot convert '1234' to boolean")
        self.assertEqual(Tel(["Random Text"]).p_logical_not().pop(), "err:bool_eval:cannot convert 'Random Text' to boolean")
        

    def test_a_multiply(self):
        self.assertEqual(Tel([1]).a_multiply().pop(), "err:a_multiply:too few parameters")
        self.assertEqual(Tel(["1", "a"]).a_multiply().pop(), "err:a_multiply:non-numeric parameter")
        self.assertEqual(Tel(["1", "2"]).a_multiply().pop(), 2)
        self.assertEqual(Tel(["1.5", "2"]).a_multiply().pop(), 3)
        self.assertEqual(Tel([2, 2]).a_multiply().pop(), 4)

    def test_a_add(self):
        self.assertEqual(Tel([1]).a_add().pop(), "err:a_add:too few parameters")
        self.assertEqual(Tel(["1", "a"]).a_add().pop(), "err:a_add:non-numeric parameter")
        self.assertEqual(Tel(["1", "2"]).a_add().pop(), 3)
        self.assertEqual(Tel(["1.5", "2"]).a_add().pop(), 3.5)
        self.assertEqual(Tel([2, 2]).a_add().pop(), 4)
        self.assertEqual(Tel([1, -1]).a_add().pop(), 0)

    def test_a_subtract(self):
        self.assertEqual(Tel([1]).a_subtract().pop(), "err:a_subtract:too few parameters")
        self.assertEqual(Tel(["1", "a"]).a_subtract().pop(), "err:a_subtract:non-numeric parameter")
        self.assertEqual(Tel(["1", "2"]).a_subtract().pop(), -1)
        self.assertEqual(Tel(["1.5", "2"]).a_subtract().pop(), -.5)
        self.assertEqual(Tel([2, 2]).a_subtract().pop(), 0)
        self.assertEqual(Tel([1, -1]).a_subtract().pop(), 2)

    def test_a_divide(self):
        self.assertEqual(Tel([1]).a_divide().pop(), "err:a_divide:too few parameters")
        self.assertEqual(Tel(["1", "a"]).a_divide().pop(), "err:a_divide:non-numeric parameter")
        self.assertEqual(Tel([1, 0]).a_divide().pop(), "err:a_divide:divide by zero error")
        self.assertEqual(Tel([1, False]).a_divide().pop(), "err:a_divide:divide by zero error")
        self.assertEqual(Tel(["4", "2"]).a_divide().pop(), 2)
        self.assertEqual(Tel([1, 2]).a_divide().pop(), .5)
        self.assertEqual(Tel([-1, 2]).a_divide().pop(), -.5)
        self.assertEqual(Tel([-1, -2]).a_divide().pop(), .5)
        self.assertEqual(Tel([1, -2]).a_divide().pop(), -.5)

    def test_f_cat(self):
        self.assertEqual(Tel([1]).f_cat().pop(), "err:f_cat:too few parameters")
        str_a = "Hello "
        str_b = "World"
        self.assertEqual(len(Tel([str_a, str_b]).f_cat().pop()), 11)
        self.assertEqual(Tel([str_a, str_b]).f_cat().pop(), "Hello World")
        a = 123
        b = 456
        self.assertEqual(Tel([a, b]).f_cat().pop(), "123456")
        self.assertEqual(Tel(["", "no error"]).f_cat().pop(), "no error")

    def test_f_length(self):
        self.assertEqual(Tel(['']).f_length().pop(), 0)
        self.assertEqual(Tel([]).f_length().pop(), 0)
        self.assertEqual(Tel(["The end of the world as we know it"]).f_length().pop(), 34)
        self.assertEqual(Tel([0]).f_length().pop(), 1)
        self.assertEqual(Tel([123]).f_length().pop(), 3)
        self.assertEqual(Tel([-123]).f_length().pop(), 4)
        # don't think I will test explicit booleans True and False

    def test_f_mid(self):
        self.assertEqual(Tel(['']).f_mid().pop(), "err:f_mid:too few parameters")
        self.assertEqual(Tel(['1', '2']).f_mid().pop(), "err:f_mid:too few parameters")
        self.assertEqual(Tel([1, 2, 3]).f_mid().pop(), "err:f_mid:first parameter is not a string")
        self.assertEqual(Tel(['Hello', 'World', 3]).f_mid().pop(), "err:f_mid:non-numeric parameter start")
        self.assertEqual(Tel(['Hello', 3, 'World']).f_mid().pop(), "err:f_mid:non-numeric parameter length")
        self.assertEqual(Tel(['Hello', 0, 5]).f_mid().pop(), "err:f_mid:invalid start parameter")
        self.assertEqual(Tel(['Hello', 6, 5]).f_mid().pop(), "err:f_mid:invalid start parameter")
        self.assertEqual(Tel(['Hello World', 7, 3]).f_mid().pop(), "Wor")
        self.assertEqual(Tel(['Hello World', "2", "4"]).f_mid().pop(), "ello")

    def test_f_find(self):
        self.assertEqual(Tel(['']).f_find().pop(), "err:f_find:too few parameters")
        self.assertEqual(Tel(['1']).f_find().pop(), "err:f_find:too few parameters")
        self.assertEqual(Tel([54321, 1]).f_find().pop(), "err:f_find:first parameter is not a string")
        self.assertEqual(Tel(["abcde", 1]).f_find().pop(), 0)
        self.assertEqual(Tel(["abcde", "c"]).f_find().pop(), 3)

    def test_f_replace(self):
        self.assertEqual(Tel(['']).f_replace().pop(), "err:f_replace:too few parameters")
        self.assertEqual(Tel(['Base String', '']).f_replace().pop(), "err:f_replace:too few parameters")
        self.assertEqual(Tel(['Base String', 'Find Str', '']).f_replace().pop(), "Base String")
        self.assertEqual(Tel([12345, '3', '5']).f_replace().pop(), "err:f_replace:first parameter is not a string")
        self.assertEqual(Tel(['12345', '3', '5']).f_replace().pop(), "12545")
        self.assertEqual(Tel(['12345345', '345', '78']).f_replace().pop(), "127878")
        self.assertEqual(Tel(['Base String', 'Find Str', 'Replace Str']).f_replace().pop(), "Base String")
        self.assertEqual(Tel(['Base String', 'Base', 'Replaced']).f_replace().pop(), "Replaced String")

    def test_f_today(self):
        import datetime
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        self.assertEqual(Tel([]).f_today().pop(), today)

    def test_f_time(self):
        # a somewhat trivial test, actually just makes sure the stack is loaded with current datetime
        from datetime import datetime
        time = datetime.now().replace(microsecond=0).isoformat(' ')
        self.assertEqual(Tel([]).f_time().pop(), time)

    def test_f_timestamp(self):
        # uses isclose function to avoid errors due to microseconds delay and comparing floats for equality
        from math import isclose
        from datetime import datetime
        ts1 = datetime.now().timestamp()
        ts2 = Tel([]).f_timestamp().pop()
        # print("to compare:",ts1, ts2)
        self.assertTrue(isclose(ts1, ts2, rel_tol=1e-03))

    def test_f_dateadd(self):
        self.assertEqual(Tel(['']).f_dateadd().pop(), 'err:f_dateadd:too few parameters (need 2)')
        self.assertEqual(Tel(['2018-07-02']).f_dateadd().pop(), 'err:f_dateadd:too few parameters (need 2)')
        self.assertEqual(Tel([2.3, '2018-07-01']).f_dateadd().pop(),
                         'err:f_date_add: first parameter, "2.3", must be an integer (number of days)')
        self.assertEqual(Tel(['2', '2018']).f_dateadd().pop(),
                         'err:f_date_add:second parameter, "2018", '
                         'is not a valid date in the proper format YYYY-MM-DD')
        self.assertEqual(Tel(['2', '2018-30-12']).f_dateadd().pop(),
                         'err:f_date_add:second parameter, "2018-30-12", '
                         'is not a valid date in the proper format YYYY-MM-DD')

        self.assertEqual(Tel(['2', '2018-07-02']).f_dateadd().pop(), "2018-07-04")
        self.assertEqual(Tel(['-2', '2018-07-02']).f_dateadd().pop(), "2018-06-30")

    def test_f_datediff(self):
        self.assertEqual(Tel(['']).f_datediff().pop(),
                         "err:f_datediff:too few parameters (need 2)")
        self.assertEqual(Tel(['2018-07-02']).f_datediff().pop(),
                         "err:f_datediff:too few parameters (need 2)")
        self.assertEqual(Tel(['2017-01-01', '2018']).f_datediff().pop(),
                         'err:f_date_diff: both parameters, "2017-01-01", "2018", '
                         'must be valid dates in the format YYYY-MM-DD')
        self.assertEqual(Tel(['2017', '2018-01-01']).f_datediff().pop(),
                         'err:f_date_diff: both parameters, "2017", "2018-01-01", '
                         'must be valid dates in the format YYYY-MM-DD')
        self.assertEqual(Tel(['2016-01-01', '2017-01-01']).f_datediff().pop(), 366)
        self.assertEqual(Tel(['2017-01-01', '2018-01-01']).f_datediff().pop(), 365)
        self.assertEqual(Tel(['2018-07-04', '2018-07-03']).f_datediff().pop(), -1)

    def test_f_dow(self):
        self.assertEqual(Tel([]).f_dow().pop(),
                         'err:f_dow:too few parameters (need 1)')
        self.assertEqual(Tel(['2018']).f_dow().pop(),
                         'err:f_dow: parameter "2018" is not a valid date in format YYYY-MM-DD')
        self.assertEqual(Tel(['2018-07-03']).f_dow().pop(), 'Tue')

    def test_f_dateformat(self):
        self.assertEqual(Tel([]).f_dateformat().pop(),
                         'err:f_dateformat:too few parameters (need 2)')
        self.assertEqual(Tel(['2018', '%m/%d/%Y']).f_dateformat().pop(),
                         'err:f_dateformat: parameter "2018" is not a valid date in format YYYY-MM-DD')
        self.assertEqual(Tel(['2018-07-03', '%m/%d/%Y']).f_dateformat().pop(), '07/03/2018')
        self.assertEqual(Tel(['2018-07-03', '%a, %b %d, %Y']).f_dateformat().pop(), 'Tue, Jul 03, 2018')

    def pat_setup(self):
        # common setup for functions patset, patget, patxget, and patxset
        global _cnx
        cursor = _cnx.cursor()
        try:
            cursor.execute("INSERT INTO `users` (`id`, `group_id`, `username`) VALUES(-10001, 0, 'tester')")
            cursor.execute("INSERT INTO `patients` (id, `user_id`,`user1`) VALUES (-10000, -10001, 'testing')")
            cursor.execute("INSERT INTO `patients_extended` (`f_patientsID`,`field_name`, `field_value`) "
                           "VALUES (-10000, 'testfieldname', 'testfieldvalue')")
            _cnx.commit()
        except mysql.connector.Error as err:
            self.db_error(err)
        finally:
            cursor.close()

    def pat_teardown(self):
        # common teardown for functions patset, patget, patxget, and patxset
        global _cnx
        cursor = _cnx.cursor()

        try:
            cursor.execute("DELETE FROM users WHERE users.id = -10001")
            cursor.execute("DELETE FROM patients WHERE patients.id = -10000")
            cursor.execute("DELETE FROM patients_extended WHERE patients_extended.f_patientsID = -10000")
            _cnx.commit()
        except mysql.connector.Error as err:
            self.db_error(err)
        finally:
            cursor.close() 


    def test_f_patset(self):
        # run teardown to remove artifacts from any previous failed test
        self.pat_teardown()
        # setup
        self.pat_setup()
        # test
        self.assertEqual(Tel([]).f_patset(-10001).pop(), "err:f_patset:too few parameters (need 2)")
        self.assertEqual(Tel(['user1']).f_patset(-10001).pop(), "err:f_patset:too few parameters (need 2)")
        self.assertEqual(Tel(['fiddlesticks', 'dum_de_dum']).f_patset(-10001).pop(),
                         'err:f_patset: fieldname "fiddlesticks" is not in the patients table')
        self.assertEqual(Tel(['fiddlesticks', 'dum_de_dum']).f_patset(-10002).pop(),
                         'err:f_patset: user "-10002" was not found in patients table')
        
        #successful update returns true
        self.assertTrue(Tel(['user1', 'tested']).f_patset(-10001).pop())
        # test that the user1 value has actually been updated
        cursor = _cnx.cursor()
        try:
            cursor.execute('SELECT `user1` FROM `patients` WHERE user_id = -10001')
            result = cursor.fetchone()
            self.assertEqual(result[0], 'tested')
        except mysql.connector.Error as err:
            self.db_error(err)
        finally:
            cursor.close()

        self.pat_teardown()

    def test_f_patget(self):
        # run teardown to remove artifacts from any previous failed test
        self.pat_teardown()
        # setup
        self.pat_setup()

        # test
        self.assertEqual(Tel([]).f_patget(-10001).pop(), "err:f_patget:missing fieldname parameter")
        self.assertEqual(Tel(['fiddlesticks']).f_patget(-10001).pop(),
                         'err:f_patget: fieldname "fiddlesticks" is not in the patients table')
        self.assertEqual(Tel(['user1']).f_patget(-10002).pop(),
                         'err:f_patget: user "-10002" was not found in patients table')
        self.assertEqual(Tel(['user1']).f_patget(-10001).pop(), 'testing')

        # cleanup
        self.pat_teardown()
    
    
    @staticmethod
    def db_error(err):
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


'''
    def test_f_patxget(self):
        # run teardown to remove artifacts from any previous failed test
        self.pat_teardown()

        # setup
        self.pat_setup()

        # test
        self.assertEqual(Tel(['']).f_patxget(-10001).pop(), "err:f_patxget:too few parameters (need 1)")
        self.assertFalse(Tel(['testfieldname']).f_patxget(-10002).pop())  # non-existent patient
        self.assertFalse(Tel(['badfieldname']).f_patxget(-10001).pop(), False)
        self.assertEqual(Tel(['testfieldname']).f_patxget(-10001).pop(), 'testfieldvalue')

        # teardown
    #    self.pat_teardown()

    def test_f_patxset(self):
        # run teardown to remove artifacts from any previous failed test
        self.pat_teardown()

        # setup
        self.pat_setup()
        self.assertEqual(Tel(['']).f_patxget(-10001).pop(), "err:f_patxset:too few parameters (need 2)")
        self.assertEqual(Tel(['testfieldname']).f_patxset(-10001).pop(), "err:f_patxset:too few parameters (need 2)")

        # test existing value: run the function then test the value using f_patxget
        # first make sure there is no current patx fieldname 'newfieldname
        self.assertFalse(Tel(['newfieldname']).fpatxget(-10001).pop())
        Tel(['testfieldname', 'updatedvalue']).f_patxset(-10001).pop()
        self.assertEqual(Tel(['testfieldname']).f_patxget(-10001).pop(), 'updatedvalue')

        # existing value run the function then test the value using f_patxget

        # test

        # teardown
        self.pat_teardown()
'''

if __name__ == "__main__":
    unittest.main()
