import network_parser
import core
import tkinter.font as tkFont
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from logging_control import configure_logging

class VM_GUI(Tk):
    def __init__(self, *args, **kwargs) -> None:
        Tk.__init__(self, *args, **kwargs)
        configure_logging()
        self.title("Max Patrol VM")
        self.resizable(0,0)
        self.controller_network = network_parser.Network_Scanner()
        self.geometry("1300x600")
        self.prev_network_frame = None
        self.network_frames = {
            "":Network_Frame_start,
            "Одно устройство":Network_Frame_single,
            "Сеть":Network_Frame_basic
        }
        
        self.core = core.Core()
        
        for i in range(8): 
            self.columnconfigure(index = i, weight=1)
            self.rowconfigure(index = i, weight=1)
        
        name_frame = ttk.LabelFrame(self, text="INT-2", labelanchor="nw")
        name_frame.grid(column=0, row = 0, sticky=NSEW, rowspan=3, columnspan=10, padx=10, pady=10)
        name_frame.pack_propagate(False)
        
        self.ilabel = ttk.Label(name_frame, text="VULNERABILITY MANAGEMENT\n                     by Dmitry Koryanov", font=("Courier", 40))
        self.ilabel.pack(fill="both", expand=False)
        
        main_frame = ttk.LabelFrame(self, text="", labelanchor="nw")
        main_frame.grid(column=0, row = 2, sticky=NSEW, rowspan=8, columnspan=10, padx=10, pady=10)
        main_frame.grid_propagate(False)
        for i in range(30): 
            main_frame.columnconfigure(index = i, weight=1)
            main_frame.rowconfigure(index = i, weight=1)
        
        mode_text = ttk.Label(main_frame, text="Режим сканирования: ")
        mode_text.grid(row = 0, column=0, padx=5, pady=10)
        
        self.subframe_network = ttk.LabelFrame(main_frame, text="Настройки сканирования", labelanchor="nw")
        self.subframe_network.grid(row=1, column=0, sticky=NSEW, rowspan=19, columnspan=2, padx=10)
        self.subframe_network.pack_propagate(False)
        for i in range(10): 
            self.subframe_network.columnconfigure(index = i, weight=1)
            self.subframe_network.rowconfigure(index = i, weight=1)
        
        # for key in self.network_frames:
        #     self.network_frames[key] = self.network_frames[key](self.subframe_network, self)
        
        self.scan_mode = StringVar(value="")
        mode_button = ttk.Combobox(main_frame,textvariable=self.scan_mode, name="Тип сканирования",state="readonly", values=list(self.network_frames)[1:])
        mode_button.grid(row=0, column=1, pady=10)
        self.scan_mode.trace("w", self.change_network_mode)
        self.scan_mode.set("")
        
        self.subframe_transport = ttk.LabelFrame(main_frame, text = "Настройки SSH", labelanchor="nw")
        self.subframe_transport.grid(row=20, column=0, sticky=NSEW, rowspan=6, columnspan=2, padx=10, pady=10)
        self.ssh_frame = ttk.Frame(self.subframe_transport)
        self.ssh_frame.pack(fill='both', anchor=W, expand=True)
        for i in range(3): 
            self.ssh_frame.rowconfigure(index = i, weight=1)
        for i in range(2):
            self.ssh_frame.columnconfigure(index = i, weight=1)
        
        ssh_user_label = ttk.Label(self.ssh_frame, text="Пользователь SSH")
        ssh_user_label.grid(row=1, column=0,sticky=NW)
        
        ssh_password_label = ttk.Label(self.ssh_frame, text="Пароль")
        ssh_password_label.grid(row=2, column=0, sticky=NW)
        
        self.ssh_user = StringVar()
        self.ssh_password = StringVar()
        
        self.ssh_user.trace("w", self.ssh_callback)
        self.ssh_password.trace("w", self.ssh_callback)
        
        ssh_user_field = ttk.Entry(self.ssh_frame, textvariable=self.ssh_user)
        ssh_user_field.grid(row=1, column=1,sticky=NW)
        
        ssh_password_field = ttk.Entry(self.ssh_frame, textvariable=self.ssh_password, show="*")
        ssh_password_field.grid(row=2, column=1,sticky=NW)
        
        self.subframe_output = ttk.LabelFrame(main_frame, text = "Вывод", labelanchor="nw")
        self.subframe_output.grid(row=0, column=10, sticky=NSEW, rowspan=26, columnspan=24, pady=10, padx=10)
        self.subframe_output.pack_propagate(False)
        
        self.subframe_database = ttk.LabelFrame(main_frame, text = "Настройки PostgreSQL", labelanchor="nw")
        self.subframe_database.grid(row=0, column=2, sticky=NSEW, rowspan=20, columnspan=8, pady=10)
        self.subframe_database.grid_propagate(False)
        for i in range(7): 
            self.subframe_database.rowconfigure(index = i, weight=1)
        for i in range(2):
            self.subframe_database.columnconfigure(index = i, weight=1)
        
        database_address_label = ttk.Label(self.subframe_database, text="IP-адрес")
        database_user_label = ttk.Label(self.subframe_database, text="Пользователь")
        database_password_label = ttk.Label(self.subframe_database, text="Пароль")
        database_name_label = ttk.Label(self.subframe_database, text="Имя БД")
        database_schema_label = ttk.Label(self.subframe_database, text="Имя схемы")
        database_table_label = ttk.Label(self.subframe_database, text="Имя таблицы")
        
        database_address_label.grid(row=1, column=0, sticky=NW)
        database_user_label.grid(row=2, column=0, sticky=NW)
        database_password_label.grid(row=3, column=0, sticky=NW)
        database_name_label.grid(row=4, column=0, sticky=NW)
        database_schema_label.grid(row=5, column=0, sticky=NW)
        database_table_label.grid(row=6, column=0, sticky=NW)
        
        self.database_address = StringVar()
        self.database_user = StringVar()
        self.database_password = StringVar()
        self.database_name = StringVar()
        self.database_schema = StringVar()
        self.database_table = StringVar()
        
        self.database_address.trace("w", self.sql_callback)
        self.database_user.trace("w", self.sql_callback)
        self.database_password.trace("w", self.sql_callback)
        self.database_name.trace("w", self.sql_callback)
        self.database_schema.trace("w", self.sql_callback)
        self.database_table.trace("w", self.sql_callback)
        
        database_address_field = ttk.Entry(self.subframe_database, textvariable=self.database_address)
        database_user_field = ttk.Entry(self.subframe_database, textvariable=self.database_user)
        database_password_field = ttk.Entry(self.subframe_database, textvariable=self.database_password, show="*")
        database_name_field = ttk.Entry(self.subframe_database, textvariable=self.database_name)
        database_schema_field = ttk.Entry(self.subframe_database, textvariable=self.database_schema)
        database_table_field = ttk.Entry(self.subframe_database, textvariable=self.database_table)
        
        database_address_field.grid(row = 1, column=1, sticky=NW)
        database_user_field.grid(row=2, column=1, sticky=NW)
        database_password_field.grid(row=3, column=1, sticky=NW)
        database_name_field.grid(row=4, column=1, sticky=NW)
        database_schema_field.grid(row=5, column=1, sticky=NW)
        database_table_field.grid(row=6, column=1, sticky=NW)
        
        self.database_address.set("localhost")
        self.database_user.set("postgres")
        self.database_name.set("VM")
        self.database_schema.set("VM_schema")
        self.database_table.set("results")
        
        self.start_button = Button(main_frame, text="НАЧАТЬ", command=self.start_button_callback)
        self.start_button.grid(row = 20, column= 2,rowspan= 5, columnspan=8, sticky=N+S+E+W)
        
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=27, column=0, sticky=NSEW, columnspan=30, rowspan=10, padx=10)
        progress_frame.pack_propagate(False)
        
        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x', side='top')
        
        self.database_var_nodrop = BooleanVar()
        self.database_drop = Checkbutton(main_frame, text="Сбросить таблицу?",variable=self.database_var_nodrop, onvalue=False, offvalue=True)
        self.database_drop.grid(row = 25, column=10)
        
        self.sql_headers = ["ID", "IP", "OS", "Version", "Architecture"]
        self.database_output = ttk.Treeview(self.subframe_output, columns=self.sql_headers, show="headings")
        self.database_output.pack(fill="both", anchor=W, expand=True)
        for col in self.sql_headers:
            self.database_output.heading(col, text=col.title(),
                command=lambda c=col: self.sortby(self.database_output, c, 0))
            self.database_output.column(col,
                width=tkFont.Font().measure(col.title()))
            
        database_scroll = ttk.Scrollbar(self.database_output, orient="vertical", command=self.database_output.yview)
        database_scroll.pack(fill='y',side='right')
        self.database_output.configure(yscrollcommand=database_scroll.set)
        
        
    def sortby(self, tree, col, descending) -> None:
        data = [(tree.set(child, col), child) \
            for child in tree.get_children('')]
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, \
            int(not descending)))    
        
    def populate_table(self) -> None:
        res = self.core.get_table()
        self.database_output.delete(*self.database_output.get_children())
        for item in res:
            self.database_output.insert('', 'end', values=item)
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.database_output.column(self.sql_headers[ix],width=None)<col_w:
                    self.database_output.column(self.sql_headers[ix], width=col_w)
        self.progress.config(value=100)
        
    def change_network_mode(self, *args, **kwargs) -> None:
        if self.prev_network_frame: self.prev_network_frame.pack_forget()
        self.frame = self.network_frames[self.scan_mode.get()](self.subframe_network, self)
        self.frame.tkraise()
        self.prev_network_frame = self.frame
        
    def sql_callback(self, *args, **kwargs) -> None:
        self.core.sql_address = self.database_address.get()
        self.core.sql_user = self.database_user.get()
        self.core.sql_password = self.database_password.get()
        self.core.sql_db = self.database_name.get()
        self.core.sql_schema = self.database_schema.get()
        self.core.sql_table = self.database_table.get()

    def ssh_callback(self, *args, **kwargs) -> None:
        self.core.ssh_user = self.ssh_user.get()
        self.core.ssh_password = self.ssh_password.get()
        
    def network_single_callback(self, *args, **kwargs) -> None:
        try:
            self.core.target = self.frame.address_variable.get()
            self.core.port = int(self.frame.port_variable.get())
            self.network_mode = 0
        except Exception: pass
        
    def network_basic_callback(self, *args, **kwargs) -> None:
        self.core.network = self.frame.network_address.get()
        self.core.ports = self.frame.port_list.get().split(",")
        self.core.exclusions = self.frame.exclusions.get()
        self.network_mode = 1
    
    def start_button_callback(self, *args, **kwargs) -> None:
        res = -3
        try:
            res = self.core.run(self.network_mode, self.database_var_nodrop.get(), progress=self.progress)
        except Exception:
            self.progress.configure(value=0)
        match res:
            case -1: messagebox.showerror('Ошибка!', message= 'Указаны не все параметры подключения к PostgreSQL')
            case -2: messagebox.showerror('Ошибка!',message= 'Указаны не все параметры транспорта')
            case -3: messagebox.showerror('Ошибка!',message= 'Не выбран режим работы с сетью')
            case _:
                self.populate_table()
        
