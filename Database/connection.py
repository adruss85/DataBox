#!/usr/bin/python
#
import pyodbc
import datetime

print('Connecting to database...\n')

con = pyodbc.connect("DSN=RIVWARE;UID=dataguys;PWD=dataguys;TDS_Version=4.2")
cursor = con.cursor()
print(con)
print('Connected')

now =  datetime.datetime.now()
print(now)

ID = '1'
Temp = '23'
Force = '32.4324'

cursor.execute("INSERT INTO dbo.Data ([Date Time], ID, Force, Temperature) VALUES (?, ?, ?, ?)", now, ID, Force, Temp) 
con.commit()

con.close()
