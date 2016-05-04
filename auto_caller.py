from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror
import caller_backend
import _thread
import _tkinter
import threading

check_urls = {'prod': 'https://aps.service-now.com/new_call.do?sysparm_stack=new_call_list.do&sys_id=-1',
              'dev': 'https://apsdev.service-now.com/new_call.do?sysparm_stack=new_call_list.do&sys_id=-1'}


class MainWindowGUI(Tk):
    """
    This is the main class for the entire program.
    It initializes the Frame, Menu, and status bar.
    I made the __init__ small because these items rarely change.
    """
    def __init__(self):
        Tk.__init__(self)
        # Main window for the tool. Hopefully no need for extra window BS.
        self.version_number = '1.2'
        self.title('IT Support Multitool v' + self.version_number)
        try:
            self.iconbitmap('apslogo.ico')
        except _tkinter.TclError:
            pass
        self.resizable(width=FALSE, height=FALSE)

        # This is for the checkbox in File Menu. It determines if tickets should be made
        # in production or dev versions of service now. It was quite a cluster to get working.
        # (global check_urls) This initializes the global that contains the URLS.
        global check_urls

        # These variables are for request dropdowns. They store the choices.
        # The other value is for the notes field.
        self.phone_value = StringVar()
        self.pw_value = StringVar()
        self.repr_value = StringVar()

        self.notes_value = StringVar()

        # These variables are for request dropdowns. These are the actual dropdowns.
        # The other value is the checkbox for notes itself.
        self.phone_box = None
        self.pw_box = None
        self.repr_box = None

        self.notes_check = None

        # Default color of the TKinter window. Which doesn't freaking have it's own color!
        self.def_clr = self.cget("bg")

        # Default URL is PROD.
        self.urls = 'https://aps.service-now.com/new_call.do?sysparm_stack=new_call_list.do&sys_id=-1'

        # This is the variable controlling Dev/Prod mode
        self.set_dev = StringVar()

        # This is the initialization of the menu bar! File, Edit, Tools
        self.menubar = Menu(self)
        self.config(menu=self.menubar)
        self.file_menu = Menu(self.menubar, tearoff=0)
        self.edit_menu = Menu(self.menubar, tearoff=0)
        self.tool_menu = Menu(self.menubar, tearoff=0)

        # Options for the File menu. Exit closes program, Dev Mode changes URL to Dev.
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command=lambda: quit())
        self.file_menu.add_checkbutton(label="Dev Mode", onvalue=1, offvalue=0,
                                       variable=self.set_dev, command=self.set_dev_func)

        # Options for the Edit menu. Ability to edit Status text.
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Edit Status Update", command=self.edit_status_update)

        # Options for the Tools menu. Currently, serves no function.
        self.menubar.add_cascade(label="Tools (not ready)", menu=self.tool_menu)
        self.tool_menu.add_command(label="Helpful KB's")
        self.tool_menu.add_command(label="Ping Tool")

        # Settings for the status bar. Fuck TKinter grids.
        self.grid_rowconfigure(6, )
        self.status = Label(self, text="Version {} | Copyright © 2016 All rights reserved".format(self.version_number),
                            bd=1, relief=SUNKEN, anchor=W)
        self.status.grid(column=0, columnspan=5, row=6, sticky=W+E)

        # The following variables are for the generate_widgets() function.
        self.uid_label = None
        self.uid_entry = None
        self.ticket_label = None
        self.ticket_entry = None
        self.phone_button = None
        self.pw_button = None
        self.repr_button = None
        self.status_button = None

        # These variables are for updating the Status Update text.
        self.status_window = None
        self.status_label = None
        self.first_line = None
        self.status_text = None
        self.status_confirm = None
        self.status_close = None

        # This is the Notes section GUI Code. Placed here in haste.
        self.top = None
        self.notes_text = None

        # Runs the function to create the rest of the UI.
        self.generate_widgets()

    def generate_widgets(self):
        # Row 0, Username label and entry. Ticket number and entry.
        self.uid_label = Label(self, text="Enter User ID:")
        self.uid_label.config(width=15)
        self.uid_label.grid(column=0, row=0, padx=3, pady=3)

        self.uid_entry = Entry(self)
        self.uid_entry.config(width=18)
        self.uid_entry.grid(column=1, row=0, padx=3, pady=3)

        self.ticket_label = Label(self, text="Enter Ticket:")
        self.ticket_label.config(width=15)
        self.ticket_label.grid(column=2, row=0, padx=3, pady=3)

        self.ticket_entry = Entry(self)
        self.ticket_entry.config(width=18)
        self.ticket_entry.grid(column=3, row=0, padx=3, pady=3)

        # Row 1, 4 buttons, Phone & Wireless, PW resets, Reprovision, Status updates
        self.phone_button = Button(self, text="Phone & Wireless", command=self.phone_selection)
        self.phone_button.config(width=15)
        self.phone_button.grid(column=0, row=1, padx=3, pady=3)

        self.pw_button = Button(self, text="Password Resets", command=self.password_selection)
        self.pw_button.config(width=15)
        self.pw_button.grid(column=1, row=1, padx=3, pady=3)

        self.repr_button = Button(self, text="Reprovisions", command=self.reprovision_selection)
        self.repr_button.config(width=15)
        self.repr_button.grid(column=2, row=1, padx=3, pady=3)

        self.status_button = Button(self, text="Status Update", command=self.status_update)
        self.status_button.config(width=15)
        self.status_button.grid(column=3, row=1, padx=3, pady=3)

        # Row 2, 3 dropdown menus for Wireless
        self.phone_box = ttk.Combobox(self, textvariable=self.phone_value)
        self.phone_box.grid(column=0, row=2, padx=3, pady=3)
        self.phone_box['values'] = ('', 'New Order', '**ESN Swap')
        self.phone_box.config(width=15)

        self.pw_box = ttk.Combobox(self, textvariable=self.pw_value)
        self.pw_box.grid(column=1, row=2, padx=3, pady=3)
        self.pw_box['values'] = ('', 'APSC Domain', 'Endpoint', 'DOMS User Tool', 'SWMS Pincode',
                                 'Mainframe Reset', 'Goodlink')
        self.pw_box.config(width=15)

        self.repr_box = ttk.Combobox(self, textvariable=self.repr_value)
        self.repr_box.grid(column=2, row=2, padx=3, pady=3)
        self.repr_box['values'] = ('', 'Goodlink iPhone', 'Goodlink Android',
                                   'Defender iPhone', 'Defender Android')
        self.repr_box.config(width=15)

        self.notes_check = Checkbutton(self, text="Show Notes", variable=self.notes_value,
                                       onvalue=True, offvalue=False, command=self.set_notes_func,
                                       state=ACTIVE)
        self.notes_check.grid(column=3, row=2, padx=3, pady=3)

    def set_dev_func(self):
        """
        This function checks the state of the set_dev variable.
        Then it sets the background color of the application.
        As well as changing the URL used by Selenium's Chromedriver.
        """
        if '1' in self.set_dev.get():
            self.urls = check_urls['dev']
            self.config(bg='orange')
            print("DEV MODE ON!")

        elif '0' in self.set_dev.get():
            self.urls = check_urls['prod']
            self.config(bg=self.def_clr)
            print("DEV MODE OFF!")

    def set_notes_func(self):
        if '1' in self.notes_value.get():
            # ADD NOTES FRAME AT BOTTOM OF GUI
            self.top = Frame(self)
            self.top.grid(columnspan=4, row=4)
            self.notes_text = Text(self.top, width=58, height=10, padx=3, pady=6)
            self.notes_text.pack()
            print("NOTES MODE ON!")

        elif '0' in self.notes_value.get():
            # REMOVE NOTES FRAME AT BOTTOM OF GUI
            self.top.destroy()
            print("NOTES MODE OFF!")

    def phone_selection(self):
        """
        This function is called by the phone_button object.
        It checks teh value of phone_box.get() based on the selected dropdown.
        Then it runs the appropriate code.
        """
        value_of_combo = self.phone_box.get()
        if value_of_combo == 'New Order':
            print(self.phone_box.get(), self.uid_entry.get())
        if value_of_combo == 'ESN Swap':
            print(self.phone_box.get(), self.uid_entry.get())

    def password_selection(self):
        """
        This function is called by the pw_button object.
        It checks teh value of pw_box.get() based on the selected dropdown.
        Then it runs the appropriate code.
        """
        value_of_combo = self.pw_box.get()
        if value_of_combo == 'APSC Domain':
            print(self.pw_box.get(), self.uid_entry.get())
            self.nt_pw_reset()
        if value_of_combo == 'Endpoint':
            print(self.pw_box.get(), self.uid_entry.get())
            self.endpoint_rec()
        if value_of_combo == 'DOMS User Tool':
            print(self.pw_box.get(), self.uid_entry.get())
            self.doms_pw_reset()
        if value_of_combo == 'Mainframe Reset':
            print(self.pw_box.get(), self.uid_entry.get())
            self.mainframe_reset()
        if value_of_combo == 'SWMS Pincode':
            print(self.pw_box.get(), self.uid_entry.get())
            self.swms_pw_reset()
        if value_of_combo == 'Goodlink':
            print(self.pw_box.get(), self.uid_entry.get())
            self.goodlink_reset()

    def reprovision_selection(self):
        """
        This function is called by the repr_button object.
        It checks teh value of pw_box.get() based on the selected dropdown.
        Then it runs the appropriate code.
        """
        value_of_combo = self.repr_box.get()
        if value_of_combo == 'Goodlink iPhone':
            print(self.repr_box.get(), self.uid_entry.get())
            self.goodlink_rep_i()
        if value_of_combo == 'Goodlink Android':
            print(self.repr_box.get(), self.uid_entry.get())
            self.goodlink_rep_a()
        if value_of_combo == 'Defender iPhone':
            print(self.repr_box.get(), self.uid_entry.get())
            self.defender_rep_i()
        if value_of_combo == 'Defender Android':
            print(self.repr_box.get(), self.uid_entry.get())
            self.defender_rep_a()

    def edit_status_update(self):
        """
        Opens a new window to view and edit the status_text file.
        read_status() and save_status_text() interact with the function.
        It allows the user to change text used in the status update.

        :return: No return value. But it does open a new window.
        """
        self.status_window = Tk()
        self.status_window.title("Update Status Text")

        self.status_label = Label(self.status_window, text="Update Status Text:")
        self.status_label.grid(columnspan=4, row=0, padx=3, pady=5)

        self.first_line = Label(self.status_window, text="Status update on TICKET NUMBER.")
        self.first_line.grid(column=0, row=1, padx=3, pady=1)

        self.status_text = Text(self.status_window, font=("Times New Roman", 12))
        self.status_text.config(width=40, height=5)
        self.status_text.grid(columnspan=4, row=2, padx=3, pady=3, sticky=W)
        self.status_text.insert(INSERT, self.read_status())

        self.status_confirm = Button(self.status_window, text="Update",
                                     command=lambda: self.save_status_text(self.status_text.get("1.0", END)))
        self.status_confirm.grid(column=1, row=3, padx=3, pady=3, sticky=E)

        self.status_close = Button(self.status_window, text="Close", command=self.status_window.destroy)
        self.status_close.grid(column=2, row=3, padx=3, pady=3, sticky=W)

    def read_status(self):
        """
        :return: Returns status_text contents.
        """
        with open('status_text') as f:
            return f.read()

    def save_status_text(self, text):
        """
        :param text: Pulls text from Text box in edit_status_update()
        :return: No return value. But it does write text to status_text
        """
        with open('status_text', 'w') as f:
            f.write(text)

    def no_user_entered(self, ticket=False):
        """
        :param ticket: Used by the status update function.
        :return: shows an error if no username is entered.
        """
        if ticket:
            showerror("Error!", "Missing Username or Ticket number!")
        else:
            showerror("Error!", "No Username entered!")

    def status_update(self):
        # This checks if UID and Ticket number contains any value.
        # Then it runs the code to start the be_status_update function.
        if self.uid_entry.get() and self.ticket_entry.get():
            _thread.start_new(caller_backend.be_status_update, (self.uid_entry.get(),
                                                                self.ticket_entry.get(), self.urls))
        # If the UID field OR the Ticket field are emtpy, a fun error is called.
        else:
            self.no_user_entered(ticket=True)

    def doms_pw_reset(self):
        # This checks if UID contains any value.
        # Then it runs the code to start the password_reset function.
        # But it uses the kwarg doms to determine workflow.
        if self.uid_entry.get():
            doms = threading.Thread(target=caller_backend.password_reset,
                                    args=(self.urls, self.uid_entry.get()),
                                    kwargs=dict(doms=True))
            doms.start()
        # If the UID field is emtpy, a fun error is called.
        else:
            self.no_user_entered()

    def nt_pw_reset(self):
        if self.uid_entry.get():
            nt = threading.Thread(target=caller_backend.password_reset,
                                  args=(self.urls, self.uid_entry.get()),
                                  kwargs=dict(nt=True))
            nt.start()
        else:
            self.no_user_entered()

    def swms_pw_reset(self):
        if self.uid_entry.get():
            swms = threading.Thread(target=caller_backend.password_reset,
                                    args=(self.urls, self.uid_entry.get()),
                                    kwargs=dict(swms=True))
            swms.start()
        else:
            self.no_user_entered()

    def endpoint_rec(self):
        if self.uid_entry.get():
            endp = threading.Thread(target=caller_backend.password_reset,
                                    args=(self.urls, self.uid_entry.get()),
                                    kwargs=dict(endpoint=True))
            endp.start()
        else:
            self.no_user_entered()

    def mainframe_reset(self):
        if self.uid_entry.get():
            mainf = threading.Thread(target=caller_backend.password_reset,
                                     args=(self.urls, self.uid_entry.get()),
                                     kwargs=dict(mainframe=True))
            mainf.start()
        else:
            self.no_user_entered()

    def goodlink_reset(self):
        if self.uid_entry.get():
            goodl = threading.Thread(target=caller_backend.password_reset,
                                     args=(self.urls, self.uid_entry.get()),
                                     kwargs=dict(good=True))
            goodl.start()
        else:
            self.no_user_entered()

    def goodlink_rep_i(self):
        if self.uid_entry.get():
            _thread.start_new(caller_backend.be_goodlink_reprovision, (self.uid_entry.get(), 'iphone', self.urls))
        else:
            self.no_user_entered()

    def goodlink_rep_a(self):
        if self.uid_entry.get():
            _thread.start_new(caller_backend.be_goodlink_reprovision, (self.uid_entry.get(), 'android', self.urls))
        else:
            self.no_user_entered()

    def defender_rep_i(self):
        if self.uid_entry.get():
            _thread.start_new(caller_backend.be_defender_reprovision, (self.uid_entry.get(), 'iphone', self.urls))
        else:
            self.no_user_entered()

    def defender_rep_a(self):
        if self.uid_entry.get():
            _thread.start_new(caller_backend.be_defender_reprovision, (self.uid_entry.get(), 'android', self.urls))
        else:
            self.no_user_entered()


def check_for_files():
    import os.path
    if os.path.isfile('status_text') and os.path.isfile('chromedriver.exe'):
        pass
    elif not os.path.isfile('status_text') and os.path.isfile('chromedriver.exe'):
        showerror('Missing File!', 'Missing "status_text" file. Please see Shelby. '
                                   'Shutting down the multitool.')
        quit()
    elif os.path.isfile('status_text') and not os.path.isfile('chromedriver.exe'):
        showerror('Missing File!', 'Missing "chromedriver.exe" file. Please see Shelby. '
                                   'Shutting down the multitool.')
        quit()
    elif not os.path.isfile('status_text') and not os.path.isfile('chromedriver.exe'):
        showerror('Missing File!', 'Missing both "chromedriver.exe" and "status_text". See Shelby. '
                                   'Shutting down the multitool.')
        quit()
    else:
        showerror('Unexpected Error', 'An unexpected error has ocurred.')
        quit()

if __name__ == "__main__":
    check_for_files()
    root = MainWindowGUI()
    root.mainloop()

