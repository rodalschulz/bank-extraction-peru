import tkinter as tk
from tkinter import ttk

import user_config_gui
from core_functions import *
from bank_functions import ibk_extract, din_extract, bbv_extract, bcp_extract, sbk_extract
from bank_functions import extracted_banks
from data_manipulation_functions import *
from utils.additional_functions import *

def open_test_gui():
    test_root = user_config_gui.create_test_gui()
    test_root.mainloop()

def main():
    global allbanks_extracted_df, updated_trx_df, df333, unique_rows_dfA 
    global ibk_checkbox_state, din_checkbox_state, bbv_checkbox_state 
    global bcp_checkbox_state, sbk_checkbox_state, ibk_df, din_df, bbv_df
    global bcp_df, sbk_df
    
    # Initialize ibk_df and din_df as empty DataFrames
    ibk_df = pd.DataFrame()
    din_df = pd.DataFrame()
    bbv_df = pd.DataFrame()
    bcp_df = pd.DataFrame()
    sbk_df = pd.DataFrame()
    
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Bank Data Extraction")
        
    style = ttk.Style(root)
    root.tk.call("source", "forest-dark.tcl")
    style.theme_use("forest-dark")
    
    frame = ttk.Frame(root)
    frame.pack()
    
    widgets_frame = ttk.LabelFrame(frame, text="Extract")
    widgets_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # Variables to track the state of the checkboxes
    ibk_checkbox_state = tk.BooleanVar()
    ibk_checkbox_state.set(False)
    din_checkbox_state = tk.BooleanVar()
    din_checkbox_state.set(False)
    bbv_checkbox_state = tk.BooleanVar()
    bbv_checkbox_state.set(False)
    bcp_checkbox_state = tk.BooleanVar()
    bcp_checkbox_state.set(False)
    sbk_checkbox_state = tk.BooleanVar()
    sbk_checkbox_state.set(False)

    # Row 1: IBK --------------------------------------------------------------

    ibk_checkbox = ttk.Checkbutton(widgets_frame, text="", variable=ibk_checkbox_state, state=tk.DISABLED)
    ibk_checkbox.grid(row=0, column=0, padx=(5, 0), pady=(5, 10))

    button_ibk_extract = ttk.Button(widgets_frame, text="Interbank", width=15,
                                    command=lambda: [globals().update(zip(['ibk_df', 'extracted_banks'], ibk_extract())),
                                                     globals().update(ibk_checkbox_state=update_ibk_checkbox_state())])
    button_ibk_extract.grid(row=0, column=1, padx=(0, 0), pady=(5, 10))

    button_ibk_visualize = ttk.Button(widgets_frame, text="Open", command=lambda: visualize_df_chrome(ibk_df))
    button_ibk_visualize.grid(row=0, column=2, padx=(8, 8), pady=(5, 10))

    # Row 2: DIN --------------------------------------------------------------
    din_checkbox = ttk.Checkbutton(widgets_frame, text="", variable=din_checkbox_state, state=tk.DISABLED)
    din_checkbox.grid(row=1, column=0, padx=(5, 0), pady=(0, 10))

    button_din_extract = ttk.Button(widgets_frame, text="Diners", width=15,
                                    command=lambda: [globals().update(zip(['din_df', 'extracted_banks'], din_extract())), 
                                                     globals().update(din_checkbox_state=update_din_checkbox_state())])
    button_din_extract.grid(row=1, column=1, padx=(0, 0), pady=(0, 10))

    button_din_visualize = ttk.Button(widgets_frame, text="Open", command=lambda: visualize_df_chrome(din_df))
    button_din_visualize.grid(row=1, column=2, padx=(8, 8), pady=(0, 10))
    
    # Row 3: BBVA --------------------------------------------------------------
    bbv_checkbox = ttk.Checkbutton(widgets_frame, text="", variable=bbv_checkbox_state, state=tk.DISABLED)
    bbv_checkbox.grid(row=2, column=0, padx=(5, 0), pady=(0, 10))

    button_bbv_extract = ttk.Button(widgets_frame, text="BBVA", width=15,
                                    command=lambda: [globals().update(zip(['bbv_df', 'extracted_banks'], bbv_extract())), 
                                                     globals().update(bbv_checkbox_state=update_bbv_checkbox_state())])
    button_bbv_extract.grid(row=2, column=1, padx=(0, 0), pady=(0, 10))

    button_bbv_visualize = ttk.Button(widgets_frame, text="Open", command=lambda: visualize_df_chrome(bbv_df))
    button_bbv_visualize.grid(row=2, column=2, padx=(8, 8), pady=(0, 10))
    
    # Row 4: BCP --------------------------------------------------------------
    bcp_checkbox = ttk.Checkbutton(widgets_frame, text="", variable=bcp_checkbox_state, state=tk.DISABLED)
    bcp_checkbox.grid(row=3, column=0, padx=(5, 0), pady=(0, 10))

    button_bcp_extract = ttk.Button(widgets_frame, text="BCP", width=15,
                                    command=lambda: [globals().update(zip(['bcp_df', 'extracted_banks'], bcp_extract())), 
                                                     globals().update(bcp_checkbox_state=update_bcp_checkbox_state())])
    button_bcp_extract.grid(row=3, column=1, padx=(0, 0), pady=(0, 10))

    button_bcp_visualize = ttk.Button(widgets_frame, text="Open", command=lambda: visualize_df_chrome(bcp_df))
    button_bcp_visualize.grid(row=3, column=2, padx=(8, 8), pady=(0, 10))
    
    # Row 4: SBK --------------------------------------------------------------
    sbk_checkbox = ttk.Checkbutton(widgets_frame, text="", variable=sbk_checkbox_state, state=tk.DISABLED)
    sbk_checkbox.grid(row=4, column=0, padx=(5, 0), pady=(0, 10))

    button_sbk_extract = ttk.Button(widgets_frame, text="Scotiabank", width=15,
                                    command=lambda: [globals().update(zip(['sbk_df', 'extracted_banks'], sbk_extract())), 
                                                     globals().update(sbk_checkbox_state=update_sbk_checkbox_state())])
    button_sbk_extract.grid(row=4, column=1, padx=(0, 0), pady=(0, 10))

    button_sbk_visualize = ttk.Button(widgets_frame, text="Open", command=lambda: visualize_df_chrome(sbk_df))
    button_sbk_visualize.grid(row=4, column=2, padx=(8, 8), pady=(0, 10))

    # Column 3 -------------------------------------------------------------------------------------
    output_frame = ttk.LabelFrame(frame, text="Output")
    output_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
    # Button that runs the concat_with_csv_and_update function when clicked, updating the CSV file
    testbutton = ttk.Button(output_frame, text="Update CSV", 
                            command=lambda: [globals().update(updated_trx_df=concat_with_csv_and_update(extracted_banks)),
                                            visualize_df_chrome(updated_trx_df)])
    testbutton.grid(row=0, column=3, padx=(8, 8), pady=(5, 10), sticky='ew')

    # Button that runs the compare_csv_to_pfm function when clicked
    test2button = ttk.Button(output_frame, text="New TRXs", 
                             command=lambda: [globals().update(df333=load_pfm_xlsm()),
                                             globals().update(unique_rows_dfA=compare_csv_to_pfm(updated_trx_df, df333)),
                                             visualize_df_chrome(unique_rows_dfA)])                        
    test2button.grid(row=1, column=3, padx=(8, 8), pady=(0, 10), sticky='ew')
    
    # Just the text frame
    text_frame = ttk.LabelFrame(frame, text="Info", padding=(0, 0, 0, 0))
    text_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0,10), sticky="nsew")  
    
    default_text = """
    Click on Extract for the banks of your choice. The checkbox
    activated indicates that the data has been extracted. Once
    this happens, you can proceed to Update CSV.
    """

    # Text label with instructions
    info_label = ttk.Label(text_frame, text=default_text, wraplength=800, justify='left', foreground='grey')
    info_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
       
    # Button that opens a window for user data configuration
    test3button = tk.Button(frame, text="User Config", command=lambda: open_test_gui(), width=10, ) 
    test3button.grid(row=2, column=1, padx=(0, 20), pady=(0, 10), sticky="e")
    
    root.mainloop()

if __name__ == "__main__":
    main()