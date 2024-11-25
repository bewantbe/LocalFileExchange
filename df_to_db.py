import pandas as pd
import sqlite3

# Read the Excel file with multiple sheets
excel_file = pd.ExcelFile('collects_mov_2.xlsx')

# Create a connection to the SQLite database
conn = sqlite3.connect('collects_mov.db')

# Iterate over each sheet and write it to the SQLite database
for sheet_name in excel_file.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df.to_sql(sheet_name, conn, if_exists='replace', index=False)

# Close the connection
conn.close()
