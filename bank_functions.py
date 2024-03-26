from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import undetected_chromedriver as uc

from core_functions import *

extracted_banks = []

# EXECUTE FUNCTION TO READ CONFIGURATION FILE
config_file_path = 'user_config.json'
config = load_config(config_file_path)
dni = config.get("dni")
ibk_card = config.get("ibk_card")
din_user = config.get("din_user")
bcp_card = config.get("bcp_card")

def ibk_extract():
    global ibk_df, extracted_banks
    
    # Chrome window initialization
    driver = webdriver.Chrome() # Initialize the Chrome WebDriver
    chr_options = Options()
    chr_options.add_experimental_option("detach", True) # Window stays open (?)
    url = "https://bancaporinternet.interbank.pe/login" # URL of the website xx
    driver.get(url) # Navigate to the website

    # Make necessary inputs on login (card number and dni)
    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "25")))
    card_num_box = driver.find_element(By.ID, "25")
    card_num_box.send_keys(ibk_card)
    dni_box = driver.find_element(By.ID, "39")
    dni_box.send_keys(dni)
    pass_box = driver.find_element(By.ID, "46")
    pass_box.click()

    # Use a while loop to keep checking until login is complete
    home_button_elm = "Inicio" # Define home button
    while not is_element_clickable(driver, By.LINK_TEXT, home_button_elm): 
        print("Waiting for login...")
        play_sound("attention_bell.wav") # play sound, login required
        try:
            driver.switch_to.window(driver.window_handles[0])
        except:
            return
        time.sleep(2)
    print("Logged in!")
    play_sound("logged_in_bell.wav")  # play logged in sound
    time.sleep(1.5)
    
    # Try to close up the new session pop-up message
    try:
        new_session_popup = driver.find_element(
            By.XPATH, "/html/body/div[1]/div[2]/div/div[8]/div/div/div/"
            "div/div[4]/div/div/button")
        new_session_popup.click()
    except:
        pass

    # Determine the quantity of accounts and create a dictionary
    home_button = driver.find_element(By.LINK_TEXT, "Inicio")
    accounts = driver.find_elements(By.CLASS_NAME, "account-home")
    accounts_quantity = len(accounts)
    dataframes_dict = {}

    # ANALYZE ALL ACCOUNTS AND EXTRACT DATA
    tables_dict = {}

    for x in range(0, accounts_quantity):
        # Wait for account links to be clickable
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "account-home")))
        time.sleep(0.5)
        
        # Extract the account's name and click
        account_name = driver.find_elements(
                        By.CLASS_NAME, "name-info")[x].text
        print("Analyzing " + account_name)
        account_link = driver.find_elements(
                        By.CLASS_NAME, "account-home")[x]
        account_link.click()

        # Wait for common table and see if contents are loading
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "common-table")))
        try:
            loading = driver.find_element(By.CLASS_NAME, "loading-small")
            while loading:
                loading = driver.find_element(By.CLASS_NAME, "loading-small")
                time.sleep(1)
        except:
            pass

        # Try clicking the wallet button pop up if it exists
        try: 
            wallet_button = driver.find_element(By.CLASS_NAME, 
                                                "ibk-ui-button")
            wallet_button.click()
        except:
            pass

        # Create variables
        data_table = []
        is_disabled = False

        # Check if table is empty
        time.sleep(2)
        if "No existen" in driver.find_element(
                                        By.CLASS_NAME, "common-table").text:
            print("No transactions in this account. Going back home.")
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Inicio")))
            first_word = account_name.split()[0]
            last_word = account_name.split()[-1]
            variable_dict_name = f'{first_word}_{last_word}_{x}'
            tables_dict[variable_dict_name] = data_table
            home_button.click()
            continue

        # Wait for "Anterior" button to exist 
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, 
                    "//button[@class='mdl-button mdl-js-button "
                    "ibtn ibtn--white ibtn-type-text ibtn--undefined']")))

        # Check if it's a normal account or a credit card account
        if "Cuenta" in account_name:
            account_cci = driver.find_element(
                By.CLASS_NAME, "block-acount-detail__info-cci").text
            parts = account_cci.split("-") # Split the string based on "-"
            account_short_number = parts[2][8:12] # Extract desired portion
        else:
            account_short_number = "CC"

        # While there is a next page, extract data
        while is_disabled == False:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((
                    By.XPATH, "//button[@class='mdl-button mdl-js-button "
                    "ibtn ibtn--white ibtn-type-text ibtn--undefined']")))
            
            # Populate list with all transactions from table
            table = driver.find_element(
                By.CLASS_NAME, "common-table")
            all_rows = table.find_elements(By.TAG_NAME, "tr")
            for row in all_rows:
                row_data = row.find_elements(By.TAG_NAME, "td")
                row_list = [data.text for data in row_data]
                data_table.append(row_list)
                first_word = account_name.split()[0]
                last_word = account_name.split()[-1]
                variable_dict_name = f'{first_word}_{last_word}_{x}'
                # Assign to a variable with a unique name
                tables_dict[variable_dict_name] = data_table
            
            # Find the "next page" button
            next_page_button = driver.find_elements(By.XPATH, 
                                "//button[@class='mdl-button "
                                "mdl-js-button ibtn ibtn--white " 
                                "ibtn-type-text ibtn--undefined']")[1]
            button_attrib = next_page_button.get_property("attributes")
            attribute_values = [(attribute['name'], 
                                attribute['value']) for 
                                attribute in button_attrib] 
            # Check if 'disabled' exists in list of attribute values
            is_disabled = any(attribute[0] == 'disabled' for 
                            attribute in attribute_values)
            
            if is_disabled:
                data_table = [[account_short_number] + 
                            sublist for sublist in data_table]
                tables_dict[variable_dict_name] = data_table
                print("Going back home")
                home_button.click()
            else:
                print("Analyzing next page") 
                next_page_button.click()
                time.sleep(1.5)

    print("Extraction successful")
    # Remove nested lists with only 1 element
    for table_name, table_data in tables_dict.items():
        tables_dict[table_name] = [nested_list for nested_list in 
                                table_data if len(nested_list) > 2]
        
    # Add columns to each kind of account table to total 6 columns each
    for table in tables_dict.keys():
        if 'Cuenta' in table and 'Soles' in table:
            tables_dict[table] = [sublist[:1] + ['PEN'] + sublist[1:] for sublist in tables_dict[table]]
            tables_dict[table] = [sublist + [0] for sublist in tables_dict[table]]
        elif 'Cuenta' in table and 'Dólares' in table:
            tables_dict[table] = [sublist[:1] + ['USD'] + sublist[1:] for sublist in tables_dict[table]]
            tables_dict[table] = [sublist[:-1] + [0] + sublist[-1:] for sublist in tables_dict[table]]
        else:
            tables_dict[table] = [sublist[:1] + [''] + sublist[1:] for sublist in tables_dict[table]]
            tables_dict[table] = [nested_list for nested_list in tables_dict[table] if 'en proceso' not in ' '.join(map(str, nested_list)).lower()]
            for nested_list in tables_dict[table]:
                if nested_list[-1] == '':
                    nested_list[1] = 'PEN'
                else:
                    nested_list[1] = 'USD'

    all_tables = []
    for table in tables_dict.values():
        for row in table:
            all_tables.append(row)

    for nested_list in all_tables:
        # Check the type of the fifth element
        if isinstance(nested_list[-2], str):
        # Remove 'S/ ' and ',' from the fifth element
            nested_list[-2] = nested_list[-2].replace('S/ ', '').replace(',', '').replace('+', '')
        # Check the type of the sixth element
        if isinstance(nested_list[-1], str):
        # Remove 'US$ ' and ',' from the sixth element
            nested_list[-1] = nested_list[-1].replace('US$ ', '').replace(',', '').replace('+', '')
        # '' with 0
        if nested_list[5] == '':
            nested_list[5] = 0
        if nested_list[4] == '':
            nested_list[4] = 0
        # Separate day and time
        if nested_list[3][-1:].isdigit(): 
            time_data = nested_list[3][-5:]
            nested_list[3] = nested_list[3][5:-6]
            nested_list.insert(4, time_data)
        else:
            nested_list[3] = nested_list[3][5:]
            nested_list.insert(4, '00:00')
        # Adjust date formatting and year
        nested_list[3] = adjust_date(nested_list[3])
        # Add 'IBK' as first element
        nested_list.insert(0, 'IBK')

    # Join the first three elements with '.' separator
    all_tables = [[col[0] + '.' + col[1] + '.' + col[2]] + col[3:] for col in all_tables]

    # Differentiate duplicates
    all_tables = enumerate_duplicates(all_tables, 1)
    
    # Convert to a dataframe
    ibk_df = pd.DataFrame(all_tables)
    ibk_df.columns = ['ACC_CODE', 'TRX_NAME', 'DATE', 'TIME', 'PEN', 'USD']
    ibk_df = ibk_df[['ACC_CODE', 'DATE', 'TIME', 'TRX_NAME', 'PEN', 'USD']]
    fix_bank_df_formatting(ibk_df)
    
    
    
    # Convert DataFrames to strings
    ibk_df_str = ibk_df.to_string()
    # Convert list of DataFrames to strings
    extracted_banks_str = [df.to_string() for df in extracted_banks]
    # Checking if df is in the list
    if ibk_df_str in extracted_banks_str:
        print("Already in list")
    else:
        extracted_banks.append(ibk_df)
    print(f"Total banks extracted: {len(extracted_banks)}")
    play_sound("finish_bell.wav")
     
    return ibk_df, extracted_banks
    
    
