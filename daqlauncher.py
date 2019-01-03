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
plt.rcParams["figure.figsize"] = (3.2,2.4)

"""FRAMES"""
root = Tk()
root.title("DAQ Launcher")

f1 = Frame(root, width=400, height=80)
f1.pack(side=TOP)

f2 = Frame(root, width=400, height=100)
f2.pack(side=LEFT)

f3 = Frame(root, width=400, height=100)
f3.pack(side=RIGHT)

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

"""FUNCTIONS TO CALL"""
def fs():
    status.config(text="Running...")
    status.update()
    print idvar.get(), chanvar.get(), ratevar.get(), totvar.get(), trigvar.get(), counter.get(),
    counter.set(counter.get() + 1)
    f = open('count.txt', 'w')
    f.write(str(counter.get()))
    f.close()

    #os.system('python ./mcc/finite_scan.py')

    Plot()
    #Window2()
    time.sleep(2)
    status.config(text="Finished...")
    status.update()



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
trigin1 = Radiobutton(f1, text="Trigger Rising", variable=trigvar, value="TriggerModes.RISING_EDGE")
trigin2 = Radiobutton(f1, text="Trigger Falling", variable=trigvar, value="TriggerModes.FALLING_EDGE")
trigin1.grid(row=1, column=2)
trigin2.grid(row=2, column=2)
counterin = Entry(f1, textvariable=counter)
counterin.grid(row=2, column=3)


"""LAUNCHER BUTTONS"""
finitebutton = Button(f1, text="Finite Scan", command=fs)
finitebutton.config(font=("Helvetica", 16))
finitebutton.grid(row=0, column=0, pady=10)

continuousbutton = Button(f1, text="Continuous Scan", command=fs)
continuousbutton.config(font=("Helvetica", 16))
continuousbutton.grid(row=0, column=1, pady=10)

fcwtbutton = Button(f1, text="Finite Scan w/Trigger", command=fs)
fcwtbutton.config(font=("Helvetica", 16))
fcwtbutton.grid(row=0, column=2, pady=10)

fcwtlbutton = Button(f1, text="Looped Triggered Scan", command=fs)
fcwtlbutton.config(font=("Helvetica", 16))
fcwtlbutton.grid(row=0, column=3, pady=10)


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
counterlab = Label(f1, text="Starting Cycle Count")
counterlab.config(font=("Helvetica", 16))
counterlab.grid(row=1, column=3)
statuslab = Label(f1, text="Scanner Status:")
statuslab.config(font=("Helvetica", 16))
statuslab.grid(row=1, column=1)
status = Label(f1, text="Ready...", fg='red')
status.config(font=("Helvetica", 16),)
status.grid(row=2, column=1)

def Window2():
    root2 = Tk()
    root2.title("Window 2")

    Label2 = Label(root2,text=ratevar.get(), width=60)
    Label2.grid(row=0, column=0)

    root2.mainloop()

def Plot():
    plt.clf()
    fig = plt.figure(1)
    t = np.arange(0.0, 3.0, 0.01)
    s = np.sin(np.pi * t)
    plt.plot(t, s)

    canvas = FigureCanvasTkAgg(fig, master=f3)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)



root.mainloop()