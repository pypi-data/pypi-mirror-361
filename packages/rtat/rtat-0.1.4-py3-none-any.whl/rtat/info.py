import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import pandas as pd
import requests  
import xnat

tempDir = "/tmp"
verbose=0

def download_file(url, local_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the download was successful
        with open(local_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully to {local_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")
##########################################################################################################################
#
##########################################################################################################################
def get_file_data(host, project_id, fileName, key, identifiers, variables):
    localFileName = os.path.join(tempDir, fileName)

    # Assuming a URL for manual download, replace with your actual file URL if needed
    file_url = f"{host}/data/projects/{project_id}/resources/Excel/files/{fileName}"

    if not os.path.exists(localFileName):
        download_file(file_url, localFileName)

    #print("localFileName", localFileName)
    # Try reading the CSV file with different encodings
    #encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252', 'ascii']
    #for encoding in encodings:
    #    try:
    #        #print(f"Successfully read CSV file with encoding: {encoding}")
    #        break
    #    except UnicodeDecodeError as e:
    #        print(f"Failed to read CSV file with encoding {encoding}: {e}")
    #else:
    #    print("Failed to read CSV file with all attempted encodings.")
    #    return

    df = pd.read_csv(localFileName, low_memory=False)
    if len(identifiers) > 0 :
       filtered_df = df[df[key].isin(identifiers)]
    else:
       filtered_df = df
    extracted_values=None
    try:
       extracted_values = filtered_df[variables]
    except Exception as e:
       print(variables," not found", e)

    return extracted_values
##########################################################################################################################
#
##########################################################################################################################
def get_files (xnat_session, host, project_id, temp_dir ):

    # Assuming a URL for manual download, replace with your actual file URL if needed
    files_url = f"{host}/data/projects/{project_id}/resources/Excel/files"
    response = xnat_session.get(files_url) 

    local_files=[]
    if response.status_code == 200:
        files = response.json().get('ResultSet', {}).get('Result', [])
        for file_info in files:
            file_name = file_info['Name']
            download_url = f"{host}{file_info['URI']}"
            local_file_path = os.path.join(temp_dir, file_name)
            if verbose > 0 : print("file_name ", file_name," download_url ", download_url)

            if not os.path.exists(local_file_path):
               try:
                  download_file(download_url, local_file_path)
                  local_files.append(local_file_path)
               except Exception as e:
                  print("Failed to download ", download_url," because ",e)
            else:
               local_files.append(local_file_path)
    else:
        print(f"Failed to retrieve file list: {response.status_code}")

    return local_files

##########################################################################################################################
#
##########################################################################################################################
def get_file_headers (host, project_id, file_name ):
    local_file_name = os.path.join(tempDir, file_name)

    # Assuming a URL for manual download, replace with your actual file URL if needed
    file_url = f"{host}/data/projects/{project_id}/resources/Excel/files/{file_name}"

    if not os.path.exists(local_file_name):
        download_file(file_url, local_file_name)

    print("localFileName", local_file_name)

    df = pd.read_csv(local_file_name, nrows=0)  # Reading only the header row
    headers = df.columns.tolist()

    print("Column Headers:")
    for header in headers:
       print(header)
    return headers
##########################################################################################################################
#
##########################################################################################################################
def check_values_in_files(file_paths, pids, columns=["apid", "amrn"], num_columns=5):
    result = {}
    if num_columns < 1 : num_columns=1

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, low_memory=False)
            elif file_path.endswith('.xls') or file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                print(f"Unsupported file type: {file_name}")
                continue

            if len(columns) > 0 :
               for column in columns:
                  if column in df.columns:
                      filtered_df = df[df[column].isin(pids)]
                      if not filtered_df.empty:
                         result[file_name] = {'key': column, 'nCols':len(df.columns), 'Cols':list(df.columns)[:num_columns]}
            else:
               result[file_name] = {'nCols':len(df.columns), 'Cols':list(df.columns)[:num_columns]}
        
        except Exception as e:
            print(f"Failed to process file {file_name}: {e}")
    
    return result