def din_extract():
    global din_df, extracted_banks

    # Chrome window initialization
    chr_options = Options()
    chr_options.add_argument("--window-size=1200,800")
    driver = webdriver.Chrome(options=chr_options) # Initialize the Chrome WebDriver
    url = "https://zonaseguradiners.pe/#/login" # URL of the website xx
    #driver.maximize_window()
    driver.get(url) # Navigate to the website

    user_num_box = driver.find_element(By.XPATH, # find user input box
                "/html/body/div[1]/div[1]/div/div[3]/"
                "div/form/div[2]/div/div[2]/div/input")
    user_num_box.send_keys(din_user) # send the user info

    # Use a while loop to keep checking until login is complete
    home_button_elm = "MIS PRODUCTOS"
    while not is_element_clickable(driver, By.LINK_TEXT, home_button_elm):
        print("Waiting for login...")
        play_sound("attention_bell.wav")
        try:
            driver.switch_to.window(driver.window_handles[0])
        except:
            return
        time.sleep(2)
    print("Logged in!")
    play_sound("logged_in_bell.wav")  # play logged in sound

    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Estado de Cuenta")))
    bank_statement_btn = driver.find_element(By.LINK_TEXT, "Estado de Cuenta")
    time.sleep(0.5)
    bank_statement_btn.click()

    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Mis Movimientos")))
    my_transactions_btn = driver.find_element(By.LINK_TEXT, "Mis Movimientos")
    time.sleep(0.5)
    my_transactions_btn.click()

    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "cabecera_select")))
    drop_down = driver.find_element(By.ID, "cabecera_select")
    time.sleep(0.5)
    drop_down.click()

    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Últimos 3 meses")))
    month_period = driver.find_element(By.LINK_TEXT, "Últimos 3 meses")
    month_period.click()
    search_btn = driver.find_element(By.LINK_TEXT, "Buscar")
    search_btn.click()
        
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "tabla-actividad")))
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'i.icon1-flecha-right')))
    time.sleep(1.5)

    no_more_pages = len(driver.find_elements(By.CSS_SELECTOR, 'a.disabled_paginador i.icon1-flecha-right'))
    data_table = []

    while no_more_pages == 0:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tabla-actividad")))
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.icon1-flecha-right')))
        # Populate a list with all transactions
        table = driver.find_element(By.CLASS_NAME, "tabla-actividad")
        all_rows = table.find_elements(By.TAG_NAME, "tr")
        for row in all_rows:
            row_data = row.find_elements(By.TAG_NAME, "td")
            row_list = [data.text for data in row_data]
            data_table.append(row_list)
        time.sleep(0.5)
        no_more_pages = len(driver.find_elements(By.CSS_SELECTOR, 'a.disabled_paginador i.icon1-flecha-right'))
        if no_more_pages == 1:
            break
        next_page = driver.find_element(By.CSS_SELECTOR, 'i.icon1-flecha-right')
        print("Analyzing next page")
        next_page.click()  
    
    data_table = [nested_list for nested_list in data_table if len(nested_list) > 2]
    data_table = [nested_list[1:] for nested_list in data_table]

    for nested_list in data_table:
        if nested_list[-1] == '':
            nested_list[-1] = 0
        if nested_list[-2] == '':
            nested_list[-2] = 0
        # Popping unnecessary elements
        nested_list.pop(4)
        nested_list.pop(3)
        nested_list.pop(1)
        # Adding USD or PEN depending on trx
        if nested_list[-1] == 0:
            nested_list.insert(0, 'USD')
        else:
            nested_list.insert(0, 'PEN')
        # Adding required elements
        nested_list.insert(0, 'CC')
        nested_list.insert(0, 'DIN')
        # INVERT POLARITY
        elem_5 = float(nested_list[-2])
        elem_6 = float(nested_list[-1])
        # Check if the element is negative, then remove the "-"
        if elem_5 < 0:
            nested_list[-2] = str(abs(elem_5))
        elif elem_5 > 0:
            nested_list[-2] = "-" + str(elem_5)
        # Check if the element is negative, then remove the "-"
        if elem_6 < 0:
            nested_list[-1] = str(abs(elem_6))
        elif elem_6 > 0:
            nested_list[-1] = "-" + str(elem_6)
        # Adjust date formatting and year
        nested_list[3] = adjust_date(nested_list[3].lower())
        # Add default time
        nested_list.insert(4, '00:00')

    # Join the first three elements with '.' separator
    data_table = [[col[0] + '.' + col[1] + '.' + col[2]] + col[3:] for col in data_table]

    # Differentiate duplicates by enumerating
    data_table = enumerate_duplicates(data_table, 3)
    
    din_df = pd.DataFrame(data_table)
    din_df.columns = ['ACC_CODE', 'DATE', 'TIME', 'TRX_NAME', 'USD', 'PEN']
    din_df = din_df[['ACC_CODE', 'DATE', 'TIME', 'TRX_NAME', 'PEN', 'USD']]
    fix_bank_df_formatting(din_df)
    
        
    
    # Convert DataFrames to strings
    din_df_str = din_df.to_string()
    # Convert list of DataFrames to strings
    extracted_banks_str = [df.to_string() for df in extracted_banks]
    # Checking if df is in the list
    if din_df_str in extracted_banks_str:
        print("Already in list")
    else:
        extracted_banks.append(din_df)
    print(f"Total banks extracted: {len(extracted_banks)}")
    play_sound("finish_bell.wav")
    
    return din_df, extracted_banks


