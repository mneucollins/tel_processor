import unittest

import processor
from tel import Tel


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
    import pymysql
    import config.database as database
    global _cnx
    _cnx = pymysql.connect(**database.pop_user_cx)

    def test_bool_eval(self):
        self.assertTrue(Tel([]).bool_eval(True))
        self.assertTrue(Tel([]).bool_eval("True"))
        self.assertTrue(Tel([]).bool_eval("1"))
        self.assertTrue(Tel([]).bool_eval(1))
        self.assertFalse(Tel([]).bool_eval(False))
        self.assertFalse(Tel([]).bool_eval("False"))
        self.assertFalse(Tel([]).bool_eval("0"))
        self.assertFalse(Tel([]).bool_eval(0))

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

    def test_f_patset(self):
        # setup
        with _cnx.cursor() as cursor:
            # setup
            cursor.execute('INSERT INTO `users` (`id`, `group_id`, `username`) VALUES(-10001, 0, "tester")')
            cursor.execute('INSERT INTO `patients` (`user_id`,`user1`) VALUES (-10001, "testing")')

        self.assertTrue(Tel(['']).f_patset(-10001).pop())

        with _cnx.cursor() as cursor:
            # grab the value and cleanup the test records
            cursor.execute('SELECT `user1` FROM `patients` WHERE user_id = -10001')
            result = cursor.fetchone()
            cursor.execute('DELETE FROM `users` WHERE `id` = -10001')
            cursor.execute('DELETE FROM `patients` WHERE `user_id`= -10001')

        self.assertEqual(result[0], 'testing')


if __name__ == "__main__":
    unittest.main()
