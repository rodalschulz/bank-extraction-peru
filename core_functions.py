import os
import simpleaudio as sa
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import tkinter as tk
import webbrowser
import json

# Custom mapping for Spanish month abbreviations to English
spanish_to_english_month = {
    'ene': 'Jan',
    'feb': 'Feb',
    'mar': 'Mar',
    'abr': 'Apr',
    'may': 'May',
    'jun': 'Jun',
    'jul': 'Jul',
    'ago': 'Aug',
    'sep': 'Sep',
    'set': 'Sep',
    'oct': 'Oct',
    'nov': 'Nov',
    'dic': 'Dec'
}

# READ USER'S CONFIGURATION JSON FILE
def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config_data = json.load(file)
        return config_data
    except FileNotFoundError:
        print(f"Config file not found at: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return None
       
# PLAY ALL SOUNDS (THIS ONE SHOULD WORK WITH THE .EXE)
def play_sound(sound_file):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    sound_path = os.path.join(script_directory, "sounds", sound_file)
    
    try:
        wave_obj = sa.WaveObject.from_wave_file(sound_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except FileNotFoundError:
        print(f"Sound file '{sound_file}' not found.")

# CHECK IF AN ELEMENT IS CLICKABLE
def is_element_clickable(driver, by, value, timeout=1):
    try:
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return True
    except Exception as e:
        return False

def adjust_date(input_date):
    # Get the current year
    current_year = datetime.now().year
    # Convert the month abbreviation to English
    input_date_parts = input_date.split()
    input_date_parts[1] = spanish_to_english_month.get(
        input_date_parts[1].lower(), input_date_parts[1])
    input_date_with_year = ' '.join(input_date_parts) + f' {current_year}'
    # Parse the input date string
    input_date = datetime.strptime(input_date_with_year, '%d %b %Y')
    # Get the current date
    current_date = datetime.now()
    # Adjust the year if the input date is after the current date
    if input_date > current_date.replace(year=input_date.year):
        input_date = input_date.replace(year=input_date.year - 1)
    # Return the adjusted date in DD/MM/YYYY format
    return input_date.strftime('%d/%m/%Y')

def fix_bank_df_formatting(df):
    df['ACC_CODE'] = df['ACC_CODE'].astype(str)
    df['DATE'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y')
    df['TIME'] = pd.to_datetime(df['TIME'], format='%H:%M').dt.time
    df['TRX_NAME'] = df['TRX_NAME'].astype(str)
    df['PEN'] = df['PEN'].astype(float).round(2)
    df['USD'] = df['USD'].astype(float).round(2)

def enumerate_duplicates(list, col):
    unique_rows = set()
    count_dict = {}
    result = []
    for row in list:
        key = tuple(row)  # Use the entire row as the key
        if key not in unique_rows:
            unique_rows.add(key)
            count_dict[key] = 1
            result.append(row)
        else:
            count = count_dict[key]
            row[col] += f' - {count + 1}'
            count_dict[key] += 1
            result.append(row)
    return list

# VISUALIZE ANY DATA FRAME USING A CHROME WINDOW
def visualize_df_chrome(df):
    # Convert the DataFrame to an HTML file
    html_content = df.to_html(index=False)

    # Save the HTML content to a file
    html_file_path = "output.html"
    with open(html_file_path, "w") as html_file:
        html_file.write(html_content)

    webbrowser.open(html_file_path, new=2)  # 'new=2' opens the file in a new tab/window
    
# Function to update the state of the checkbox based on the global variable ibk_df
def update_ibk_checkbox_state():
    ibk_checkbox_state = tk.BooleanVar()
    if 'ibk_df' in globals() and not ibk_df.empty:
        ibk_checkbox_state.set(True)
    else:
        ibk_checkbox_state.set(False)

# Function to update the state of the checkbox based on the global variable din_df
def update_din_checkbox_state():
    din_checkbox_state = tk.BooleanVar()
    if 'din_df' in globals() and not din_df.empty:
        din_checkbox_state.set(True)
    else:
        din_checkbox_state.set(False)

# Function to update the state of the checkbox based on the global variable bbv_df
def update_bbv_checkbox_state():
    bbv_checkbox_state = tk.BooleanVar()
    if 'bbv_df' in globals() and not bbv_df.empty:
        bbv_checkbox_state.set(True)
    else:
        bbv_checkbox_state.set(False)

# Function to update the state of the checkbox based on the global variable bbv_df
def update_bcp_checkbox_state():
    bcp_checkbox_state = tk.BooleanVar()
    if 'bcp_df' in globals() and not bcp_df.empty:
        bcp_checkbox_state.set(True)
    else:
        bcp_checkbox_state.set(False)

# Function to update the state of the checkbox based on the global variable bbv_df
def update_sbk_checkbox_state():
    sbk_checkbox_state = tk.BooleanVar()
    if 'sbk_df' in globals() and not sbk_df.empty:
        sbk_checkbox_state.set(True)
    else:
        sbk_checkbox_state.set(False)