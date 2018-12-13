#!/usr/bin/python
#
import pyodbc

print('Connecting to database...\n')

con = pyodbc.connect("DSN=RIVWARE;UID=dataguys;PWD=dataguys;TDS_Version=4.2")

print(con)

