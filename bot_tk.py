#!/usr/bin/env python
import threading
import os.path
from tkinter import *
from tkinter.ttk import *
import tkinter.filedialog
import tkinter.messagebox
from sqlite3 import IntegrityError
from botm2.storage import get_source_list, add_source, delete_source, get_text
from botm2.generator import TextGenerator




s = Style()
s.theme_use('clam')

class Gui(Frame):
    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)
        self.grid(column=0, row=0, sticky=NSEW)
        # Initialise variables for text lengh and chain order
        self.length = StringVar()
        self.order = StringVar()
        self.ch_buttons = []
        self.sources = {}
        # Make GUI
        self.make_resizeable()
        self.make_widgets()
        self.refresh_sources()
        # Update scroll reginon when window has changed
        self.bind('<Configure>', self.set_scroll_region)

    def make_resizeable(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def make_widgets(self):
        # Create list of sources and scrollbar for it
        self.s_scroll = Scrollbar(self)
        self.s_canvas = Canvas(self, yscrollcommand=self.s_scroll.set)
        self.s_scroll.config(command=self.s_canvas.yview)
        self.s_canvas.grid(column=0, row=0, sticky=NSEW)
        self.s_scroll.grid(column=1, row=0, sticky=NS)
        self.s_frame = Frame(self.s_canvas)
        self.s_canvas.create_window(0, 0, anchor=NW, window=self.s_frame)
        # Create control buttons for manage sources
        frame = Frame(self)
        frame.grid(column=0, row=1, columnspan=2, sticky=SE, pady=2)
        Button(frame, text='Add', command=self.add_source).grid(column=0, row=0)
        Button(frame, text='Delete', command=self.delete_source).\
            grid(column=1, row=0)
        Button(frame, text='Edit').grid(column=2, row=0)
        Button(frame, text='Select all', command=self.select_all).\
            grid(column=3, row=0)
        Button(frame, text='Invert', command=self.invert).grid(column=4, row=0)
        # Create text wiget and scrollbar for text
        self.t_scroll = Scrollbar(self)
        self.text = Text(self, yscrollcommand=self.t_scroll.set)
        self.t_scroll.config(command=self.text.yview)
        self.text.grid(column=0, row=2, sticky=NSEW)
        self.t_scroll.grid(column=1, row=2, sticky=NS)
        frame = Frame(self)
        frame.grid(column=0, row=3, sticky=SE, columnspan=2, pady=2)
        # Set entry widgets and validator for it
        vl_command = self.register(self.validate_number)
        # Lenght
        Label(frame, text='Length (max=1000)').grid(row=0, column=0)
        entry = Entry(frame, width=5, validate='all',
                      validatecommand=(vl_command, '%P', 1000),
                      textvariable=self.length)
        # Set default value
        entry.insert(0, 1000)
        entry.grid(row=0, column=1)
        # Order
        Label(frame, text='Order (max=5)').grid(row=0, column=2)
        entry = Entry(frame, width=1, validate='all',
                      validatecommand=(vl_command, '%P', 1000),
                      textvariable=self.order)
        entry.insert(0, 2)
        entry.grid(row=0, column=3)
        self.btn_generate = Button(frame, text='Generate',
                                   command=self.generate_text,
                                   state=DISABLED)
        self.btn_generate.grid(column=4, row=0)
        Button(frame, text='Save', command=self.save_result).\
            grid(column=5, row=0)
        Button(frame, text='Quit', command=self.quit).grid(column=6, row=0)

    def refresh_sources(self):
        n = 0
        self.sources = {}
        if self.ch_buttons:
            for c in self.ch_buttons:
                c.destroy()
            self.ch_buttons = []
        for i, t in get_source_list():
            iv = IntVar()
            cb = Checkbutton(self.s_frame, text=t, variable=iv,
                             command=self.check_ready)
            cb.grid(column=n%2, row=n//2, sticky=NW)
            self.ch_buttons.append(cb)
            self.sources[i] = iv
            n += 1
            self.set_scroll_region(None)

    def check_ready(self):
        for i in self.sources:
            if self.sources[i].get():
                # Set button state to NORMAL
                self.btn_generate.config(state=NORMAL)
                return
        # # Set button state to DISABLED
        self.btn_generate.config(state=DISABLED)

    def select_all(self):
        for s in self.sources:
            self.sources[s].set(1)
        self.check_ready()

    def invert(self):
        for s in self.sources:
            value = self.sources[s].get()
            self.sources[s].set(1 if value == 0 else 0)
        self.check_ready()

    def add_source(self):
        filenames = tkinter.filedialog.askopenfilenames(
            initialdir=os.path.expanduser('~'))
        for filename in filenames:
            try:
                add_source(filename)
            except IntegrityError:
                tkinter.messagebox.showerror(
                    'Error', '{}\nalready exists'.format(filename),
                    icon=tkinter.messagebox.ERROR)
        self.refresh_sources()

    def delete_source(self):
        for s in self.sources:
            if self.sources[s].get():
                delete_source(s)
        self.refresh_sources()

    def validate_number(self, new_value, max_num=None):
        try:
            new_value = int(new_value if new_value else 1)
            max_num = int(max_num)
        except ValueError:
            return False
        else:
            if max_num and new_value <= max_num:
                return True
            return False

    def set_scroll_region(self, event):
        """Callback whis set "scrollregion"
        when window has changes"""
        self.s_canvas.config(scrollregion=self.s_canvas.bbox(ALL))

    def generate_text(self):
        self.text.delete('1.0', '1.end')
        source_list = []
        for s in self.sources:
            if self.sources[s].get():
                source_list.append(s)
        words = get_text(source_list)
        tg = TextGenerator(words, n=int(self.order.get()))
        g = tg.generate_text()
        threading.Thread(target=self.fill_text, args=(g,)).start()

    def fill_text(self, g):
        for i in range(int(self.length.get())):
            self.text.insert('1.end', next(g) + ' ')

    def save_result(self):
        out = tkinter.filedialog.asksaveasfile(
            initialdir=os.path.expanduser('~'), initialfile='untitled')
        for line in self.text.get('1.0', END):
            out.write(line)
        out.close()



def main():
    gui = Gui()
    gui.mainloop()


if __name__ == '__main__':
    main()