class Network_Frame_start(Frame):
    def __init__(self, parent, control) -> None:
        Frame.__init__(self, parent)
        self.pack(fill='both', anchor=W, expand=True)
        for i in range(10): 
            self.columnconfigure(index = i, weight=1)
            self.rowconfigure(index = i, weight=1)
        default_network_message = ttk.Label(self, text="Выберите режим сканирования")
        default_network_message.grid(row=4, column=5)

class Network_Frame_single(Frame):
    def __init__(self, parent, control) -> None:
        Frame.__init__(self, parent)
        self.pack(fill='both', anchor=W, expand=True)
        for i in range(3): 
            self.rowconfigure(index = i, weight=1)
        for i in range(2):
            self.columnconfigure(index = i, weight=1)
            
        address_label = ttk.Label(self, text="Адрес устройства")
        address_label.grid(row=1, column=0, sticky=NW)
        
        self.address_variable = StringVar(value="")
        self.address_variable.trace("w", control.network_single_callback)
        address_field = ttk.Entry(self, textvariable=self.address_variable)
        address_field.grid(row=1, column=1,sticky=NW)
        
        port_label = ttk.Label(self, text="Порт для подключения")
        port_label.grid(row=2, column=0,sticky=NW)
        
        self.port_variable = StringVar()
        self.port_variable.trace("w", control.network_single_callback)
        port_field = ttk.Entry(self, textvariable=self.port_variable)
        port_field.grid(row=2, column=1,sticky=NW)
        self.port_variable.set("22")
    
        
