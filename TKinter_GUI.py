import tkinter as tk
from Parser import MySPARQL
from tkinter import ttk, messagebox, WORD, CENTER
import webbrowser


class MyGUI:
    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry('1100x600')
        self.root.config(bg='maroon')

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.menubar = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='help', command=self.help_popup)
        self.menubar.add_cascade(label='help', menu=self.filemenu)
        self.root.config(menu=self.menubar)

        # Frames
        self.frame1 = tk.Frame(self.root, bg='maroon')
        self.frame2 = tk.Frame(self.root, bg='maroon')
        self.frame3 = tk.Frame(self.root, bg='maroon')
        self.frame4 = tk.Frame(self.root, bg='maroon')

        self.q = MySPARQL('ISSTO.owl')

        # Frame 1 -- Search bar
        self.header = tk.Label(self.root, text='UAS Integration Safety and Security Technology Ontology',
                               font=('Roboto', 20), fg='white', bg='maroon', pady=10)

        self.input_text = tk.Label(self.frame1, text='Search: ', fg='white', bg='maroon')
        self.user_input = tk.Entry(self.frame1, font=('Arial', 18))
        self.user_input.bind('<Return>', self.submit)
        self.submit_button = tk.Button(self.frame1, text="Submit", command=self.submit, padx=10)

        # Frame 2 -- Tables
        # Search results table
        self.table = ttk.Treeview(self.frame2, height=11)
        self.table['columns'] = ('Labels', 'Score')
        self.table.column('#0', width=0, stretch=tk.NO)  # Hide the first column
        self.table.column('Labels', anchor=tk.W, width=260)
        self.table.column('Score', anchor=tk.W, width=260)

        # Superclass Table
        self.table2 = ttk.Treeview(self.frame2)
        self.table2['columns'] = 'Superclass'
        self.table2.column('#0', width=0, stretch=tk.NO)
        self.table2.column('Superclass', anchor=tk.W, width=250)

        # Subclasses Table
        self.table3 = ttk.Treeview(self.frame2)
        self.table3['columns'] = 'Subclasses'
        self.table3.column('#0', width=250, stretch=tk.NO)
        self.table3.column('Subclasses', anchor=tk.W, width=0)

        # Table Headings
        self.table.heading('#0', text='', anchor=tk.W)
        self.table.heading('Labels', text='Labels', anchor=tk.W)
        self.table.heading('Score', text='Score', anchor=tk.W)

        self.table2.heading('#0', text='', anchor=tk.W)
        self.table2.heading('Superclass', text='Superclass', anchor=tk.W)

        self.table3.heading('#0', text='Subclasses', anchor=tk.W)

        # Frame 3 -- Output Window
        self.my_link = tk.Label(self.frame3, text='See More', fg='blue', cursor='hand2', font='Roboto')
        self.output_window = tk.Text(self.frame3, height=25, width=40, wrap=WORD, font='Roboto')

        # Frame 4 -- Instances table
        self.table4 = ttk.Treeview(self.frame4, height=23)
        self.table4['columns'] = 'Instances'
        self.table4.column('#0', width=250, stretch=tk.NO)
        self.table4.column('Instances', anchor=tk.W, width=0)

        # self.instance_window = tk.Text(self.frame4, height=30, width=40, wrap=WORD, font='Roboto')

        # Table Headings
        self.table4.heading('#0', text='', anchor=tk.W)
        self.table4.heading('#0', text='Instances', anchor=tk.W)

        # Pack the widgets
        self.header.pack()
        self.input_text.pack(side=tk.LEFT, padx=(50, 0))
        self.user_input.pack(side=tk.LEFT)
        self.submit_button.pack(side=tk.LEFT, padx=5)
        self.table.pack(padx=(10, 5), pady=0, expand=True)
        self.table2.pack(side=tk.LEFT, padx=(5, 0), pady=(10, 0), expand=True)
        self.table3.pack(side=tk.LEFT, padx=(0, 0), pady=(10, 0), expand=True)
        self.table4.pack(side=tk.LEFT, padx=(10, 5), pady=(0, 5), expand=True)

        self.table.bind("<<TreeviewSelect>>", self.on_single_click)
        self.table2.bind("<<TreeviewSelect>>", self.on_single_click2)
        self.table3.bind("<<TreeviewSelect>>", self.on_single_click3)
        self.table4.bind("<<TreeviewSelect>>", self.on_single_click4)

        self.table.bind("<Double-1>", self.on_double_click)
        self.table2.bind("<Double-1>", self.on_double_click2)
        self.table3.bind("<Double-1>", self.on_double_click3)

        self.my_link.pack(anchor='w', padx=5, ipadx=20)
        self.output_window.pack(side=tk.LEFT, padx=5, pady=5)

        # Pack the frames
        self.frame1.pack(anchor='w', padx=(10, 0), pady=0)
        self.frame2.pack(side=tk.LEFT)
        self.frame4.pack(side=tk.LEFT)
        self.frame3.pack(side=tk.LEFT)

        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.root.mainloop()

    def submit(self, event=None):
        self.clear_table()
        search_query = self.user_input.get()

        search_results = self.q.search(search_query)
        for result in search_results:
            labels = result[0]
            comment = result[1]
            seeAlso = result[2]
            superclass = result[4]
            subclasses = result[5]
            score = result[6]

            self.table.insert(parent='', index='end', text='', values=(labels, score, superclass, comment, seeAlso,
                                                                       subclasses))

    def on_closing(self):
        if messagebox.askyesno(title='Quit?', message='Do you really want to quit?'):
            self.root.destroy()

    def on_double_click(self, event):
        self.output_window.delete(1.0, tk.END)
        item = self.table.selection()[0]
        arg = self.table.item(item)["values"]
        self.output_window.insert(tk.END, f"{arg[0]}\n\n{arg[3]}\n\n{arg[4]}")

    def on_double_click2(self, event):
        self.output_window.delete(1.0, tk.END)
        item = self.table2.selection()[0]
        arg = self.table2.item(item)["values"]

        search_query = arg[0]

        search_results = self.q.search_label(search_query)
        self.clear_table()
        for result in search_results:
            labels = result[0]
            comment = result[1]
            seeAlso = result[2]
            superclass = result[4]
            subclasses = result[5]
            score = result[6]

            self.table.insert(parent='', index='end', text='', values=(labels, score, superclass, comment, seeAlso,
                                                                       subclasses))

    def on_double_click3(self, event):
        self.output_window.delete(1.0, tk.END)
        item = self.table3.selection()[0]
        arg = self.table3.item(item)["values"]

        search_query = arg[0]
        search_results = self.q.search_label(search_query)
        self.clear_table()
        for result in search_results:
            labels = result[0]
            comment = result[1]
            seeAlso = result[2]
            superclass = result[4]
            subclasses = result[5]
            score = result[6]

            self.table.insert(parent='', index='end', text='', values=(labels, score, superclass, comment, seeAlso,
                                                                       subclasses))

    def clear_table(self):
        self.table.delete(*self.table.get_children())

    def clear_window(self):
        self.output_window.delete(1.0, tk.END)
        self.table2.delete(*self.table2.get_children())
        self.table3.delete(*self.table3.get_children())

    def on_single_click(self, event):
        self.output_window.delete(1.0, tk.END)
        self.table2.delete(*self.table2.get_children())
        self.table3.delete(*self.table3.get_children())

        item = self.table.selection()[0]
        arg = self.table.item(item)["values"]

        self.output_window.insert(tk.END, f"{arg[0]}\n\n{arg[3]}\n\n{arg[4]}")
        self.table2.insert(parent='', index='end', text='', values=([arg[2]]))
        self.table4.delete(*self.table4.get_children())
        self.show_instances(str(arg[0]))

        if arg[4] != 'None':
            self.open_link(arg[4])
        search_query = arg[0]
        search_results = self.q.search_label(search_query)
        subclasses = []
        for result in search_results:
            if result[0].lower() == search_query.lower():
                subclasses = result[5]

        for thing in subclasses:
            self.table3.insert(parent='', index='end', text=thing, values=[thing])

    def on_single_click2(self, event):
        self.output_window.delete(1.0, tk.END)

        self.output_window.delete(1.0, tk.END)

        item = self.table2.selection()[0]
        arg = self.table2.item(item)["values"]
        self.output_window.insert(tk.END, f"{arg[0]}")
        self.show_instances(arg[0])

    def on_single_click3(self, event):
        self.output_window.delete(1.0, tk.END)

        item = self.table3.selection()[0]
        arg = self.table3.item(item)["values"]
        self.output_window.insert(tk.END, f"{arg[0]}")
        self.show_instances(arg[0])

    def on_single_click4(self, event):
        self.output_window.delete(1.0, tk.END)
        item = self.table4.selection()[0]
        arg = self.table4.item(item)["values"]
        self.output_window.insert(tk.END, f"{arg[0]}\n\n{arg[1]}\n\n{arg[2]}")
        if arg[2] is not None:
            self.open_link(arg[2])

    def open_link(self, link):
        self.my_link.bind('<Button-1>', lambda x: webbrowser.open_new(str(link)))

    def show_instances(self, label):
        self.table4.delete(*self.table4.get_children())
        search_instance = self.q.get_instances(label)
        for item in search_instance:
            labels = item[0]
            comments = item[1]
            seeAlso = item[2]
            self.table4.insert(parent='', index='end', text=labels, values=(labels, comments, seeAlso))

    def help_popup(self):
        popup = tk.Tk()
        popup.geometry('800x400')
        popup.wm_title('Help')
        Linebreak = '----------------------------------------------------------------------------------------------' \
                    '-----------------'
        msg = f'How to use this application:\n{Linebreak}\n\n' \
              '1. Search for an item in the ontology by typing into the search bar\n' \
              '2. Single clicks in the Labels table will populate the Superclass and Subclass\n' \
              '      tables if any exist for the selected label\n' \
              '3. Double clicks in any table will populate the output window with the \n' \
              '     annotations associated with the selected label\n' \
              '4. The instances table shows instances of a class in the ontology. This\n' \
              '     includes products such as UAVs and counter UAS devices. Single clicks\n' \
              '     in this table will populate the output window with their associated annotations\n' \
              f'{Linebreak}'
        close_button = tk.Button(popup, text='Okay', command=popup.destroy)
        label = ttk.Label(popup, text=msg, anchor='c', font=25)
        label.pack(pady=(40, 0), anchor=CENTER)
        close_button.pack(anchor='s')


MyGUI()
