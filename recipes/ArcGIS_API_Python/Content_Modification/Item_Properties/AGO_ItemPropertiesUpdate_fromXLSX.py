'''
Author:     Wes Smith (with borrowed code from Jing Zhang)
Date:       Feb 2023

Overview:  This script was written as the 1st of a 2 script workflow for updating Ago item properties 
based on a user specified AGO group.  This script reads the item properties and writes them to an xlsx 
file.  User inputs are captured via a tkinter gui. 
'''

from arcgis.gis import GIS
import datetime, time
import os
import sys
import pandas as pd
import tkinter as tk

def main():
    
    # record start time
    start_time = time.time()
    
    print("\n\n***Running AGO Item Properties From XLSX Script***\n")

    ### PRELIMINARIES ###

    # Datestamps for filename
    datestamp = datetime.datetime.now().strftime("%Y%m%d").replace("/","")
    year = datetime.datetime.now().strftime("%Y")

    # Run the GUI to collect User Input
    # 'year' variable supplied as default value to tool's year parameter
    input_dict = run_the_gui()

    # Parameter Check
    print("Input Parameters:")
    for k, v in input_dict.items():
        if k != "ago_password":
            print(f"   {k}:  {v}")
        else:
            print(f"   {k}:  {'*' * len(v)}")

    # Sign in 
    global gis
    gis = GIS(  username=input_dict["ago_username"], 
                password=input_dict["ago_password"])

    ### PROCESS ###

    # Read in XLSX
    dataframe = xlsx_to_df(input_dict["input_xlsx"])

    # Push the updated to AGO
    update_items(dataframe)

    print("\nScript is complete...")

    # record end time
    print(f"Runtime:  {time.strftime('%Hh %Mm %Ss', time.gmtime(time.time()-start_time))}\n\n")

def xlsx_to_df(xlsx_file):
    try:
        return pd.read_excel(xlsx_file)
    except:
        print("Not able to read XLSX file.  EXITING")
        sys.quit()

def update_items(dataframe):
    print("Updateing AGO items")
    # Loop through rows in the data frame
    for index, row in dataframe.iterrows():
        print("   {}".format(row["Title"]))
        # Prepare properties dictionary
        item_properties_dict = {'title':row["Title"],\
                                'snippet':row["Summary"],\
                                'description':row["Description"],\
                                'tags':row["Tags"],\
                                'accessInformation':row["Credits"],\
                                'licenseInfo':row["Term of Use"]}
        
        # Get AGO item object by item ID, and update object properties by data frame row data
        gis.content.get(row["Item ID"]).update(item_properties_dict)

#_________________________________________________________________

def run_the_gui():
    
    def get_user_input():
        
        user_input_1 = entry1.get()
        user_input_2 = entry2.get()
        user_input_3 = entry3.get()

        global input_dict
        input_dict = {
            "input_xlsx": user_input_1.strip(),
            "ago_username":   user_input_2.upper().strip(),
            "ago_password":   user_input_3.strip(),
        }

    def quit_gui():
        root.quit()

    def combine_functions(*funcs):
    
        def combined_functions(*args, **kwargs):
            # Call the passed functions, with their arguments (if they have any)
            for func in funcs:
                func(*args, **kwargs)
    
        return combined_functions

    root = tk.Tk()
    root.title("AGO Item Properties to XLSX by Group")
    
    label1 = tk.Label(root, text="Input XLSX Path:")
    label2 = tk.Label(root, text="AGO Username:")
    label3 = tk.Label(root, text="AGO Password:")

    entry1 = tk.Entry(root)
    entry2 = tk.Entry(root)
    entry3 = tk.Entry(root, show="*")
    
    label1.grid(row=0, column=0, sticky="W")
    label2.grid(row=1, column=0, sticky="W")
    label3.grid(row=2, column=0, sticky="W")

    entry1.grid(row=0, column=1)
    entry2.grid(row=1, column=1)
    entry3.grid(row=2, column=1)

    submit_button = tk.Button(root, 
                            text="Submit", 
                            command=combine_functions(get_user_input, quit_gui))
    submit_button.grid(row=3, column=1, pady=10)

    root.mainloop()
    
    return input_dict

#_________________________________________________________________

if __name__ == '__main__':
    main()