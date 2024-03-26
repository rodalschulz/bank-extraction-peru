import pandas as pd

from core_functions import load_config

# EXECUTE FUNCTION TO READ CONFIGURATION FILE
config_file_path = 'user_config.json'
config = load_config(config_file_path)
trx_csv_path = config.get("trx_csv_path")
pfm_path = config.get("pfm_path")
sheet_name = config.get("sheet_name")
columns = config.get("columns")
skip_rows = config.get("skip_rows")

def concat_extracted(df_list):
    global allbanks_extracted_df
    print("Printing...")
    #print(len(df_list))
    allbanks_extracted_df = pd.concat(df_list, ignore_index=True)  # Set ignore_index=True to reindex the resulting DataFrame
    return allbanks_extracted_df

def load_trx_csv(): # READ AND LOAD THE SAVED VERSION OF THE TRANSACTIONS
    global all_trx_df
    all_trx_df = pd.read_csv(trx_csv_path) # Use the read_csv function to read the CSV file into a DataFrame
    return all_trx_df

def extracted_to_trx_csv(): # PREPARE THE TRANSACTIONS CSV ADDING THE NEWLY EXTRACTED DATA (UPDATE IT)
    global allbanks_extracted_df, updated_trx_df
    # Concatenate extracted transactions with saved transactions
    superimposed_df = pd.concat([allbanks_extracted_df, all_trx_df], ignore_index=True)
    # Fix date column
    #superimposed_df.loc[:, 'DATE'] = pd.to_datetime(superimposed_df['DATE']).dt.date
    superimposed_df['DATE'] = pd.to_datetime(superimposed_df['DATE']).dt.date
    # Fix TIME column by replacing NaT with 00 and reformat to time
    superimposed_df['TIME'] = superimposed_df['TIME'].fillna('00:00:00')
    superimposed_df['TIME'] = pd.to_datetime(superimposed_df['TIME'].astype(str), format='%H:%M:%S').dt.time
    # Fix formatting of PEN and USD
    superimposed_df['PEN'] = pd.to_numeric(superimposed_df['PEN'], errors='coerce')
    superimposed_df['USD'] = pd.to_numeric(superimposed_df['USD'], errors='coerce')
    # Replace NaN values in 'PEN' and 'USD' columns with default value 0.0
    superimposed_df['PEN'] = superimposed_df['PEN'].fillna(0.0)
    superimposed_df['USD'] = superimposed_df['USD'].fillna(0.0)
    # Drop duplicates, sort and reset index
    superimposed_df.drop_duplicates(inplace=True)
    superimposed_df = superimposed_df.sort_values(by='DATE', ascending=False)
    updated_trx_df = superimposed_df.reset_index(drop=True)
    return updated_trx_df

def update_trx_csv():
    global updated_trx_df
    updated_trx_df.to_csv(trx_csv_path, index=False)
    print("Updated .csv file with newly extracted transactions!")
    
def concat_with_csv_and_update(df_list):
    global updated_trx_df # DEBUGGING
    if len(df_list) == 0:
        print("No new bank data extracted yet")
        load_trx_csv()
        updated_trx_df = all_trx_df
        #print(len(updated_trx_df)) # DEBUGGING
        return updated_trx_df
    else:
        concat_extracted(df_list)
        load_trx_csv()
        extracted_to_trx_csv()
        update_trx_csv()
        #print(len(updated_trx_df)) # DEBUGGING
        return updated_trx_df


def load_pfm_xlsm(): # READ AND LOAD THE PERSONAL FINANCE MODEL'S TRXS
    global df333
    sheet_name = 'TRX'
    # Read the specific table from the Excel file
    df333 = pd.read_excel(pfm_path, sheet_name=sheet_name, skiprows=int(skip_rows), usecols=columns)
    # Reformat
    df333 = df333.rename(columns={'ACCOUNT CODE': 'ACC_CODE', 'TRANSACTION NAME': 'TRX_NAME', '2ND CURRENCY': 'PEN'})
    df333['DATE'] = pd.to_datetime(df333['DATE']).dt.date
    df333['PEN'] = pd.to_numeric(df333['PEN'], errors='coerce')
    df333['USD'] = pd.to_numeric(df333['USD'], errors='coerce')
    df333['PEN'] = df333['PEN'].fillna(0.0)
    df333['USD'] = df333['USD'].fillna(0.0)
    df333 = df333.sort_values(by="DATE", ascending=False)
    return df333

def compare_csv_to_pfm(updated_csv, pfm):
    updated_csv['DATE'] = pd.to_datetime(updated_csv['DATE']).dt.date
    pfm['DATE'] = pd.to_datetime(pfm['DATE']).dt.date
    # Merge the two dataframes on the specified columns
    unique_rows_dfA = pd.merge(updated_csv, pfm, on=['ACC_CODE', 'DATE', 'TRX_NAME', 'PEN', 'USD'], how='left', indicator=True)
    
    # Select rows that are only in the left dataframe (indicator column will be 'left_only')
    unique_rows_dfA = unique_rows_dfA[unique_rows_dfA['_merge'] == 'left_only']

    # Drop the indicator column
    unique_rows_dfA = unique_rows_dfA.drop(columns=['_merge'])
    unique_rows_dfA = unique_rows_dfA.drop('TIME_y', axis=1)
    unique_rows_dfA = unique_rows_dfA.rename(columns={'TIME_x': 'TIME'})
    print("Showing new transactions...")

    return unique_rows_dfA