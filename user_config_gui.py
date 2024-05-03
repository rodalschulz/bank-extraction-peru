import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog

entry_fields = []

def create_test_gui():
    global entry_fields

    root2 = tk.Tk()
    root2.title('User Configuration')
    
    style = ttk.Style(root2)
    root2.tk.call("source", "forest-dark.tcl")
    style.theme_use("forest-dark")

    config = load_config()

    entry_fields = []

    for row, (key, value) in enumerate(config.items()):
        tk.Label(root2, text=key + ':').grid(row=row, column=0)
        entry = tk.Entry(root2, width=100)
        entry.grid(row=row, column=1)
        entry.insert(0, value)
        entry_fields.append(entry)

    convert_slashes_button = tk.Button(root2, text='Reformat Entries', command=convert_slashes)
    convert_slashes_button.grid(row=row+1, column=1, sticky='w')

    save_button = tk.Button(root2, text='Save', command=save_and_close)
    save_button.grid(row=row+1, column=1, sticky='e', pady=5, padx=5)

    return root2

def load_config():
    try:
        with open('user_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
    return config

def save_config(config):
    with open('user_config.json', 'w') as f:
        json.dump(config, f, indent=4)

def save_and_close():
    global entry_fields

    config = load_config()
    for entry, (key, _) in zip(entry_fields, config.items()):
        config[key] = entry.get()

    save_config(config)
    messagebox.showinfo('Success', 'Configuration saved successfully.')

def convert_slashes():
    global entry_fields 
    for entry in entry_fields:
        entry_text = entry.get()
        if entry_text:
            # Replace backslashes
            entry_text = entry_text.replace('\\', '/')
            # Remove double quotes
            entry_text = entry_text.replace('"', '')
            entry.delete(0, tk.END)
            entry.insert(0, entry_text)

if __name__ == "__main__":
    root2 = create_test_gui()
    root2.mainloop()


