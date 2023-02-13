import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob

'''
I WANT THIS CODE TO:
STEP 1:
Look for all JTL files in a directory provided
Add all JTL results into a dataframe
Timestamp as an index? (is this possible or maybe duplicates)
Sorted by time into one big dataframe


STEP 2: Output some stats from the dataframe
A count of all transactions seen during the test
An average response time for each transaction
An error count

'''


#Get all the JTL files from the directory and put them in a list
jtl_files_list= []

for jtl_file in glob.glob("TestResults/2023 01 30 Peak Load Test Round 1/*.jtl"):
    jtl_files_list.append(jtl_file)

print(jtl_files_list)


#Read all the JTL files into a single data frame

jmeter_results_df = pd.concat(map(pd.read_csv, jtl_files_list))  

#Print out some details here to check it worked and if timeStamp has only unique values (it doesn't!)
print(jmeter_results_df.head())
print(jmeter_results_df["timeStamp"].is_unique)

#jmeter_results_df = pd.read_csv("TestResults/2023 01 30 Peak Load Test Round 1/20230130_TST1_160514_test_results.jtl")

#print(jmeter_results_df.iloc[1640])
#print(jmeter_results_df.columns)