def bbv_extract():
    global bbv_df, extracted_banks

    options = uc.ChromeOptions() 
    options.headless = False  # Set headless to False to run in non-headless mode
    url = "https://www.bbva.pe/personas/acceso-banca-por-internet.html"
    driver = uc.Chrome(use_subprocess=True, options=options) 
    driver.get(url)
    driver.set_window_size(1200, 800)

    login_block = True
    while login_block == True:
        try:
            driver.switch_to.window(driver.window_handles[1])
            login_block = False
        except:
            print("Waiting for login...")
            play_sound("attention_bell.wav")
            try:
                driver.switch_to.window(driver.window_handles[0])
            except:
                return
            time.sleep(2)
    print("Login sent")

    login_block_2 = True
    while login_block_2 == True:
        try:
            close_ad = driver.find_element(By.XPATH, "/html/body/div[6]/div/div/div/div[1]/button")
            close_ad.click()
            login_block_2 = False
        except:
            print("Checking login...")
            time.sleep(1)
    print("Login successful!")
    play_sound("logged_in_bell.wav")

    WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "close-icon")))

    close_tutorial = driver.find_elements(By.CLASS_NAME, "close-icon")[-1]
    close_tutorial.click()

    cuentas = driver.find_element(By.LINK_TEXT, "Cuentas")
    cuentas.click()

    WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "content-column")))

    normal_accounts = driver.find_elements(By.CLASS_NAME, "link")
    acc_quantity = len(normal_accounts)
    print(f"Total normal accounts detected: {acc_quantity}")

    normal_tables_dict = {}
    data_table_1 = []

    # Extract normal accounts
    for x in range(0, acc_quantity):
        account_names = driver.find_elements(By.ID, "print-section")[x]
        text = account_names.text
        parts = text.split('\n')
        first_part = parts[0]
        print(f"Analyzing: {first_part}")

        acc_digits = driver.find_elements(By.CLASS_NAME, "producto")[x].text
        parts = acc_digits.split('\n')
        first_part = parts[0]
        acc_4_digits = first_part[-4:]

        curr_symbol = driver.find_elements(
                    By.CLASS_NAME, "saldo-total-cuentas")[0].text[0:3]
        if curr_symbol == 'S/ ':
            currency = 'PEN'
            curr_name = 'Soles'
        elif curr_symbol == 'US$':
            currency = 'USD'
            curr_name = 'Dólares'
        
        normal_accounts = driver.find_elements(By.CLASS_NAME, "link")[x]
        normal_accounts.click()
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sortable")))
        
        # Populate a list with all transactions
        table = driver.find_element(By.CLASS_NAME, "sortable")
        all_rows = table.find_elements(By.TAG_NAME, "tr")
        for row in all_rows:
            row_data = row.find_elements(By.TAG_NAME, "td")
            row_list = [data.text for data in row_data]
            data_table_1.append(row_list)
            
        cuentas = driver.find_element(By.LINK_TEXT, "Cuentas")
        cuentas.click()
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "content-column")))

        data_table_1 = [sublist for sublist in 
                                data_table_1 if len(sublist) > 1]
        data_table_1 = [[currency] + 
                sublist for sublist in data_table_1]
        data_table_1 = [[acc_4_digits] + 
                    sublist for sublist in data_table_1]
        variable_dict_name = f'Cuenta_{curr_name}_{x}'
        # Assign to a variable with a unique name
        normal_tables_dict[variable_dict_name] = data_table_1


    tarjetas = driver.find_element(By.LINK_TEXT, "Tarjetas")
    tarjetas.click()
    time.sleep(1)
    WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "content-column")))

    credit_accounts = driver.find_elements(By.CLASS_NAME, "progress-bar-default")
    acc_quantity = len(credit_accounts)
    print(f"Total credit accounts detected: {acc_quantity}")

    credit_tables_dict = {}
    data_table_2 = []

    # Extract credit accounts
    for x in range(0, acc_quantity):
        account_names = driver.find_elements(By.CLASS_NAME, "link")[x]
        text = account_names.text
        print(f"Analyzing Credit Card Account related to: {text}")
        account_names.click()
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "content-column")))
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        time.sleep(1)

        frame = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(frame)
        time.sleep(2)
        account_names = driver.find_element(By.ID, "app__content")
        input_text = account_names.text

        # Split the input text into lines
        lines = input_text.split('\n')
        # Iterate through the lines, excluding the first four lines (header)
        for i in range(4, len(lines), 3):
            # Extract the three elements for each row
            fecha = lines[i]
            descripcion = lines[i + 1]
            monto = lines[i + 2]
            # Append the row to the table list
            data_table_2.append([fecha, descripcion, monto])
        
        driver.switch_to.default_content()
        
        tarjetas = driver.find_element(By.LINK_TEXT, "Tarjetas")
        tarjetas.click()
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "content-column")))

        data_table_2 = [['CC'] + sublist for sublist in data_table_2]
        data_table_2 = [sublist + [''] for sublist in data_table_2]
        
        variable_dict_name = f'CC_{x}'
        # Assign to a variable with a unique name
        credit_tables_dict[variable_dict_name] = data_table_2

    driver.quit()
    print("Extraction finished")
    
    # Add columns to each credit account tables to total 6 columns
    for table in credit_tables_dict.keys():
        credit_tables_dict[table] = [sublist[:1] + [''] + sublist[1:] for sublist in credit_tables_dict[table]]
        for sublist in credit_tables_dict[table]:
            if sublist[-1] == '':
                sublist[1] = 'PEN'
            else:
                sublist[1] = 'USD'

    all_tables = []
    credit_tables = []
    for table in normal_tables_dict.values():
        for row in table:
            all_tables.append(row)
    for table in credit_tables_dict.values():
        for row in table:
            credit_tables.append(row)
    for row in credit_tables:
        all_tables.append(row)


    for nested_list in all_tables:
        nested_list.insert(0, 'BBV')
        nested_list.insert(4, '00:00')
        nested_list[-2] = nested_list[-2].replace('S/ ', '').replace(',', '').replace('+', '')
        nested_list[-1] = nested_list[-1].replace('US$ ', '').replace(',', '').replace('+', '')
        if nested_list[-2] == '':
            nested_list[-2] = 0
        if nested_list[-1] == '':
            nested_list[-1] = 0
        if 'CC' in nested_list[1]:
            if float(nested_list[-2]) > 0:
                nested_list[-2] = '-' + nested_list[-2]
            elif float(nested_list[-2]) < 0:
                nested_list[-2] = str(abs(float(nested_list[-2])))
            if float(nested_list[-1]) > 0:
                nested_list[-1] = '-' + nested_list[-2]
            elif float(nested_list[-1]) < 0:
                nested_list[-1] = str(abs(float(nested_list[-2])))
            
    # Join the first three elements with '.' separator
    all_tables = [[col[0] + '.' + col[1] + '.' + col[2]] + col[3:] for col in all_tables]

    # Differentiate duplicates
    all_tables = enumerate_duplicates(all_tables, 1)

    bbv_df = pd.DataFrame(all_tables)
    bbv_df.columns = ['ACC_CODE', 'DATE', 'TIME', 'TRX_NAME', 'PEN', 'USD']
    fix_bank_df_formatting(bbv_df)
    
    
    # Convert DataFrames to strings
    bbv_df_str = bbv_df.to_string()
    # Convert list of DataFrames to strings
    extracted_banks_str = [df.to_string() for df in extracted_banks]
    # Checking if df is in the list
    if bbv_df_str in extracted_banks_str:
        print("Already in list")
    else:
        extracted_banks.append(bbv_df)
    print(f"Total banks extracted: {len(extracted_banks)}")
    play_sound("finish_bell.wav")
    
    return bbv_df, extracted_banks


