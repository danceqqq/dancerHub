import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import sqlite3


class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Note and Password Manager")

        self.tab_control = ttk.Notebook(root)

        self.note_tab = ttk.Frame(self.tab_control)
        self.password_tab = ttk.Frame(self.tab_control)
        self.settings_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.note_tab, text='Notes')
        self.tab_control.add(self.password_tab, text='Passwords')
        self.tab_control.add(self.settings_tab, text='Settings')

        self.tab_control.pack(expand=1, fill='both')

        self.setup_database()
        self.create_note_tab()
        self.create_password_tab()
        self.create_settings_tab()

    def create_note_tab(self):
        self.note_frame = ttk.Frame(self.note_tab)
        self.note_frame.pack(expand=1, fill='both', padx=10, pady=10)

        self.note_list = tk.Listbox(self.note_frame)
        self.note_list.pack(side='left', fill='both', expand=1)

        self.scrollbar = ttk.Scrollbar(self.note_frame, orient='vertical', command=self.note_list.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.note_list.config(yscrollcommand=self.scrollbar.set)

        self.note_text = tk.Text(self.note_tab, wrap='word')
        self.note_text.pack(expand=1, fill='both')

        self.button_frame = ttk.Frame(self.note_tab)
        self.button_frame.pack(fill='x', padx=10, pady=10)

        self.new_note_button = ttk.Button(self.button_frame, text="New Note", command=self.new_note)
        self.new_note_button.pack(side='left')

        self.delete_note_button = ttk.Button(self.button_frame, text="Delete Note", command=self.delete_note)
        self.delete_note_button.pack(side='left')

        self.load_notes()

    def create_password_tab(self):
        self.password_frame = ttk.Frame(self.password_tab)
        self.password_frame.pack(expand=1, fill='both', padx=10, pady=10)

        self.website_label = ttk.Label(self.password_frame, text="Website:")
        self.website_label.grid(row=0, column=0, sticky='w')
        self.website_entry = ttk.Entry(self.password_frame)
        self.website_entry.grid(row=0, column=1, sticky='ew')

        self.username_label = ttk.Label(self.password_frame, text="Username:")
        self.username_label.grid(row=1, column=0, sticky='w')
        self.username_entry = ttk.Entry(self.password_frame)
        self.username_entry.grid(row=1, column=1, sticky='ew')

        self.password_label = ttk.Label(self.password_frame, text="Password:")
        self.password_label.grid(row=2, column=0, sticky='w')
        self.password_entry = ttk.Entry(self.password_frame)
        self.password_entry.grid(row=2, column=1, sticky='ew')

        self.save_button = ttk.Button(self.password_frame, text="Save", command=self.save_password)
        self.save_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.password_frame.columnconfigure(1, weight=1)

        self.password_list = tk.Listbox(self.password_frame)
        self.password_list.grid(row=4, column=0, columnspan=2, sticky='nsew')
        self.password_frame.rowconfigure(4, weight=1)

        self.scrollbar = ttk.Scrollbar(self.password_frame, orient='vertical', command=self.password_list.yview)
        self.scrollbar.grid(row=4, column=2, sticky='ns')
        self.password_list.config(yscrollcommand=self.scrollbar.set)

        self.edit_button = ttk.Button(self.password_frame, text="Edit", command=self.edit_password)
        self.edit_button.grid(row=5, column=0, pady=5)

        self.delete_button = ttk.Button(self.password_frame, text="Delete", command=self.delete_password)
        self.delete_button.grid(row=5, column=1, pady=5)

        self.load_passwords()

    def create_settings_tab(self):
        self.theme_var = tk.StringVar(value='light')

        self.light_theme_radio = ttk.Radiobutton(self.settings_tab, text='Light Theme', variable=self.theme_var,
                                                 value='light', command=self.change_theme)
        self.light_theme_radio.pack(anchor='w', padx=10, pady=5)

        self.dark_theme_radio = ttk.Radiobutton(self.settings_tab, text='Dark Theme', variable=self.theme_var,
                                                value='dark', command=self.change_theme)
        self.dark_theme_radio.pack(anchor='w', padx=10, pady=5)

    def setup_database(self):
        self.conn = sqlite3.connect('app_data.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                content TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def new_note(self):
        content = self.note_text.get("1.0", tk.END).strip()
        if content:
            self.cursor.execute('INSERT INTO notes (content) VALUES (?)', (content,))
            self.conn.commit()
            self.load_notes()
            self.note_text.delete("1.0", tk.END)
        else:
            messagebox.showwarning("Input Error", "Note content cannot be empty")

    def delete_note(self):
        selected = self.note_list.curselection()
        if selected:
            index = selected[0]
            note_id = self.note_list.get(index).split(' ')[0]
            self.cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            self.conn.commit()
            self.load_notes()
        else:
            messagebox.showwarning("Selection Error", "Select a note to delete")

    def load_notes(self):
        self.note_list.delete(0, tk.END)
        self.cursor.execute('SELECT id, content FROM notes')
        for row in self.cursor.fetchall():
            self.note_list.insert(tk.END, f"{row[0]} {row[1]}")

    def save_password(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if website and username and password:
            self.cursor.execute('''
                INSERT INTO passwords (website, username, password)
                VALUES (?, ?, ?)
            ''', (website, username, password))
            self.conn.commit()
            self.load_passwords()
            self.website_entry.delete(0, tk.END)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "All fields are required")

    def load_passwords(self):
        self.password_list.delete(0, tk.END)
        self.cursor.execute('SELECT id, website, username, password FROM passwords')
        for row in self.cursor.fetchall():
            self.password_list.insert(tk.END, f"{row[1]} | {row[2]} | {row[3]}")

    def edit_password(self):
        selected = self.password_list.curselection()
        if selected:
            index = selected[0]
            item = self.password_list.get(index)
            website, username, password = item.split(' | ')
            self.website_entry.delete(0, tk.END)
            self.website_entry.insert(0, website)
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, username)
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)
            self.delete_password()
        else:
            messagebox.showwarning("Selection Error", "Select an item to edit")

    def delete_password(self):
        selected = self.password_list.curselection()
        if selected:
            index = selected[0]
            item = self.password_list.get(index)
            website, username, password = item.split(' | ')
            self.cursor.execute('''
                DELETE FROM passwords
                WHERE website = ? AND username = ? AND password = ?
            ''', (website, username, password))
            self.conn.commit()
            self.load_passwords()
        else:
            messagebox.showwarning("Selection Error", "Select an item to delete")

    def change_theme(self):
        theme = self.theme_var.get()
        if theme == 'light':
            self.root.set_theme("default")
        else:
            self.root.set_theme("equilux")


if __name__ == "__main__":
    root = ThemedTk(theme="default")
    app = NoteApp(root)
    root.mainloop()