class Network_Frame_basic(Frame):
    def __init__(self, parent, control) -> None:
        Frame.__init__(self, parent)
        self.pack(fill='both', anchor=W, expand=True)
        
        self.parent = control
        for i in range(6): 
            self.rowconfigure(index = i, weight=1)
        for i in range(4):
            self.columnconfigure(index = i, weight=1)
    
        address_label = ttk.Label(self, text="Сеть")
        address_label.grid(row=1, column=0, sticky=NW)
        
        port_label = ttk.Label(self, text="Возможные порты")
        port_label.grid(row=2, column=0,sticky=NW)
        exclusion_label = ttk.Label(self, text="Исключения")
        exclusion_label.grid(row=5, column=0,sticky=NW)
        
        self.network_address = StringVar()
        self.network_address.trace("w", control.network_basic_callback)
        address_field = ttk.Entry(self, textvariable=self.network_address)
        address_field.grid(row=1, column=2, sticky=NW)
        
        self.port_list = StringVar()
        self.port_list.trace("w", control.network_basic_callback)
        port_field = ttk.Entry(self, textvariable=self.port_list)
        port_field.grid(row=2, column=2, sticky=NW)
        
        self.exclusions = StringVar()
        self.exclusions.trace("w", control.network_basic_callback)
        exclusion_field = ttk.Entry(self, textvariable=self.exclusions, width=30)
        exclusion_field.grid(row=5, column=2,sticky=NE)
    
def main(*args, **kwargs) -> None:
    gui = VM_GUI()
    gui.mainloop()

if __name__ == "__main__":
    main()