def bcp_extract():
    global bcp_df, extracted_banks

    # Chrome window initialization
    driver = webdriver.Chrome() # Initialize the Chrome WebDriver
    url = "https://www.viabcp.com/canales/banca-por-internet" # URL of the website xx
    driver.get(url) # Navigate to the website

    driver.find_element(By.LINK_TEXT, 'Banca').click()

    WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'custom-control-label-radio')))
    
    person_checkbox = driver.find_element(By.CLASS_NAME, 'custom-control-label-radio')
    person_checkbox.click()

    WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, "//input[@class='form-control']")))

    #dni_box = driver.find_element(By.CLASS_NAME, 'form-control')
    dni_box = driver.find_element(By.XPATH, "//input[@class='form-control']")
    dni_box.send_keys(dni)

    card_num_box = driver.find_element(By.XPATH, "//input[@class='form-control ng-untouched ng-pristine ng-invalid']")
    card_num_box.send_keys(bcp_card)

    # Use a while loop to keep checking until login is complete
    home_button_elm = "bcp_btn_aceptar" # Define home button
    while not is_element_clickable(driver, By.CLASS_NAME, home_button_elm): 
        print("Waiting for login...")
        play_sound("attention_bell.wav")
        try:
            driver.switch_to.window(driver.window_handles[0])
        except:
            return
        time.sleep(2)
    print("Logged in!")
    play_sound("logged_in_bell.wav")
    time.sleep(1.5)

    accept_cookies = driver.find_element(By.CLASS_NAME, 'bcp_btn_aceptar')
    accept_cookies.click()

    not_for_now = driver.find_element(By.CLASS_NAME, 'btn-outline-primary')
    not_for_now.click()

    all_products = driver.find_element(By.CLASS_NAME, 'btn-text')
    all_products.click()

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//bcp-card[@class='pointer-cursor hydrated']")))
    time.sleep(1)

    acc_quantity = len(driver.find_elements(By.XPATH, "//bcp-card[@class='pointer-cursor hydrated']"))

    tables_dict = {}

    for x in range(0, acc_quantity):
        acc = driver.find_elements(
                        By.XPATH, "//bcp-card[@class='pointer-cursor hydrated']")[x]
        curr_symbol = acc.text.split('\n')[-1][0:2]
        acc_name = acc.text.split('\n')[0]
        print(f"Analyzing: {acc_name}")
        acc.click()
    
        # Wait for common table and see if contents are loading
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-card-wrapper")))
        
        acc_number = driver.find_element(
                        By.XPATH, "//p[@class='paragraph-md bcp-font-regular text']").text
        acc_4_digits = acc_number[-4:]
        
        data_table = []

        if curr_symbol == 'S/':
            currency = 'PEN'
        elif curr_symbol == '$ ':
            currency = 'USD'
        
        all_trx = driver.find_elements(By.CLASS_NAME, 'product-card-wrapper')
        
        for trx in all_trx:
            text = trx.text
            text_split = text.split('\n')
            date = text_split[3]
            name = text_split[1]
            amount = text_split[4]
            sublist = [date, name, amount]
            data_table.append(sublist)

        for sublist in data_table:
            sublist.insert(0, acc_4_digits)
        
        variable_dict_name = f'Cuenta_{currency}_{x}'
        # Assign to a variable with a unique name
        tables_dict[variable_dict_name] = data_table

        button_back = driver.find_elements(By.XPATH, "//button[@class='btn btn-text-secondary']")[1]
        button_back.click()

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//bcp-card[@class='pointer-cursor hydrated']")))

    print("Extraction finished")

    # Add columns to each kind of account table to total 6 columns each
    for table in tables_dict.keys():
        if 'Cuenta' in table and 'PEN' in table:
            tables_dict[table] = [sublist[:1] + ['PEN'] + sublist[1:] for sublist in tables_dict[table]]
            tables_dict[table] = [sublist + [0] for sublist in tables_dict[table]]
        elif 'Cuenta' in table and 'USD' in table:
            tables_dict[table] = [sublist[:1] + ['USD'] + sublist[1:] for sublist in tables_dict[table]]
            tables_dict[table] = [sublist[:-1] + [0] + sublist[-1:] for sublist in tables_dict[table]]

    all_tables = []
    for table in tables_dict.values():
        for row in table:
            all_tables.append(row)


    for nested_list in all_tables:
        # Check the type of the fifth element
        if isinstance(nested_list[-2], str):
        # Remove 'S/ ' and ',' from the fifth element
            nested_list[-2] = nested_list[-2].replace('S/ ', '').replace(',', '').replace('+', '')
        # Check the type of the sixth element
        if isinstance(nested_list[-1], str):
        # Remove '$ ' and ',' from the sixth element
            nested_list[-1] = nested_list[-1].replace('$ ', '').replace(',', '').replace('+', '')
        
        day = nested_list[2].split(' ')[0]
        month = nested_list[2].split(' ')[1][0:3].lower()
        date = day + ' ' + month
        nested_list[2] = adjust_date(date)

        # Add default time
        nested_list.insert(3, '00:00')
        
        # Add 'BCP' as first element
        nested_list.insert(0, 'BCP')


    # Join the first three elements with '.' separator
    all_tables = [[col[0] + '.' + col[1] + '.' + col[2]] + col[3:] for col in all_tables]

    # Differentiate duplicates
    all_tables = enumerate_duplicates(all_tables, 1)


    bcp_df = pd.DataFrame(all_tables)
    bcp_df.columns = ['ACC_CODE', 'DATE', 'TIME', 'TRX_NAME', 'PEN', 'USD']
    fix_bank_df_formatting(bcp_df)
    

    # Convert DataFrames to strings
    bcp_df_str = bcp_df.to_string()
    # Convert list of DataFrames to strings
    extracted_banks_str = [df.to_string() for df in extracted_banks]
    # Checking if df is in the list
    if bcp_df_str in extracted_banks_str:
        print("Already in list")
    else:
        extracted_banks.append(bcp_df)
    print(f"Total banks extracted: {len(extracted_banks)}")
    play_sound("finish_bell.wav")
    
    return bcp_df, extracted_banks


