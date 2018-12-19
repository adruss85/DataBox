#!/usr/bin/python

from Tkinter import*
import os
import subprocess
import sys

"""FRAMES"""
root = Tk()
root.title("DAQ Launcher")

f1 = Frame(root, width=400, height=80)
f1.pack(side=TOP)

f2 = Frame(root, width=400, height=100)
f2.pack(side=BOTTOM)

""""VARIABLES"""
idvar = 1
chanvar = StringVar()
ratevar = StringVar()
totvar = StringVar()

"""FUNCTIONS TO CALL"""
def fs():
    print(idvar.get(), chanvar.get(), ratevar.get(), totvar.get())
    #os.system('python ./mcc/finite_scan.py')

def cs():
    subprocess.call('python ./mcc/continuous_scan.py')

def fswt():
    os.system('python ./mcc/finite_scan_with_trigger.py')

"""LAUNCHER BUTTONS"""
finitebutton = Button(f1, text="Finite Scan", command=fs)
finitebutton.grid(row=0, column=0, pady=10)

continuousbutton = Button(f1, text="Continuous Scan", command=cs)
continuousbutton.grid(row=0, column=1, pady=10)

fcwtbutton = Button(f1, text="Finite Scan w/Trigger", command=fswt)
fcwtbutton.grid(row=0, column=2, pady=10)

"""INPUTS"""
idin = Label(f2, text=idvar, justify='center')
idin.grid(row=0, column=1, padx=20, pady=10)
chanin = Entry(f2, textvariable=chanvar, justify='center')
chanin.grid(row=1, column=1, padx=20, pady=10)
ratein = Entry(f2, textvariable=ratevar, justify='center')
ratein.grid(row=2, column=1, padx=20, pady=10)
totin = Entry(f2, textvariable=totvar, justify='center')
totin.grid(row=3, column=1, padx=20, pady=10)

"""LABELS"""

idlab = Label(f2, text="DataBox ID")
idlab.grid(row=0, column=0)
chanlab = Label(f2, text="Number of channels")
chanlab.grid(row=1, column=0)
ratelab = Label(f2, text="Sample rate (Hz)")
ratelab.grid(row=2, column=0)
totlab = Label(f2, text="Samples per channel")
totlab.grid(row=3, column=0)

root.mainloop()