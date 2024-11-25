import re
import pandas as pd

df = pd.read_excel('collects_mov.xlsx')

def extract_pattern(s):
    if not isinstance(s, str):
        return s
    #match = re.search(r'^\.*\/([a-zA-Z]+-\d+)[-a-zA-Z]*$', s)
    match = re.search(r'/([0-9a-zA-Z-_]+\d)[-.a-zA-Z]*$', s)
    if match:
        #print(match.group(1))
        return match.group(1)
    return s

col_headers = df.columns.tolist()

# remove essential empty lines in df
df = df.dropna(how='all')

# filter the 3rd column save result to 1st column
df.iloc[:,0] = df.iloc[:,2].apply(extract_pattern)

# save the file as another xlsx file
df.to_excel('collects_mov_1.xlsx', index=False)