def sbk_extract():
    global sbk_df, extracted_banks
    
    options = uc.ChromeOptions()
    options.headless = False  # Set headless to False to run in non-headless mode
    url = "https://mi.scotiabank.com.pe/login"
    driver = uc.Chrome(use_subprocess=True, options=options)
    driver.get(url)
    driver.set_window_size(1200, 800)
    
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/joy-login[1]/main/app-login/div/app-welcome/joy-progress-box/mat-card/section[1]/form/mat-form-field[2]/div/div[1]/div/input')))
    
    dni_box = driver.find_element(By.XPATH, '/html/body/joy-login[1]/main/app-login/div/app-welcome/joy-progress-box/mat-card/section[1]/form/mat-form-field[2]/div/div[1]/div/input')
    dni_box.send_keys(dni)
    
    button_continue = driver.find_element(By.XPATH, "//button[@class='mat-focus-indicator mat-raised-button mat-button-base mat-primary']")
    button_continue.click()
    
    # Use a while loop to keep checking until login is complete
    home_button_elm = "//div[@class='product-card hub-card ng-star-inserted']" # Define home button
    while not is_element_clickable(driver, By.XPATH, home_button_elm): 
        print("Waiting for login...")
        play_sound("attention_bell.wav") # play sound, login required
        try:
            driver.switch_to.window(driver.window_handles[0])
        except:
            return
        time.sleep(2)
    print("Logged in!")
    play_sound("logged_in_bell.wav")  # play logged in sound
    time.sleep(2)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[4]/div/mat-dialog-container/app-whats-new/div/div[2]/button")))

    btn_underst = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/mat-dialog-container/app-whats-new/div/div[2]/button")
    btn_underst.click()
    
    btn_cancel = driver.find_element(By.ID, 'cancel-button')
    btn_cancel.click()
    
    credit_cards = driver.find_element(By.XPATH, "//div[@class='product-card hub-card ng-star-inserted']")
    credit_cards.click()

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='product-card product-card-dialog']")))

    cards_quantity = len(driver.find_elements(By.XPATH, "//div[@class='product-card product-card-dialog']"))
    cards_quantity

    credit_tables_dict = {}

    for x in range(0, cards_quantity):
        card = driver.find_elements(By.XPATH, "//div[@class='product-card product-card-dialog']")[x]
        card_num = card.text.split('\n')[0][-4:]
        print(f'Analyzing credit card: {card_num}')
        card.click()

        WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/joy-channels/main/app-user/div/div/app-dashboard/app-side-accounts-menu/mat-sidenav-container/mat-sidenav-content/div/app-product-credit-card-detail/app-product-template/div[2]/div/app-product-transactions-template[1]/div[2]/app-product-transactions/div[2]")))
        
        table_scroll = driver.find_element(By.XPATH, "/html/body/joy-channels/main/app-user/div/div/app-dashboard/app-side-accounts-menu/mat-sidenav-container/mat-sidenav-content/div/app-product-credit-card-detail/app-product-template/div[2]/div/app-product-transactions-template[1]/div[2]/app-product-transactions/div[2]")
        
        driver.execute_script("arguments[0].scrollTo(0,18000);", table_scroll)
        WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/joy-channels/main/app-user/div/div/app-dashboard/app-side-accounts-menu/mat-sidenav-container/mat-sidenav-content/div/app-product-credit-card-detail/app-product-template/div[2]/div/app-product-transactions-template[1]/div[2]/app-product-transactions/div[2]")))
        time.sleep(1)
        driver.execute_script("arguments[0].scrollTo(0,18000);", table_scroll)
        WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/joy-channels/main/app-user/div/div/app-dashboard/app-side-accounts-menu/mat-sidenav-container/mat-sidenav-content/div/app-product-credit-card-detail/app-product-template/div[2]/div/app-product-transactions-template[1]/div[2]/app-product-transactions/div[2]")))
        time.sleep(1)
        driver.execute_script("arguments[0].scrollTo(0,18000);", table_scroll)
        WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/joy-channels/main/app-user/div/div/app-dashboard/app-side-accounts-menu/mat-sidenav-container/mat-sidenav-content/div/app-product-credit-card-detail/app-product-template/div[2]/div/app-product-transactions-template[1]/div[2]/app-product-transactions/div[2]")))
        time.sleep(1)
        driver.execute_script("arguments[0].scrollTo(0,18000);", table_scroll)
        WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/joy-channels/main/app-user/div/div/app-dashboard/app-side-accounts-menu/mat-sidenav-container/mat-sidenav-content/div/app-product-credit-card-detail/app-product-template/div[2]/div/app-product-transactions-template[1]/div[2]/app-product-transactions/div[2]")))
        

        # Populate list with all transactions from table
        data_table = []
        table = driver.find_element(
            By.ID, "table-transactions")
        all_rows = table.find_elements(By.TAG_NAME, "tr")
        for row in all_rows:
            row_data = row.find_elements(By.TAG_NAME, "td")
            row_list = [data.text for data in row_data]
            data_table.append(row_list)
            
            variable_dict_name = f'CC{x+1}_{card_num}'
            # Assign to a variable with a unique name
            credit_tables_dict[variable_dict_name] = data_table

        credit_cards = driver.find_element(By.XPATH, "//div[@class='product-card hub-card ng-star-inserted']")
        credit_cards.click()
        
    for pair in credit_tables_dict.items():
        card_id = pair[0][:3]
        for row in pair[1]:
            row[0] = card_id

    all_tables = []
    for table in credit_tables_dict.values():
        for row in table:
            all_tables.append(row)
            
    for row in all_tables:
        if 'procesar' in row[1]:
            all_tables.remove(row)

    for row in all_tables:
        row.insert(0, 'SBK')
        if '1' in row[1]:
            row[1] = row[1][0:2]
        if row[3][0:2] == 'S/':
            row.insert(2, 'PEN')
        elif row[3][0:2] == 'US':
            row.insert(2,'USD')
        row[0] = row[0] + '.' + row[1] + '.' + row[2]
        row.remove(row[1])
        row.remove(row[1])
        datex = row[1].split('\n')[1][:6]
        row[1] = row[1].split('\n')[0]
        row.insert(1, datex)
        row[1] = adjust_date(row[1])
        row.insert(2, '00:00')
        row[3] = row[3].rstrip()
        # Check the type of the sixth element
        if isinstance(row[-1], str):
        # Remove 'US$ ' and ',' from the sixth element
            row[-1] = row[-1].replace('US$ ', '').replace(',', '').replace('+', '').replace('S/ ', '')
        if row[0][-3:] == 'PEN':
            row.append(0)
        elif row[0][-3:] == 'USD':
            usd_amount = row[4]
            row[4] = 0
            row.append(usd_amount)

    # Differentiate duplicates
    all_tables = enumerate_duplicates(all_tables, 1)

    sbk_df = pd.DataFrame(all_tables)
    sbk_df.columns = ['ACC_CODE', 'DATE', 'TIME', 'TRX_NAME', 'PEN', 'USD']
    fix_bank_df_formatting(sbk_df)
    
    # Convert DataFrames to strings
    sbk_df_str = sbk_df.to_string()
    # Convert list of DataFrames to strings
    extracted_banks_str = [df.to_string() for df in extracted_banks]
    # Checking if df is in the list
    if sbk_df_str in extracted_banks_str:
        print("Already in list")
    else:
        extracted_banks.append(sbk_df)
    print(f"Total banks extracted: {len(extracted_banks)}")
    play_sound("finish_bell.wav")
    
    return sbk_df, extracted_banks
    

