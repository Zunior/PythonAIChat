from tkinter import *
from tkinter.messagebox import askyesno

class CustomDialog(Toplevel):
    def __init__(self, parent, prompt):
        Toplevel.__init__(self, parent)

        self.title(prompt)
        # self.label = Label(self, text=prompt)
        self.geometry('300x150')

        quit_button = Button(self, text='Quit', command=self.confirm)

        def confirm(self):
            answer = askyesno(title='Confirmation',
                              message='Are you sure that you want to quit?')
            if answer:
                self.destroy()


        # self.var = StringVar()
        #
        #
        # self.entry = Entry(self, textvariable=self.var)
        # self.ok_button = Button(self, text="OK", command=self.on_ok)
        #
        # self.label.pack(side="top", fill="x")
        # self.entry.pack(side="top", fill="x")
        # self.ok_button.pack(side="right")
        #
        # self.entry.bind("<Return>", self.on_ok)

    def on_ok(self, event=None):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.entry.focus_force()
        self.wait_window()
        return self.var.get()