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
idvar = StringVar()
chanvar = StringVar()
ratevar = StringVar()
totvar = StringVar()
"""FUNCTIONS TO CALL"""
def fs():
    print(idvar.get(), chanvar.get(), ratevar.get(), totvar.get())
    #os.system('python ./mcc/finite_scan.py')
    Window2()

def cs():
    subprocess.call('python ./mcc/continuous_scan.py')

def fswt():
    os.system('python ./mcc/finite_scan_with_trigger.py')

"""INPUTS"""
idin = OptionMenu(f2, idvar, 1, 2, 3, 4, 5, 6, 7, 8)
idin.grid(row=0, column=1, padx=20, pady=10)
chanin = OptionMenu(f2, chanvar, 1, 2, 3, 4, 5, 6, 7, 8)
chanin.grid(row=1, column=1, padx=20, pady=10)
ratein = OptionMenu(f2, ratevar, 500, 1000, 2000, 4000, 8000)
ratein.grid(row=2, column=1, padx=20, pady=10)
totin = OptionMenu(f2, totvar, 500, 1000, 2000, 5000, 10000)
totin.grid(row=3, column=1, padx=20, pady=10)

"""LAUNCHER BUTTONS"""
finitebutton = Button(f1, text="Finite Scan", command=fs)
finitebutton.config(font=("Helvetica", 16))
finitebutton.grid(row=0, column=0, pady=10)

continuousbutton = Button(f1, text="Continuous Scan", command=cs)
continuousbutton.config(font=("Helvetica", 16))
continuousbutton.grid(row=0, column=1, pady=10)

fcwtbutton = Button(f1, text="Finite Scan w/Trigger", command=fswt)
fcwtbutton.config(font=("Helvetica", 16))
fcwtbutton.grid(row=0, column=2, pady=10)

"""LABELS"""

idlab = Label(f2, text="DataBox ID")
idlab.config(font=("Helvetica", 16))
idlab.grid(row=0, column=0)
chanlab = Label(f2, text="Number of channels")
chanlab.config(font=("Helvetica", 16))
chanlab.grid(row=1, column=0)
ratelab = Label(f2, text="Sample rate (Hz)")
ratelab.config(font=("Helvetica", 16))
ratelab.grid(row=2, column=0)
totlab = Label(f2, text="Sample duration (ms)")
totlab.config(font=("Helvetica", 16))
totlab.grid(row=3, column=0)

def Window2():
    root2 = Tk()
    root2.title("Window 2")

    Label2 = Label(root2,text=ratevar.get() ,width=60)
    Label2.grid(row=0, column=0)

    root2.mainloop()

root.mainloop()