# # Function to generate an ibk DataFrame and assign it to a global variable
# def ibk_extract():
#     global ibk_df, extracted_banks
#     # Your DataFrame generation logic here
#     data = {'Column1': [1, 2, 3], 'Column2': ['A', 'B', 'C']}
#     ibk_df = pd.DataFrame(data)
    

#     # Convert DataFrames to strings
#     ibk_df_str = ibk_df.to_string()
#     # Convert list of DataFrames to strings
#     extracted_banks_str = [df.to_string() for df in extracted_banks]

#     # Checking if df1 is in the list
#     if ibk_df_str in extracted_banks_str:
#         print("Already in list")
#     else:
#         extracted_banks.append(ibk_df)
    
#     print(len(extracted_banks))
#     return ibk_df, extracted_banks

# # Function to generate an IBK DataFrame and assign it to a global variable
# def din_extract():
#     global din_df, extracted_banks
#     # Your DataFrame generation logic here
#     data = {'Column1': [4, 5, 6], 'Column2': ['A', 'B', 'C']}
#     din_df = pd.DataFrame(data)
    

#     # Convert DataFrames to strings
#     din_df_str = din_df.to_string()
#     # Convert list of DataFrames to strings
#     extracted_banks_str = [df.to_string() for df in extracted_banks]

#     # Checking if df1 is in the list
#     if din_df_str in extracted_banks_str:
#         print("Already in list")
#     else:
#         extracted_banks.append(din_df)
    
#     print(len(extracted_banks))
    
#     return din_df, extracted_banks


