#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymysql
import config.database as database

# connection = pymysql.connect(host='localhost', user='beta3_user', password = 'ym0|{NvH|tow:c<oft#}{', db = 'psp_beta3')
connection = pymysql.connect(**database.pop_user_cx)

with connection.cursor() as cursor:
    sql = "SELECT * FROM `patients` WHERE `id`=%s"
    cursor.execute(sql, (1,))
    result = cursor.fetchone()
    print(result)
connection.close()
