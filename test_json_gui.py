import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog

# Define entry_fields as a global variable
entry_fields = []

def create_test_gui():
    global entry_fields  # Make entry_fields accessible globally

    root2 = tk.Tk()
    root2.title('User Configuration')
    
    style = ttk.Style(root2)
    root2.tk.call("source", "forest-dark.tcl")
    style.theme_use("forest-dark")

    # Load existing config or create empty config
    config = load_config()

    entry_fields = []  # Clear entry_fields in case it was previously populated

    for row, (key, value) in enumerate(config.items()):
        tk.Label(root2, text=key + ':').grid(row=row, column=0)
        entry = tk.Entry(root2, width=100)
        entry.grid(row=row, column=1)
        entry.insert(0, value)
        entry_fields.append(entry)

    # Button to convert slashes
    convert_slashes_button = tk.Button(root2, text='Reformat Entries', command=convert_slashes)
    convert_slashes_button.grid(row=row+1, column=1, sticky='w')

    # Save button
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
    global entry_fields  # Access the global entry_fields variable

    config = load_config()
    # Update config with values from GUI fields
    for entry, (key, _) in zip(entry_fields, config.items()):
        config[key] = entry.get()

    # Save updated config to file
    save_config(config)
    messagebox.showinfo('Success', 'Configuration saved successfully.')
    #root2.destroy()

def convert_slashes():
    global entry_fields  # Access the global entry_fields variable

    # Iterate over all entry fields and replace backslashes with forward slashes
    for entry in entry_fields:
        entry_text = entry.get()
        if entry_text:
            # Replace backslashes with forward slashes
            entry_text = entry_text.replace('\\', '/')
            # Remove double quotes
            entry_text = entry_text.replace('"', '')
            entry.delete(0, tk.END)
            entry.insert(0, entry_text)

if __name__ == "__main__":
    root2 = create_test_gui()
    root2.mainloop()


