#!/usr/bin/python

from Tkinter import*
import time
import os
import subprocess
import numpy as np
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sys
plt.rcParams["figure.figsize"] = (4,2.4)

"""FUNCTIONS TO CALL"""
def fs():
    status.config(text="Waiting...")
    status.update()
    print idvar.get(), chanvar.get(), ratevar.get(), totvar.get(), trigvar.get(), counter.get(),
    counter.set(counter.get() + 1)
    f = open('count.txt', 'w')
    f.write(str(counter.get()))
    f.close()

    #os.system('python ./mcc/finite_scan.py')

    Plot()
    #Window2()
    time.sleep(5)
    status.config(text="Finished...")
    status.update()


def cs():
    subprocess.call('python ./mcc/continuous_scan.py')

def fswt():
    os.system('python ./mcc/finite_scan_with_trigger.py')

def Qf():
    print('Quit')

"""FRAMES"""
root = Tk()
root.title("DAQ Launcher")
root.minsize(800,400)

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=5)

control = Frame(root, borderwidth=2, relief=RAISED)
control.grid_columnconfigure(0, weight=1)
control.grid(row=0, column=0, sticky=N+S+E+W)

inout = Frame(root, bg='yellow')
inout.grid(row=1, column=0, sticky=N+S+E+W)

inout.grid_columnconfigure(0, weight=1)
inout.grid_columnconfigure(1, weight=3)
inout.grid_rowconfigure(0, weight=1)

f1 = Frame(control)
f1.grid(row=0, column=0)

f2 = Frame(inout, borderwidth=2, relief=RAISED)
f2.grid(row=0, column=0, sticky=W+E+N+S)
f2.grid_columnconfigure(0, weight=1)
f2.grid_columnconfigure(3, weight=1)
f2.grid_rowconfigure(0, weight=1)
f2.grid_rowconfigure(8, weight=1)

f3 = Frame(inout, relief=RAISED)
f3.grid(row=0, column=1, sticky=W+E+N+S)
f3.grid_columnconfigure(0, weight=1)
f3.grid_columnconfigure(2, weight=1)
f3.grid_rowconfigure(0, weight=1)
f3.grid_rowconfigure(3, weight=1)

f4 = Frame(f3)
f4.grid(row=3, column=1, sticky=W+E+N+S)
f4.grid_columnconfigure(0, weight=1)
f4.grid_columnconfigure(5, weight=1)
f4.grid_rowconfigure(0, weight=1)
f4.grid_rowconfigure(3, weight=1)

""""VARIABLES"""
idvar = StringVar()
chanvar = StringVar()
ratevar = StringVar()
totvar = StringVar()
trigvar = StringVar()
counter = IntVar()
idvar.set(1)
chanvar.set(1)
ratevar.set(4000)
totvar.set(1000)
trigvar.set("TriggerModes.RISING_EDGE")
f = open("count.txt", "r")
counter.set(f.read())

"""INPUTS"""
idin = OptionMenu(f2, idvar, 1, 2, 3, 4, 5, 6, 7, 8)
idin.grid(row=1, column=2, padx=20, pady=10)
chanin = OptionMenu(f2, chanvar, 1, 2, 3, 4, 5, 6, 7, 8)
chanin.grid(row=2, column=2, padx=20, pady=10)
ratein = OptionMenu(f2, ratevar, 500, 1000, 2000, 4000, 8000)
ratein.grid(row=3, column=2, padx=20, pady=10)
totin = OptionMenu(f2, totvar, 500, 1000, 2000, 5000, 10000)
totin.grid(row=4, column=2, padx=20, pady=10)
trigin1 = Radiobutton(f1, text="Trigger Rising", variable=trigvar, value="TriggerModes.RISING_EDGE")
trigin2 = Radiobutton(f1, text="Trigger Falling", variable=trigvar, value="TriggerModes.FALLING_EDGE")
trigin1.grid(row=1, column=2)
trigin2.grid(row=2, column=2)
counterin = Entry(f1, textvariable=counter)
counterin.grid(row=2, column=3)

"""LABELS"""
idlab = Label(f2, text="DataBox ID")
idlab.grid(row=1, column=1)
chanlab = Label(f2, text="Number of channels")
chanlab.grid(row=2, column=1)
ratelab = Label(f2, text="Sample rate (Hz)")
ratelab.grid(row=3, column=1)
totlab = Label(f2, text="Sample duration (ms)")
totlab.grid(row=4, column=1)
counterlab = Label(f1, text="Starting Cycle Count")
counterlab.grid(row=1, column=3)
statuslab = Label(f1, text="Scanner Status:")
statuslab.grid(row=1, column=0, columnspan=2)
status = Label(f1, text="Ready...", fg='red', bg='white', relief=SUNKEN, width=10)
status.grid(row=2, column=0, columnspan=2)
LabelForce = Label(f3, text="Force (kN)")
LabelForce.grid(row=0, column=1)
LabelTemp1 = Label(f4, text="Bearing Temp (C)")
LabelTemp1.grid(row=1, column=1)
LabelTemp2 = Label(f4, text="Motor Temp (C)")
LabelTemp2.grid(row=1, column=2)
LabelTemp3 = Label(f4, text="Ambient Temp (C)")
LabelTemp3.grid(row=1, column=3)
LabelTemp4 = Label(f4, text="Aux Temp (C)")
LabelTemp4.grid(row=1, column=4)
ResultForce = Label(f3, text="Force", fg='red', bg='white', relief=SUNKEN, width=10)
ResultForce.grid(row=1, column=1)
ResultTemp1 = Label(f4, text="Temp", fg='red', bg='white', relief=SUNKEN, width=10)
ResultTemp1.grid(row=2, column=1)
ResultTemp2 = Label(f4, text="Temp", fg='red', bg='white', relief=SUNKEN, width=10)
ResultTemp2.grid(row=2, column=2)
ResultTemp3 = Label(f4, text="Temp", fg='red', bg='white', relief=SUNKEN, width=10)
ResultTemp3.grid(row=2, column=3)
ResultTemp4 = Label(f4, text="Temp", fg='red', bg='white', relief=SUNKEN, width=10)
ResultTemp4.grid(row=2, column=4)

"""LAUNCHER BUTTONS"""
finitebutton = Button(f1, text="Finite Scan", command=fs)
finitebutton.grid(row=0, column=0, pady=10)

continuousbutton = Button(f1, text="Continuous Scan", command=fs)
continuousbutton.grid(row=0, column=1, pady=10)

fcwtbutton = Button(f1, text="Finite Scan w/Trigger", command=fs)
fcwtbutton.grid(row=0, column=2, pady=10)

fcwtlbutton = Button(f1, text="Looped Triggered Scan", command=fs)
fcwtlbutton.grid(row=0, column=3, pady=10)

quitbutton = Button(f1, text="Quit", command=Qf)
quitbutton.grid(row=0, column=4, pady=10)

root.mainloop()